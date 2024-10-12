import pytest
import pandas as pd
from core.data_processor import DataProcessor
from core.models import ExpenseReport, JoinedData

def test_join_data():
    expense_reports = [
        ExpenseReport(id=1, amount=100.0, description="Lunch", date="2023-10-01"),
        ExpenseReport(id=2, amount=200.0, description="Travel", date="2023-10-02")
    ]

    csv_data = {
        'expense_id': [1, 2],
        'csv_field1': ['A', 'B'],
        'csv_field2': ['X', 'Y']
    }

    csv_df = pd.DataFrame(csv_data)
    processor = DataProcessor(csv_path='dummy_path')
    joined = processor.join_data(expense_reports, csv_df)

    assert len(joined) == 2
    assert joined[0].csv_field1 == 'A'
    assert joined[1].csv_field2 == 'Y'
