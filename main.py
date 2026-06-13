import yaml
from src.extractor import WorldBankExtractor
from src.loader import PostgresLoader
from src.transformer import DataLakeOrganizer

def load_config():
    with open("config/pipeline_config.yaml", "r") as f:
        return yaml.safe_load(f)

def main():
    config = load_config()
    
    extractor = WorldBankExtractor(config)
    
    print("Fetching raw data from API...")
    raw_file_path = extractor.fetch_indicator('NY.GDP.MKTP.CD')
    
    loader = PostgresLoader(config) 
    loader.connect()
    
    if raw_file_path and loader.conn:
        loader.load_files_to_postgres([raw_file_path])
    
    transformer = DataLakeOrganizer(config['database'])
    transformer.process_landing_to_parquet()
    
    print("\n--- Project 2 Complete: Data Lake Organizer Secured ---")

if __name__ == "__main__":
    main()