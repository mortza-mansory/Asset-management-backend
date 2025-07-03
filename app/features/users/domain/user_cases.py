from app.core.validators.role_validator import RoleValidator
from app.features.users.domain.entities import UserEntity
from app.features.auth.data.repository import UserRepository
from app.core.security import get_password_hash
from fastapi import HTTPException, status
from typing import Optional, List
from datetime import datetime

class CreateUserUseCase:
    def __init__(self, repository: UserRepository):
        self.repository = repository

    def execute(
        self,
        username: str,
        phone_num: Optional[str],
        email: Optional[str],
        password: str,
        role: str,
        company_id: Optional[int],
        can_delete_government: Optional[bool],
        can_manage_government_admins: Optional[bool],
        can_manage_operators: Optional[bool],
        current_user: dict
    ) -> UserEntity:
        RoleValidator.validate_role_assignment(current_user["role"], role)
        
        if not email and not phone_num:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="At least one of email or phone number must be provided")
        
        if self.repository.get_user_by_username(username) or (email and self.repository.get_user_by_email(email)):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username or email already exists")
        
        if current_user["role"] == "S":
            pass
        elif current_user["role"] == "A1":
            if role not in ["A2", "O"]:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Owners can only create Non-Owner Government Admins or Operators")
            user_company = self.repository.get_user_by_id(current_user["id"]).company_id
            if company_id != user_company:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Owners can only create users for their own company")
        elif current_user["role"] == "A2":
            current_user_entity = self.repository.get_user_by_id(current_user["id"])
            if not current_user_entity.can_manage_operators:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not authorized to manage operators")
            if role != "O":
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Non-Owner Government Admins can only create Operators")
            user_company = current_user_entity.company_id
            if company_id != user_company:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Non-Owner Government Admins can only create users for their own company")
        else:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only authorized users can create users")
        
        hashed_password = get_password_hash(password)
        user = UserEntity(
            id=None,
            username=username,
            phone_num=phone_num,
            email=email,
            hashed_password=hashed_password,
            role=role,
            company_id=company_id,
            is_active=True,
            can_delete_government=can_delete_government or False,
            can_manage_government_admins=can_manage_government_admins or False,
            can_manage_operators=can_manage_operators or False
        )
        return self.repository.create_user(user)

class UpdateUserUseCase:
    def __init__(self, repository: UserRepository):
        self.repository = repository

    def execute(
        self,
        user_id: int,
        username: Optional[str],
        phone_num: Optional[int],
        email: Optional[str],
        password: Optional[str],
        role: Optional[str],
        company_id: Optional[int],
        is_active: Optional[bool],
        can_delete_government: Optional[bool],
        can_manage_government_admins: Optional[bool],
        can_manage_operators: Optional[bool],
        current_user: dict
    ) -> UserEntity:
        user = self.repository.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        
        if current_user["role"] == "S":
            pass
        elif current_user["role"] == "A1":
            user_company = self.repository.get_user_by_id(current_user["id"]).company_id
            if user.company_id != user_company or (role and role not in ["A2", "O"]):
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Owners can only edit Non-Owner Government Admins or Operators in their own company")
        elif current_user["role"] == "A2":
            current_user_entity = self.repository.get_user_by_id(current_user["id"])
            if not current_user_entity.can_manage_operators:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not authorized to manage operators")
            user_company = current_user_entity.company_id
            if user.company_id != user_company or user.role != "O":
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Non-Owner Government Admins can only edit Operators in their own company")
        else:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only authorized users can update users")
        
        user.username = username or user.username
        user.phone_num = phone_num or user.phone_num
        user.email = email or user.email
        user.hashed_password = get_password_hash(password) if password else user.hashed_password
        user.role = role or user.role
        user.company_id = company_id or user.company_id
        user.is_active = is_active if is_active is not None else user.is_active
        user.can_delete_government = can_delete_government if can_delete_government is not None else user.can_delete_government
        user.can_manage_government_admins = can_manage_government_admins if can_manage_government_admins is not None else user.can_manage_government_admins
        user.can_manage_operators = can_manage_operators if can_manage_operators is not None else user.can_manage_operators
        return self.repository.update_user(user)

class DeleteUserUseCase:
    def __init__(self, repository: UserRepository):
        self.repository = repository

    def execute(self, user_id: int, current_user: dict) -> None:
        user = self.repository.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        
        if current_user["role"] == "S":
            pass
        elif current_user["role"] == "A1":
            user_company = self.repository.get_user_by_id(current_user["id"]).company_id
            if user.company_id != user_company or user.role not in ["A2", "O"]:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Owners can only delete Non-Owner Government Admins or Operators in their own company")
        elif current_user["role"] == "A2":
            current_user_entity = self.repository.get_user_by_id(current_user["id"])
            if not current_user_entity.can_manage_operators:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not authorized to manage operators")
            user_company = current_user_entity.company_id
            if user.company_id != user_company or user.role != "O":
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Non-Owner Government Admins can only delete Operators in their own company")
            if user_id == current_user["id"] and current_user_entity.can_delete_government:
                pass
            else:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this user")
        else:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only authorized users can delete users")
        
        self.repository.delete_user(user_id)

class ListUsersUseCase:
    def __init__(self, repository: UserRepository):
        self.repository = repository

    def execute(self, company_id: Optional[int], current_user: dict, page: int, per_page: int) -> List[UserEntity]:
        if current_user["role"] == "S":
            return self.repository.get_users_by_company(company_id)
        elif current_user["role"] in ["A1", "A2"]:
            user_company = self.repository.get_user_by_id(current_user["id"]).company_id
            if company_id and company_id != user_company:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You can only view users in your own company")
            return self.repository.get_users_by_company(user_company)
        else:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only authorized users can list users")