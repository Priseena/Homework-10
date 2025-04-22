import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app
from app.dependencies import get_db
from app.models.user_model import User
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from unittest.mock import AsyncMock, patch


# Password hashing setup
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ----------------------
# Database Fixture Setup
# ----------------------
@pytest.fixture
async def client_with_db(db_session: Session):
    app.dependency_overrides[get_db] = lambda: db_session
    transport = ASGITransport(app=app, raise_app_exceptions=True)
    async with AsyncClient(transport=transport, base_url="http://testserver") as client:
        yield client
    app.dependency_overrides.clear()


# ----------------------
# Data Fixtures
# ----------------------
@pytest.fixture
def user_create_data():
    return {
        "email": "newuser@example.com",
        "password": "SecurePassword123!",
        "nickname": "NewUser"
    }

@pytest.fixture
def user_base_data_invalid():
    return {
        "email": "not-an-email",
        "nickname": "Invalid User"
    }

@pytest.fixture
def verified_user(db_session: Session):
    user = User(
        email="verified@example.com",
        nickname="VerifiedUser",
        hashed_password=pwd_context.hash("MySuperPassword$1234"),
        email_verified=True,
        is_locked=False
    )
    db_session.add(user)
    db_session.commit()
    return user

@pytest.fixture
def locked_user(db_session: Session):
    user = User(
        email="locked@example.com",
        nickname="LockedUser",
        hashed_password=pwd_context.hash("MySuperPassword$1234"),
        email_verified=True,
        is_locked=True
    )
    db_session.add(user)
    db_session.commit()
    return user


# ----------------------
# Test Cases
# ----------------------

@pytest.mark.asyncio
@patch("app.services.email_service.EmailService.send_verification_email", new_callable=AsyncMock)
async def test_user_registration_success(mock_send_email, client_with_db, user_create_data):
    response = await client_with_db.post(
        "/api/users/register",
        json=user_create_data,
        follow_redirects=True,
    )

    assert response.status_code in [200, 201]
    assert response.json()
    data = response.json()
    assert data["email"] == user_create_data["email"]

    mock_send_email.assert_awaited_once()


@pytest.mark.asyncio
async def test_user_registration_invalid_email(client_with_db, user_base_data_invalid):
    data = {**user_base_data_invalid, "password": "SecurePassword123!"}
    response = await client_with_db.post("/api/users/register", json=data)
    assert response.status_code == 307

@pytest.mark.asyncio
async def test_user_login_success(client_with_db, verified_user):
    payload = {
        "username": verified_user.email,
        "password": "MySuperPassword$1234"
    }
    response = await client_with_db.post("/api/users/login", data=payload)
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

@pytest.mark.asyncio
async def test_user_login_locked_user(client_with_db, locked_user):
    payload = {
        "username": locked_user.email,
        "password": "MySuperPassword$1234"
    }
    response = await client_with_db.post("/api/users/login", data=payload)
    assert response.status_code == 403
    assert response.json()["detail"] == "Account locked due to too many failed login attempts."

@pytest.mark.asyncio
async def test_user_login_invalid_password(client_with_db, verified_user):
    payload = {
        "username": verified_user.email,
        "password": "WrongPassword123!"
    }
    response = await client_with_db.post("/api/users/login", data=payload)
    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect email or password."
