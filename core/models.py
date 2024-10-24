from pydantic import BaseModel
from typing import Dict, Any, List, Literal

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

class InputDataItem(BaseModel):
    placeholders: Dict[str, Any]
    params: Dict[str, Any]  # Changed from List[Dict[str, Any]] to Dict[str, Any]

class RequestConfig(BaseModel):
    baseUrl: str
    headers: Dict[str, Any]
    method: Literal['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'HEAD', 'OPTIONS'] = 'GET'  # Constrained with valid HTTP methods
    id: Any
    inputData: List[InputDataItem]
