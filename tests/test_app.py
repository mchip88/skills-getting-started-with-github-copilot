"""
Tests for Mergington High School Activities API.
Using Arrange-Act-Assert (AAA) pattern for test clarity.
"""

import pytest


class TestGetActivities:
    """Tests for GET /activities endpoint"""

    def test_get_all_activities_success(self, client, fresh_activities):
        """
        Arrange: Set up test client and fresh activities
        Act: Fetch all activities
        Assert: Verify status code and response contains all activities
        """
        # Arrange
        expected_activity_count = len(fresh_activities)

        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        activities = response.json()
        assert len(activities) == expected_activity_count
        assert "Chess Club" in activities
        assert "Programming Class" in activities

    def test_get_activities_contains_participant_info(self, client):
        """
        Arrange: Set up test client with activities
        Act: Fetch activities
        Assert: Verify each activity contains required fields
        """
        # Arrange & Act
        response = client.get("/activities")

        # Assert
        activities = response.json()
        for activity_name, activity_details in activities.items():
            assert "description" in activity_details
            assert "schedule" in activity_details
            assert "max_participants" in activity_details
            assert "participants" in activity_details
            assert isinstance(activity_details["participants"], list)


class TestSignup:
    """Tests for POST /activities/{activity_name}/signup endpoint"""

    def test_signup_successful(self, client, sample_emails):
        """
        Arrange: New student email and valid activity name
        Act: Submit signup request
        Assert: Verify status code, response message, and participant was added
        """
        # Arrange
        activity = "Chess Club"
        email = sample_emails["new_student"]

        # Act
        response = client.post(f"/activities/{activity}/signup?email={email}")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "Signed up" in data["message"]
        assert email in data["message"]
        assert activity in data["message"]

        # Verify participant was actually added
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert email in activities[activity]["participants"]

    def test_signup_duplicate_registration_fails(self, client, sample_emails):
        """
        Arrange: Student already registered for an activity
        Act: Attempt to sign up same student again
        Assert: Verify 400 status code and error message
        """
        # Arrange
        activity = "Chess Club"
        email = sample_emails["existing_student"]  # michael@mergington.edu already in Chess Club

        # Act
        response = client.post(f"/activities/{activity}/signup?email={email}")

        # Assert
        assert response.status_code == 400
        data = response.json()
        assert "already signed up" in data["detail"].lower()

    def test_signup_activity_not_found(self, client, sample_emails):
        """
        Arrange: Non-existent activity name
        Act: Submit signup request for invalid activity
        Assert: Verify 404 status code and error message
        """
        # Arrange
        activity = "Nonexistent Activity"
        email = sample_emails["new_student"]

        # Act
        response = client.post(f"/activities/{activity}/signup?email={email}")

        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]

    def test_signup_multiple_different_activities(self, client, sample_emails):
        """
        Arrange: New student, two different activities
        Act: Sign up for first activity, then second
        Assert: Verify both signups succeed and participant appears in both
        """
        # Arrange
        email = sample_emails["new_student"]
        activity1 = "Chess Club"
        activity2 = "Programming Class"

        # Act
        response1 = client.post(f"/activities/{activity1}/signup?email={email}")
        response2 = client.post(f"/activities/{activity2}/signup?email={email}")

        # Assert
        assert response1.status_code == 200
        assert response2.status_code == 200

        # Verify in both activities
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert email in activities[activity1]["participants"]
        assert email in activities[activity2]["participants"]

    @pytest.mark.parametrize("invalid_activity", [
        "Art", "Club", "Team", "Unknown Activity"
    ])
    def test_signup_various_invalid_activities(self, client, sample_emails, invalid_activity):
        """
        Arrange: Various invalid activity names
        Act: Attempt signup with each invalid activity
        Assert: All return 404
        """
        # Arrange & Act
        response = client.post(f"/activities/{invalid_activity}/signup?email={sample_emails['new_student']}")

        # Assert
        assert response.status_code == 404


