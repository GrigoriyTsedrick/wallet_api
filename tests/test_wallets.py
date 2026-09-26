import asyncio
import uuid

import pytest


@pytest.mark.asyncio
async def test_create_wallet(client):
    response = await client.post("/api/v1/wallets/")
    assert response.status_code == 201
    assert float(response.json()["balance"]) == 0.0


@pytest.mark.asyncio
async def test_deposit(client):
    wallet_id = (await client.post("/api/v1/wallets/")).json()["id"]

    response = await client.post(
        f"/api/v1/wallets/{wallet_id}/operation",
        json={"operation_type": "DEPOSIT", "amount": 1000},
    )
    assert response.status_code == 200
    assert float(response.json()["balance"]) == 1000.0


@pytest.mark.asyncio
async def test_withdraw_ok(client):
    wallet_id = (await client.post("/api/v1/wallets/")).json()["id"]
    await client.post(
        f"/api/v1/wallets/{wallet_id}/operation",
        json={"operation_type": "DEPOSIT", "amount": 500},
    )

    response = await client.post(
        f"/api/v1/wallets/{wallet_id}/operation",
        json={"operation_type": "WITHDRAW", "amount": 200},
    )
    assert response.status_code == 200
    assert float(response.json()["balance"]) == 300.0


@pytest.mark.asyncio
async def test_withdraw_not_enough_money(client):
    wallet_id = (await client.post("/api/v1/wallets/")).json()["id"]

    response = await client.post(
        f"/api/v1/wallets/{wallet_id}/operation",
        json={"operation_type": "WITHDRAW", "amount": 500},
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Недостаточно средств"


@pytest.mark.asyncio
async def test_get_wallet_not_found(client):
    response = await client.get(f"/api/v1/wallets/{uuid.uuid4()}")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_amount_must_be_positive(client):
    wallet_id = (await client.post("/api/v1/wallets/")).json()["id"]
    response = await client.post(
        f"/api/v1/wallets/{wallet_id}/operation",
        json={"operation_type": "DEPOSIT", "amount": -100},
    )
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_concurrent_deposits(client):
    """10 параллельных пополнений по 100 → должно быть ровно 1000."""
    wallet_id = (await client.post("/api/v1/wallets/")).json()["id"]

    tasks = [
        client.post(
            f"/api/v1/wallets/{wallet_id}/operation",
            json={"operation_type": "DEPOSIT", "amount": 100},
        )
        for _ in range(10)
    ]
    responses = await asyncio.gather(*tasks)
    assert all(r.status_code == 200 for r in responses)

    final = await client.get(f"/api/v1/wallets/{wallet_id}")
    assert float(final.json()["balance"]) == 1000.0
