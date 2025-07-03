from datetime import datetime
from app.features.auth.data.models import UserCompanyRole
from app.features.logs.data.models import Log
from app.features.auth.data.repository import UserRepository
from app.features.subscription.service.subscription_service import SubscriptionService
from app.features.users.domain.user_cases import CreateUserUseCase, UpdateUserUseCase, DeleteUserUseCase, ListUsersUseCase
from typing import Optional, List
from app.features.users.domain.entities import UserEntity
from fastapi import HTTPException, status, Request

from app.features.work_flow.data.models import WorkflowActionType

class UserService:
    
    def __init__(self, repository: UserRepository, subscription_service: SubscriptionService):
        self.repository = repository
        self.db = repository.db
        self.subscription_service = subscription_service

    def create_user(
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
    ) -> dict:
        try:
            use_case = CreateUserUseCase(self.repository)
            user = use_case.execute(
                username,
                phone_num,
                email,
                password,
                role,
                company_id,
                can_delete_government,
                can_manage_government_admins,
                can_manage_operators,
                current_user
            )
            self._log_action(
                user_id=current_user["id"],
                action="USER_CREATE",
                entity_type="USER",
                entity_id=user.id,
                details=f"Created user {user.username}"
            )
            return {
                "id": user.id,
                "username": user.username,
                "phone_num": user.phone_num,
                "email": user.email,
                "role": user.role,
                "company_id": user.company_id,
                "is_active": user.is_active,
                "can_delete_government": user.can_delete_government,
                "can_manage_government_admins": user.can_manage_government_admins,
                "can_manage_operators": user.can_manage_operators
            }
        except Exception as e:
            self._log_action(
                user_id=current_user["id"],
                action="USER_CREATE_FAILED",
                entity_type="USER",
                details=str(e)
            )
            raise

    def update_user(
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
    ) -> dict:
        use_case = UpdateUserUseCase(self.repository)
        user = use_case.execute(
            user_id,
            username,
            phone_num,
            email,
            password,
            role,
            company_id,
            is_active,
            can_delete_government,
            can_manage_government_admins,
            can_manage_operators,
            current_user
        )
        self._log_action(
            user_id=current_user["id"],
            action="USER_UPDATE",
            entity_type="USER",
            entity_id=user.id,
            details=f"Updated user {user.username}"
        )
        return {
            "id": user.id,
            "username": user.username,
            "phone_num": user.phone_num,
            "email": user.email,
            "role": user.role,
            "company_id": user.company_id,
            "is_active": user.is_active,
            "can_delete_government": user.can_delete_government,
            "can_manage_government_admins": user.can_manage_government_admins,
            "can_manage_operators": user.can_manage_operators
        }

    def delete_user(self, user_id: int, current_user: dict) -> None:
        use_case = DeleteUserUseCase(self.repository)
        use_case.execute(user_id, current_user)
        self._log_action(
            user_id=current_user["id"],
            action="USER_DELETE",
            entity_type="USER",
            entity_id=user_id,
            details=f"Deleted user {user_id}"
        )

    def list_users(self, company_id: Optional[int], current_user: dict, page: int, per_page: int) -> List[dict]:
        use_case = ListUsersUseCase(self.repository)
        all_users = use_case.execute(company_id, current_user, page, per_page)
        
        start = (page - 1) * per_page
        end = start + per_page
        
        return {
            "data": [
                {
                    "id": user.id,
                    "username": user.username,
                    "phone_num": user.phone_num,
                    "email": user.email,
                    "role": user.role,
                    "company_id": user.company_id,
                    "is_active": user.is_active,
                    "can_delete_government": user.can_delete_government,
                    "can_manage_government_admins": user.can_manage_government_admins,
                    "can_manage_operators": user.can_manage_operators
                }
                for user in all_users[start:end]
            ],
            "pagination": {
                "total": len(all_users),
                "page": page,
                "per_page": per_page,
                "total_pages": (len(all_users) + per_page - 1) // per_page
            }
        }

    def change_user_role(self, user_id: int, new_role: str, current_user: dict) -> dict:
        use_case = UpdateUserUseCase(self.repository)
        user = self.repository.get_user_by_id(user_id)
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        
        user = use_case.execute(
            user_id=user_id,
            username=user.username,
            phone_num=user.phone_num,
            email=user.email,
            password=None,
            role=new_role,
            company_id=user.company_id,
            is_active=user.is_active,
            can_delete_government=user.can_delete_government,
            can_manage_government_admins=user.can_manage_government_admins,
            can_manage_operators=user.can_manage_operators,
            current_user=current_user
        )
        self._log_action(
            user_id=current_user["id"],
            action="USER_ROLE_CHANGE",
            entity_type="USER",
            entity_id=user.id,
            details=f"Changed role of user {user.username} to {new_role}"
        )
        return {
            "id": user.id,
            "username": user.username,
            "phone_num": user.phone_num,
            "email": user.email,
            "role": user.role,
            "company_id": user.company_id,
            "is_active": user.is_active,
            "can_delete_government": user.can_delete_government,
            "can_manage_government_admins": user.can_manage_government_admins,
            "can_manage_operators": user.can_manage_operators
        }
        
    def update_user_role(self, user_id: int, company_id: int, new_role: str, current_user: dict) -> dict:
        current_role = self._get_user_role(current_user["id"], company_id)
        if current_role != "S" and not self._can_manage_roles(current_user["id"], company_id):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only SuperAdmins or authorized users can change roles")
        
        if new_role not in ["A1", "A2", "O"]:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid role")
        
        target_user_role = self.db.query(UserCompanyRole).filter(
            UserCompanyRole.user_id == user_id,
            UserCompanyRole.company_id == company_id
        ).first()
        if not target_user_role:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not associated with this company")
        
        old_role = target_user_role.role
        target_user_role.role = new_role
        target_user_role.updated_at = datetime.utcnow()
        self.db.commit()
        
        self._log_action(
            user_id=current_user["id"],
            company_id=company_id,
            action="USER_ROLE_UPDATE",
            entity_type="USER",
            entity_id=user_id,
            details=f"Changed role from {old_role} to {new_role}"
        )
        self.workflow_repository.create_workflow(
            company_id=company_id,
            user_id=current_user["id"],
            asset_id=None,
            asset_name="User Role Update",
            action_type=WorkflowActionType.STATUS_CHANGED,
            details=f"Changed user role from {old_role} to {new_role}"
        )
        return {"user_id": user_id, "company_id": company_id, "role": new_role}
    
    def _can_manage_roles(self, user_id: int, company_id: int) -> bool:
        role = self.db.query(UserCompanyRole).filter(
            UserCompanyRole.user_id == user_id,
            UserCompanyRole.company_id == company_id
        ).first()
        return role and (role.can_manage_government_admins or role.can_manage_operators)

    def _log_action(self, user_id: int, company_id: int, action: str, entity_type: str, entity_id: int = None, details: str = ""):
        log = Log(
            user_id=user_id,
            company_id=company_id,
            action=action,
            entity_type=entity_type,
            entity_id=entity_id,
            details=details,
            timestamp=datetime.utcnow()
        )
        self.db.add(log)
        self.db.commit()

    def get_current_user_profile(self, current_user: dict) -> dict:
        user = self.repository.get_user_by_id(current_user["id"])
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        active_sub = self.subscription_service.get_user_active_subscription_details(user.id)
        
        subscription_details = None
        if active_sub:
            subscription_details = {
                "plan_type": active_sub.plan_type,
                "end_date": active_sub.end_date
            }

        return {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "phone_num": user.phone_num,
            "is_active": user.is_active,
            "subscription": subscription_details
        }
    