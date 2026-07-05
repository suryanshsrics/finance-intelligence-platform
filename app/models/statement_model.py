from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base

# from user_model import User

class Statement(Base):
    __tablename__ = "statements"

    statement_id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.user_id"), nullable=False)
    filename = Column(String(255), nullable=False)
    bank_name = Column(String)
    account_number_last4 = Column(String)

    statement_start_date = Column(Date)
    statement_end_date = Column(Date)

    upload_ts = Column(DateTime(timezone=True), server_default=func.now())

    total_transactions = Column(Integer, default=0)

    # Many statements belong to one user
    user = relationship("User", back_populates="statements")

    # One statement has many transactions
    transactions = relationship(
        "Transaction",
        back_populates="statement",
        cascade="all, delete-orphan"
    )
    
