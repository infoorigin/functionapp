# function_app/__init__.py
import azure.functions as func
import logging
import json
from core.db_client import DBClient
from core.query_manager import QueryManager

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Received request for database query execution.')

    try:
        req_body = req.get_json()
    except ValueError:
        logging.error("Invalid JSON in request body.")
        return func.HttpResponse("Invalid JSON in request body.", status_code=400)

    dbid = req_body.get('dbid')
    query_key = req_body.get('query_key')
    params = req_body.get('params', {})

    if not dbid or not query_key:
        logging.error("Missing 'dbid' or 'query_key' in request.")
        return func.HttpResponse("Missing 'dbid' or 'query_key' in request.", status_code=400)

    try:
        query_manager = QueryManager()
        sql = query_manager.get_query(dbid, query_key)

        db_client = DBClient(dbid=dbid)
        results = db_client.execute_query(sql, params)

        response = {
            'status': 'success',
            'data': results
        }
        return func.HttpResponse(
            json.dumps(response),
            status_code=200,
            mimetype="application/json"
        )

    except Exception as e:
        logging.exception("Error processing request.")
        response = {
            'status': 'error',
            'message': str(e)
        }
        return func.HttpResponse(
            json.dumps(response),
            status_code=500,
            mimetype="application/json"
        )
