"""Inventory Router.

Exposes endpoints for inventory CRUD.
"""
import uuid
from typing import Any

from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.core.database.session import get_db_session
from app.core.security.rbac import RequiresRole
from app.modules.inventory.repository import InventoryRepository
from app.modules.inventory.schemas import InventoryItemCreate, InventoryItemResponse
from app.modules.inventory.service import InventoryService
from app.shared.response import APIResponse, success_response
from app.shared.pagination import PaginatedResponse, paginate

router = APIRouter()


class StockUpdateRequest(BaseModel):
    quantity: int


def get_inventory_service(db: AsyncSession = Depends(get_db_session)) -> InventoryService:
    repo = InventoryRepository(db)
    return InventoryService(repo)


@router.get("", response_model=APIResponse[PaginatedResponse[InventoryItemResponse]])
async def list_inventory(
    request: Request,
    skip: int = 0,
    limit: int = 100,
    inventory_service: InventoryService = Depends(get_inventory_service),
    # Hospital staff can view inventory
    user: dict = Depends(RequiresRole(["SYS_ADMIN", "HOSPITAL_ADMIN", "NURSE", "DOCTOR"]))
) -> Any:
    """List all inventory items within the actor's hospital."""
    hospital_id = uuid.UUID(user["hospital_id"])
    items = await inventory_service.get_all_items(hospital_id, skip, limit)
    paginated = paginate(items=items, total=len(items), page=(skip // limit) + 1, size=limit)
    return success_response(data=paginated)


@router.post("", response_model=APIResponse[InventoryItemResponse])
async def create_inventory_item(
    request: Request,
    data: InventoryItemCreate,
    inventory_service: InventoryService = Depends(get_inventory_service),
    user: dict = Depends(RequiresRole(["SYS_ADMIN", "HOSPITAL_ADMIN"]))
) -> Any:
    """Create a new inventory item."""
    actor_id = uuid.UUID(user["sub"])
    actor_hospital_id = uuid.UUID(user["hospital_id"])
    
    new_item = await inventory_service.create_item(data, actor_hospital_id, actor_id)
    return success_response(data=new_item, message="Inventory item created successfully")


@router.patch("/{item_id}/stock", response_model=APIResponse[InventoryItemResponse])
async def update_stock(
    item_id: uuid.UUID,
    data: StockUpdateRequest,
    inventory_service: InventoryService = Depends(get_inventory_service),
    user: dict = Depends(RequiresRole(["SYS_ADMIN", "HOSPITAL_ADMIN", "NURSE"]))
) -> Any:
    """Update stock quantity for an item."""
    actor_id = uuid.UUID(user["sub"])
    actor_hospital_id = uuid.UUID(user["hospital_id"])
    
    updated_item = await inventory_service.update_stock(item_id, data.quantity, actor_hospital_id, actor_id)
    return success_response(data=updated_item, message="Stock updated successfully")
