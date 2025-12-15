"""
Data seeding script for the social network.
Creates sample users, companies, skills, and relationships.
"""
import os
import sys
import random
from faker import Faker
from dotenv import load_dotenv

# Add parent directory to path to import app modules
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.database.connection import Neo4jConnection

load_dotenv()

fake = Faker()


# Sample data
COMPANIES = [
    {"name": "TechCorp", "industry": "Technology", "location": "San Francisco, CA", "size": "500+"},
    {"name": "DataSystems Inc", "industry": "Software", "location": "New York, NY", "size": "201-500"},
    {"name": "CloudWorks", "industry": "Cloud Computing", "location": "Seattle, WA", "size": "500+"},
    {"name": "AI Innovations", "industry": "Artificial Intelligence", "location": "Boston, MA", "size": "51-200"},
    {"name": "FinTech Solutions", "industry": "Finance", "location": "London, UK", "size": "201-500"},
    {"name": "HealthTech", "industry": "Healthcare", "location": "Austin, TX", "size": "51-200"},
    {"name": "EduPlatform", "industry": "Education", "location": "Chicago, IL", "size": "11-50"},
    {"name": "GreenEnergy Co", "industry": "Energy", "location": "Portland, OR", "size": "201-500"},
]

SKILLS = [
    {"name": "Python", "category": "Programming"},
    {"name": "JavaScript", "category": "Programming"},
    {"name": "Java", "category": "Programming"},
    {"name": "C++", "category": "Programming"},
    {"name": "Go", "category": "Programming"},
    {"name": "Rust", "category": "Programming"},
    {"name": "React", "category": "Frontend"},
    {"name": "Vue.js", "category": "Frontend"},
    {"name": "Angular", "category": "Frontend"},
    {"name": "Node.js", "category": "Backend"},
    {"name": "Django", "category": "Backend"},
    {"name": "FastAPI", "category": "Backend"},
    {"name": "PostgreSQL", "category": "Database"},
    {"name": "MongoDB", "category": "Database"},
    {"name": "Neo4j", "category": "Database"},
    {"name": "Redis", "category": "Database"},
    {"name": "Docker", "category": "DevOps"},
    {"name": "Kubernetes", "category": "DevOps"},
    {"name": "AWS", "category": "Cloud"},
    {"name": "Azure", "category": "Cloud"},
    {"name": "GCP", "category": "Cloud"},
    {"name": "Machine Learning", "category": "AI/ML"},
    {"name": "Deep Learning", "category": "AI/ML"},
    {"name": "NLP", "category": "AI/ML"},
    {"name": "Data Analysis", "category": "Data Science"},
    {"name": "Data Visualization", "category": "Data Science"},
    {"name": "Product Management", "category": "Management"},
    {"name": "Agile", "category": "Management"},
    {"name": "UX Design", "category": "Design"},
    {"name": "UI Design", "category": "Design"},
]

JOB_TITLES = [
    "Software Engineer",
    "Senior Software Engineer",
    "Staff Software Engineer",
    "Data Scientist",
    "Senior Data Scientist",
    "Machine Learning Engineer",
    "DevOps Engineer",
    "Cloud Architect",
    "Product Manager",
    "Engineering Manager",
    "Frontend Developer",
    "Backend Developer",
    "Full Stack Developer",
    "UX Designer",
    "UI Designer",
    "Database Administrator",
    "Security Engineer",
    "QA Engineer",
]


