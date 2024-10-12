from pydantic import BaseModel
from typing import List

class ExpenseReport(BaseModel):
    id: int
    amount: float
    description: str
    date: str

class JoinedData(BaseModel):
    expense_id: int
    amount: float
    description: str
    date: str
    csv_field1: str
    csv_field2: str
