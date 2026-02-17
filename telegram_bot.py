from config import Config
from database import Database

import json

import requests as re

class TelegramBot:
    def __init__(self):
        self.db = Database()
        self.chat_id = Config.TELEGRAM_CHAT_ID
        self.token = Config.TELEGRAM_BOT_TOKEN
        self.base_url = f'https://api.telegram.org/bot{self.token}'
    
    def send_message(self, text: str):
        try:
            url = f'{self.base_url}/sendMessage'
            playload = {
                'chat_id' : self.chat_id,
                'text' : text,
                'parse_mode' : 'HTML'
            }
            
            re.post(url, json=playload, timeout=60)
        except Exception as e:
            raise e
    
    def analyse_alert(self, alert_type: str, sell_price: float, buy_price: float, item_name: str, sell_order_volume: int, buy_order_volume: int, ratio: float, max_sell, min_buy, spread) -> str:
        if alert_type == 'COMPRA':
            text = f'''
                📈 <b>ALERTA CRIAR ORDEM DE COMPRA</b> 📈\n
                📋 NOME DO ITEM: {item_name} \n
                💰 VALOR DE COMPRA: {buy_price:.2f} gp \n
                💰 MÍNIMO HISTÓRICO(72): {min_buy:.2f} gp \n
                📊 VOLUME DE ORDENS DE VENDA: {sell_order_volume} \n
                ⚖️ RELAÇÃO RATIO COMPRA/VENDA: {ratio:.2f}
            '''
        elif alert_type == 'VENDA':
            text = f'''
                📉 <b>ALERTA CRIAR ORDEM DE VENDA</b> 📉\n
                📋 NOME DO ITEM: {item_name} \n
                💰 VALOR DE VENDA: {sell_price:.2f} gp \n
                💰 MÁXIMO HISTÓRICO(72h): {max_sell:.2f} gp \n
                📊 VOLUME DE ORDENS DE COMPRA: {buy_order_volume} \n
                ⚖️ RELAÇÃO RATIO COMPRA/VENDA: {ratio:.2f}
            '''
        elif alert_type == 'COMPRA E VENDA':
            text = f'''
                📉 <b>ALERTA SPREAD ACIMA DE 5000GP</b> 📈\n
                📋 NOME DO ITEM: {item_name} \n
                💰 VALOR DE COMPRA: {buy_price:.2f} gp \n
                💰 VALOR DE VENDA: {sell_price:.2f} gp \n
                💰 POSSÍVEL LUCRO: {spread:.2f} gp \n
                📊 VOLUME DE ORDENS DE COMPRA: {buy_order_volume} \n
                📊 VOLUME DE ORDENS DE VENDA: {sell_order_volume} \n
                ⚖️ RELAÇÃO RATIO COMPRA/VENDA: {ratio:.2f}
                
            '''
            
        self.send_message(text)
