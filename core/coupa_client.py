import requests
from typing import List
from .models import ExpenseReport

class CoupaClient:
    def __init__(self, api_key: str, base_url: str):
        self.api_key = api_key
        self.base_url = base_url

    def get_expense_reports(self) -> List[ExpenseReport]:
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Accept': 'application/json'
        }
        response = requests.get(f"{self.base_url}/expense_reports", headers=headers)
        response.raise_for_status()
        data = response.json()
        return [ExpenseReport(**item) for item in data]
