import sys
from pathlib import Path
import pytest
from fastapi import HTTPException, status
from datetime import datetime, timedelta
from unittest.mock import MagicMock, patch, create_autospec
from jose import jwt

root_dir = Path(__file__).parent.parent
sys.path.append(str(root_dir))

from app.features.auth.data.models import User
from app.features.auth.data.repository import SQLAlchemyUserRepository
from app.features.auth.domain.entities import UserEntity,ResetCodeEntity
from app.features.auth.service.auth_service import AuthService
from app.features.auth.data.schemas import UserCreate
from app.core.security import SECRET_KEY, ALGORITHM, get_password_hash, verify_password

@pytest.fixture
def mock_db_session():
    session = MagicMock()
    session.commit.return_value = None
    session.refresh.return_value = None
    return session

@pytest.fixture
def auth_repo(mock_db_session):
    return SQLAlchemyUserRepository(mock_db_session)

@pytest.fixture
def auth_service(auth_repo):
    return AuthService(auth_repo)

@pytest.fixture
def test_user_data():
    return {
        "username": "testuser",
        "phone_num": "1234567890",
        "email": "test@example.com",
        "password": "testpass",
        "company_name": "Test Co"
    }

@pytest.fixture
def test_user_entity(test_user_data):
    return UserEntity(
        id=1,
        username=test_user_data["username"],
        phone_num=test_user_data["phone_num"],
        email=test_user_data["email"],
        hashed_password=get_password_hash(test_user_data["password"])
    )

class TestAuthRepository:
    def test_create_user(self, auth_repo, mock_db_session, test_user_entity):
        mock_db_session.add.return_value = None
        
        result = auth_repo.create_user(test_user_entity)
        
        assert mock_db_session.add.called
        assert mock_db_session.commit.called
        assert isinstance(result, UserEntity)
        assert result.username == test_user_entity.username

    def test_get_user_by_username(self, auth_repo, mock_db_session, test_user_entity):
        mock_user = User(
            username=test_user_entity.username,
            phone_num=test_user_entity.phone_num,
            email=test_user_entity.email,
            hashed_password=test_user_entity.hashed_password
        )
        mock_db_session.query().filter().first.return_value = mock_user
        
        result = auth_repo.get_user_by_username(test_user_entity.username)
        
        assert isinstance(result, UserEntity)
        assert result.username == test_user_entity.username

class TestAuthService:
    def test_signup_success(self, auth_service, auth_repo, test_user_data):
        auth_repo.get_user_by_username.return_value = None
        auth_repo.get_user_by_email.return_value = None
        auth_repo.create_user.return_value = UserEntity(
            id=1,
            username=test_user_data["username"],
            phone_num=test_user_data["phone_num"],
            email=test_user_data["email"],
            hashed_password=get_password_hash(test_user_data["password"])
        )
        
        result = auth_service.signup(UserCreate(**test_user_data))
        
        assert "user_id" in result
        assert result["user_id"] == 1

    def test_login_success(self, auth_service, auth_repo, test_user_data):
        auth_repo.get_user_by_username.return_value = UserEntity(
            username=test_user_data["username"],
            hashed_password=get_password_hash(test_user_data["password"])
        )
        
        result = auth_service.login(
            username=test_user_data["username"],
            password=test_user_data["password"]
        )
        
        assert "access_token" in result
        assert result["token_type"] == "bearer"

class TestSecurity:
    def test_password_hashing(self):
        password = "testpass"
        hashed = get_password_hash(password)
        assert verify_password(password, hashed)
        assert not verify_password("wrongpass", hashed)
    
    def test_token_creation(self):
        token = jwt.encode(
            {"sub": "testuser", "exp": datetime.utcnow() + timedelta(minutes=30)},
            SECRET_KEY,
            algorithm=ALGORITHM
        )
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        assert payload["sub"] == "testuser"