# Social Network Recommendation System

[![Tests](https://github.com/widodu77/social-network-neo4j/workflows/Tests/badge.svg)](https://github.com/widodu77/social-network-neo4j/actions)
[![Lint](https://github.com/widodu77/social-network-neo4j/workflows/Lint/badge.svg)](https://github.com/widodu77/social-network-neo4j/actions)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109.0-009688.svg)](https://fastapi.tiangolo.com)
[![Neo4j](https://img.shields.io/badge/Neo4j-5.15.0-008CC1.svg)](https://neo4j.com)
[![Docker](https://img.shields.io/badge/docker-ready-blue.svg)](https://www.docker.com/)

A LinkedIn-style professional network recommendation system built with Neo4j, FastAPI, and Docker. This project implements friend recommendations, job suggestions, network path finding, and LLM-powered graph queries using advanced graph database algorithms.

## 🚀 Quick Start

Once the services are running (see [Getting Started](#getting-started)), you can access:

- **Neo4j Browser**: [http://localhost:7474](http://localhost:7474)
- **API Documentation**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **API Endpoint**: [http://localhost:8000](http://localhost:8000)

All credentials are configured via environment variables (see `.env.example`).

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Architecture](#architecture)
- [Getting Started](#getting-started)
- [API Documentation](#api-documentation)
- [Data Model](#data-model)
- [Testing](#testing)
- [Development](#development)
- [Team Contributions](#team-contributions)

## 🎯 Overview

This project demonstrates the power of graph databases for social network analysis and recommendations. It models a professional network similar to LinkedIn, with users, skills, companies, and their interconnections.

**Key Capabilities:**
- Friend recommendations based on mutual connections
- Job recommendations based on skill matching
- "People you may know" suggestions
- Shortest path finding between professionals
- Graph-based scoring algorithms

## ✨ Features

### Core Functionality

- **User Management**: Create and manage user profiles with skills and company affiliations
- **Friend Recommendations**: Find potential connections through mutual friends and common interests
- **Job Recommendations**: Match users with opportunities based on their skill graph
- **People Suggestions**: Discover professionals with shared connections, skills, or company
- **Network Paths**: Find the shortest connection path between any two professionals

### Technical Features

- RESTful API with FastAPI
- Neo4j graph database with APOC and GDS plugins
- Docker Compose orchestration
- Nginx reverse proxy with rate limiting
- Comprehensive test suite with pytest
- Code quality enforcement with pylint
- Automated data seeding

## 🛠 Tech Stack

- **Database**: Neo4j 5.15.0 (with APOC & Graph Data Science)
- **Backend**: Python 3.11+ with FastAPI
- **API Documentation**: OpenAPI/Swagger
- **Containerization**: Docker & Docker Compose
- **Reverse Proxy**: Nginx
- **Testing**: pytest with coverage
- **Code Quality**: pylint, black, flake8

## 🏗 Architecture

```
┌─────────────┐
│   Nginx     │  Port 80 (Reverse Proxy + Rate Limiting)
│  (Proxy)    │
└──────┬──────┘
       │
       ├─────> Neo4j Browser (Port 7474)
       ├─────> Neo4j Bolt (Port 7687)
       │
┌──────▼───────┐
│   FastAPI    │  Port 8000 (REST API)
│     API      │
└──────┬───────┘
       │
┌──────▼───────┐
│    Neo4j     │  Graph Database
│   Database   │
└──────────────┘
```

### Services

1. **Neo4j**: Graph database storing users, skills, companies, and relationships
2. **FastAPI**: REST API exposing graph queries and recommendations
3. **Nginx**: Reverse proxy with security headers and rate limiting

## 🚀 Getting Started

### Prerequisites

- **Docker** and **Docker Compose** installed
- **Python 3.11+** (for seeding data)
- **Git** for cloning the repository

### Quick Start (Recommended)

Follow these steps to run the entire project in under 5 minutes:

#### 1. Clone the Repository
```bash
git clone <your-repo-url>
cd Graph-knowledge-Final
```

#### 2. Start Docker Services
```bash
docker-compose up -d
```

Wait ~30 seconds for Neo4j to fully start. You should see:
```
✓ Container neo4j    Started
✓ Container api      Started
✓ Container nginx    Started
```

#### 3. Verify Services Are Running
```bash
# Check if all services are healthy
docker-compose ps
```

All services should show "Up" status.

#### 4. Access the Services
- **Neo4j Browser**: http://localhost:7474 (credentials are in your `.env` file)
- **FastAPI Docs**: http://localhost:8000/docs
- **API via Nginx**: http://localhost/docs

#### 5. Seed the Database with Sample Data

**Option A - Using Python locally:**
```bash
# Create virtual environment
python -m venv .venv

# Activate it
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run the seeding script
python scripts/seed_data.py
```

**Option B - Using Docker exec:**
```bash
# Copy script into API container and run
docker-compose exec api python scripts/seed_data.py
```

The seeding script will create:
- 100 users with realistic profiles
- 30 skills across 5 categories
- 8 companies in various industries
- ~500 random connections between users
- User-skill relationships
- User-company employment relationships

Expected output:
```
✓ Connected to Neo4j
✓ Created constraints
✓ Created indexes
✓ Created 100 users
✓ Created 30 skills
✓ Created 8 companies
✓ Created 487 connections
✓ Created 276 user-skill relationships
✓ Created 100 employment relationships
Database seeded successfully!
```

#### 6. Test the API

**Get friend recommendations:**
```bash
# First, get a user ID from Neo4j Browser or API
# Then request recommendations:
curl "http://localhost:8000/api/users/{user_id}/recommendations/friends?limit=5"
```

**Or explore with Swagger UI:**
Go to http://localhost:8000/docs and try the interactive API documentation.

#### 7. Explore the Graph in Neo4j Browser

Open http://localhost:7474 and run these Cypher queries:

```cypher
// View 25 users and their connections
MATCH (u:User)-[r:KNOWS]-(friend:User)
RETURN u, r, friend
LIMIT 25

// Find most connected users
MATCH (u:User)-[:KNOWS]-(friend)
WITH u, COUNT(friend) AS connections
RETURN u.name, u.title, connections
ORDER BY connections DESC
LIMIT 10

// View skills distribution
MATCH (u:User)-[:HAS_SKILL]->(s:Skill)
WITH s, COUNT(u) AS users
RETURN s.name, s.category, users
ORDER BY users DESC
LIMIT 10
```

### Windows-Specific Instructions (Without Make)

If you're on Windows and don't have `make` installed, use these PowerShell commands:

```powershell
# Start services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f

# Stop services
docker-compose down

# Stop and remove volumes (clean slate)
docker-compose down -v

# Install Python dependencies
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt

# Seed database
python scripts\seed_data.py

# Run tests
pytest tests\ -v --cov=app

# Lint code
pylint app\ --rcfile=.pylintrc
```

### Troubleshooting

**Issue: Neo4j container exits immediately**
```bash
# Solution: Remove old volumes and restart
docker-compose down -v
docker-compose up -d
```

**Issue: "Cannot resolve address neo4j:7687" when seeding**
- Make sure Docker containers are running: `docker-compose ps`
- The `.env` file should have `NEO4J_URI=bolt://localhost:7687` for local Python execution
- If running inside Docker: `NEO4J_URI=bolt://neo4j:7687`

**Issue: API returns "User not found" for recommendations**
- Make sure you've run the seeding script: `python scripts/seed_data.py`
- Verify data exists in Neo4j Browser: `MATCH (u:User) RETURN COUNT(u)`

**Issue: Port already in use**
```bash
# Change ports in docker-compose.yml if needed
# Or stop conflicting services
docker ps  # Find conflicting containers
docker stop <container_id>
```

### Demo Notebook

For a comprehensive walkthrough, open the Jupyter notebook:

```bash
# Install Jupyter
pip install jupyter

# Run notebook
jupyter notebook demo_fixed.ipynb
```

The notebook demonstrates:
- Database statistics
- Finding well-connected users
- Friend recommendations with scoring
- Job recommendations based on skills
- People you may know suggestions
- Shortest path between users
- Network analytics (most connected users, popular skills, company density)

## 📚 API Documentation

### Base URL

- Direct: `http://localhost:8000`
- Through Nginx: `http://localhost`

### Endpoints

#### Health Check
```http
GET /health
```

#### Users
```http
POST   /api/users                    # Create a user
GET    /api/users                    # List all users
GET    /api/users/{user_id}          # Get user details
```

#### Recommendations
```http
GET /api/users/{user_id}/recommendations/friends?limit=10
GET /api/users/{user_id}/recommendations/jobs?limit=10
GET /api/users/{user_id}/suggestions/people?limit=10
```

#### Paths
```http
GET /api/paths/shortest?from={user_id_a}&to={user_id_b}
```

### Example API Calls

**Create a User**
```bash
curl -X POST http://localhost:8000/api/users \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john@example.com",
    "title": "Software Engineer",
    "location": "San Francisco, CA",
    "bio": "Passionate about graph databases",
    "skills": ["Python", "Neo4j", "Docker"],
    "company": "TechCorp"
  }'
```

**Get Friend Recommendations**
```bash
curl http://localhost:8000/api/users/{user_id}/recommendations/friends?limit=5
```

**Find Shortest Path**
```bash
curl "http://localhost:8000/api/paths/shortest?from=user-1&to=user-2"
```

## 🗄 Data Model

### Graph Schema

```cypher
// Nodes
(User {user_id, name, email, title, location, bio, created_at})
(Skill {name, category})
(Company {name, industry, location, size})

// Relationships
(User)-[:KNOWS]-(User)           // Bidirectional friendship
(User)-[:HAS_SKILL]->(Skill)     // User possesses skill
(User)-[:WORKS_AT]->(Company)    // Employment relationship
```

### Constraints

```cypher
CREATE CONSTRAINT user_id_unique FOR (u:User) REQUIRE u.user_id IS UNIQUE;
CREATE CONSTRAINT user_email_unique FOR (u:User) REQUIRE u.email IS UNIQUE;
CREATE CONSTRAINT skill_name_unique FOR (s:Skill) REQUIRE s.name IS UNIQUE;
CREATE CONSTRAINT company_name_unique FOR (c:Company) REQUIRE c.name IS UNIQUE;
```

### Indexes

```cypher
CREATE INDEX user_name_idx FOR (u:User) ON (u.name);
CREATE INDEX skill_category_idx FOR (s:Skill) ON (s.category);
CREATE INDEX company_industry_idx FOR (c:Company) ON (c.industry);
```

## 🧪 Testing

### Run Tests

```bash
# Using Make
make test

# Or directly with pytest
pytest tests/ -v --cov=app --cov-report=html
```

### Test Coverage

The project includes tests for:
- API endpoints (users, recommendations, paths)
- Health checks
- Input validation
- Error handling

View coverage report: `htmlcov/index.html`

## 💻 Development

### Local Development Setup

1. **Create virtual environment**
```bash
make venv
source .venv/bin/activate  # Linux/Mac
# or
.venv\Scripts\activate  # Windows
```

2. **Install dependencies**
```bash
make install
```

3. **Run locally** (requires Neo4j running)
```bash
make run
```

### Code Quality

**Linting**
```bash
make lint
```

Target: pylint score ≥ 9.5/10

**Formatting**
```bash
make format
```

Uses `black` with 120 character line length.

### Available Make Commands

```bash
make help           # Show all available commands
make init           # Initialize project (.env, directories)
make venv           # Create virtual environment
make install        # Install dependencies
make run            # Run FastAPI locally
make docker-build   # Build Docker image
make docker-run     # Start all services
make docker-stop    # Stop all services
make test           # Run tests with coverage
make lint           # Run pylint
make format         # Format code with black
make clean          # Remove cache files
make tree           # Show project structure
make seed-data      # Seed database with sample data
make logs           # View docker-compose logs
make health         # Check service health
```

## 👥 Team Contributions

### Commit Statistics

| Member             | Commits | Percentage | Pull Requests |
|--------------------|---------|------------|---------------|
| ajobi-uhc          | 20      | 34.5%      | 1 merged      |
| widodu77           | 17      | 29.3%      | 1 merged      |
| SauceXAlgerienne   | 12      | 20.7%      | 0 merged      |
| alain-rostomyan    | 9       | 15.5%      | 0 merged      |

**Total**: 58 commits

**Project Statistics:**
- Test Coverage: 66%
- Pylint Score: 9.89/10
- CI/CD: Automated testing and linting workflows

### Role Distribution

- **ajobi-uhc**: Neo4j architecture, graph schema design, constraints and indexes setup, LLM integration
- **widodu77**: FastAPI backend development, API endpoints, Pydantic models, Docker configuration
- **SauceXAlgerienne**: Pytest suite implementation, CI/CD workflows, code quality improvements
- **alain-rostomyan**: Data ingestion scripts, recommendation algorithms, query optimization

### Major Pull Requests

1. [#1 - Add Docker registry link and improve code quality](https://github.com/widodu77/social-network-neo4j/pull/1)
2. [#2 - Refactor services and fix test initialization](https://github.com/widodu77/social-network-neo4j/pull/2)
3. [#3 - Add database constraints and indexes setup](https://github.com/widodu77/social-network-neo4j/pull/3)
4. [#4 - Add comprehensive query optimization documentation](https://github.com/widodu77/social-network-neo4j/pull/4)

### Contribution Guidelines

1. Create a feature branch from `main`
2. Implement your feature with tests
3. Ensure `make lint` passes (score ≥ 9.5/10)
4. Ensure `make test` passes
5. Create a Pull Request
6. Request review from team lead
7. Team lead merges after approval

## 📊 Graph Algorithms Used

### Friend Recommendations
- **Algorithm**: 2-hop friend-of-friend traversal
- **Scoring**: Weighted by mutual connections (0.6) + common skills (0.4)
- **Complexity**: O(d²) where d is average degree

### Job Recommendations
- **Algorithm**: Skill matching with collaborative filtering
- **Scoring**: Skill match percentage
- **Query Optimization**: Uses index on skills for fast lookup

### People Suggestions
- **Algorithm**: Multi-signal scoring
- **Signals**: Mutual connections (0.5) + common skills (0.3) + same company (0.2)
- **Pathfinding**: Uses Neo4j `shortestPath()` for connection distance

### Shortest Path
- **Algorithm**: Neo4j built-in `shortestPath()`
- **Time Complexity**: O(V + E) using BFS
- **Use Case**: Find introduction paths between professionals

## 🔒 Security Features

- Environment-based configuration (no hardcoded secrets)
- Nginx rate limiting (10 requests/second)
- Security headers (X-Frame-Options, X-Content-Type-Options, etc.)
- Input validation with Pydantic
- CORS configuration
- Health check endpoints

## 📈 Performance Optimizations

1. **Database Indexes**: On frequently queried properties
2. **Query Optimization**: Uses `LIMIT` to prevent large result sets
3. **Parameterized Queries**: Prevents query plan cache pollution
4. **Connection Pooling**: Neo4j driver manages connection pool
5. **Pagination**: All list endpoints support limit/offset

## 🐳 Docker Images

The project uses official images:
- `neo4j:5.15.0`
- `python:3.11-slim`
- `nginx:1.25-alpine`

**Published Custom Image:**
- [`ajobi/social-network-api:latest`](https://hub.docker.com/r/ajobi/social-network-api) - FastAPI application image

To use the published image:
```bash
docker pull ajobi/social-network-api:latest
```

To build and push your own image:
```bash
make docker-build TAG=your-registry/social-network:latest
make docker-push REGISTRY=your-registry/social-network
```

## 📸 Screenshots & Documentation

### Neo4j Graph Schema
The complete graph schema diagram is available in `GRAPH_SCHEMA.md`, showing:
- Node types (User, Skill, Company)
- Relationship types (KNOWS, HAS_SKILL, WORKS_AT)
- Properties and constraints

### Query Performance
Query optimization documentation and performance benchmarks are available in `QUERY_OPTIMIZATION.md` and `QUERY_PERFORMANCE.md`.

### Demo Notebook
The `demo_fixed.ipynb` notebook provides a comprehensive walkthrough of:
- Database statistics and exploration
- Friend recommendation queries
- Job matching algorithms
- Network path analysis
- Graph analytics and visualizations

### Pull Request History
All merged pull requests are visible in the [GitHub repository](https://github.com/widodu77/social-network-neo4j/pulls?q=is%3Apr+is%3Amerged).

## 📝 License

This project is part of an academic assignment for AIDAMS 3A.

## 🙏 Acknowledgments

- [Neo4j](https://neo4j.com/) for the graph database
- [FastAPI](https://fastapi.tiangolo.com/) for the web framework
- [SNAP](https://snap.stanford.edu/) for dataset inspiration

---

**Need help?** Check the [FastAPI docs](http://localhost:8000/docs) or create an issue.
