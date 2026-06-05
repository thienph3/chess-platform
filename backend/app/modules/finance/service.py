import uuid
from datetime import date
from decimal import Decimal

from app.core.exceptions import NotFoundException
from app.modules.finance.models import Transaction, TransactionCategory, TransactionType
from app.modules.finance.repository import TransactionRepository
from app.modules.finance.schemas import (
    BalanceResponse,
    PeriodSummary,
    ReportResponse,
    TransactionCreate,
    TransactionResponse,
    TransactionUpdate,
)


class TransactionService:
    def __init__(self, repository: TransactionRepository):
        self.repository = repository

    async def list_transactions(
        self,
        page: int,
        page_size: int,
        type_filter: TransactionType | None = None,
        category_filter: TransactionCategory | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
        tournament_id: uuid.UUID | None = None,
    ) -> tuple[list[TransactionResponse], int]:
        transactions, total = await self.repository.get_all(
            page, page_size, type_filter, category_filter, date_from, date_to, tournament_id
        )
        return [TransactionResponse.model_validate(t) for t in transactions], total

    async def create_transaction(self, data: TransactionCreate) -> TransactionResponse:
        transaction = Transaction(**data.model_dump())
        transaction = await self.repository.create(transaction)
        return TransactionResponse.model_validate(transaction)

    async def update_transaction(self, transaction_id: uuid.UUID, data: TransactionUpdate) -> TransactionResponse:
        transaction = await self.repository.get_by_id(transaction_id)
        if not transaction:
            raise NotFoundException("Giao dịch không tồn tại")
        for field, value in data.model_dump(exclude_unset=True).items():
            setattr(transaction, field, value)
        transaction = await self.repository.update(transaction)
        return TransactionResponse.model_validate(transaction)

    async def delete_transaction(self, transaction_id: uuid.UUID) -> None:
        transaction = await self.repository.get_by_id(transaction_id)
        if not transaction:
            raise NotFoundException("Giao dịch không tồn tại")
        await self.repository.soft_delete(transaction)

    async def get_balance(self, tournament_id: uuid.UUID | None = None) -> BalanceResponse:
        total_income, total_expense = await self.repository.get_balance(tournament_id)
        return BalanceResponse(
            total_income=total_income,
            total_expense=total_expense,
            balance=total_income - total_expense,
            tournament_id=tournament_id,
        )

    async def get_report(self, year: int, period: str = "monthly") -> ReportResponse:
        if period == "quarterly":
            return await self._build_quarterly_report(year)
        return await self._build_monthly_report(year)

    async def _build_monthly_report(self, year: int) -> ReportResponse:
        rows = await self.repository.get_monthly_report(year)
        monthly_data: dict[int, dict[str, Decimal]] = {}
        for row in rows:
            month = int(row["month"])
            monthly_data.setdefault(month, {"income": Decimal("0"), "expense": Decimal("0")})
            monthly_data[month][row["type"].value] = Decimal(str(row["total"]))

        items = []
        for month in range(1, 13):
            data = monthly_data.get(month, {"income": Decimal("0"), "expense": Decimal("0")})
            items.append(PeriodSummary(
                period=f"{year}-{month:02d}",
                total_income=data["income"],
                total_expense=data["expense"],
                balance=data["income"] - data["expense"],
            ))
        return ReportResponse(year=year, period_type="monthly", items=items)

    async def _build_quarterly_report(self, year: int) -> ReportResponse:
        rows = await self.repository.get_quarterly_report(year)
        quarterly_data: dict[int, dict[str, Decimal]] = {}
        for row in rows:
            quarter = int(row["quarter"])
            quarterly_data.setdefault(quarter, {"income": Decimal("0"), "expense": Decimal("0")})
            quarterly_data[quarter][row["type"].value] = Decimal(str(row["total"]))

        items = []
        for quarter in range(1, 5):
            data = quarterly_data.get(quarter, {"income": Decimal("0"), "expense": Decimal("0")})
            items.append(PeriodSummary(
                period=f"{year}-Q{quarter}",
                total_income=data["income"],
                total_expense=data["expense"],
                balance=data["income"] - data["expense"],
            ))
        return ReportResponse(year=year, period_type="quarterly", items=items)
