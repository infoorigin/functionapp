import json
import azure.functions as func
from unittest.mock import patch, MagicMock
from HttpTriggerFunction1 import __init__ as func1
from HttpTriggerFunction2 import __init__ as func2
import pandas as pd
import os

@patch('core.coupa_client.CoupaClient.get_expense_reports')
@patch('core.data_processor.DataProcessor.read_csv')
def test_http_trigger_function1(mock_read_csv, mock_get_expense_reports):
    with open(os.path.join(os.path.dirname(__file__), 'sample_expense_reports.json')) as f:
        sample_expense_reports = json.load(f)
    mock_get_expense_reports.return_value = [ExpenseReport(**item) for item in sample_expense_reports]
    
    csv_data = {
        'expense_id': [1, 2, 3],
        'csv_field1': ['A', 'B', 'C'],
        'csv_field2': ['X', 'Y', 'Z']
    }
    mock_read_csv.return_value = pd.DataFrame(csv_data)

    req = func.HttpRequest(method='GET', url='/api/HttpTriggerFunction1')
    resp = func1.main(req)

    assert resp.status_code == 200
    response_data = json.loads(resp.get_body())
    assert len(response_data) == 3
    assert response_data[0]['expense_id'] == 1
    assert response_data[1]['csv_field1'] == 'B'
    assert response_data[2]['csv_field2'] == 'Z'

@patch('core.coupa_client.CoupaClient.get_expense_reports')
@patch('core.data_processor.DataProcessor.read_csv')
def test_http_trigger_function2(mock_read_csv, mock_get_expense_reports):
    with open(os.path.join(os.path.dirname(__file__), 'sample_expense_reports.json')) as f:
        sample_expense_reports = json.load(f)
    mock_get_expense_reports.return_value = [ExpenseReport(**item) for item in sample_expense_reports]
    
    csv_data = {
        'expense_id': [1, 2, 3],
        'csv_field1': ['A', 'B', 'C'],
        'csv_field2': ['X', 'Y', 'Z']
    }
    mock_read_csv.return_value = pd.DataFrame(csv_data)

    req = func.HttpRequest(method='GET', url='/api/HttpTriggerFunction2')
    resp = func2.main(req)

    assert resp.status_code == 200
    response_data = json.loads(resp.get_body())
    assert len(response_data) == 3
    assert response_data[0]['expense_id'] == 1
    assert response_data[1]['csv_field1'] == 'B'
    assert response_data[2]['csv_field2'] == 'Z'
