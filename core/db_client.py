# core/db_client.py
import os
import threading
import yaml
import logging
from sqlalchemy import create_engine, text
from sqlalchemy.pool import QueuePool
import urllib.parse

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
                self.use_odbc = db_config.get('use_odbc', False)
                if self.use_odbc:
                    odbc_conn_str_env_var = db_config.get('odbc_connection_string_env_var')
                    if odbc_conn_str_env_var:
                        self.db_config['odbc_connection_string'] = os.environ.get(odbc_conn_str_env_var)
                        if not self.db_config['odbc_connection_string']:
                            raise ValueError(f"Environment variable '{odbc_conn_str_env_var}' for database '{self.dbid}' is not set.")
                    else:
                        raise ValueError(f"'odbc_connection_string_env_var' is not specified for database '{self.dbid}'.")
                else:
                    # Load connection parameters from environment variables
                    self.db_config['host'] = os.environ.get(db_config.get('host_env_var'))
                    self.db_config['port'] = os.environ.get(db_config.get('port_env_var'))
                    self.db_config['database'] = os.environ.get(db_config.get('database_env_var'))
                    self.db_config['username'] = os.environ.get(db_config.get('username_env_var'))
                    self.db_config['password'] = os.environ.get(db_config.get('password_env_var'))
                    if not all([
                        self.db_config['host'],
                        self.db_config['port'],
                        self.db_config['database'],
                        self.db_config['username'],
                        self.db_config['password']
                    ]):
                        missing_vars = [key for key in ['host', 'port', 'database', 'username', 'password'] if not self.db_config.get(key)]
                        raise ValueError(f"Missing environment variables for database '{self.dbid}': {', '.join(missing_vars)}")
                break
        else:
            raise ValueError(f"Database configuration for '{self.dbid}' not found.")

    def create_engine(self):
        dialect = self.db_config['dialect']

        if self.use_odbc:
            # ODBC Connection
            odbc_connection_string = self.db_config['odbc_connection_string']
            # Encode the ODBC connection string
            params = urllib.parse.quote_plus(odbc_connection_string)
            # Construct the database URL for SQLAlchemy
            db_url = f"{dialect}:///?odbc_connect={params}"
            self.engine = create_engine(db_url, poolclass=QueuePool)
            logging.info(f"Database engine created for '{self.dbid}' using ODBC.")
        else:
            # Direct Driver Connection
            username = self.db_config['username']
            password = self.db_config['password']
            host = self.db_config['host']
            port = self.db_config['port']
            database = self.db_config['database']

            # Construct the database URL for SQLAlchemy
            db_url = f"{dialect}://{username}:{password}@{host}:{port}/{database}"
            self.engine = create_engine(db_url, poolclass=QueuePool)
            logging.info(f"Database engine created for '{self.dbid}' using direct driver.")

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
