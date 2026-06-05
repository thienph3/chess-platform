import enum
import uuid
from datetime import date
from decimal import Decimal

from sqlalchemy import Date, Enum, ForeignKey, Numeric, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.shared.base_model import BaseModel


class TransactionType(str, enum.Enum):
    income = "income"
    expense = "expense"


class IncomeCategory(str, enum.Enum):
    membership_fee = "membership_fee"
    sponsorship = "sponsorship"
    donation = "donation"
    other_income = "other_income"


class ExpenseCategory(str, enum.Enum):
    venue = "venue"
    prize = "prize"
    equipment = "equipment"
    food = "food"
    other_expense = "other_expense"


# Tất cả category gộp lại để dùng trong DB
class TransactionCategory(str, enum.Enum):
    membership_fee = "membership_fee"
    sponsorship = "sponsorship"
    donation = "donation"
    other_income = "other_income"
    venue = "venue"
    prize = "prize"
    equipment = "equipment"
    food = "food"
    other_expense = "other_expense"


class Transaction(BaseModel):
    __tablename__ = "transactions"

    type: Mapped[TransactionType] = mapped_column(Enum(TransactionType), nullable=False)
    category: Mapped[TransactionCategory] = mapped_column(Enum(TransactionCategory), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(precision=15, scale=2), nullable=False)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    member_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("members.id"), nullable=True
    )
    tournament_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tournaments.id"), nullable=True
    )
