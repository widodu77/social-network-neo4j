# How the Social Network System Works - Complete Guide

## Table of Contents
1. [System Startup Flow](#system-startup-flow)
2. [Request Flow (End-to-End)](#request-flow)
3. [Data Layer (Neo4j)](#data-layer)
4. [Business Logic Layer (Services)](#business-logic-layer)
5. [API Layer (FastAPI)](#api-layer)
6. [Proxy Layer (Nginx)](#proxy-layer)
7. [How Tests Work](#how-tests-work)
8. [How Data Seeding Works](#how-data-seeding-works)

---

## 1. System Startup Flow

### When you run `docker-compose up -d`:

```
Step 1: Docker Compose reads docker-compose.yml
   ↓
Step 2: Creates Docker network: "social-network" (bridge)
   ↓
Step 3: Creates volumes for persistent data
   ↓
Step 4: Starts Neo4j container (first!)
   ↓
Step 5: Waits for Neo4j healthcheck to pass
   ↓
Step 6: Builds & starts FastAPI container
   ↓
Step 7: Starts Nginx container
   ↓
Step 8: System ready!
```

### Why This Order Matters:

**Neo4j starts first** because:
```yaml
# In docker-compose.yml
api:
  depends_on:
    neo4j:
      condition: service_healthy  # API waits for Neo4j to be healthy
```

If API started before Neo4j, connection would fail!

---

## 2. Request Flow (End-to-End)

Let's trace: `GET http://localhost/api/users?limit=5`

### Layer 1: Nginx (Reverse Proxy)

```
Browser sends: GET http://localhost/api/users?limit=5
                    ↓
            Nginx receives on port 80
                    ↓
        Checks nginx.conf for routing
```

**In `nginx/nginx.conf`:**
```nginx
location /api/ {
    limit_req zone=api_limit burst=20 nodelay;  # Rate limit check
    proxy_pass http://api;  # Forward to FastAPI
}
```

**What happens:**
1. **Rate limiting**: Checks if user exceeded 10 requests/second
   - If yes: Return 429 (Too Many Requests)
   - If no: Continue
2. **Security headers**: Adds X-Frame-Options, X-XSS-Protection
3. **Forwards request** to `http://api:8000/api/users?limit=5`

**Key concept:** `api` resolves to `api:8000` because they're on same Docker network!

---

### Layer 2: FastAPI (Application Server)

```
Request arrives: http://api:8000/api/users?limit=5
                        ↓
                FastAPI main.py
                        ↓
                Router matching
```

**In `app/main.py`:**
```python
# Line 67: Router registration
app.include_router(users.router, prefix="/api", tags=["Users"])
```

**What this means:**
- Request path: `/api/users`
- FastAPI strips `/api` prefix (handled by main.py)
- Routes remaining `/users` to `users.router`

**In `app/routers/users.py`:**
```python
@router.get("/users", response_model=List[User])
async def list_users(
    limit: int = Query(100, ge=1, le=1000),  # ge=greater or equal, le=less or equal
    offset: int = Query(0, ge=0),
):
```

**Validation happens here:**
- `limit=5` → Valid (1 ≤ 5 ≤ 1000) ✅
- If `limit=9999` → Invalid! Returns 422 error ❌

**Parameter extraction:**
- `?limit=5` → `limit = 5`
- No offset in URL → `offset = 0` (default)

**Then:**
```python
return user_service.list_users(limit=5, offset=0)
```

---

### Layer 3: Service Layer (Business Logic)

```
Call: user_service.list_users(limit=5, offset=0)
              ↓
    app/services/user_service.py
              ↓
    Constructs Cypher query
              ↓
    Executes on Neo4j
```

**In `app/services/user_service.py`:**
```python
def list_users(self, limit: int = 100, offset: int = 0) -> List[User]:
    query = """
    MATCH (u:User)
    OPTIONAL MATCH (u)-[:KNOWS]-(conn:User)
    OPTIONAL MATCH (u)-[:HAS_SKILL]->(s:Skill)
    WITH u, COUNT(DISTINCT conn) AS connection_count, COUNT(DISTINCT s) AS skill_count
    RETURN u.user_id, u.name, u.email, u.title, u.location, u.bio,
           connection_count, skill_count
    ORDER BY u.name
    SKIP $offset
    LIMIT $limit
    """

    with self.driver.session() as session:
        result = session.run(query, limit=5, offset=0)
```

**Breaking down the Cypher query:**

```cypher
MATCH (u:User)
```
- Find all nodes with label `User`
- Think of it like: `SELECT * FROM users` in SQL

```cypher
OPTIONAL MATCH (u)-[:KNOWS]-(conn:User)
```
- For each user, find connections via KNOWS relationship
- `OPTIONAL` means: "If no connections exist, still include the user"
- Like SQL `LEFT JOIN`

```cypher
OPTIONAL MATCH (u)-[:HAS_SKILL]->(s:Skill)
```
- Find skills each user has
- Arrow `->` means direction matters (user HAS a skill, not skill HAS user)

```cypher
WITH u, COUNT(DISTINCT conn) AS connection_count, COUNT(DISTINCT s) AS skill_count
```
- `WITH` = intermediate step (like a subquery)
- `COUNT(DISTINCT conn)` = count unique connections
- Aggregates data before returning

```cypher
RETURN u.user_id, u.name, ..., connection_count, skill_count
```
- Return specific properties

```cypher
ORDER BY u.name
```
- Sort alphabetically

```cypher
SKIP $offset
LIMIT $limit
```
- `$offset = 0` → Skip 0 users
- `$limit = 5` → Return only 5 users
- **Pagination!**

---

### Layer 4: Neo4j (Database)

```
Query arrives at Neo4j via Bolt protocol (port 7687)
                    ↓
          Query planner creates execution plan
                    ↓
          Executes plan on graph
                    ↓
          Returns results
```

**How Neo4j executes the query:**

1. **Index Lookup**: Uses indexes on User nodes
2. **Graph Traversal**: Follows KNOWS relationships from each user
3. **Aggregation**: Counts connections and skills
4. **Sorting**: Orders by name
5. **Pagination**: Applies SKIP and LIMIT

**Returns data like:**
```json
[
  {
    "user_id": "abc-123",
    "name": "Alice Smith",
    "email": "alice@example.com",
    "title": "Software Engineer",
    "location": "San Francisco, CA",
    "bio": "Loves graphs!",
    "connection_count": 15,
    "skill_count": 5
  },
  ...4 more users
]
```

---

### Layer 5: Response Transformation

```
Neo4j results → Service layer
                    ↓
          Creates User objects (Pydantic models)
                    ↓
          Returns to router
                    ↓
          FastAPI serializes to JSON
                    ↓
          Returns to Nginx
                    ↓
          Nginx forwards to browser
```

**In service layer:**
```python
return [
    User(
        user_id=record["user_id"],
        name=record["name"],
        ...
    )
    for record in result
]
```

**Pydantic Model (`app/models/user.py`):**
```python
class User(BaseModel):
    user_id: str
    name: str
    email: str
    ...
    connection_count: Optional[int] = 0
```

**Why Pydantic?**
- **Type validation**: Ensures data matches expected types
- **Serialization**: Automatically converts to JSON
- **Documentation**: Auto-generates API docs

**Final response:**
```json
HTTP/1.1 200 OK
Content-Type: application/json

[
  {"user_id": "abc-123", "name": "Alice Smith", ...},
  {"user_id": "def-456", "name": "Bob Jones", ...},
  ...
]
```

---

## 3. Data Layer (Neo4j)

### Graph Structure

```
       (User)
         |
         |--[KNOWS]---> (User)
         |
         |--[HAS_SKILL]---> (Skill)
         |
         |--[WORKS_AT]---> (Company)
```

### Why Graph Database?

**Traditional SQL:**
```sql
-- Finding friends of friends requires complex JOIN
SELECT u3.*
FROM users u1
JOIN connections c1 ON u1.id = c1.user_id
JOIN users u2 ON c1.friend_id = u2.id
JOIN connections c2 ON u2.id = c2.user_id
JOIN users u3 ON c2.friend_id = u3.id
WHERE u1.id = 123
AND u3.id != 123
```

**Neo4j Cypher:**
```cypher
MATCH (u:User {user_id: '123'})-[:KNOWS]-()-[:KNOWS]-(friend)
WHERE u <> friend
RETURN friend
```

**Much simpler!** This is why we use graphs for social networks.

### Indexes and Constraints

**Created during seeding:**
```cypher
CREATE CONSTRAINT user_id_unique FOR (u:User) REQUIRE u.user_id IS UNIQUE;
CREATE INDEX user_name_idx FOR (u:User) ON (u.name);
```

**Why?**
- **Constraints**: Prevent duplicate users
- **Indexes**: Speed up lookups (like database indexes in SQL)

**Performance:**
- Without index: O(n) scan all users
- With index: O(log n) binary search

---

## 4. Business Logic Layer (Services)

### Service Pattern

**Why separate services from routers?**

```
BAD (everything in router):
@router.get("/users/{id}")
def get_user(id: str):
    query = "MATCH..."  # ← Database code in router
    result = db.run(query)
    return process(result)  # ← Business logic in router
```

**GOOD (service layer):**
```
Router → Service → Database
```

**Benefits:**
1. **Testability**: Can test business logic without FastAPI
2. **Reusability**: Multiple endpoints can use same service
3. **Separation of Concerns**: Router handles HTTP, service handles logic

### Example: Friend Recommendations

**Router (`app/routers/recommendations.py`):**
```python
@router.get("/users/{user_id}/recommendations/friends")
async def get_friend_recommendations(user_id: str, limit: int = 10):
    return recommendation_service.get_friend_recommendations(user_id, limit)
```

**Service (`app/services/recommendation_service.py`):**
```python
def get_friend_recommendations(self, user_id: str, limit: int = 10):
    query = """
    MATCH (u:User {user_id: $user_id})-[:KNOWS]-(friend)-[:KNOWS]-(rec:User)
    WHERE u <> rec AND NOT (u)-[:KNOWS]-(rec)
    WITH rec, COUNT(DISTINCT friend) AS mutual_count
    OPTIONAL MATCH (u)-[:HAS_SKILL]->(s:Skill)<-[:HAS_SKILL]-(rec)
    WITH rec, mutual_count, COLLECT(DISTINCT s.name) AS common_skills
    WITH rec, mutual_count, common_skills,
         (mutual_count * 0.6 + SIZE(common_skills) * 0.4) / 10.0 AS score
    RETURN rec.user_id, rec.name, rec.title, mutual_count, common_skills,
           CASE WHEN score > 1.0 THEN 1.0 ELSE score END AS score
    ORDER BY score DESC
    LIMIT $limit
    """
    # Execute query...
```

**Algorithm explanation:**

```cypher
MATCH (u:User {user_id: $user_id})-[:KNOWS]-(friend)-[:KNOWS]-(rec:User)
```
- **Pattern**: `me → friend → recommendation`
- **Result**: Friend-of-friend (2 hops away)

```cypher
WHERE u <> rec AND NOT (u)-[:KNOWS]-(rec)
```
- `u <> rec`: Recommendation isn't me
- `NOT (u)-[:KNOWS]-(rec)`: We're not already friends

```cypher
WITH rec, COUNT(DISTINCT friend) AS mutual_count
```
- Count how many mutual friends we have
- More mutual friends = better recommendation

```cypher
OPTIONAL MATCH (u)-[:HAS_SKILL]->(s:Skill)<-[:HAS_SKILL]-(rec)
```
- Find skills we both have
- Common interests!

```cypher
(mutual_count * 0.6 + SIZE(common_skills) * 0.4) / 10.0 AS score
```
- **Scoring algorithm:**
  - 60% weight on mutual connections
  - 40% weight on common skills
  - Normalized to 0-1 scale

**Example calculation:**
- Mutual connections: 8
- Common skills: 3
- Score = (8 * 0.6 + 3 * 0.4) / 10 = (4.8 + 1.2) / 10 = 0.6

---

## 5. API Layer (FastAPI)

### Why FastAPI?

1. **Automatic validation** (Pydantic)
2. **Auto-generated docs** (Swagger/OpenAPI)
3. **Async support** (handles concurrent requests)
4. **Type hints** (catches bugs early)

### Example: Input Validation

**Model definition (`app/models/user.py`):**
```python
from pydantic import BaseModel, EmailStr, Field

class UserCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    email: EmailStr  # Must be valid email format
    title: Optional[str] = Field(None, max_length=100)
```

**What happens when you POST invalid data:**

```json
// Invalid: empty name, bad email
{
  "name": "",
  "email": "not-an-email"
}
```

**FastAPI response:**
```json
{
  "detail": [
    {
      "loc": ["body", "name"],
      "msg": "ensure this value has at least 1 characters",
      "type": "value_error.any_str.min_length"
    },
    {
      "loc": ["body", "email"],
      "msg": "value is not a valid email address",
      "type": "value_error.email"
    }
  ]
}
```

**No manual validation needed!** Pydantic handles it.

---

## 6. Proxy Layer (Nginx)

### Why Nginx?

**Without Nginx:**
```
Browser → FastAPI (port 8000)
```
Problems:
- No rate limiting
- No SSL termination
- Single point of failure
- No load balancing

**With Nginx:**
```
Browser → Nginx (port 80) → FastAPI (port 8000)
```
Benefits:
- **Rate limiting**: Prevent abuse
- **SSL/TLS**: HTTPS support
- **Load balancing**: Multiple FastAPI instances
- **Static files**: Serve images, CSS
- **Security headers**: Prevent XSS, clickjacking

### Rate Limiting Example

**In `nginx.conf`:**
```nginx
limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;

location /api/ {
    limit_req zone=api_limit burst=20 nodelay;
    proxy_pass http://api;
}
```

**What this means:**
- `rate=10r/s`: Max 10 requests per second per IP
- `burst=20`: Allow burst of 20 requests
- `nodelay`: Don't delay requests within burst

**Example scenario:**
```
Time 0s: User sends 25 requests
  - First 10: ✅ Processed (within rate)
  - Next 10: ✅ Processed (within burst)
  - Last 5: ❌ Rejected (429 Too Many Requests)

Time 1s: User sends 10 requests
  - All 10: ✅ Processed (rate limit reset)
```

---

## 7. How Tests Work

### Test Structure

```
tests/
├── conftest.py          # Fixtures (shared setup)
├── test_health.py       # Health endpoint tests
├── test_users.py        # User endpoint tests
├── test_recommendations.py
└── test_paths.py
```

### Fixtures (`conftest.py`)

```python
@pytest.fixture
def client():
    return TestClient(app)  # Creates test client for FastAPI
```

**Why fixtures?**
- DRY (Don't Repeat Yourself)
- Each test gets fresh client
- No shared state between tests

### Example Test

**In `test_users.py`:**
```python
def test_list_users(client):
    response = client.get("/api/users")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
```

**What happens when you run `pytest`:**

1. **pytest discovers tests** (functions starting with `test_`)
2. **Runs conftest.py** to set up fixtures
3. **For each test:**
   ```
   Set up → Run test → Assert → Tear down
   ```
4. **Reports results:**
   ```
   test_list_users PASSED [20%]
   test_create_user PASSED [40%]
   ...
   ```

### Coverage Report

**Command:**
```bash
pytest --cov=app --cov-report=html
```

**What it does:**
1. **Instruments code**: Adds tracking to every line
2. **Runs tests**: Records which lines execute
3. **Generates report**: Shows covered vs uncovered lines

**Example:**
```python
def get_user(user_id: str):  # ✅ Covered (test calls this)
    user = db.query(user_id)  # ✅ Covered
    if not user:              # ❌ Not covered (test doesn't check this path)
        raise NotFound()      # ❌ Not covered
    return user               # ✅ Covered
```

**Coverage: 60% (3 of 5 lines)**

---

## 8. How Data Seeding Works

### Seed Script Flow

**Command:**
```bash
python scripts/seed_data.py
```

**Execution:**

```
Step 1: Load environment variables (.env)
   ↓
Step 2: Connect to Neo4j (bolt://localhost:7687)
   ↓
Step 3: Create constraints & indexes
   ↓
Step 4: Generate fake data with Faker
   ↓
Step 5: Insert companies
   ↓
Step 6: Insert skills
   ↓
Step 7: Insert users
   ↓
Step 8: Create relationships (KNOWS, HAS_SKILL, WORKS_AT)
   ↓
Step 9: Print statistics
```

### Creating Constraints

```python
queries = [
    "CREATE CONSTRAINT user_id_unique FOR (u:User) REQUIRE u.user_id IS UNIQUE",
    "CREATE INDEX user_name_idx FOR (u:User) ON (u.name)",
]

for query in queries:
    conn.execute_query(query)
```

**Why constraints first?**
- Prevents duplicate data
- Ensures data integrity
- Must be created before inserting data

### Generating Fake Users

```python
from faker import Faker
fake = Faker()

users = []
for _ in range(100):
    user = {
        "user_id": fake.uuid4(),        # Random UUID
        "name": fake.name(),            # "John Smith"
        "email": fake.email(),          # "john@example.com"
        "title": random.choice(JOB_TITLES),
        "location": fake.city() + ", " + fake.state_abbr(),
        "bio": fake.text(max_nb_chars=200),
    }
    users.append(user)
```

**Faker library generates realistic data:**
- Names: "Alice Johnson", "Bob Chen"
- Emails: "alice.johnson@example.com"
- Cities: "San Francisco, CA"

### Batch Insert

```python
query = """
UNWIND $users AS user
CREATE (u:User)
SET u.user_id = user.user_id,
    u.name = user.name,
    u.email = user.email,
    ...
"""

conn.execute_query(query, {"users": users})
```

**UNWIND** = like a loop:
```cypher
UNWIND [user1, user2, user3] AS user
CREATE (u:User)
SET u = user
```

**Equivalent to:**
```cypher
CREATE (u:User) SET u = user1
CREATE (u:User) SET u = user2
CREATE (u:User) SET u = user3
```

But **much faster** (single transaction)!

### Creating Relationships

```python
# Create random connections
query = """
MATCH (u1:User)
MATCH (u2:User)
WHERE u1 <> u2 AND rand() < $probability
MERGE (u1)-[:KNOWS]-(u2)
"""

probability = 0.15  # 15% chance any two users are connected
conn.execute_query(query, {"probability": probability})
```

**How it works:**
- `MATCH (u1:User)` - Get all users as u1
- `MATCH (u2:User)` - Get all users as u2
- Cartesian product: 100 × 100 = 10,000 pairs
- `rand() < 0.15` - 15% probability = ~1,500 connections
- `MERGE` - Create if doesn't exist (prevents duplicates)

---

## Summary: Complete Data Flow

```
1. User visits: http://localhost/api/users?limit=5

2. Nginx (Port 80):
   - Rate limiting check ✅
   - Add security headers
   - Forward to FastAPI

3. FastAPI (Port 8000):
   - Match route: /api/users
   - Validate parameters: limit=5 ✅
   - Call service: user_service.list_users(5, 0)

4. Service Layer:
   - Build Cypher query
   - Add business logic
   - Execute on Neo4j

5. Neo4j (Port 7687):
   - Parse Cypher query
   - Use indexes for optimization
   - Traverse graph (MATCH)
   - Count relationships (OPTIONAL MATCH)
   - Sort and paginate (ORDER BY, LIMIT)
   - Return results

6. Service Layer:
   - Convert Neo4j records to Pydantic models
   - Return User objects

7. FastAPI:
   - Serialize to JSON
   - Add HTTP headers
   - Return 200 response

8. Nginx:
   - Add security headers
   - Forward to browser

9. Browser:
   - Receives JSON
   - Displays data
```

**Total time: ~50ms**

---

## Key Concepts

### 1. Separation of Concerns

```
Router    → Handles HTTP (requests, responses, status codes)
Service   → Handles business logic (algorithms, calculations)
Database  → Handles data storage (queries, persistence)
Models    → Handles data validation (types, constraints)
```

### 2. Dependency Injection

```python
class UserService:
    def __init__(self, driver: Optional[Driver] = None):
        self.driver = driver or get_neo4j_driver()
```

**Benefits:**
- Easy testing (inject mock driver)
- Flexible configuration
- No global state

### 3. Asynchronous Processing

```python
@router.get("/users")
async def list_users(...):  # async = non-blocking
    return user_service.list_users(...)
```

**Why async?**
- Handle 1000s of concurrent requests
- Don't block while waiting for database
- Better resource utilization

### 4. Parameterized Queries

```cypher
MATCH (u:User {user_id: $user_id})  // ✅ GOOD
```

**vs**

```cypher
MATCH (u:User {user_id: 'abc-123'})  // ❌ BAD
```

**Why parameterized?**
- Prevents injection attacks
- Query plan caching (faster)
- Cleaner code

---

This is how everything works together to create a production-ready social network API!
