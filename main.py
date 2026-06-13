import yaml
from src.extractor import DataExtractor
from src.loader import DataLoader
from src.transformer import DataLakeOrganizer  # New import

def load_config():
    with open("config/pipeline_config.yaml", "r") as f:
        return yaml.safe_load(f)

def main():
    config = load_config()
    
    extractor = DataExtractor(config['api'])
    raw_files = extractor.fetch_all_data()
    
    loader = DataLoader(config['database'])
    loader.load_files_to_postgres(raw_files)
    
    transformer = DataLakeOrganizer(config['database'])
    transformer.process_landing_to_parquet()
    
    print("\n--- Project 2 Complete: Data Lake Organizer Secured ---")

if __name__ == "__main__":
    main()