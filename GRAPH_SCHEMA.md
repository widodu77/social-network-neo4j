# Graph Database Schema

## Visual Schema

```
                    ┌──────────────┐
                    │    Company   │
                    ├──────────────┤
                    │ name         │
                    │ industry     │
                    │ location     │
                    │ size         │
                    └──────┬───────┘
                           │
                           │ WORKS_AT
                           │
                    ┌──────▼───────┐
                    │     User     │
                    ├──────────────┤
                    │ user_id      │
                    │ name         │
                    │ email        │
                    │ title        │
                    │ location     │
                    │ bio          │
                    │ created_at   │
                    └──┬────────┬──┘
                       │        │
           HAS_SKILL   │        │  KNOWS (bidirectional)
                       │        │
                ┌──────▼──┐  ┌──▼────┐
                │  Skill  │  │  User │
                ├─────────┤  └───────┘
                │ name    │
                │ category│
                └─────────┘
```

## Node Types

### User
- **Labels**: `User`
- **Properties**:
  - `user_id` (STRING, UNIQUE, INDEXED)
  - `name` (STRING, INDEXED)
  - `email` (STRING, UNIQUE)
  - `title` (STRING)
  - `location` (STRING, INDEXED)
  - `bio` (TEXT)
  - `created_at` (DATETIME)

### Skill
- **Labels**: `Skill`
- **Properties**:
  - `name` (STRING, UNIQUE)
  - `category` (STRING, INDEXED)

### Company
- **Labels**: `Company`
- **Properties**:
  - `name` (STRING, UNIQUE)
  - `industry` (STRING, INDEXED)
  - `location` (STRING)
  - `size` (STRING)

## Relationship Types

### KNOWS
- **Direction**: Bidirectional (User)-[:KNOWS]-(User)
- **Properties**: None (can add: `since`, `strength`)
- **Meaning**: Connection between two professionals in the network
- **Use Cases**:
  - Friend recommendations (friends of friends)
  - Network path finding
  - Mutual connection analysis

### HAS_SKILL
- **Direction**: (User)-[:HAS_SKILL]->(Skill)
- **Properties**: None (can add: `proficiency_level`, `years_experience`)
- **Meaning**: User possesses a particular skill
- **Use Cases**:
  - Skill-based recommendations
  - Job matching
  - Common interest identification

### WORKS_AT
- **Direction**: (User)-[:WORKS_AT]->(Company)
- **Properties**: None (can add: `start_date`, `position`)
- **Meaning**: User is employed at a company
- **Use Cases**:
  - Same company suggestions
  - Company network analysis
  - Career path recommendations

## Constraints

```cypher
// Uniqueness constraints
CREATE CONSTRAINT user_id_unique IF NOT EXISTS
FOR (u:User) REQUIRE u.user_id IS UNIQUE;

CREATE CONSTRAINT user_email_unique IF NOT EXISTS
FOR (u:User) REQUIRE u.email IS UNIQUE;

CREATE CONSTRAINT skill_name_unique IF NOT EXISTS
FOR (s:Skill) REQUIRE s.name IS UNIQUE;

CREATE CONSTRAINT company_name_unique IF NOT EXISTS
FOR (c:Company) REQUIRE c.name IS UNIQUE;
```

## Indexes

```cypher
// Search performance indexes
CREATE INDEX user_name_idx IF NOT EXISTS
FOR (u:User) ON (u.name);

CREATE INDEX user_location_idx IF NOT EXISTS
FOR (u:User) ON (u.location);

CREATE INDEX skill_category_idx IF NOT EXISTS
FOR (s:Skill) ON (s.category);

CREATE INDEX company_industry_idx IF NOT EXISTS
FOR (c:Company) ON (c.industry);
```

## Sample Cypher Queries

### Create a User with Skills and Company

