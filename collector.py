import requests as re
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from config import Config
from database import Database
from datetime import datetime

class Collector:
    def __init__(self):
        self.api_base = Config.OSRS_API_BASE
        self.headers = Config.OSRS_USER_AGENT
        
        self.session = re.Session()
        self.session.headers.update({'user-agent': self.headers})
        retry = Retry(
            total=5,
            connect=5,
            read=5,
            backoff_factor=0.8,  # 0.8s, 1.6s, 3.2s...
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=['GET'],
            raise_on_status=False,
            respect_retry_after_header=True,
        )
        
        adapter = HTTPAdapter(max_retries=retry, pool_connections=10, pool_block=10)
        self.session.mount('https://', adapter)
        self.session.mount('http://', adapter)
        
    def data_fetch(self, endpoint:str) -> dict:
        try:
            url = f'{self.api_base}/{endpoint}'
            response = self.session.get(url, timeout=(5, 30))
            response.raise_for_status()
            
            
            payload = response.json()
            return payload if endpoint == "mapping" else payload.get("data", {})
        
        except re.exceptions.RequestException as e:
            print(f"Erro ao buscar preços ({endpoint}): {e}")
            return {}
        except ValueError as e:
            print(f"Erro ao decodificar JSON ({endpoint}): {e}")
            return {}
    
    def data_collect(self, table:str) -> None:
        try:
            print(f'Salvando dados da tabela {table} : {datetime.now()}')
            data = self.data_fetch(table)
            Database().save_database(table, data)
        except Exception as e:
            print(f'Erro ao processar tabela {table} : Erro {e}')
        