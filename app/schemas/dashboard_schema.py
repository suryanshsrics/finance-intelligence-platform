from pydantic import BaseModel

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