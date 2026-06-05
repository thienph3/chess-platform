import uuid
from datetime import date

from fastapi import APIRouter, Depends, Query, status

from app.modules.finance.dependencies import get_transaction_service
from app.modules.finance.models import TransactionCategory, TransactionType
from app.modules.finance.schemas import TransactionCreate, TransactionResponse, TransactionUpdate
from app.modules.finance.service import TransactionService
from app.shared.schemas import PaginatedResponse, ResponseEnvelope

router = APIRouter(prefix="/transactions", tags=["Transactions"])


@router.get("", response_model=PaginatedResponse[TransactionResponse])
async def list_transactions(
    page: int = 1,
    page_size: int = 20,
    type: TransactionType | None = None,
    category: TransactionCategory | None = None,
    date_from: date | None = Query(default=None),
    date_to: date | None = Query(default=None),
    tournament_id: uuid.UUID | None = None,
    service: TransactionService = Depends(get_transaction_service),
):
    transactions, total = await service.list_transactions(
        page, page_size, type, category, date_from, date_to, tournament_id
    )
    return PaginatedResponse(data=transactions, total=total, page=page, page_size=page_size)


@router.post("", response_model=ResponseEnvelope[TransactionResponse], status_code=status.HTTP_201_CREATED)
async def create_transaction(
    data: TransactionCreate,
    service: TransactionService = Depends(get_transaction_service),
):
    transaction = await service.create_transaction(data)
    return ResponseEnvelope(data=transaction, message="Tạo giao dịch thành công")


@router.patch("/{transaction_id}", response_model=ResponseEnvelope[TransactionResponse])
async def update_transaction(
    transaction_id: uuid.UUID,
    data: TransactionUpdate,
    service: TransactionService = Depends(get_transaction_service),
):
    transaction = await service.update_transaction(transaction_id, data)
    return ResponseEnvelope(data=transaction, message="Cập nhật giao dịch thành công")


@router.delete("/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_transaction(
    transaction_id: uuid.UUID,
    service: TransactionService = Depends(get_transaction_service),
):
    await service.delete_transaction(transaction_id)
