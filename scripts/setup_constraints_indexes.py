"""
Script to create Neo4j constraints and indexes.
This ensures optimal query performance and data integrity.
"""
import os
import sys
from dotenv import load_dotenv

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.database.connection import Neo4jConnection

load_dotenv()


def create_constraints_and_indexes():
    """Create all required constraints and indexes."""

    conn = Neo4jConnection()

    print("Setting up Neo4j constraints and indexes...\n")

    # Constraints (ensure uniqueness and data integrity)
    constraints = [
        ("user_id_unique", "CREATE CONSTRAINT user_id_unique IF NOT EXISTS FOR (u:User) REQUIRE u.user_id IS UNIQUE"),
        ("user_email_unique", "CREATE CONSTRAINT user_email_unique IF NOT EXISTS FOR (u:User) REQUIRE u.email IS UNIQUE"),
        ("skill_name_unique", "CREATE CONSTRAINT skill_name_unique IF NOT EXISTS FOR (s:Skill) REQUIRE s.name IS UNIQUE"),
        ("company_name_unique", "CREATE CONSTRAINT company_name_unique IF NOT EXISTS FOR (c:Company) REQUIRE c.name IS UNIQUE"),
    ]

    print("Creating constraints...")
    for name, query in constraints:
        try:
            conn.execute_query(query)
            print(f"✓ {name}")
        except Exception as e:
            print(f"✗ {name}: {e}")

    print("\nCreating indexes...")

    # Indexes (speed up frequent queries)
    indexes = [
        ("user_name_idx", "CREATE INDEX user_name_idx IF NOT EXISTS FOR (u:User) ON (u.name)"),
        ("user_title_idx", "CREATE INDEX user_title_idx IF NOT EXISTS FOR (u:User) ON (u.title)"),
        ("skill_category_idx", "CREATE INDEX skill_category_idx IF NOT EXISTS FOR (s:Skill) ON (s.category)"),
        ("company_industry_idx", "CREATE INDEX company_industry_idx IF NOT EXISTS FOR (c:Company) ON (c.industry)"),
        ("company_location_idx", "CREATE INDEX company_location_idx IF NOT EXISTS FOR (c:Company) ON (c.location)"),
    ]

    for name, query in indexes:
        try:
            conn.execute_query(query)
            print(f"✓ {name}")
        except Exception as e:
            print(f"✗ {name}: {e}")

    print("\n" + "="*60)
    print("Verifying setup...")
    print("="*60 + "\n")

    # Verify constraints
    constraints_query = "SHOW CONSTRAINTS"
    result = conn.execute_query(constraints_query)

    print("Existing constraints:")
    for record in result:
        print(f"  - {record.get('name', 'N/A')}: {record.get('type', 'N/A')}")

    # Verify indexes
    print("\nExisting indexes:")
    indexes_query = "SHOW INDEXES"
    result = conn.execute_query(indexes_query)

    for record in result:
        print(f"  - {record.get('name', 'N/A')}: {record.get('type', 'N/A')}")

    print("\n✓ Setup complete!")

    conn.close()


if __name__ == "__main__":
    create_constraints_and_indexes()
