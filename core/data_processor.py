import pandas as pd
from typing import List
from .models import ExpenseReport, JoinedData

class DataProcessor:
    def __init__(self, csv_path: str):
        self.csv_path = csv_path

    def read_csv(self) -> pd.DataFrame:
        return pd.read_csv(self.csv_path)

    def join_data(self, expense_reports: List[ExpenseReport], csv_df: pd.DataFrame) -> List[JoinedData]:
        expense_df = pd.DataFrame([report.dict() for report in expense_reports])
        joined_df = pd.merge(expense_df, csv_df, how='inner', left_on='id', right_on='expense_id')
        return [JoinedData(**row) for row in joined_df.to_dict(orient='records')]
