import sqlite3
import pandas as pd
from config import Config

class Database:
    def __init__(self):
        self.db_path = Config.DB_PATH
        self.init_database()
    
    def init_database(self) -> None:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        #tabela latest
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS latest(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_id INTEGER,
            high INTEGER,
            high_time INTEGER,
            low INTEGER,
            low_time INTEGER,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        #tabela 5m
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS fiveminutes(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_id INTEGER,
            avg_high_price INTEGER,
            high_price_volume INTEGER,
            avg_low_price INTEGER,
            low_price_volume INTEGER,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        #tabela mapping
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS mapping(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            examine TEXT,
            item_id INTEGER,
            members TEXT,  -- 'true' | 'false'
            lowalch INTEGER,
            "limit" INTEGER,
            value INTEGER,
            highalch INTEGER,
            icon TEXT,
            name TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        ''')
        #tabela de alertas
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS alerts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_id INTEGER,
            high INTEGER,
            low INTEGER,
            mid REAL,
            ema21 REAL,
            ema9 REAL,
            ema_valley REAL,
            ema_peak REAL,
            z_ema_valley REAL,
            z_ema_peak REAL,
            ratio REAL,
            alert_type TEXT,  -- 'COMPRA' | 'VENDA' | 'NADA' | 'COMPRA E VENDA' | 'POSSIVEL COMPRA' | 'POSSIVEL VENDA'
            conditions TEXT,
            timestamp_collected DATETIME,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(item_id, timestamp_collected)
        )
        ''')
        
        conn.commit()
        conn.close()
    
    def delete_table(self, table: str) -> None:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()


        cursor.execute(f'DROP TABLE IF EXISTS {table}')

        conn.commit()
        conn.close()
        
    def save_database(self, table:str, data) -> None:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        match table:
            case 'latest':
                query = '''
                INSERT INTO latest
                    (item_id, high, high_time, low, low_time)
                VALUES
                    (?, ?, ?, ?, ?)                   
                '''
                value_keys = ['item_id','high','highTime','low','lowTime']
                
            case '5m':
                query = '''
                INSERT INTO fiveminutes
                    (item_id, avg_high_price, high_price_volume, avg_low_price, low_price_volume)
                VALUES
                    (?, ?, ?, ?, ?)                   
                '''
                value_keys = ['item_id', 'avgHighPrice','highPriceVolume','avgLowPrice','lowPriceVolume']
                
            case 'mapping':
                query = '''
                INSERT INTO mapping
                    (examine, item_id, members, lowalch, "limit", value, highalch, icon, name)
                VALUES
                    (?, ?, ?, ?, ?, ?, ?, ?, ?)                   
                '''
                value_keys = ['examine','id', 'members','lowalch','limit','value', 'highalch', 'icon', 'name']
            
            case 'alerts':
                query = '''
                INSERT OR REPLACE INTO alerts
                    (item_id, high, mid, low, ema21, ema9, ema_valley, ema_peak, 'z_ema_valley', 'z_ema_peak', ratio, alert_type, conditions, timestamp_collected)
                VALUES
                    (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)                   
                '''
                value_keys = ['item_id', 'high', 'mid', 'low', 'ema21', 'ema9', 'ema_valley', 'ema_peak', 'z_ema_valley', 'z_ema_peak', 'ratio', 'alert_type', 'conditions', 'timestamp_collected'] 
        try:
            if isinstance(data, list):
                for item_data in data:
                    row_values = [] 
                    for key in value_keys:
                        row_values.append(item_data.get(key))
                        
                    cursor.execute(query, row_values)
            elif table == 'alerts':
                for _, item_data in data.items():
                    row_values = []
                    for key in value_keys:
                        row_values.append(item_data.get(key))
                        
                    cursor.execute(query, row_values)
            else:    
                for item_id, item_data in data.items():
                    row_values = [] 
                    for key in value_keys:
                        if key == 'item_id':
                            row_values.append(int(item_id))
                        else:
                            row_values.append(item_data.get(key))
                            
                    cursor.execute(query, row_values)
            conn.commit()
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def delete_old_records(self, table: str, hours:int =72) -> None:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
                (table,)
            )
            if not cursor.fetchone():
                print(f'A tabela {table} não existe')
                return
            
            query = f'''
            DELETE FROM {table}
            WHERE timestamp < datetime('now', '-{hours} hours')
            '''
            cursor.execute(query)
            deleted_count = cursor.rowcount
            
            conn.commit()
            if deleted_count > 1000:
                cursor.execute("VACUUM")
        except Exception as e:
            conn.rollback()
            raise Exception(f'Erro ao deletar registros antigos da tabela {table}: {str(e)}')
        finally:
            conn.close()
    
    def cleanup_old_data(self, hours:int = 72) -> None:
        tables_to_clean = ['latest', 'fiveminutes', 'alerts']
        for table  in tables_to_clean:
            try:
                self.delete_old_records(table, hours)
            except Exception as e:
                print(f'Erro ao limpar a tabela {table}, Erro: {e}')
        
    def get_database(self, table:str) -> pd.DataFrame:
        conn = sqlite3.connect(self.db_path)
        try:
            df = pd.read_sql_query(f'SELECT * FROM {table}', con=conn)
            return df
        except Exception as e:
            raise Exception(f'Erro ao carregar a tabela{table}: {str(e)}')
        finally:
            conn.close()