import uuid
from datetime import date
from decimal import Decimal

from sqlalchemy import extract, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.modules.finance.models import Transaction, TransactionCategory, TransactionType


class TransactionRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_all(
        self,
        page: int = 1,
        page_size: int = 20,
        type_filter: TransactionType | None = None,
        category_filter: TransactionCategory | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
        tournament_id: uuid.UUID | None = None,
    ) -> tuple[list[Transaction], int]:
        query = select(Transaction).where(Transaction.is_deleted.is_(False))
        count_query = select(func.count()).select_from(Transaction).where(Transaction.is_deleted.is_(False))

        query, count_query = self._apply_filters(
            query, count_query, type_filter, category_filter, date_from, date_to, tournament_id
        )

        offset = (page - 1) * page_size
        query = query.order_by(Transaction.date.desc()).offset(offset).limit(page_size)

        result = await self.db.execute(query)
        transactions = list(result.scalars().all())
        total = (await self.db.execute(count_query)).scalar() or 0
        return transactions, total

    def _apply_filters(self, query, count_query, type_filter, category_filter, date_from, date_to, tournament_id):
        """Áp dụng bộ lọc cho cả query chính và count query."""
        if type_filter:
            query = query.where(Transaction.type == type_filter)
            count_query = count_query.where(Transaction.type == type_filter)
        if category_filter:
            query = query.where(Transaction.category == category_filter)
            count_query = count_query.where(Transaction.category == category_filter)
        if date_from:
            query = query.where(Transaction.date >= date_from)
            count_query = count_query.where(Transaction.date >= date_from)
        if date_to:
            query = query.where(Transaction.date <= date_to)
            count_query = count_query.where(Transaction.date <= date_to)
        if tournament_id:
            query = query.where(Transaction.tournament_id == tournament_id)
            count_query = count_query.where(Transaction.tournament_id == tournament_id)
        return query, count_query

    async def get_by_id(self, transaction_id: uuid.UUID) -> Transaction | None:
        query = select(Transaction).where(Transaction.id == transaction_id, Transaction.is_deleted.is_(False))
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def create(self, transaction: Transaction) -> Transaction:
        self.db.add(transaction)
        await self.db.commit()
        await self.db.refresh(transaction)
        return transaction

    async def update(self, transaction: Transaction) -> Transaction:
        await self.db.commit()
        await self.db.refresh(transaction)
        return transaction

    async def soft_delete(self, transaction: Transaction) -> None:
        transaction.is_deleted = True
        await self.db.commit()

    async def get_balance(self, tournament_id: uuid.UUID | None = None) -> tuple[Decimal, Decimal]:
        """Trả về (total_income, total_expense)."""
        base_filter = Transaction.is_deleted.is_(False)
        income_query = select(func.coalesce(func.sum(Transaction.amount), 0)).where(
            base_filter, Transaction.type == TransactionType.income
        )
        expense_query = select(func.coalesce(func.sum(Transaction.amount), 0)).where(
            base_filter, Transaction.type == TransactionType.expense
        )
        if tournament_id:
            income_query = income_query.where(Transaction.tournament_id == tournament_id)
            expense_query = expense_query.where(Transaction.tournament_id == tournament_id)

        total_income = (await self.db.execute(income_query)).scalar() or Decimal("0")
        total_expense = (await self.db.execute(expense_query)).scalar() or Decimal("0")
        return Decimal(str(total_income)), Decimal(str(total_expense))

    async def get_monthly_report(self, year: int) -> list[dict]:
        """Lấy báo cáo thu chi theo tháng."""
        base_filter = (Transaction.is_deleted.is_(False),)
        query = (
            select(
                extract("month", Transaction.date).label("month"),
                Transaction.type,
                func.coalesce(func.sum(Transaction.amount), 0).label("total"),
            )
            .where(*base_filter, extract("year", Transaction.date) == year)
            .group_by(extract("month", Transaction.date), Transaction.type)
            .order_by(extract("month", Transaction.date))
        )
        result = await self.db.execute(query)
        return [{"month": row.month, "type": row.type, "total": row.total} for row in result.all()]

    async def get_quarterly_report(self, year: int) -> list[dict]:
        """Lấy báo cáo thu chi theo quý."""
        base_filter = (Transaction.is_deleted.is_(False),)
        quarter_expr = func.ceil(extract("month", Transaction.date) / 3)
        query = (
            select(
                quarter_expr.label("quarter"),
                Transaction.type,
                func.coalesce(func.sum(Transaction.amount), 0).label("total"),
            )
            .where(*base_filter, extract("year", Transaction.date) == year)
            .group_by(quarter_expr, Transaction.type)
            .order_by(quarter_expr)
        )
        result = await self.db.execute(query)
        return [{"quarter": row.quarter, "type": row.type, "total": row.total} for row in result.all()]
