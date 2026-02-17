from config import Config
from database import Database
from datetime import datetime, timedelta

import streamlit as st
import plotly.graph_objects as go
import pandas as pd

st.set_page_config(page_title='OSRS Grand Exchange Analysis', page_icon='📈', layout='wide')


db_path = Config.DB_PATH
item_list = Config.ITEM_LIST
df_mapping = Database().get_database('mapping')
df_5m = Database().get_database('fiveminutes')
df_latest = Database().get_database('latest')
df_alerts = Database().get_database('alerts')

# all_itens = {}
# df_map = df_mapping.drop_duplicates(subset=['item_id'], keep='first')
# for index, row in df_map.iterrows():
#     all_itens[row['item_id']] = row['name']

    
st.sidebar.header('Config')
item_id = st.sidebar.selectbox(
    'Item',
    options=list(item_list.keys()),
    format_func=lambda x: f'{item_list[x]} ({x})'
    )

hours = st.sidebar.slider('Janela de horas', 2, 72, 24, 2)
limit_hours = datetime.now() - timedelta(hours=hours)
df_latest['timestamp'] = pd.to_datetime(df_latest['timestamp'])
df_mapping['timestamp'] = pd.to_datetime(df_mapping['timestamp'])
df_5m['timestamp'] = pd.to_datetime(df_5m['timestamp'])
df_alerts['timestamp_collected'] = pd.to_datetime(df_alerts['timestamp_collected'])

df_latest_filtred = df_latest[df_latest['timestamp'] >= limit_hours]
df_latest_filtred = df_latest_filtred[df_latest_filtred['item_id'] == item_id]

df_mapping_filtred = df_mapping[df_mapping['timestamp'] >= limit_hours]
df_mapping_filtred = df_mapping_filtred[df_mapping_filtred['item_id'] == item_id]

df_5m_filtred = df_5m[df_5m['timestamp'] >= limit_hours]
df_5m_filtred = df_5m_filtred[df_5m_filtred['item_id'] == item_id]

df_alerts_filtred = df_alerts[df_alerts['timestamp_collected'] >= limit_hours]
df_alerts_filtred = df_alerts_filtred[df_alerts_filtred['item_id'] == item_id]

# min_high = float(df_latest['high'].min())
# max_low = float(df_latest['low'].max())
# latest = df.iloc[-1]

#grafico principal, cruzamento entre latest e alerts, basicamente vai sinalizar compra e vendas , plotando high/low, alertas de compra/venda e ema21
fig_buy_sell = go.Figure()
fig_buy_sell.add_trace(go.Scatter(x=df_latest_filtred['timestamp'], y=df_latest_filtred['high'], mode='lines', name='high(ordens de compra)'))
fig_buy_sell.add_trace(go.Scatter(x=df_latest_filtred['timestamp'], y=df_latest_filtred['low'], mode='lines', name='low(ordens de venda)'))
fig_buy_sell.add_trace(go.Scatter(x=df_alerts_filtred['timestamp_collected'], y=df_alerts_filtred['ema21'], mode='lines', name='ema21'))
# fig_buy_sell.add_trace(go.Scatter(x=df_alerts_filtred['timestamp_collected'], y=min_high, mode='lines', name='mínimo de compra(high)'))
# fig_buy_sell.add_trace(go.Scatter(x=df_alerts_filtred['timestamp_collected'], y=max_low, mode='lines', name='máximo de venda(low)'))
if not df_alerts_filtred.empty:
    compra_alerts = df_alerts_filtred[df_alerts_filtred['alert_type'] == 'COMPRA']
    venda_alerts = df_alerts_filtred[df_alerts_filtred['alert_type'] == 'VENDA']
    pos_compra_alerts = df_alerts_filtred[df_alerts_filtred['alert_type'] == 'POSSIVEL COMPRA']
    pos_venda_alerts = df_alerts_filtred[df_alerts_filtred['alert_type'] == 'POSSIVEL VENDA']
    
    if not compra_alerts.empty:
        fig_buy_sell.add_trace(go.Scatter(
            x=compra_alerts['timestamp_collected'],
            y=compra_alerts['low'],
            mode='markers',
            name='COMPRA',
            marker=dict(
                symbol='triangle-up',
                size=12,
                color='red',
                line=dict(width=1, color='darkgreen')
            ),
            hovertemplate='COMPRA<br>Preço: %{y}<br>Hora: %{x}<extra></extra>'
        ))
    
    if not venda_alerts.empty:
        fig_buy_sell.add_trace(go.Scatter(
            x=venda_alerts['timestamp_collected'],
            y=venda_alerts['high'],
            mode='markers',
            name='VENDA',
            marker=dict(
                symbol='triangle-down',
                size=12,
                color='green',
                line=dict(width=1, color='darkred')
            ),
            hovertemplate='VENDA<br>Preço: %{y}<br>Hora: %{x}<extra></extra>'
        ))
    if not compra_alerts.empty:
        fig_buy_sell.add_trace(go.Scatter(
            x=pos_compra_alerts['timestamp_collected'],
            y=pos_compra_alerts['low'],
            mode='markers',
            name='POSSIVEL COMPRA',
            marker=dict(
                symbol='circle',
                size=5,
                color='yellow',
                line=dict(width=1, color='darkgreen')
            ),
            hovertemplate='COMPRA<br>Preço: %{y}<br>Hora: %{x}<extra></extra>'
        ))
    
    if not venda_alerts.empty:
        fig_buy_sell.add_trace(go.Scatter(
            x=pos_venda_alerts['timestamp_collected'],
            y=pos_venda_alerts['high'],
            mode='markers',
            name='POSSIVEL VENDA',
            marker=dict(
                symbol='circle',
                size=5,
                color='yellow',
                line=dict(width=1, color='darkred')
            ),
            hovertemplate='VENDA<br>Preço: %{y}<br>Hora: %{x}<extra></extra>'
        ))

