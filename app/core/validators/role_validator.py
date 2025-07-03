from fastapi import HTTPException

class RoleValidator:
    ROLES_HIERARCHY = {
        "S": ["S", "A1", "A2", "O"],
        "A1": ["A2", "O"],
        "A2": ["O"],
        "O": []
    }

    @classmethod
    def validate_role_assignment(cls, current_role: str, new_role: str):
        if new_role not in cls.ROLES_HIERARCHY.get(current_role, []):
            raise HTTPException(
                status_code=403,
                detail=f"Role {current_role} cannot assign role {new_role}"
            )