import uuid
from datetime import date as Date
from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, Field

from app.modules.finance.models import TransactionCategory, TransactionType


class TransactionCreate(BaseModel):
    type: TransactionType
    category: TransactionCategory
    amount: Decimal = Field(gt=0)
    date: Date
    description: Optional[str] = None
    member_id: Optional[uuid.UUID] = None
    tournament_id: Optional[uuid.UUID] = None


class TransactionUpdate(BaseModel):
    type: Optional[TransactionType] = None
    category: Optional[TransactionCategory] = None
    amount: Optional[Decimal] = Field(default=None, gt=0)
    date: Optional[Date] = None
    description: Optional[str] = None
    member_id: Optional[uuid.UUID] = None
    tournament_id: Optional[uuid.UUID] = None


class TransactionResponse(BaseModel):
    id: uuid.UUID
    type: TransactionType
    category: TransactionCategory
    amount: Decimal
    date: Date
    description: Optional[str]
    member_id: Optional[uuid.UUID]
    tournament_id: Optional[uuid.UUID]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class BalanceResponse(BaseModel):
    total_income: Decimal
    total_expense: Decimal
    balance: Decimal
    tournament_id: Optional[uuid.UUID] = None


class PeriodSummary(BaseModel):
    period: str
    total_income: Decimal
    total_expense: Decimal
    balance: Decimal


class ReportResponse(BaseModel):
    year: int
    period_type: str
    items: list[PeriodSummary]