```cypher
// Create user
CREATE (u:User {
  user_id: randomUUID(),
  name: 'Jane Doe',
  email: 'jane@example.com',
  title: 'Senior Software Engineer',
  location: 'San Francisco, CA',
  bio: 'Passionate about graph databases and distributed systems',
  created_at: datetime()
})

// Add skills
WITH u
MERGE (s1:Skill {name: 'Python', category: 'Programming'})
MERGE (s2:Skill {name: 'Neo4j', category: 'Database'})
MERGE (s3:Skill {name: 'Docker', category: 'DevOps'})
MERGE (u)-[:HAS_SKILL]->(s1)
MERGE (u)-[:HAS_SKILL]->(s2)
MERGE (u)-[:HAS_SKILL]->(s3)

// Add company
WITH u
MERGE (c:Company {name: 'TechCorp', industry: 'Technology'})
MERGE (u)-[:WORKS_AT]->(c)

RETURN u
```

### Find Friend Recommendations

```cypher
// Friends of friends with mutual connection count
MATCH (me:User {user_id: $my_id})-[:KNOWS]-(friend)-[:KNOWS]-(suggestion)
WHERE me <> suggestion
  AND NOT (me)-[:KNOWS]-(suggestion)
WITH suggestion, COUNT(DISTINCT friend) AS mutual_count
OPTIONAL MATCH (me:User {user_id: $my_id})-[:HAS_SKILL]->(s:Skill)<-[:HAS_SKILL]-(suggestion)
WITH suggestion, mutual_count, COLLECT(DISTINCT s.name) AS common_skills
RETURN suggestion.user_id, suggestion.name, suggestion.title,
       mutual_count, common_skills,
       (mutual_count * 0.6 + SIZE(common_skills) * 0.4) / 10.0 AS score
ORDER BY score DESC
LIMIT 10
```

### Find Shortest Path

```cypher
MATCH (from:User {user_id: $from_id})
MATCH (to:User {user_id: $to_id})
MATCH path = shortestPath((from)-[:KNOWS*]-(to))
RETURN path, LENGTH(path) AS path_length, nodes(path) AS users
```

### Job Recommendations (Skill Matching)

```cypher
MATCH (me:User {user_id: $my_id})-[:HAS_SKILL]->(my_skill:Skill)
WITH me, COLLECT(my_skill.name) AS my_skills

MATCH (other:User)-[:HAS_SKILL]->(skill:Skill)
WHERE other <> me AND skill.name IN my_skills

MATCH (other)-[:WORKS_AT]->(company:Company)
WHERE NOT (me)-[:WORKS_AT]->(company)

WITH company, my_skills, COLLECT(DISTINCT skill.name) AS company_skills
WITH company, my_skills, company_skills,
     SIZE([s IN company_skills WHERE s IN my_skills]) AS matching_count
RETURN company.name, company.industry, company.location,
       company_skills AS required_skills,
       toFloat(matching_count) / SIZE(company_skills) AS match_rate
ORDER BY match_rate DESC
LIMIT 10
```

## Graph Statistics (Sample Dataset)

After running `scripts/seed_data.py`:

- **Nodes**:
  - Users: ~100
  - Skills: ~30
  - Companies: ~8

- **Relationships**:
  - KNOWS: ~750 (avg 15 connections per user)
  - HAS_SKILL: ~450 (avg 4-5 skills per user)
  - WORKS_AT: ~100 (1 company per user)

## Modeling Rationale

### Why Graph Database?

1. **Natural Representation**: Social networks are inherently graph-structured
2. **Efficient Traversals**: O(1) relationship traversal vs JOIN operations
3. **Flexible Schema**: Easy to add new relationship types
4. **Pattern Matching**: Native support for graph patterns (friend-of-friend)
5. **Path Finding**: Built-in algorithms for shortest path, centrality, etc.

### Design Decisions

1. **Bidirectional KNOWS**: Represents mutual friendships (like LinkedIn)
2. **Skill Categories**: Enables skill grouping and category-based recommendations
3. **Company Size**: Useful for filtering opportunities by company size
4. **UUID for user_id**: Distributed system compatibility
5. **Indexed Properties**: Optimizes common query patterns (name, location searches)

### Scalability Considerations

- **Indexes**: On frequently queried properties
- **LIMIT Clauses**: Prevent unbounded result sets
- **Parameterized Queries**: Query plan caching
- **APOC Procedures**: For advanced batch operations
- **GDS Plugin**: For graph algorithms at scale
