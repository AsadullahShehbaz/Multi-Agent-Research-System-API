import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.main import app   # <-- your FastAPI app entrypoint
from app.database.db import Base, get_db, DATABASE_URL

# --- Test Database Setup ---
# Use a separate SQLite DB for tests
TEST_DATABASE_URL = "sqlite:///./test_research_assistant.db"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Override get_db dependency
def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

# Create tables before tests
Base.metadata.create_all(bind=engine)

# --- Fixtures ---
@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture
def db():
    return TestingSessionLocal()

@pytest.fixture
def token(client):
    """Register + login a user, return JWT token"""
    client.post("/auth/register", json={
        "username": "asad",
        "email": "asad@test.com",
        "password": "pass123"
    })
    response = client.post("/auth/login", json={
        "username": "asad",
        "password": "pass123"
    })
    return response.json()["access_token"]

# --- Tests ---
def test_register_user(client, db):
    response = client.post("/auth/register", json={
        "username": "asad",
        "email": "asad@test.com",
        "password": "pass123"
    })
    assert response.status_code == 201
    assert response.json()["username"] == "asad"

def test_login(client, db):
    client.post("/auth/register", json={
        "username": "asad",
        "email": "asad@test.com",
        "password": "pass123"
    })
    response = client.post("/auth/login", json={
        "username": "asad",
        "password": "pass123"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_research_flow(client, token):
    response = client.post(
        "/research/",
        headers={"Authorization": f"Bearer {token}"},
        json={"query": "AI agents"}   # use params for GET
    )
    assert response.status_code == 200
    data = response.json()
    
    # Optional: Add more assertions
    assert "id" in data
    assert "query" in data
    assert data["query"] == "AI agents"
    assert "final_report" in data
    assert data["status"] == "completed"

