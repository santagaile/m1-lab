"""CR-1: personas koda formāta pārbaude (tracker/CR-1.md). Visi kodi ir sintētiski."""

import logging

import pytest

from app import storage


def post(client, payload, code):
    payload["personalCode"] = code
    return client.post("/submissions", json=payload)


def stored_code(client, response):
    assert response.status_code == 201
    return client.get(f"/submissions/{response.json()['id']}").json()["personalCode"]


def assert_rejected(response, issue, fake_omd):
    assert response.status_code == 400
    error = response.json()["error"]
    assert error["code"] == "VALIDATION_ERROR"
    assert error["details"] == [{"field": "personalCode", "issue": issue}]
    # Nederīgu iesniegumu nesaglabā un OMD nesauc.
    assert fake_omd.calls == []
    assert storage.get("IES-2026-000001") is None


# Kritēriji 1, 2, 3, 8: derīgs formāts, saglabā 11 ciparus
@pytest.mark.parametrize(
    "code, expected",
    [
        ("32000000001", "32000000001"),  # 1
        ("320000-00001", "32000000001"),  # 2
        (" 32000000001 ", "32000000001"),  # 3
        ("311299-21233", "31129921233"),  # 8
    ],
)
def test_valid_code_is_saved_as_11_digits(client, valid_payload, code, expected):
    assert stored_code(client, post(client, valid_payload, code)) == expected


# Kritēriji 4, 5, 6, 9: nederīgs formāts
@pytest.mark.parametrize(
    "code",
    [
        "3200000000",  # 4: 10 cipari
        "320000000012",  # 5: 12 cipari
        "32000000O01",  # 6: burts O
        "3200-0000001",  # 9: defise nepareizā vietā
        "320000--00001",
        "320000 00001",  # atstarpe vidū
        "32000000001-",
        "３２００００００００１",  # ne-ASCII cipari
    ],
)
def test_invalid_format_rejected(client, valid_payload, fake_omd, code):
    assert_rejected(post(client, valid_payload, code), "INVALID_FORMAT", fake_omd)


def test_non_string_rejected(client, valid_payload, fake_omd):
    assert_rejected(
        post(client, valid_payload, 32000000001), "INVALID_FORMAT", fake_omd
    )


# Kritērijs 7: lauka nav
def test_missing_code_required(client, valid_payload, fake_omd):
    del valid_payload["personalCode"]
    response = client.post("/submissions", json=valid_payload)
    assert_rejected(response, "REQUIRED", fake_omd)


# Precizējums: tukša virkne vai tikai atstarpes → REQUIRED
@pytest.mark.parametrize("code", ["", "   "])
def test_empty_code_required(client, valid_payload, fake_omd, code):
    assert_rejected(post(client, valid_payload, code), "REQUIRED", fake_omd)


# Precizējums: kodu neatkārto ne atbildē, ne žurnālā
def test_code_not_in_error_response_or_log(client, valid_payload, caplog):
    code = "3200-0000001"
    with caplog.at_level(logging.DEBUG):
        response = post(client, valid_payload, code)
    assert response.status_code == 400
    assert code not in response.text
    assert code not in caplog.text


def test_code_not_in_log_on_success(client, valid_payload, caplog):
    with caplog.at_level(logging.DEBUG):
        response = post(client, valid_payload, "32000000001")
    assert response.status_code == 201
    assert "32000000001" not in caplog.text
    assert valid_payload["body"] not in caplog.text