def create_constraints_and_indexes(conn: Neo4jConnection):
    """Create database constraints and indexes."""
    print("Creating constraints and indexes...")

    queries = [
        # Constraints
        "CREATE CONSTRAINT user_id_unique IF NOT EXISTS FOR (u:User) REQUIRE u.user_id IS UNIQUE",
        "CREATE CONSTRAINT user_email_unique IF NOT EXISTS FOR (u:User) REQUIRE u.email IS UNIQUE",
        "CREATE CONSTRAINT skill_name_unique IF NOT EXISTS FOR (s:Skill) REQUIRE s.name IS UNIQUE",
        "CREATE CONSTRAINT company_name_unique IF NOT EXISTS FOR (c:Company) REQUIRE c.name IS UNIQUE",

        # Indexes
        "CREATE INDEX user_name_idx IF NOT EXISTS FOR (u:User) ON (u.name)",
        "CREATE INDEX user_location_idx IF NOT EXISTS FOR (u:User) ON (u.location)",
        "CREATE INDEX skill_category_idx IF NOT EXISTS FOR (s:Skill) ON (s.category)",
        "CREATE INDEX company_industry_idx IF NOT EXISTS FOR (c:Company) ON (c.industry)",
    ]

    for query in queries:
        try:
            conn.execute_query(query)
            print(f"  ✓ Executed: {query[:50]}...")
        except Exception as e:
            print(f"  ⚠ Warning: {str(e)[:100]}")


def seed_companies(conn: Neo4jConnection):
    """Seed companies."""
    print(f"\nSeeding {len(COMPANIES)} companies...")

    query = """
    UNWIND $companies AS company
    MERGE (c:Company {name: company.name})
    SET c.industry = company.industry,
        c.location = company.location,
        c.size = company.size
    """

    conn.execute_query(query, {"companies": COMPANIES})
    print(f"  ✓ Created {len(COMPANIES)} companies")


def seed_skills(conn: Neo4jConnection):
    """Seed skills."""
    print(f"\nSeeding {len(SKILLS)} skills...")

    query = """
    UNWIND $skills AS skill
    MERGE (s:Skill {name: skill.name})
    SET s.category = skill.category
    """

    conn.execute_query(query, {"skills": SKILLS})
    print(f"  ✓ Created {len(SKILLS)} skills")


def seed_users(conn: Neo4jConnection, num_users: int = 100):
    """Seed users with random data."""
    print(f"\nSeeding {num_users} users...")

    users = []
    for _ in range(num_users):
        user = {
            "user_id": fake.uuid4(),
            "name": fake.name(),
            "email": fake.email(),
            "title": random.choice(JOB_TITLES),
            "location": fake.city() + ", " + fake.state_abbr(),
            "bio": fake.text(max_nb_chars=200),
        }
        users.append(user)

    query = """
    UNWIND $users AS user
    CREATE (u:User)
    SET u.user_id = user.user_id,
        u.name = user.name,
        u.email = user.email,
        u.title = user.title,
        u.location = user.location,
        u.bio = user.bio,
        u.created_at = datetime()
    """

    conn.execute_query(query, {"users": users})
    print(f"  ✓ Created {num_users} users")

    return [u["user_id"] for u in users]


def create_user_skills(conn: Neo4jConnection):
    """Create HAS_SKILL relationships."""
    print("\nCreating user-skill relationships...")

    query = """
    MATCH (u:User)
    MATCH (s:Skill)
    WITH u, s
    WHERE rand() < 0.15
    MERGE (u)-[:HAS_SKILL]->(s)
    """

    conn.execute_query(query)

    # Get count
    count_query = "MATCH ()-[r:HAS_SKILL]->() RETURN COUNT(r) AS count"
    result = conn.execute_query(count_query)
    count = result[0]["count"] if result else 0
    print(f"  ✓ Created {count} HAS_SKILL relationships")


def create_user_companies(conn: Neo4jConnection):
    """Create WORKS_AT relationships."""
    print("\nCreating user-company relationships...")

    query = """
    MATCH (u:User)
    MATCH (c:Company)
    WITH u, c
    WHERE rand() < 0.4
    WITH u, c
    ORDER BY rand()
    LIMIT 1
    MERGE (u)-[:WORKS_AT]->(c)
    """

    # Run for each user
    conn.execute_query("""
        MATCH (u:User)
        WHERE NOT (u)-[:WORKS_AT]->()
        WITH u
        MATCH (c:Company)
        WITH u, c
        ORDER BY rand()
        LIMIT 1
        MERGE (u)-[:WORKS_AT]->(c)
    """)

    # Get count
    count_query = "MATCH ()-[r:WORKS_AT]->() RETURN COUNT(r) AS count"
    result = conn.execute_query(count_query)
    count = result[0]["count"] if result else 0
    print(f"  ✓ Created {count} WORKS_AT relationships")