fig_buy_sell.update_layout(
    height=520,
    xaxis_title="Tempo",
    yaxis_title="Preço (gp)",
    legend_title="High/low compra/venda",
)

st.plotly_chart(fig_buy_sell, use_container_width=True)

#grafico de medias, mostrando todas as medias e comportamentos, media instantanea 'mid', ema21, ema9, media_high, media_low 
fig_mean = go.Figure()
fig_mean.add_trace(go.Scatter(x=df_alerts_filtred['timestamp_collected'], y=df_alerts_filtred['mid'], mode='lines', name='média instantânea'))
fig_mean.add_trace(go.Scatter(x=df_alerts_filtred['timestamp_collected'], y=df_alerts_filtred['ema21'], mode='lines', name='média movel exponencial 21 períodos'))
fig_mean.add_trace(go.Scatter(x=df_alerts_filtred['timestamp_collected'], y=df_alerts_filtred['ema9'], mode='lines', name='média movel exponencial 9 períodos'))
fig_mean.add_trace(go.Scatter(x=df_alerts_filtred['timestamp_collected'], y=df_alerts_filtred['ema_valley'], mode='lines', name='média de ordens de venda(low)'))
fig_mean.add_trace(go.Scatter(x=df_alerts_filtred['timestamp_collected'], y=df_alerts_filtred['ema_peak'], mode='lines', name='média de ordens de compra(high)'))

fig_mean.update_layout(
    height=520,
    xaxis_title="Tempo",
    yaxis_title="Preço (gp)",
    legend_title="Representação das médias",
)

st.plotly_chart(fig_mean, use_container_width=True)

#grafico 5m monstrando fluxo de compra e venda
fig_5m = go.Figure()
fig_5m.add_trace(go.Scatter(x=df_5m_filtred['timestamp'], y=df_5m_filtred['high_price_volume'], mode='lines', name='high price volume(compra)'))
fig_5m.add_trace(go.Scatter(x=df_5m_filtred['timestamp'], y=df_5m_filtred['low_price_volume'], mode='lines', name='low price volume(venda)'))

fig_5m.update_layout(
    height=520,
    xaxis_title="Tempo",
    yaxis_title="Volume de vendas",
    legend_title="relação volume de compra e venda",
)

st.plotly_chart(fig_5m, use_container_width=True)

with st.expander("Dados crus (últimos 200) alerts"):
    st.dataframe(df_alerts_filtred.tail(200), use_container_width=True)        
