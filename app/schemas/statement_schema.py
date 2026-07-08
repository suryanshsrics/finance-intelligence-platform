from pydantic import BaseModel, Field, ConfigDict
from datetime import date, datetime

class StatementCreate(BaseModel):
    user_id: int
    file_name: str = Field(..., min_length=1)
    bank_name: str | None = None
    account_number_last4: int | None = None
    statement_start_date: date
    statement_end_date: date

class StatementResponse(BaseModel):
    statement_id: int
    user_id: int
    file_name: str
    bank_name: str | None = None
    account_number_last4: int | None = None
    statement_start_date: date
    statement_end_date: date
    total_transactions: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)