# core/query_manager.py
import json
import os
import threading
import logging

class QueryManager:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(QueryManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if hasattr(self, 'initialized'):
            return
        self.initialized = True
        self.queries = {}
        self.load_queries()

    def load_queries(self):
        config_path = os.path.join(os.path.dirname(__file__), '../config/query_config.json')
        with open(config_path, 'r') as file:
            self.queries = json.load(file)
        logging.info("Query configurations loaded.")

    def get_query(self, dbid, query_key):
        db_queries = self.queries.get(dbid, {}).get('queries', [])
        for query in db_queries:
            if query['key'] == query_key:
                return query['sql']
        raise ValueError(f"Query with key '{query_key}' not found for database '{dbid}'.")
