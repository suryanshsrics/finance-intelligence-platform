from sqlalchemy import Column, Integer, String, Date, DateTime, Numeric, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base

class Transaction(Base):
    __tablename__ = 'transactions'

    transaction_id = Column(Integer, primary_key=True)
    statement_id = Column(Integer, ForeignKey("statements.statement_id"), nullable=False)
    transaction_date = Column(Date, nullable=False)
    description = Column(String(500), nullable=False)
    amount = Column(Numeric(12, 2), nullable=False)
    transaction_type = Column(String(20), nullable=False)
    category = Column(String(50), default="Others")
    balance_after_transaction = Column(Numeric(12, 2))
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    # Many transactions belong to one statement
    statement = relationship("Statement", back_populates="transactions")