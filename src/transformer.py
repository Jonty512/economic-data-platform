import os
import psycopg2
import pandas as pd

class DataLakeOrganizer:
    def __init__(self, db_config):
        self.db_config = db_config
        self.output_base_dir = "data_lake/processed"

    def process_landing_to_parquet(self):
        print("--- Starting Data Lake Organizer Layer ---")
        
        try:
            conn = psycopg2.connect(
                host=self.db_config.get('host', 'localhost'),
                port=self.db_config.get('port', 5442),
                database=self.db_config.get('name', 'economic_raw'),
                user=self.db_config.get('user', 'postgres'),
                password=self.db_config.get('password', 'postgres')
)
            print("Successfully extracted data from Postgres landing table.")
        except Exception as e:
            print(f"Failed to connect to database: {e}")
            return

        query = "SELECT indicator_id, countryiso3code, date_year, value FROM landing_economic_data;"
        df = pd.read_sql_query(query, conn)
        conn.close()

        if df.empty:
            print("No data found in landing table to process.")
            return

        df['date_year'] = df['date_year'].astype(int)

        print(f"Organizing and partitioning {len(df)} records into Parquet format...")
        
        try:
            df.to_parquet(
                self.output_base_dir,
                engine='pyarrow',
                partition_cols=['indicator_id', 'date_year'],
                index=False
            )
            print(f"Data Lake partition sync complete! Files saved to: {self.output_base_dir}")
        except Exception as e:
            print(f"Error writing Parquet partitions: {e}")