import os
import json
import psycopg2
from psycopg2.extras import execute_values

class PostgresLoader:
    def __init__(self, config: dict):
        self.db_config = config['database']
        self.raw_dir = "data_archive/raw"
        self.conn = None

    def connect(self):
        """Connect to PostgreSQL, creating the database if it doesn't exist."""
        try:
            # 1. First, connect to the default 'postgres' management database
            admin_conn = psycopg2.connect(
                host=self.db_config['host'],
                port=self.db_config['port'],
                database="postgres",  # Default system DB
                user=self.db_config['user'],
                password="postgres"
            )
            admin_conn.autocommit = True
            
            # 2. Check if 'economic_raw' already exists
            with admin_conn.cursor() as cursor:
                cursor.execute(f"SELECT 1 FROM pg_catalog.pg_database WHERE datname = '{self.db_config['name']}';")
                exists = cursor.fetchone()
                
                # If it doesn't exist, create it programmatically
                if not exists:
                    print(f"Database '{self.db_config['name']}' not found. Creating it now...")
                    cursor.execute(f"CREATE DATABASE {self.db_config['name']};")
            
            admin_conn.close()

            # 3. Now connect to our freshly ensured target database
            self.conn = psycopg2.connect(
                host=self.db_config['host'],
                port=self.db_config['port'],
                database=self.db_config['name'],
                user=self.db_config['user'],
                password="postgres"
            )
            self.conn.autocommit = True
            print(f"Successfully connected to PostgreSQL database: {self.db_config['name']}")

            # ADD THESE DIAGNOSTIC LINES:
            print("--- EXTRA CONNECTION DETAILS ---")
            print(f"DSN: {self.conn.dsn}")
            print(f"Server Version: {self.conn.server_version}")
            print("--------------------------------")
            
        except Exception as e:
            print(f"Database connection failed: {e}")
            raise e

    def create_landing_table(self):
        create_table_query = """
        CREATE TABLE IF NOT EXISTS landing_economic_data (
            id SERIAL PRIMARY KEY,
            indicator_id VARCHAR(50),
            indicator_value VARCHAR(255),
            country_id VARCHAR(10),
            country_value VARCHAR(255),
            countryiso3code VARCHAR(10),
            date_year VARCHAR(10),
            value NUMERIC,
            unit VARCHAR(50),
            obs_status VARCHAR(50),
            decimal_places INT,
            extracted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
        """
        with self.conn.cursor() as cursor:
            cursor.execute(create_table_query)
            print("Landing table 'landing_economic_data' is ready.")

    def load_raw_jsons(self):
        if not os.path.exists(self.raw_dir):
            print("No raw directory found. Run the extractor first.")
            return

        json_files = [f for f in os.listdir(self.raw_dir) if f.endswith('.json')]
        
        if not json_files:
            print("No JSON files found to load.")
            return

        query = """
            INSERT INTO landing_economic_data 
            (indicator_id, indicator_value, country_id, country_value, countryiso3code, date_year, value, unit, obs_status, decimal_places)
            VALUES %s;
        """

        for file_name in json_files:
            file_path = os.path.join(self.raw_dir, file_name)
            print(f"Loading data from file: {file_name}...")

            with open(file_path, 'r', encoding='utf-8') as f:
                records = json.load(f)

            data_to_insert = []
            for item in records:
                data_to_insert.append((
                    item.get('indicator', {}).get('id'),
                    item.get('indicator', {}).get('value'),
                    item.get('country', {}).get('id'),
                    item.get('country', {}).get('value'),
                    item.get('countryiso3code'),
                    item.get('date'),
                    item.get('value'),
                    item.get('unit'),
                    item.get('obs_status'),
                    item.get('decimal')
                ))

            with self.conn.cursor() as cursor:
                execute_values(cursor, query, data_to_insert)
                print(f"Successfully loaded {len(data_to_insert)} records into Postgres.")
                
    def close(self):
        if self.conn:
            self.conn.close()
            print("Database connection closed.")