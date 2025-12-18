# Neo4j Graph Schema Diagram

## Visual Representation

```
┌─────────────────────────────────────────────────────────────────┐
│                     Neo4j Graph Schema                          │
└─────────────────────────────────────────────────────────────────┘

    ┌──────────────────┐
    │      User        │
    │──────────────────│
    │ user_id (unique) │
    │ name             │
    │ email (unique)   │
    │ title            │
    │ location         │
    │ bio              │
    │ created_at       │
    └────────┬─────────┘
             │
             │ KNOWS (bidirectional)
             ├─────────────────────┐
             │                     │
             ▼                     ▼
    ┌────────────────┐    ┌────────────────┐
    │     User       │    │     User       │
    └────────────────┘    └────────────────┘
             │
             │ HAS_SKILL
             │
             ▼
    ┌──────────────────┐
    │      Skill       │
    │──────────────────│
    │ name (unique)    │
    │ category         │
    └──────────────────┘
             │
             │
    ┌──────────────────┐
    │      User        │
    └────────┬─────────┘
             │
             │ WORKS_AT
             │
             ▼
    ┌──────────────────┐
    │     Company      │
    │──────────────────│
    │ name (unique)    │
    │ industry         │
    │ location         │
    │ size             │
    └──────────────────┘
```

## Node Types

### 1. User
- **Properties:**
  - `user_id` (String, Unique) - Primary identifier
  - `name` (String) - Full name
  - `email` (String, Unique) - Email address
  - `title` (String) - Professional title
  - `location` (String) - Geographic location
  - `bio` (String) - Biography/description
  - `created_at` (DateTime) - Account creation timestamp

### 2. Skill
- **Properties:**
  - `name` (String, Unique) - Skill name (e.g., "Python", "Neo4j")
  - `category` (String) - Skill category (e.g., "Programming", "Database")

### 3. Company
- **Properties:**
  - `name` (String, Unique) - Company name
  - `industry` (String) - Industry sector
  - `location` (String) - Company headquarters location
  - `size` (String) - Company size classification

## Relationship Types

### 1. KNOWS (User → User)
- **Direction:** Bidirectional
- **Description:** Represents friendship/connection between two users
- **Properties:** None
- **Usage:** Friend recommendations, network path finding

### 2. HAS_SKILL (User → Skill)
- **Direction:** Unidirectional (User to Skill)
- **Description:** User possesses a particular skill
- **Properties:**
  - `proficiency` (Optional) - Skill level
  - `years_experience` (Optional) - Years of experience
- **Usage:** Skill matching, job recommendations

### 3. WORKS_AT (User → Company)
- **Direction:** Unidirectional (User to Company)
- **Description:** Current employment relationship
- **Properties:**
  - `position` (Optional) - Job position
  - `start_date` (Optional) - Employment start date
- **Usage:** Company network analysis, colleague suggestions

## Constraints

```cypher
CREATE CONSTRAINT user_id_unique IF NOT EXISTS FOR (u:User) REQUIRE u.user_id IS UNIQUE;
CREATE CONSTRAINT user_email_unique IF NOT EXISTS FOR (u:User) REQUIRE u.email IS UNIQUE;
CREATE CONSTRAINT skill_name_unique IF NOT EXISTS FOR (s:Skill) REQUIRE s.name IS UNIQUE;
CREATE CONSTRAINT company_name_unique IF NOT EXISTS FOR (c:Company) REQUIRE c.name IS UNIQUE;
```

## Indexes

```cypher
CREATE INDEX user_name_idx IF NOT EXISTS FOR (u:User) ON (u.name);
CREATE INDEX user_title_idx IF NOT EXISTS FOR (u:User) ON (u.title);
CREATE INDEX skill_category_idx IF NOT EXISTS FOR (s:Skill) ON (s.category);
CREATE INDEX company_industry_idx IF NOT EXISTS FOR (c:Company) ON (c.industry);
CREATE INDEX company_location_idx IF NOT EXISTS FOR (c:Company) ON (c.location);
```

## How to Visualize in Neo4j Browser

1. Open Neo4j Browser at http://localhost:7474
2. Run the following query to see the schema:
   ```cypher
   CALL db.schema.visualization()
   ```
3. Or visualize sample data:
   ```cypher
   MATCH (u:User)-[r]-(n)
   RETURN u, r, n
   LIMIT 25
   ```

## Schema Statistics

Run these queries in Neo4j Browser to see statistics:

```cypher
// Count nodes by type
MATCH (u:User) RETURN 'Users' AS type, COUNT(u) AS count
UNION
MATCH (s:Skill) RETURN 'Skills' AS type, COUNT(s) AS count
UNION
MATCH (c:Company) RETURN 'Companies' AS type, COUNT(c) AS count;

// Count relationships by type
MATCH ()-[r:KNOWS]->() RETURN 'KNOWS' AS type, COUNT(r) AS count
UNION
MATCH ()-[r:HAS_SKILL]->() RETURN 'HAS_SKILL' AS type, COUNT(r) AS count
UNION
MATCH ()-[r:WORKS_AT]->() RETURN 'WORKS_AT' AS type, COUNT(r) AS count;
```

## To Create a Screenshot for Documentation

1. Navigate to http://localhost:7474 in your browser
2. Login with username: `neo4j`, password: `password123`
3. Run: `CALL db.schema.visualization()`
4. Take a screenshot of the visualization
5. Save as `docs/neo4j-schema.png`
6. Add to README.md:
   ```markdown
   ![Neo4j Schema](docs/neo4j-schema.png)
   ```
