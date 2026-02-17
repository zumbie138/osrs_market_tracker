import pandas as pd

from typing import Dict, Optional
from config import Config
from database import Database
from telegram_bot import TelegramBot

class MarketAnalysis:
    def __init__(self):
        self.item_list = Config.ITEM_LIST
        self.db_path = Config.DB_PATH
        self.db = Database()
    
    def ema_calculus(self, serie: pd.Series, periods: int) -> pd.Series:
        return serie.ewm(span=periods, adjust=False).mean()
    
    def mean_calculus(self, serie: pd.Series) -> float:
        return serie.mean()
    
    def create_alerts_table(self, df_latest:pd.DataFrame, df_5m: pd.DataFrame) -> dict:
        if df_latest.empty:
            return {}
        
        df_latest = df_latest.sort_values('timestamp').copy()
        df_5m = df_5m.sort_values('timestamp').copy()
        
        df_alerts = pd.DataFrame({
            'item_id': df_latest['item_id'], 
            'high':df_latest['high'], 
            'low':df_latest['low'],
            'mid': df_latest[['high', 'low']].mean(axis=1),
            'ema21': None, 
            'ema9': None,
            'ema_valley': None,
            'ema_peak': None,
            'z_ema_valley': None,
            'z_ema_peak': None,
            'ratio':None, 
            'alert_type': None, 
            'conditions': None, 
            'timestamp_collected': df_latest['timestamp']
        })
        
        
        df_alerts['ema21'] = self.ema_calculus(df_alerts['mid'], 21)
        df_alerts['ema9'] = self.ema_calculus(df_alerts['mid'], 9)
        #ordens de compra no high price, quanto maior, mais caro se vende o item (peaks no high, melhores ordens de venda)
        df_alerts['rolling_max_high'] = df_alerts['high'].rolling(window=3, center=True).max()
        #ordens de venda no low price, precido do menor valor possivel, quanto menor mais barato as ordens de compra que vou criar(valleys no low)
        df_alerts['rolling_min_low'] = df_alerts['low'].rolling(window=3, center=True).min()
        
        #verificar se a ordem de compra esta no pico
        df_alerts['is_peak'] = (
            df_alerts['high'] == df_alerts['rolling_max_high']
        )

        #verificar se a ordem de venda esta no vale
        df_alerts['is_valley'] = (
            df_alerts['low'] == df_alerts['rolling_min_low']
        )

        df_valley = df_alerts[df_alerts['low'] < df_alerts['ema21']]
        df_peak = df_alerts[df_alerts['high'] > df_alerts['ema21']]

        df_alerts['ema_valley'] = df_valley['low'].ewm(span=21, adjust=False).mean()
        df_alerts['std_valley'] = df_valley['low'].rolling(21).std()
        df_alerts['ema_peak'] = df_peak['high'].ewm(span=21, adjust=False).mean()
        df_alerts['std_peak'] = df_peak['high'].rolling(21).std()
        df_alerts['z_ema_valley'] = (df_alerts['low'] - df_alerts['ema_valley']) / df_alerts['std_valley']
        df_alerts['z_ema_peak'] = (df_alerts['high'] - df_alerts['ema_peak']) / df_alerts['std_peak']
        if not df_5m.empty:
            df_5m['ratio'] = (df_5m['high_price_volume'] +1) / (df_5m['low_price_volume'] + 1)
        
        df_alerts['alert_type'] = df_alerts.apply(
            lambda row: self.analysis_test(row),
            axis=1
        )
        
        
        self.alert_alarm_test(df_alerts, df_5m)
        
        df_alerts.drop(columns=['rolling_max_high', 'rolling_min_low', 'std_valley', 'std_peak', 'is_peak', 'is_valley'], inplace=True)
        
        return df_alerts.to_dict(orient='index')
        # if df_alerts_db.empty:
        #     # print(df_alerts)
        #     return df_alerts.to_dict(orient='index')
        # else:
        #     df_alerts = df_alerts[~df_alerts['timestamp_collected'].isin(df_alerts_db['timestamp_collected'])].copy()
        #     # print(df_alerts)
        #     return df_alerts.to_dict(orient='index')
            
    def alert_alarm_test(self, df_alerts: pd.DataFrame, df_5m:pd.DataFrame):
        
        latest = df_alerts.iloc[-1]
        latest_5m = df_5m.iloc[-1]

        
        max_sell = df_alerts['high'].max()
        min_buy = df_alerts['low'].min()
        alert_type = str(latest['alert_type'])
        buy_price = 1.01 * float(latest['low'])
        sell_price = 0.99 * float(latest['high'])
        item_name = Config.ITEM_LIST[int(latest['item_id'])]
        buy_order_volume = latest_5m['high_price_volume']
        sell_order_volume = latest_5m['low_price_volume']
        ratio = latest_5m['ratio']
        spread = sell_price * 0.98 - buy_price
        
        if alert_type == 'COMPRA':
            TelegramBot().analyse_alert(alert_type, sell_price, buy_price, item_name, sell_order_volume, buy_order_volume, ratio, max_sell, min_buy, spread)
        elif alert_type == 'VENDA':
            TelegramBot().analyse_alert(alert_type, sell_price, buy_price, item_name ,sell_order_volume, buy_order_volume, ratio, max_sell, min_buy, spread)
        elif alert_type == 'COMPRA E VENDA':
            TelegramBot().analyse_alert(alert_type, sell_price, buy_price, item_name, sell_order_volume, buy_order_volume, ratio, max_sell, min_buy, spread)
                
    def analysis_test(self, row: pd.Series) -> str:

        ema21_value = row['ema21']
        latest_high = row['high']
        latest_low = row['low']
        spread = (0.99 * (row['high'] * 0.98)) - (1.1 * row['low'])
        is_valley = row['is_valley']
        is_peak = row['is_peak']
        z_ema_valley = row['z_ema_valley']
        z_ema_peak = row['z_ema_peak']
        
        
        if latest_low < ema21_value and z_ema_valley < -1.0:
            return 'COMPRA'
        elif latest_high > ema21_value and z_ema_peak > 1.0:
            return 'VENDA'
        elif spread > 10000.00:
            return 'COMPRA E VENDA'
        elif latest_low < ema21_value and is_valley:
            return 'POSSIVEL COMPRA'
        elif latest_high > ema21_value and is_peak:
            return 'POSSIVEL VENDA'
        else:
            return 'NADA'
    
    def process_analysis_data(self, df_latest: pd.DataFrame, df_5m: pd.DataFrame):
        # df_map = df_mapping.drop_duplicates(subset=['item_id'], keep='first')
        # list_item_id = df_map['item_id'].to_list()
        save_data = {}
        
        for item_id in self.item_list:
            
            df_latest_filtred = df_latest[df_latest['item_id'] == item_id].copy()      
            df_5m_filtred = df_5m[df_5m['item_id'] == item_id].copy()
            
            
            data = self.create_alerts_table(df_latest_filtred, df_5m_filtred)
            save_data.update(data)
        
        if save_data:    
            self.db.save_database('alerts', save_data)