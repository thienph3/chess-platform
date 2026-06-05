import uuid

from fastapi import APIRouter, Depends, Query

from app.modules.finance.dependencies import get_transaction_service
from app.modules.finance.schemas import BalanceResponse, ReportResponse
from app.modules.finance.service import TransactionService
from app.shared.schemas import ResponseEnvelope

finance_router = APIRouter(prefix="/finance", tags=["Finance"])


@finance_router.get("/balance", response_model=ResponseEnvelope[BalanceResponse])
async def get_balance(
    service: TransactionService = Depends(get_transaction_service),
):
    balance = await service.get_balance()
    return ResponseEnvelope(data=balance)


@finance_router.get("/balance/{tournament_id}", response_model=ResponseEnvelope[BalanceResponse])
async def get_tournament_balance(
    tournament_id: uuid.UUID,
    service: TransactionService = Depends(get_transaction_service),
):
    balance = await service.get_balance(tournament_id)
    return ResponseEnvelope(data=balance)


@finance_router.get("/report", response_model=ResponseEnvelope[ReportResponse])
async def get_report(
    year: int = Query(..., ge=2000, le=2100),
    period: str = Query(default="monthly", pattern="^(monthly|quarterly)$"),
    service: TransactionService = Depends(get_transaction_service),
):
    report = await service.get_report(year, period)
    return ResponseEnvelope(data=report)
