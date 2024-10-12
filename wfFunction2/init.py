import logging
import azure.functions as func
from core.coupa_client import CoupaClient
from core.data_processor import DataProcessor
from core.models import JoinedData
from typing import List
import os
import json

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('HttpTriggerFunction2 processed a request.')

    api_key = os.getenv('COUPA_API_KEY')
    base_url = os.getenv('COUPA_BASE_URL')
    csv_path = os.path.join(os.getcwd(), 'data', 'local_data.csv')

    try:
        coupa_client = CoupaClient(api_key=api_key, base_url=base_url)
        data_processor = DataProcessor(csv_path=csv_path)

        expense_reports = coupa_client.get_expense_reports()
        joined_data: List[JoinedData] = data_processor.join_data(expense_reports, data_processor.read_csv())

        response = [data.dict() for data in joined_data]

        return func.HttpResponse(
            json.dumps(response),
            status_code=200,
            mimetype="application/json"
        )
    except Exception as e:
        logging.error(f"Error: {e}")
        return func.HttpResponse(
            "Internal Server Error",
            status_code=500
        )
