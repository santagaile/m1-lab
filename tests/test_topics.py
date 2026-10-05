"""CR-0: tēma "Parki un skvēri" un tēmu saraksts."""

import pytest


def test_list_topics_returns_all_topics_in_order(client):
    response = client.get("/topics")
    assert response.status_code == 200
    assert response.json() == [
        {"code": "ROADS", "name": "Ceļi un ielas"},
        {"code": "WASTE", "name": "Atkritumi"},
        {"code": "PLANNING", "name": "Teritorijas plānošana"},
        {"code": "PARKS", "name": "Parki un skvēri"},
        {"code": "OTHER", "name": "Cits"},
    ]


def test_submission_with_parks_topic_returns_201(client, valid_payload):
    valid_payload["topic"] = "PARKS"
    response = client.post("/submissions", json=valid_payload)
    assert response.status_code == 201


def test_submission_with_unknown_topic_returns_400(client, valid_payload):
    valid_payload["topic"] = "ZOO"
    response = client.post("/submissions", json=valid_payload)
    assert response.status_code == 400
    error = response.json()["error"]
    assert error["code"] == "VALIDATION_ERROR"
    assert {"field": "topic", "issue": "INVALID_FORMAT"} in error["details"]


@pytest.mark.parametrize("topic", ["ROADS", "WASTE", "PLANNING", "OTHER"])
def test_existing_topics_still_accepted(client, valid_payload, topic):
    valid_payload["topic"] = topic
    response = client.post("/submissions", json=valid_payload)
    assert response.status_code == 201
