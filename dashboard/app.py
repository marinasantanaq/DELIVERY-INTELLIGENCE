import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import pandas as pd
import plotly.express as px
import streamlit as st

from src.config import DATABASE_PATH
from src.database import read_orders
from src.metrics import calculate_kpis, revenue_over_time, orders_by_hour

st.set_page_config(page_title="Delivery Intelligence", page_icon="🍽️",
                   layout="wide")
st.title("🍽️ Delivery Intelligence")
st.caption("Painel de desempenho operacional e comercial de delivery")

try:
    df = read_orders(DATABASE_PATH)
except FileNotFoundError as error:
    st.warning(str(error))
    st.code("python main.py")
    st.stop()

df["data_pedido"] = pd.to_datetime(df["data_pedido"])
min_date = df["data_pedido"].min().date()
max_date = df["data_pedido"].max().date()

with st.sidebar:
    st.header("Filtros")
    restaurants = sorted(df["nome_restaurante"].dropna().unique().tolist())
    selected_restaurants = st.multiselect(
        "Restaurante", restaurants, default=restaurants
    )
    date_range = st.date_input(
        "Período", value=(min_date, max_date),
        min_value=min_date, max_value=max_date
    )
    statuses = sorted(df["status"].dropna().unique().tolist())
    selected_statuses = st.multiselect("Status", statuses, default=statuses)

filtered = df[df["nome_restaurante"].isin(selected_restaurants)]
if len(date_range) == 2:
    start_date, end_date = date_range
    filtered = filtered[
        filtered["data_pedido"].dt.date.between(start_date, end_date)
    ]
if selected_statuses:
    filtered = filtered[filtered["status"].isin(selected_statuses)]
else:
    filtered = filtered.iloc[0:0]

kpis = calculate_kpis(filtered)
cols = st.columns(4)
cols[0].metric("Faturamento válido", f"R$ {kpis['revenue']:,.2f}")
cols[1].metric("Pedidos", f"{kpis['total_orders']:,}")
cols[2].metric("Ticket médio", f"R$ {kpis['average_ticket']:,.2f}")
cols[3].metric("Cancelamentos", f"{kpis['cancellation_rate']:.1f}%")

cols2 = st.columns(3)
cols2[0].metric("Tempo médio de preparo", f"{kpis['average_prep_time']:.1f} min")
cols2[1].metric("Tempo médio de entrega", f"{kpis['average_delivery_time']:.1f} min")
cols2[2].metric("Avaliação média", f"{kpis['average_rating']:.2f} / 5")

st.divider()
left, right = st.columns(2)

with left:
    st.subheader("Faturamento ao longo do tempo")
    trend = revenue_over_time(filtered)
    if trend.empty:
        st.info("Não há pedidos entregues para os filtros selecionados.")
    else:
        fig = px.line(trend, x="data", y="faturamento", markers=True,
                      labels={"data": "Data", "faturamento": "Faturamento (R$)"})
        st.plotly_chart(fig, use_container_width=True)

with right:
    st.subheader("Pedidos por horário")
    hourly = orders_by_hour(filtered)
    fig = px.bar(hourly, x="hora_pedido", y="pedidos",
                 labels={"hora_pedido": "Hora", "pedidos": "Pedidos"})
    st.plotly_chart(fig, use_container_width=True)

st.subheader("Pedidos por restaurante")
by_restaurant = (filtered.groupby("nome_restaurante", as_index=False)
                 .agg(pedidos=("id_pedido", "count"),
                      faturamento=("valor", lambda s: s[filtered.loc[s.index, "status"].eq("entregue")].sum())))
if not by_restaurant.empty:
    st.dataframe(by_restaurant, use_container_width=True, hide_index=True)

st.subheader("Dados filtrados")
st.dataframe(filtered, use_container_width=True, hide_index=True)
st.download_button(
    "Baixar dados filtrados (CSV)",
    data=filtered.to_csv(index=False).encode("utf-8"),
    file_name="delivery_intelligence_dados.csv",
    mime="text/csv",
)
