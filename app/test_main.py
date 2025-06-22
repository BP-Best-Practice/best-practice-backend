import logging

from fastapi.testclient import TestClient

from app import dummy

from app.main import app

client = TestClient(app)

# test pr generation
def test_pr_generation():
    # given
    commits = dummy.commit_history

    # when
    response = client.post("/pr_generation", json={"commits" : commits})

    response_data = response.json()

    # then
    assert response.status_code == 200, "Expected status code 200, got %s" % response.status_code
    assert response_data["title"] == "Test PR"
    assert response_data["body"] == "This is a test PR body"