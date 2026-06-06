import os
import json
import time
import requests

class WorldBankExtractor:
    def __init__(self, config: dict):
        self.api_config = config['api_sources']['world_bank']
        self.base_url = self.api_config['base_url']
        self.format = self.api_config['format']
        self.per_page = self.api_config['per_page']
        self.raw_dir = "data_archive/raw"
        
        # Ensure raw directory exists
        os.makedirs(self.raw_dir, exist_ok=True)

    def fetch_indicator(self, indicator_id: str):
        page = 1
        has_more = True
        
        print(f"Starting extraction for indicator: {indicator_id}")
        
        while has_more: 
            # http://api.worldbank.org/v2/country/all/indicator/NY.GDP.MKTP.CD?format=json&page=1&per_page=500
            url = f"{self.base_url}/country/{self.api_config['countries']}/indicator/{indicator_id}"
            params = {
                'format': self.format,
                'page': page,
                'per_page': self.per_page
            }
            
            try:
                response = requests.get(url, params=params)
                response.raise_for_status()
                data = response.json()
                
                if len(data) < 2 or not data[1]:
                    print(f"No data returned or end of pages reached for {indicator_id}.")
                    break
                
                file_path = os.path.join(self.raw_dir, f"{indicator_id}_page_{page}.json")
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(data[1], f, ensure_ascii=False, indent=4)
                
                print(f"Successfully saved page {page} to {file_path}")
                
                meta = data[0]
                total_pages = meta.get('pages', 1)
                
                if page >= total_pages:
                    has_more = False
                else:
                    page += 1
                    time.sleep(1)
                    
            except requests.exceptions.RequestException as e:
                print(f"Error fetching page {page} for {indicator_id}: {e}")
                break