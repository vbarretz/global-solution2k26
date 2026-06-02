import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import folium
from streamlit_folium import st_folium
from datetime import datetime

# ─────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="FloodVision — Monitoramento de Enchentes",
    page_icon="🌊",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# ESTILOS
# ─────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=DM+Sans:wght@300;400;600;700&display=swap');
html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
.stApp { background-color: #0a0f1e; color: #e2e8f0; }
[data-testid="stSidebar"] { background-color: #0d1424; border-right: 1px solid #1e2d4a; }
[data-testid="stMetric"] {
    background: linear-gradient(135deg, #0d1b2e 0%, #122040 100%);
    border: 1px solid #1e3a5f; border-radius: 12px; padding: 16px 20px;
}
[data-testid="stMetricLabel"] { color: #7fa8cc !important; font-size: 0.75rem !important; letter-spacing: 0.1em; text-transform: uppercase; }
[data-testid="stMetricValue"] { color: #e2f0ff !important; font-family: 'Space Mono', monospace !important; }
.alert-card { border-radius: 12px; padding: 16px 20px; margin: 8px 0; border-left: 4px solid; }
.alert-verde   { background: #0a2016; border-color: #22c55e; color: #86efac; }
.alert-amarelo { background: #1f1600; border-color: #eab308; color: #fde047; }
.alert-laranja { background: #1f0d00; border-color: #f97316; color: #fdba74; }
.alert-vermelho{ background: #1f0007; border-color: #ef4444; color: #fca5a5; }
.stTabs [data-baseweb="tab-list"] { background-color: #0d1424; border-radius: 10px; padding: 4px; gap: 4px; }
.stTabs [data-baseweb="tab"] { border-radius: 8px; color: #7fa8cc; font-weight: 600; padding: 8px 20px; }
.stTabs [aria-selected="true"] { background-color: #1a3a5c !important; color: #60b8ff !important; }
.main-title { font-family: 'Space Mono', monospace; font-size: 2rem; font-weight: 700; color: #60b8ff; letter-spacing: -0.02em; margin-bottom: 0; }
.sub-title { color: #4a7fa0; font-size: 0.9rem; letter-spacing: 0.05em; margin-top: 4px; }
hr { border-color: #1e2d4a; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# CARREGAMENTO DOS DADOS REAIS
# ─────────────────────────────────────────────
@st.cache_data
def carregar_dados():
    df = pd.read_csv("data/dados_clima_tratados.csv", parse_dates=["data_hora"])
    df["data"] = df["data_hora"].dt.date
    df["cidade_label"] = df["cidade"].str.replace("_", " ")
    return df

@st.cache_data
def coordenadas_cidades():
    return {
        "Sao_Paulo":   {"lat": -23.5505, "lon": -46.6333, "label": "São Paulo"},
        "Guarulhos":   {"lat": -23.4543, "lon": -46.5333, "label": "Guarulhos"},
        "Santo_Andre": {"lat": -23.6618, "lon": -46.5289, "label": "Santo André"},
    }


# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown('<p class="main-title">🌊 FloodVision</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-title">SISTEMA PREDITIVO DE ENCHENTES</p>', unsafe_allow_html=True)
    st.markdown("---")

    df_raw = carregar_dados()

    st.markdown("#### 🏙️ Cidade")
    cidades_disponiveis = sorted(df_raw["cidade"].unique())
    cidade_selecionada = st.selectbox(
        "Selecionar cidade",
        options=["Todas"] + cidades_disponiveis,
        format_func=lambda x: x.replace("_", " ") if x != "Todas" else "Todas as cidades",
    )

    st.markdown("#### 🗓️ Período de Análise")
    datas_unicas = sorted(df_raw["data"].unique())
    data_inicio = st.date_input("De",  value=datas_unicas[0])
    data_fim    = st.date_input("Até", value=datas_unicas[-1])

    st.markdown("---")
    st.markdown("#### 🌡️ Limiar de Alerta")
    limiar_chuva = st.slider("Precipitação crítica 24h (mm)", 0, 100, 20)
    limiar_umidade = st.slider("Umidade crítica (%)", 50, 100, 85)

    st.markdown("---")
    st.success("📡 **DADOS REAIS**\nINPE via OpenWeather\nSão Paulo · Guarulhos · Santo André")
    st.caption("FloodVision v1.0 · FIAP Global Solution 2025")


# ─────────────────────────────────────────────
# FILTROS
# ─────────────────────────────────────────────
df = df_raw.copy()
df = df[(df["data"] >= data_inicio) & (df["data"] <= data_fim)]
if cidade_selecionada != "Todas":
    df = df[df["cidade"] == cidade_selecionada]


# ─────────────────────────────────────────────
# CABEÇALHO
# ─────────────────────────────────────────────
col_titulo, col_status = st.columns([3, 1])
with col_titulo:
    st.markdown('<h1 class="main-title">🌊 FloodVision</h1>', unsafe_allow_html=True)
    st.markdown('<p class="sub-title">MONITORAMENTO E PREDIÇÃO DE ENCHENTES URBANAS — GRANDE SÃO PAULO</p>', unsafe_allow_html=True)
with col_status:
    agora = datetime.now().strftime("%d/%m/%Y %H:%M")
    st.markdown(f"""
    <div style="text-align:right; padding-top:8px;">
        <span style="background:#0d2a1f; color:#22c55e; border:1px solid #22c55e;
                     border-radius:20px; padding:4px 12px; font-size:0.75rem; font-family:'Space Mono',monospace;">
            ● AO VIVO
        </span>
        <br/><small style="color:#4a7fa0;">{agora}</small>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ─────────────────────────────────────────────
# MÉTRICAS TOPO
# ─────────────────────────────────────────────
total_registros  = len(df)
dias_chuva       = int(df[df["chovendo"] == 1]["data"].nunique())
chuva_max_24h    = df["precipitacao_24h"].max()
temp_media        = df["temperatura"].mean()
umidade_media     = df["umidade"].mean()
dias_risco_medio  = int((df["risco"] == "Médio").sum())

m1, m2, m3, m4, m5 = st.columns(5)
m1.metric("📋 Registros",         f"{total_registros:,}",          f"{df['cidade'].nunique()} cidades")
m2.metric("🌧️ Dias com Chuva",   f"{dias_chuva}",                  "no período")
m3.metric("💧 Chuva Máx 24h",    f"{chuva_max_24h:.1f} mm",        "pico registrado")
m4.metric("🌡️ Temp. Média",      f"{temp_media:.1f} °C",           "média do período")
m5.metric("⚠️ Alertas Médio",    f"{dias_risco_medio}",             "registros de risco")

st.markdown("---")


# ─────────────────────────────────────────────
# TABS
# ─────────────────────────────────────────────
tab1, tab2, tab3, tab4 = st.tabs([
    "🗺️  Mapa de Risco",
    "📈  Séries Temporais",
    "🤖  Predição IA",
    "🚨  Central de Alertas",
])


# ══════════════════════════════════════════════
# TAB 1 — MAPA
# ══════════════════════════════════════════════
with tab1:
    st.subheader("Mapa de Risco — Grande São Paulo")

    coords = coordenadas_cidades()

    # Calcula risco atual por cidade (último registro disponível)
    resumo_cidade = (
        df.sort_values("data_hora")
          .groupby("cidade")
          .last()
          .reset_index()[["cidade", "temperatura", "umidade", "precipitacao_24h", "precipitacao_48h", "risco"]]
    )

    col_mapa, col_painel = st.columns([2, 1])

    COR_RISCO = {"Crítico": "#ef4444", "Alto": "#f97316", "Médio": "#eab308", "Baixo": "#22c55e"}

    with col_mapa:
        m = folium.Map(location=[-23.55, -46.60], zoom_start=11, tiles="CartoDB dark_matter")

        for _, row in resumo_cidade.iterrows():
            cidade_key = row["cidade"]
            if cidade_key not in coords:
                continue
            cor = COR_RISCO.get(row["risco"], "#94a3b8")
            label = coords[cidade_key]["label"]

            folium.CircleMarker(
                location=[coords[cidade_key]["lat"], coords[cidade_key]["lon"]],
                radius=18,
                color=cor, fill=True, fill_color=cor, fill_opacity=0.75,
                popup=folium.Popup(f"""
                    <b style='color:{cor}'>{label}</b><br>
                    Risco: <b>{row['risco']}</b><br>
                    Temp: {row['temperatura']:.1f} °C<br>
                    Umidade: {row['umidade']:.0f}%<br>
                    Chuva 24h: {row['precipitacao_24h']:.1f} mm<br>
                    Chuva 48h: {row['precipitacao_48h']:.1f} mm
                """, max_width=200),
                tooltip=f"{label} — {row['risco']}",
            ).add_to(m)

            folium.Marker(
                location=[coords[cidade_key]["lat"] + 0.018, coords[cidade_key]["lon"]],
                icon=folium.DivIcon(html=f"""
                    <div style="font-family:monospace; font-size:11px; color:{cor};
                                background:rgba(0,0,0,0.7); padding:2px 6px; border-radius:4px;
                                white-space:nowrap; border:1px solid {cor};">
                        {label}
                    </div>
                """),
            ).add_to(m)

        st_folium(m, width=680, height=460)

    with col_painel:
        st.markdown("#### 📋 Status Atual por Cidade")
        for _, row in resumo_cidade.sort_values("precipitacao_24h", ascending=False).iterrows():
            cidade_key = row["cidade"]
            if cidade_key not in coords:
                continue
            label = coords[cidade_key]["label"]
            classe = {"Crítico": "alert-vermelho", "Alto": "alert-laranja",
                      "Médio": "alert-amarelo", "Baixo": "alert-verde"}.get(row["risco"], "alert-verde")
            emoji  = {"Crítico": "🔴", "Alto": "🟠", "Médio": "🟡", "Baixo": "🟢"}.get(row["risco"], "⚪")
            st.markdown(f"""
            <div class="alert-card {classe}">
                <b>{emoji} {label}</b><br>
                <small>🌡 {row['temperatura']:.1f}°C &nbsp;|&nbsp; 💧 {row['umidade']:.0f}%</small><br>
                <small>🌧 24h: {row['precipitacao_24h']:.1f}mm &nbsp;|&nbsp; 48h: {row['precipitacao_48h']:.1f}mm</small>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("---")
        st.markdown("#### 🗺️ Legenda")
        for nivel, cor in COR_RISCO.items():
            st.markdown(f"""
            <div style="display:flex; align-items:center; gap:8px; margin:4px 0;">
                <div style="width:14px; height:14px; border-radius:50%; background:{cor};"></div>
                <span style="color:{cor}; font-size:0.9rem;">{nivel}</span>
            </div>
            """, unsafe_allow_html=True)


# ══════════════════════════════════════════════
# TAB 2 — SÉRIES TEMPORAIS
# ══════════════════════════════════════════════
with tab2:
    st.subheader("Análise Temporal — Dados Horários")

    # Agrega por dia para visualização
    df_diario = (
        df.groupby(["data", "cidade_label"])
          .agg(
              precipitacao_24h=("precipitacao_24h", "max"),
              temperatura=("temperatura", "mean"),
              umidade=("umidade", "mean"),
              chovendo=("chovendo", "sum"),
          )
          .reset_index()
    )

    cor_cidades = {
        "Sao Paulo":   "#60b8ff",
        "Guarulhos":   "#a78bfa",
        "Santo Andre": "#22c55e",
    }

    # Gráfico 1 — Precipitação acumulada 24h
    fig_chuva = px.line(
        df_diario, x="data", y="precipitacao_24h", color="cidade_label",
        color_discrete_map=cor_cidades,
        labels={"precipitacao_24h": "Precipitação 24h (mm)", "data": "", "cidade_label": "Cidade"},
        title="Precipitação Acumulada 24h",
    )
    fig_chuva.add_hline(y=limiar_chuva, line_dash="dash", line_color="#ef4444",
                        annotation_text=f"Limiar ({limiar_chuva}mm)")
    fig_chuva.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(13,20,36,0.8)",
        font=dict(color="#94a3b8"), height=280, margin=dict(l=0, r=0, t=40, b=0),
        legend=dict(bgcolor="rgba(0,0,0,0)"),
    )
    fig_chuva.update_xaxes(gridcolor="#1e2d4a")
    fig_chuva.update_yaxes(gridcolor="#1e2d4a")
    st.plotly_chart(fig_chuva, use_container_width=True)

    col_t, col_u = st.columns(2)

    with col_t:
        fig_temp = px.line(
            df_diario, x="data", y="temperatura", color="cidade_label",
            color_discrete_map=cor_cidades,
            labels={"temperatura": "Temperatura Média (°C)", "data": "", "cidade_label": "Cidade"},
            title="Temperatura Média Diária",
        )
        fig_temp.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(13,20,36,0.8)",
            font=dict(color="#94a3b8"), height=280, margin=dict(l=0, r=0, t=40, b=0),
            legend=dict(bgcolor="rgba(0,0,0,0)"),
        )
        fig_temp.update_xaxes(gridcolor="#1e2d4a")
        fig_temp.update_yaxes(gridcolor="#1e2d4a")
        st.plotly_chart(fig_temp, use_container_width=True)

    with col_u:
        fig_umid = px.line(
            df_diario, x="data", y="umidade", color="cidade_label",
            color_discrete_map=cor_cidades,
            labels={"umidade": "Umidade Média (%)", "data": "", "cidade_label": "Cidade"},
            title="Umidade Relativa Média Diária",
        )
        fig_umid.add_hline(y=limiar_umidade, line_dash="dash", line_color="#f97316",
                           annotation_text=f"Limiar ({limiar_umidade}%)")
        fig_umid.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(13,20,36,0.8)",
            font=dict(color="#94a3b8"), height=280, margin=dict(l=0, r=0, t=40, b=0),
            legend=dict(bgcolor="rgba(0,0,0,0)"),
        )
        fig_umid.update_xaxes(gridcolor="#1e2d4a")
        fig_umid.update_yaxes(gridcolor="#1e2d4a")
        st.plotly_chart(fig_umid, use_container_width=True)

    # Heatmap hora × dia da semana (precipitação)
    st.markdown("#### 🔥 Mapa de Calor — Precipitação por Hora e Dia da Semana")
    dias_nome = ["Seg", "Ter", "Qua", "Qui", "Sex", "Sáb", "Dom"]
    heatmap_data = (
        df.groupby(["dia_semana", "hora_dia"])["precipitacao"]
          .mean()
          .reset_index()
          .pivot(index="dia_semana", columns="hora_dia", values="precipitacao")
          .fillna(0)
    )
    heatmap_data.index = [dias_nome[i] for i in heatmap_data.index]

    fig_heat = px.imshow(
        heatmap_data,
        color_continuous_scale="Blues",
        labels=dict(x="Hora do Dia", y="Dia da Semana", color="Chuva (mm)"),
        title="Precipitação Média por Hora × Dia da Semana",
        aspect="auto",
    )
    fig_heat.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(13,20,36,0.8)",
        font=dict(color="#94a3b8"), height=280, margin=dict(l=0, r=0, t=40, b=0),
    )
    st.plotly_chart(fig_heat, use_container_width=True)


# ══════════════════════════════════════════════
# TAB 3 — PREDIÇÃO IA
# ══════════════════════════════════════════════
with tab3:
    st.subheader("🤖 Predição de Risco — Modelo IA")
    st.info(
        "**Placeholder do modelo ML.** "
        "Substitua `prever_risco()` pelo modelo Random Forest treinado com Scikit-Learn "
        "quando estiver pronto. A estrutura de entrada/saída já está preparada."
    )

    st.markdown("#### Simule um cenário")
    col_a, col_b, col_c, col_d = st.columns(4)
    chuva_24h  = col_a.number_input("🌧️ Chuva 24h (mm)",  0.0, 200.0, float(df["precipitacao_24h"].mean()), step=1.0)
    chuva_48h  = col_b.number_input("🌧️ Chuva 48h (mm)",  0.0, 200.0, float(df["precipitacao_48h"].mean()), step=1.0)
    umidade    = col_c.number_input("💧 Umidade (%)",       0.0, 100.0, float(df["umidade"].mean()),         step=1.0)
    temp       = col_d.number_input("🌡️ Temperatura (°C)", 0.0,  45.0, float(df["temperatura"].mean()),     step=0.5)

    # ── Substitua esta função pelo modelo treinado ──────────────────────────
    def prever_risco(c24, c48, umid, tmp):
        """
        SUBSTITUIR POR:
            modelo = joblib.load('modelo_rf.pkl')
            X = pd.DataFrame([[c24, c48, umid, tmp]],
                              columns=['precipitacao_24h','precipitacao_48h','umidade','temperatura'])
            classe = modelo.predict(X)[0]
            proba  = modelo.predict_proba(X)[0].tolist()
            return classe, proba
        """
        score = 0
        if c24  > 30: score += 3
        elif c24 > 15: score += 1
        if c48  > 50: score += 2
        elif c48 > 25: score += 1
        if umid > 90: score += 2
        elif umid > 80: score += 1

        classes = ["Baixo", "Médio", "Alto", "Crítico"]
        if score >= 5: idx, proba = 3, [0.05, 0.10, 0.15, 0.70]
        elif score >= 3: idx, proba = 2, [0.10, 0.20, 0.55, 0.15]
        elif score >= 1: idx, proba = 1, [0.20, 0.55, 0.20, 0.05]
        else:            idx, proba = 0, [0.75, 0.18, 0.05, 0.02]
        return classes[idx], proba
    # ────────────────────────────────────────────────────────────────────────

    resultado, probabilidades = prever_risco(chuva_24h, chuva_48h, umidade, temp)
    COR = {"Crítico": "#ef4444", "Alto": "#f97316", "Médio": "#eab308", "Baixo": "#22c55e"}
    EMOJI = {"Crítico": "🔴", "Alto": "🟠", "Médio": "🟡", "Baixo": "🟢"}
    cor = COR[resultado]

    st.markdown(f"""
    <div style="background:linear-gradient(135deg,#0d1b2e,#122040); border:2px solid {cor};
                border-radius:16px; padding:28px 32px; text-align:center; margin:16px 0;">
        <div style="font-size:3.5rem">{EMOJI[resultado]}</div>
        <div style="font-family:'Space Mono',monospace; font-size:1.8rem; color:{cor}; font-weight:700;">
            RISCO {resultado.upper()}
        </div>
        <div style="color:#7fa8cc; margin-top:8px; font-size:0.9rem;">
            Chuva 24h: {chuva_24h}mm · Chuva 48h: {chuva_48h}mm · Umidade: {umidade:.0f}% · Temp: {temp:.1f}°C
        </div>
    </div>
    """, unsafe_allow_html=True)

    fig_proba = go.Figure(go.Bar(
        x=["Baixo", "Médio", "Alto", "Crítico"],
        y=[p * 100 for p in probabilidades],
        marker_color=["#22c55e", "#eab308", "#f97316", "#ef4444"],
        text=[f"{p*100:.0f}%" for p in probabilidades],
        textposition="outside",
    ))
    fig_proba.update_layout(
        title="Probabilidade por Classe de Risco",
        yaxis_title="Probabilidade (%)", yaxis_range=[0, 100],
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(13,20,36,0.8)",
        font=dict(color="#94a3b8"), height=280, margin=dict(l=0, r=0, t=40, b=0),
    )
    fig_proba.update_xaxes(gridcolor="#1e2d4a")
    fig_proba.update_yaxes(gridcolor="#1e2d4a")
    st.plotly_chart(fig_proba, use_container_width=True)

    # Estatísticas dos dados reais como referência
    st.markdown("#### 📊 Valores de Referência do Dataset")
    col_r1, col_r2, col_r3, col_r4 = st.columns(4)
    col_r1.metric("Chuva 24h máx",  f"{df['precipitacao_24h'].max():.1f} mm")
    col_r2.metric("Chuva 48h máx",  f"{df['precipitacao_48h'].max():.1f} mm")
    col_r3.metric("Umidade máx",    f"{df['umidade'].max():.0f}%")
    col_r4.metric("Temp mín/máx",   f"{df['temperatura'].min():.1f}/{df['temperatura'].max():.1f}°C")


# ══════════════════════════════════════════════
# TAB 4 — CENTRAL DE ALERTAS
# ══════════════════════════════════════════════
with tab4:
    st.subheader("🚨 Central de Alertas — Grande São Paulo")

    # Últimas ocorrências de risco no período
    df_alertas = df[df["risco"] != "Baixo"].sort_values("data_hora", ascending=False).head(20)

    col_esq, col_dir = st.columns([3, 2])

    with col_esq:
        st.markdown("#### Últimas Ocorrências de Risco")
        if df_alertas.empty:
            st.success("✅ Nenhuma ocorrência de risco no período selecionado.")
        else:
            for _, row in df_alertas.iterrows():
                classe = {"Crítico": "alert-vermelho", "Alto": "alert-laranja",
                          "Médio": "alert-amarelo"}.get(row["risco"], "alert-verde")
                emoji  = {"Crítico": "🔴", "Alto": "🟠", "Médio": "🟡"}.get(row["risco"], "🟢")
                acao   = {
                    "Crítico": "⚠️ Evacuação imediata recomendada",
                    "Alto":    "📢 Monitoramento contínuo ativo",
                    "Médio":   "👀 Atenção preventiva",
                }.get(row["risco"], "✅ Sem ação necessária")
                cidade_label = row["cidade"].replace("_", " ")
                dt_str = pd.Timestamp(row["data_hora"]).strftime("%d/%m %H:%M")
                st.markdown(f"""
                <div class="alert-card {classe}">
                    <b>{emoji} {cidade_label}</b> &nbsp;<small style="opacity:0.7">{dt_str}</small><br>
                    <small>🌧 24h: {row['precipitacao_24h']:.1f}mm &nbsp;|&nbsp; 💧 {row['umidade']:.0f}% &nbsp;|&nbsp; 🌡 {row['temperatura']:.1f}°C</small><br>
                    <small style="opacity:0.8">{acao}</small>
                </div>
                """, unsafe_allow_html=True)

    with col_dir:
        st.markdown("#### Distribuição de Risco no Período")
        dist = df["risco"].value_counts().reset_index()
        dist.columns = ["Risco", "Registros"]
        cor_map = {"Crítico": "#ef4444", "Alto": "#f97316", "Médio": "#eab308", "Baixo": "#22c55e"}
        fig_pizza = px.pie(
            dist, names="Risco", values="Registros",
            color="Risco", color_discrete_map=cor_map, hole=0.5,
        )
        fig_pizza.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", font=dict(color="#94a3b8"),
            margin=dict(l=0, r=0, t=20, b=0), height=260,
            legend=dict(bgcolor="rgba(0,0,0,0)"),
        )
        st.plotly_chart(fig_pizza, use_container_width=True)

        st.markdown("#### 📊 Resumo do Período")
        total = len(df)
        for nivel in ["Crítico", "Alto", "Médio", "Baixo"]:
            qtd = int((df["risco"] == nivel).sum())
            pct = qtd / total * 100 if total > 0 else 0
            cor = cor_map[nivel]
            emoji = {"Crítico": "🔴", "Alto": "🟠", "Médio": "🟡", "Baixo": "🟢"}[nivel]
            st.markdown(f"""
            <div style="display:flex; align-items:center; gap:12px; margin:6px 0;">
                <span>{emoji}</span>
                <div style="flex:1">
                    <div style="display:flex; justify-content:space-between;">
                        <span style="color:{cor}; font-weight:600; font-size:0.9rem;">{nivel}</span>
                        <span style="color:#94a3b8; font-size:0.85rem;">{qtd:,} ({pct:.1f}%)</span>
                    </div>
                    <div style="background:#1e2d4a; border-radius:4px; height:5px; margin-top:3px;">
                        <div style="background:{cor}; width:{pct}%; height:100%; border-radius:4px;"></div>
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)