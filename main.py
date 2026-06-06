import yaml
from src.extractor import WorldBankExtractor
from src.loader import PostgresLoader

def load_config(config_path="config/pipeline_config.yaml"):
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def main():
    print("--- Launching Global Economic Data Platform ---")
    
    config = load_config()
    
    extractor = WorldBankExtractor(config)
    indicators = config['api_sources']['world_bank']['indicators']
    for indicator in indicators:
        extractor.fetch_indicator(indicator['id'])
        
    print("\n--- Starting Database Loading Layer ---")
    
    loader = PostgresLoader(config)
    try:
        loader.connect()
        loader.create_landing_table()
        loader.load_raw_jsons()
    finally:
        loader.close()
        
    print("\n--- Project 1 Complete: Ingestion & Raw Storage MVP Secured ---")

if __name__ == "__main__":
    main()