class TestUnregister:
    """Tests for POST /activities/{activity_name}/unregister endpoint"""

    def test_unregister_successful(self, client):
        """
        Arrange: Existing participant in an activity
        Act: Submit unregister request
        Assert: Verify status code, response message, and participant was removed
        """
        # Arrange
        activity = "Chess Club"
        email = "michael@mergington.edu"  # Existing participant

        # Act
        response = client.post(f"/activities/{activity}/unregister?email={email}")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert "Unregistered" in data["message"]
        assert email in data["message"]

        # Verify participant was actually removed
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert email not in activities[activity]["participants"]

    def test_unregister_not_registered_fails(self, client, sample_emails):
        """
        Arrange: Student not registered for an activity
        Act: Attempt to unregister
        Assert: Verify 400 status code and error message
        """
        # Arrange
        activity = "Chess Club"
        email = sample_emails["new_student"]  # Not in any activity

        # Act
        response = client.post(f"/activities/{activity}/unregister?email={email}")

        # Assert
        assert response.status_code == 400
        data = response.json()
        assert "not signed up" in data["detail"].lower()

    def test_unregister_activity_not_found(self, client):
        """
        Arrange: Non-existent activity name
        Act: Submit unregister request for invalid activity
        Assert: Verify 404 status code and error message
        """
        # Arrange
        activity = "Nonexistent Activity"
        email = "michael@mergington.edu"

        # Act
        response = client.post(f"/activities/{activity}/unregister?email={email}")

        # Assert
        assert response.status_code == 404
        data = response.json()
        assert "Activity not found" in data["detail"]

    def test_unregister_then_signup_again(self, client, sample_emails):
        """
        Arrange: Participant already in an activity
        Act: Unregister, then sign up again
        Assert: Both operations succeed and participant is back
        """
        # Arrange
        activity = "Chess Club"
        email = sample_emails["new_student"]

        # First, sign up
        signup_response = client.post(f"/activities/{activity}/signup?email={email}")
        assert signup_response.status_code == 200

        # Act - Unregister
        unregister_response = client.post(f"/activities/{activity}/unregister?email={email}")

        # Assert unregister
        assert unregister_response.status_code == 200

        # Act - Sign up again
        signup_again_response = client.post(f"/activities/{activity}/signup?email={email}")

        # Assert signup again
        assert signup_again_response.status_code == 200

        # Verify participant is back
        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert email in activities[activity]["participants"]

    @pytest.mark.parametrize("invalid_activity", [
        "Art", "Club", "Team", "Unknown Activity"
    ])
    def test_unregister_various_invalid_activities(self, client, invalid_activity):
        """
        Arrange: Various invalid activity names
        Act: Attempt unregister with each invalid activity
        Assert: All return 404
        """
        # Arrange & Act
        response = client.post(f"/activities/{invalid_activity}/unregister?email=test@example.com")

        # Assert
        assert response.status_code == 404


class TestIntegration:
    """Integration tests combining multiple operations"""

    def test_full_workflow(self, client, sample_emails):
        """
        Arrange: Fresh state, new student, and activity
        Act: Get activities, sign up, verify, unregister, verify
        Assert: State changes correctly throughout workflow
        """
        # Arrange
        activity = "Debate Team"
        email = sample_emails["new_student"]

        # Act & Assert - Get initial state
        activities_response = client.get("/activities")
        initial_activities = activities_response.json()
        assert email not in initial_activities[activity]["participants"]
        initial_participant_count = len(initial_activities[activity]["participants"])

        # Act - Sign up
        signup_response = client.post(f"/activities/{activity}/signup?email={email}")
        assert signup_response.status_code == 200

        # Assert - Verify signup
        activities_response = client.get("/activities")
        after_signup = activities_response.json()
        assert email in after_signup[activity]["participants"]
        assert len(after_signup[activity]["participants"]) == initial_participant_count + 1

        # Act - Unregister
        unregister_response = client.post(f"/activities/{activity}/unregister?email={email}")
        assert unregister_response.status_code == 200

        # Assert - Verify unregister
        activities_response = client.get("/activities")
        after_unregister = activities_response.json()
        assert email not in after_unregister[activity]["participants"]
        assert len(after_unregister[activity]["participants"]) == initial_participant_count

    def test_multiple_students_same_activity(self, client, sample_emails):
        """
        Arrange: Multiple different students
        Act: Sign up all for same activity
        Assert: All appear in participants list
        """
        # Arrange
        activity = "Science Club"
        email1 = sample_emails["new_student"]
        email2 = sample_emails["another_student"]

        # Act
        response1 = client.post(f"/activities/{activity}/signup?email={email1}")
        response2 = client.post(f"/activities/{activity}/signup?email={email2}")

        # Assert
        assert response1.status_code == 200
        assert response2.status_code == 200

        activities_response = client.get("/activities")
        activities = activities_response.json()
        assert email1 in activities[activity]["participants"]
        assert email2 in activities[activity]["participants"]
        # Both original participants plus new ones
        assert len(activities[activity]["participants"]) == 4
