from abc import ABC, abstractmethod
from app.features.auth.domain.entities import UserEntity, ResetCodeEntity
from typing import Optional

class UserRepository(ABC):
    @abstractmethod
    def create_user(self, user: UserEntity) -> UserEntity:
        pass

    @abstractmethod
    def get_user_by_username(self, username: str) -> Optional[UserEntity]:
        pass

    @abstractmethod
    def get_user_by_email(self, email: str) -> Optional[UserEntity]:
        pass

    @abstractmethod
    def update_user(self, user: UserEntity) -> None:
        pass

    @abstractmethod
    def create_reset_code(self, reset_code: ResetCodeEntity) -> ResetCodeEntity:
        pass

    @abstractmethod
    def get_reset_code(self, code: str) -> Optional[ResetCodeEntity]:
        pass

    @abstractmethod
    def delete_reset_code(self, code: str) -> None:
        pass