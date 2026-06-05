from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.modules.finance.repository import TransactionRepository
from app.modules.finance.service import TransactionService


def get_transaction_repository(db: AsyncSession = Depends(get_db)) -> TransactionRepository:
    return TransactionRepository(db)


def get_transaction_service(
    repo: TransactionRepository = Depends(get_transaction_repository),
) -> TransactionService:
    return TransactionService(repo)
