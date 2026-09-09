"""
Pytest configuration and shared fixtures for activity API tests.
"""

import pytest
from fastapi.testclient import TestClient
from src.app import app, get_activities_db


@pytest.fixture
def fresh_activities():
    """
    Provide a fresh, isolated copy of the activities database for each test.
    This ensures test isolation and prevents state leakage between tests.
    """
    return {
        "Chess Club": {
            "description": "Learn strategies and compete in chess tournaments",
            "schedule": "Fridays, 3:30 PM - 5:00 PM",
            "max_participants": 12,
            "participants": ["michael@mergington.edu", "daniel@mergington.edu"]
        },
        "Programming Class": {
            "description": "Learn programming fundamentals and build software projects",
            "schedule": "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
            "max_participants": 20,
            "participants": ["emma@mergington.edu", "sophia@mergington.edu"]
        },
        "Gym Class": {
            "description": "Physical education and sports activities",
            "schedule": "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
            "max_participants": 30,
            "participants": ["john@mergington.edu", "olivia@mergington.edu"]
        },
        "Basketball Team": {
            "description": "Compete in competitive basketball games and tournaments",
            "schedule": "Mondays, Wednesdays, Fridays, 4:00 PM - 5:30 PM",
            "max_participants": 15,
            "participants": ["james@mergington.edu"]
        },
        "Soccer Club": {
            "description": "Join our soccer team and develop skills through practice and matches",
            "schedule": "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
            "max_participants": 18,
            "participants": ["lucas@mergington.edu", "maya@mergington.edu"]
        },
        "Art Studio": {
            "description": "Explore painting, drawing, and other visual arts",
            "schedule": "Wednesdays, 3:30 PM - 5:00 PM",
            "max_participants": 16,
            "participants": ["isabella@mergington.edu"]
        },
        "Music Band": {
            "description": "Join our school band and perform at concerts and events",
            "schedule": "Thursdays, 3:30 PM - 5:00 PM",
            "max_participants": 25,
            "participants": ["noah@mergington.edu", "ava@mergington.edu"]
        },
        "Debate Team": {
            "description": "Develop public speaking and critical thinking through competitive debate",
            "schedule": "Mondays and Fridays, 3:30 PM - 4:45 PM",
            "max_participants": 10,
            "participants": ["liam@mergington.edu"]
        },
        "Science Club": {
            "description": "Conduct experiments and explore scientific concepts through hands-on activities",
            "schedule": "Wednesdays, 4:00 PM - 5:30 PM",
            "max_participants": 14,
            "participants": ["charlotte@mergington.edu", "benjamin@mergington.edu"]
        }
    }


@pytest.fixture
def client(fresh_activities):
    """
    Provide a TestClient with the activities dependency overridden to use fresh_activities.
    This ensures each test gets isolated activities data.
    """
    def override_get_activities():
        return fresh_activities
    
    app.dependency_overrides[get_activities_db] = override_get_activities
    
    test_client = TestClient(app)
    yield test_client
    
    # Clean up: remove the override after the test
    app.dependency_overrides.clear()


@pytest.fixture
def sample_emails():
    """
    Provide common test email addresses for use in tests.
    """
    return {
        "new_student": "new_student@mergington.edu",
        "another_student": "another_student@mergington.edu",
        "existing_student": "michael@mergington.edu"  # Already in Chess Club
    }
