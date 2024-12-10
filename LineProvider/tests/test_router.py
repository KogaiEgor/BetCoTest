import pytest
import time
from fastapi.testclient import TestClient
from app.lines.models import EventState


@pytest.mark.asyncio
async def test_create_event_success(test_client: TestClient):
    payload = {
        "coefficient": 1.5,
        "deadline": int(time.time()) + 3600,
        "state": EventState.NEW.value,
    }
    response = test_client.post("/events/", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["coefficient"] == payload["coefficient"]
    assert data["deadline"] == payload["deadline"]
    assert data["state"] == payload["state"]
    assert "event_id" in data


@pytest.mark.asyncio
async def test_create_event_invalid_coefficient(test_client: TestClient):
    payload = {
        "coefficient": -1.0,
        "deadline": int(time.time()) + 3600,
        "state": EventState.NEW.value,
    }
    response = test_client.post("/events/", json=payload)
    assert response.status_code == 422
    assert "Input should be greater than 0" == response.json()["detail"][0]['msg']


@pytest.mark.asyncio
async def test_create_event_past_deadline(test_client: TestClient):
    payload = {
        "coefficient": 1.5,
        "deadline": 100,
        "state": EventState.NEW.value,
    }
    response = test_client.post("/events/", json=payload)
    assert response.status_code == 422
    print(response.json())
    assert "Value error, Deadline must be greater than the current time" == response.json()["detail"][0]['msg']


@pytest.mark.asyncio
async def test_update_event_success(test_client: TestClient):
    payload = {
        "coefficient": 1.5,
        "deadline": int(time.time()) + 3600,
        "state": EventState.NEW.value,
    }
    create_response = test_client.post("/events/", json=payload)
    event_id = create_response.json()["event_id"]

    update_payload = {"state": EventState.FINISHED_WIN.value}
    response = test_client.put(f"/events/{event_id}", json=update_payload)
    assert response.status_code == 200
    data = response.json()
    assert data["state"] == update_payload["state"]


@pytest.mark.asyncio
async def test_update_event_invalid_id(test_client: TestClient):
    update_payload = {"state": EventState.FINISHED_WIN.value}
    response = test_client.put("/events/nonexistent_id", json=update_payload)
    assert response.status_code == 400
    assert "Event not found" in response.json()["detail"]


@pytest.mark.asyncio
async def test_get_event_success(test_client: TestClient):
    payload = {
        "coefficient": 1.5,
        "deadline": int(time.time()) + 3600,
        "state": EventState.NEW.value,
    }
    create_response = test_client.post("/events/", json=payload)
    event_id = create_response.json()["event_id"]

    response = test_client.get(f"/events/{event_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["event_id"] == event_id
    assert data["coefficient"] == payload["coefficient"]


@pytest.mark.asyncio
async def test_get_event_not_found(test_client: TestClient):
    response = test_client.get("/events/nonexistent_id")
    assert response.status_code == 404
    assert "Event not found" in response.json()["detail"]


@pytest.mark.asyncio
async def test_get_active_events(test_client: TestClient):
    current_time = int(time.time())
    from app.lines.services import repository
    repository.events.clear()
    payload1 = {
        "coefficient": 1.5,
        "deadline": current_time + 3600,
        "state": EventState.NEW.value,
    }
    payload2 = {
        "coefficient": 1.7,
        "deadline": current_time + 7200,
        "state": EventState.NEW.value,
    }
    test_client.post("/events/", json=payload1)
    test_client.post("/events/", json=payload2)

    response = test_client.get("/events/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["coefficient"] == payload1["coefficient"]
    assert data[1]["coefficient"] == payload2["coefficient"]
