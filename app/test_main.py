import logging

from fastapi.testclient import TestClient

from app import dummy

from app.main import app

client = TestClient(app)
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

logger = logging.getLogger(__name__)

# test pr generation
def test_pr_generation():
    # given
    commits = dummy.commit_history
    logging.debug("Commit history: %s", commits)

    # when
    response = client.post("/generate_pr", json=commits)
    logger.debug("Response: %s", response.json())

    response_data = response.json()
    logger.debug("Response data: %s", response_data)

    # then
    assert response.status_code == 200, "Expected status code 200, got %s" % response.status_code
    assert response_data["title"] == "Test PR"
