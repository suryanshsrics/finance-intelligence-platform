from pydantic import BaseModel
from datetime import date

class DashboardSummaryResponse(BaseModel):
    total_income: float
    total_expense: float
    net_savings: float
    total_transactions: int
    total_statements: int

class CategoryBreakdownResponse(BaseModel):
    category: str
    amount: float

class MonthlyTrendResponse(BaseModel):
    month: str
    income: float
    expense: float

class LargestTransactionResponse(BaseModel):
    largest_debit_amount: float
    description: str
    transaction_date: date
    category: str

class SpendingInsightsResponse(BaseModel):
    highest_spending_category: str
    highest_spent_amount: float
    average_monthly_expense: float
    largest_transaction: LargestTransactionResponse | None = None
    # total_income: float
    # total_expense: float
    # most_frequent_spending_category: str
