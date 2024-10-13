# shared_code/query_manager.py
import json
import threading
import logging

class QueryManager:
    _instances = {}
    _lock = threading.Lock()

    def __new__(cls, query_config_path):
        with cls._lock:
            if query_config_path not in cls._instances:
                cls._instances[query_config_path] = super(QueryManager, cls).__new__(cls)
        return cls._instances[query_config_path]

    def __init__(self, query_config_path):
        if hasattr(self, 'initialized'):
            return
        self.initialized = True
        self.queries = {}
        self.load_queries(query_config_path)

    def load_queries(self, query_config_path):
        try:
            with open(query_config_path, 'r') as file:
                self.queries = json.load(file)
            logging.info(f"Query configurations loaded from {query_config_path}.")
        except Exception as e:
            logging.error(f"Error loading query configurations: {e}")
            raise

    def get_query(self, dbid, query_key):
        db_queries = self.queries.get(dbid, {}).get('queries', [])
        for query in db_queries:
            if query['key'] == query_key:
                return query['sql']
        raise ValueError(f"Query with key '{query_key}' not found for database '{dbid}'.")
