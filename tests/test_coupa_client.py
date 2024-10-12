import pytest
from unittest.mock import patch
from core.coupa_client import CoupaClient
from core.models import ExpenseReport
import json
import os

@pytest.fixture
def sample_expense_reports():
    with open(os.path.join(os.path.dirname(__file__), 'sample_expense_reports.json')) as f:
        return json.load(f)

@patch('core.coupa_client.requests.get')
def test_get_expense_reports(mock_get, sample_expense_reports):
    mock_response = mock_get.return_value
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = sample_expense_reports

    client = CoupaClient(api_key="test_key", base_url="https://api.coupa.com")
    reports = client.get_expense_reports()

    assert len(reports) == 3
    assert isinstance(reports[0], ExpenseReport)
    assert reports[0].id == 1
    assert reports[0].amount == 150.75
    assert reports[1].description == "Flight to NYC"
    assert reports[2].date == "2024-04-17"
