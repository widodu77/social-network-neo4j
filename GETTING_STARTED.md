# Getting Started Guide

## 🚀 Quick Start (5 minutes)

### Option 1: Using Make (Recommended)

```bash
# 1. Initialize project (creates .env file)
make init

# 2. Start all services
make docker-run

# Wait 30 seconds for services to start, then:

# 3. Seed the database (in a new terminal)
# First install Python dependencies
make install

# Then run the seeding script
make seed-data

# 4. Access the application
# - API Docs: http://localhost:8000/docs
# - Neo4j Browser: http://localhost:7474 (user: neo4j, password: password123)
# - Nginx Proxy: http://localhost/docs
```

### Option 2: Manual Setup

```bash
# 1. Copy environment file
cp .env.example .env

# 2. (Optional) Edit .env to customize passwords

# 3. Start services
docker-compose up -d

# 4. Wait for services to be healthy
docker-compose ps

# 5. Install Python dependencies
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
pip install -r requirements.txt

# 6. Seed the database
python scripts/seed_data.py

# 7. Test the API
curl http://localhost:8000/health
```

## 📋 Pre-Flight Checklist

Before starting, ensure you have:

- ✅ Docker Desktop installed and running
- ✅ Python 3.11+ installed
- ✅ At least 4GB of available RAM
- ✅ Ports 80, 7474, 7687, 8000 are free

### Check Port Availability

**On Linux/Mac:**
```bash
lsof -i :80 -i :7474 -i :7687 -i :8000
```

**On Windows:**
```powershell
netstat -ano | findstr ":80 :7474 :7687 :8000"
```

## 🧪 Verify Installation

### 1. Check Service Health

```bash
# Using Make
make health

# Or manually
curl http://localhost:8000/health
curl http://localhost:7474  # Should show Neo4j Browser
```

Expected response from `/health`:
```json
{
  "status": "healthy",
  "database": "connected",
  "health_check": true
}
```

### 2. Run Tests

```bash
make test
```

You should see:
- ✅ All tests passing
- ✅ Coverage report generated
- ✅ No critical errors

### 3. Check Database

Open Neo4j Browser: http://localhost:7474

Login with:
- Username: `neo4j`
- Password: `password123` (or whatever you set in `.env`)

Run this query to verify data:
```cypher
MATCH (u:User)
RETURN COUNT(u) AS user_count
```

Expected: ~100 users

## 🎯 First API Calls

### 1. List Users

```bash
curl http://localhost:8000/api/users?limit=5
```

### 2. Get Friend Recommendations

First, get a user ID:
```bash
USER_ID=$(curl -s http://localhost:8000/api/users?limit=1 | jq -r '.[0].user_id')
```

Then get recommendations:
```bash
curl "http://localhost:8000/api/users/$USER_ID/recommendations/friends?limit=5"
```

### 3. Find Shortest Path

```bash
# Get two user IDs
USER1=$(curl -s http://localhost:8000/api/users?limit=1&offset=0 | jq -r '.[0].user_id')
USER2=$(curl -s http://localhost:8000/api/users?limit=1&offset=1 | jq -r '.[0].user_id')

# Find path
curl "http://localhost:8000/api/paths/shortest?from=$USER1&to=$USER2"
```

## 📖 Interactive API Documentation

Visit http://localhost:8000/docs for Swagger UI where you can:

1. See all available endpoints
2. Try them out interactively
3. View request/response schemas
4. See example values

## 🐳 Docker Commands

### View Logs

```bash
# All services
make logs

# Specific service
docker-compose logs -f api
docker-compose logs -f neo4j
```

### Restart Services

```bash
# Restart all
docker-compose restart

# Restart specific service
docker-compose restart api
```

### Stop Services

```bash
# Stop but keep data
make docker-stop

# Stop and remove all data
make docker-clean
```

### Rebuild After Code Changes

```bash
# Rebuild API service
make docker-build

# Restart with new image
docker-compose up -d --force-recreate api
```

## 🔧 Development Workflow

### 1. Local Development (Without Docker)

```bash
# Ensure Neo4j is running in Docker
docker-compose up -d neo4j

# Activate virtual environment
source .venv/bin/activate

# Run API locally
make run

# API will be available at http://localhost:8000
```

### 2. Code Changes

```bash
# 1. Make your changes in app/

# 2. Format code
make format

# 3. Check linting
make lint

# 4. Run tests
make test

# 5. If all pass, commit
git add .
git commit -m "feat: your feature description"
```

### 3. Adding New Endpoints

1. Create service in `app/services/`
2. Create router in `app/routers/`
3. Register router in `app/main.py`
4. Write tests in `tests/`
5. Update documentation

## 🐛 Troubleshooting

### Issue: Services won't start

**Solution:**
```bash
# Check if ports are in use
make docker-stop
docker-compose down -v  # Remove all containers and volumes
make docker-run
```

### Issue: Neo4j connection refused

**Solution:**
```bash
# Wait longer for Neo4j to fully start
docker-compose logs neo4j

# Look for: "Started."
# Usually takes 30-60 seconds on first start
```

### Issue: Permission denied errors

**Solution:**
```bash
# On Linux, you may need to adjust ownership
sudo chown -R $USER:$USER .
```

### Issue: Database is empty

**Solution:**
```bash
# Re-run seeding script
make seed-data

# Or manually
python scripts/seed_data.py
```

### Issue: Tests failing

**Solution:**
```bash
# Ensure services are running
make health

# Clear test cache
make clean

# Run tests with verbose output
pytest tests/ -v
```

## 📊 Understanding the Sample Data

After seeding, you'll have:

- **100 Users**: Randomly generated with realistic names and profiles
- **30 Skills**: Programming languages, frameworks, tools
- **8 Companies**: Various tech companies
- **~750 Connections**: Average 15 connections per user
- **~450 Skills**: Average 4-5 skills per user

All data is generated using the Faker library for realistic values.

## 🎓 Next Steps

1. ✅ **Explore the API**: Try all endpoints in Swagger UI
2. ✅ **Query Neo4j**: Run Cypher queries in the browser
3. ✅ **Read the code**: Understand the service architecture
4. ✅ **Modify queries**: Experiment with recommendation algorithms
5. ✅ **Add features**: Implement your own endpoints

## 📚 Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Neo4j Cypher Manual](https://neo4j.com/docs/cypher-manual/current/)
- [Docker Compose Reference](https://docs.docker.com/compose/)
- [Pytest Documentation](https://docs.pytest.org/)

## 🆘 Need Help?

1. Check the logs: `make logs`
2. Review `README.md` for detailed documentation
3. Check `GRAPH_SCHEMA.md` for database structure
4. Review `PROJECT_SUMMARY.md` for project overview

## ✅ Success Criteria

You're ready to proceed when:

- ✅ `make health` returns healthy status for all services
- ✅ Neo4j Browser shows ~100 users
- ✅ API documentation loads at `/docs`
- ✅ `make test` shows all tests passing
- ✅ You can successfully call API endpoints

---

**Time to complete setup**: 5-10 minutes (including Docker image downloads)

**Estimated first-run database seeding**: 30-60 seconds

Happy coding! 🚀
