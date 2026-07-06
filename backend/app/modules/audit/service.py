"""Audit Service logic.

Handles business logic for retrieving and creating audit logs.
"""
import uuid
from typing import Sequence, Any

from app.modules.audit.models import AuditLog
from app.modules.audit.repository import AuditLogRepository


class AuditService:
    """Service layer for audit logging."""
    
    def __init__(self, repo: AuditLogRepository) -> None:
        self.repo = repo

    async def get_hospital_logs(self, hospital_id: uuid.UUID, skip: int = 0, limit: int = 100) -> Sequence[AuditLog]:
        """Fetch audit logs for a hospital."""
        return await self.repo.get_hospital_logs(hospital_id=hospital_id, skip=skip, limit=limit)

    async def create_log(
        self, 
        action: str, 
        actor_id: uuid.UUID, 
        entity_type: str, 
        entity_id: str, 
        hospital_id: uuid.UUID,
        details: dict[str, Any] = None
    ) -> AuditLog:
        """Create a new audit log entry."""
        return await self.repo.create(
            action=action,
            actor_id=actor_id,
            entity_type=entity_type,
            entity_id=entity_id,
            hospital_id=hospital_id,
            details=details or {}
        )