def create_user_connections(conn: Neo4jConnection, avg_connections: int = 15):
    """Create KNOWS relationships between users."""
    print(f"\nCreating user connections (avg {avg_connections} per user)...")

    # Create random connections
    query = """
    MATCH (u1:User)
    MATCH (u2:User)
    WHERE u1 <> u2 AND rand() < $probability
    MERGE (u1)-[:KNOWS]-(u2)
    """

    # Calculate probability to get desired average
    # For undirected relationships, we need to adjust
    user_count_query = "MATCH (u:User) RETURN COUNT(u) AS count"
    result = conn.execute_query(user_count_query)
    user_count = result[0]["count"] if result else 0

    if user_count > 0:
        probability = (avg_connections * 2) / user_count
        conn.execute_query(query, {"probability": min(probability, 0.3)})

    # Get count
    count_query = "MATCH ()-[r:KNOWS]-() RETURN COUNT(r) / 2 AS count"
    result = conn.execute_query(count_query)
    count = int(result[0]["count"]) if result else 0
    print(f"  ✓ Created {count} KNOWS relationships")


def print_statistics(conn: Neo4jConnection):
    """Print database statistics."""
    print("\n" + "=" * 50)
    print("DATABASE STATISTICS")
    print("=" * 50)

    stats_query = """
    MATCH (u:User) WITH COUNT(u) AS users
    MATCH (s:Skill) WITH users, COUNT(s) AS skills
    MATCH (c:Company) WITH users, skills, COUNT(c) AS companies
    MATCH ()-[knows:KNOWS]-() WITH users, skills, companies, COUNT(knows) / 2 AS connections
    MATCH ()-[has:HAS_SKILL]->() WITH users, skills, companies, connections, COUNT(has) AS user_skills
    MATCH ()-[works:WORKS_AT]->() WITH users, skills, companies, connections, user_skills, COUNT(works) AS employments
    RETURN users, skills, companies, connections, user_skills, employments
    """

    result = conn.execute_query(stats_query)
    if result:
        stats = result[0]
        print(f"\nNodes:")
        print(f"  Users:     {stats['users']}")
        print(f"  Skills:    {stats['skills']}")
        print(f"  Companies: {stats['companies']}")
        print(f"\nRelationships:")
        print(f"  KNOWS:     {stats['connections']}")
        print(f"  HAS_SKILL: {stats['user_skills']}")
        print(f"  WORKS_AT:  {stats['employments']}")

    print("\n" + "=" * 50)


def main():
    """Main seeding function."""
    print("=" * 50)
    print("SOCIAL NETWORK DATA SEEDING")
    print("=" * 50)

    # Get configuration from environment
    uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
    user = os.getenv("NEO4J_USER", "neo4j")
    password = os.getenv("NEO4J_PASSWORD", "password123")

    print(f"\nConnecting to Neo4j at {uri}...")

    try:
        with Neo4jConnection(uri, user, password) as conn:
            if not conn.verify_connectivity():
                print("❌ Failed to connect to Neo4j")
                return

            print("✓ Connected successfully\n")

            # Create constraints and indexes
            create_constraints_and_indexes(conn)

            # Seed data
            seed_companies(conn)
            seed_skills(conn)
            seed_users(conn, num_users=100)
            create_user_skills(conn)
            create_user_companies(conn)
            create_user_connections(conn, avg_connections=15)

            # Print statistics
            print_statistics(conn)

            print("\n✓ Data seeding completed successfully!")

    except Exception as e:
        print(f"\n❌ Error during seeding: {e}")
        raise


if __name__ == "__main__":
    main()
