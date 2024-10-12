# core/db_client.py
import os
import threading
import yaml
import logging
from sqlalchemy import create_engine, text
from sqlalchemy.pool import QueuePool

class DBClient:
    _instances = {}
    _lock = threading.Lock()

    def __new__(cls, dbid):
        with cls._lock:
            if dbid not in cls._instances:
                cls._instances[dbid] = super(DBClient, cls).__new__(cls)
        return cls._instances[dbid]

    def __init__(self, dbid):
        if hasattr(self, 'initialized'):
            return
        self.initialized = True
        self.dbid = dbid
        self.engine = None
        self.db_config = {}
        self.load_config()
        self.create_engine()

    def load_config(self):
        config_path = os.path.join(os.path.dirname(__file__), '../config/db_config.yaml')
        with open(config_path, 'r') as file:
            configs = yaml.safe_load(file)

        db_configs = configs.get('databases', [])
        for db_config in db_configs:
            if db_config['dbid'] == self.dbid:
                self.db_config = db_config
                # Load actual values from environment variables
                self.db_config['url'] = os.environ.get(self.db_config['url_env_var'])
                self.db_config['username'] = os.environ.get(self.db_config['username_env_var'])
                self.db_config['password'] = os.environ.get(self.db_config['password_env_var'])
                if not all([self.db_config['url'], self.db_config['username'], self.db_config['password']]):
                    raise ValueError(f"Environment variables for database '{self.dbid}' are not properly set.")
                break
        else:
            raise ValueError(f"Database configuration for '{self.dbid}' not found.")

    def create_engine(self):
        dialect = self.db_config['dialect']
        url = self.db_config['url']
        username = self.db_config['username']
        password = self.db_config['password']

        # Remove 'jdbc:' prefix if present (from Java configurations)
        if url.startswith('jdbc:'):
            url = url[5:]

        # Construct the database URL for SQLAlchemy
        db_url = f"{dialect}://{username}:{password}@{url}"

        self.engine = create_engine(db_url, poolclass=QueuePool)
        logging.info(f"Database engine created for '{self.dbid}'.")

    def execute_query(self, query, params=None):
        try:
            with self.engine.connect() as connection:
                result = connection.execute(text(query), params or {})
                rows = result.fetchall()
                columns = result.keys()
                return [dict(zip(columns, row)) for row in rows]
        except Exception as e:
            logging.error(f"Error executing query on '{self.dbid}': {e}")
            raise
