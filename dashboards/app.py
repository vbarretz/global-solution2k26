import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import folium
from streamlit_folium import st_folium
from datetime import datetime
import google.generativeai as genai
from dotenv import load_dotenv
import os

load_dotenv("chave_api.env")
genai.configure(
    api_key=os.getenv("GEMINI_API_KEY")
)
model = genai.GenerativeModel("gemini-2.5-flash")
# ─────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="FloodVision — Inteligência Orbital para Gestão de Desastres",
    page_icon="🛰️",
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

/* Fundo com estrelas via gradiente pontilhado */
.stApp {
    background-color: #060912;
    background-image:
        radial-gradient(1px 1px at 10% 15%, rgba(255,255,255,0.6) 0%, transparent 100%),
        radial-gradient(1px 1px at 25% 40%, rgba(255,255,255,0.4) 0%, transparent 100%),
        radial-gradient(1px 1px at 40% 10%, rgba(255,255,255,0.5) 0%, transparent 100%),
        radial-gradient(1px 1px at 55% 60%, rgba(255,255,255,0.3) 0%, transparent 100%),
        radial-gradient(1px 1px at 70% 25%, rgba(255,255,255,0.6) 0%, transparent 100%),
        radial-gradient(1px 1px at 80% 75%, rgba(255,255,255,0.4) 0%, transparent 100%),
        radial-gradient(1px 1px at 90% 45%, rgba(255,255,255,0.5) 0%, transparent 100%),
        radial-gradient(1px 1px at 15% 80%, rgba(255,255,255,0.3) 0%, transparent 100%),
        radial-gradient(1px 1px at 60% 90%, rgba(255,255,255,0.4) 0%, transparent 100%),
        radial-gradient(2px 2px at 35% 55%, rgba(255,140,0,0.2) 0%, transparent 100%),
        radial-gradient(2px 2px at 75% 15%, rgba(30,120,255,0.2) 0%, transparent 100%),
        linear-gradient(180deg, #060912 0%, #0a1020 50%, #060c18 100%);
    color: #e8eaf0;
}

[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #080d1a 0%, #0c1528 100%);
    border-right: 1px solid #ff8c00;
}

/* Métricas com borda laranja */
[data-testid="stMetric"] {
    background: linear-gradient(135deg, #0d1220 0%, #14203a 100%);
    border: 1px solid rgba(255, 120, 0, 0.4);
    border-radius: 12px;
    padding: 16px 20px;
    box-shadow: 0 0 12px rgba(255, 100, 0, 0.08);
}
[data-testid="stMetricLabel"] { color: #f0a060 !important; font-size: 0.75rem !important; letter-spacing: 0.1em; text-transform: uppercase; }
[data-testid="stMetricValue"] { color: #ffe0b0 !important; font-family: 'Space Mono', monospace !important; }

/* Cards de alerta */
.alert-card { border-radius: 12px; padding: 16px 20px; margin: 8px 0; border-left: 4px solid; }
.alert-verde   { background: #0a2016; border-color: #22c55e; color: #86efac; }
.alert-amarelo { background: #1f1600; border-color: #eab308; color: #fde047; }
.alert-laranja { background: #1f0d00; border-color: #f97316; color: #fdba74; }
.alert-vermelho{ background: #1f0007; border-color: #ef4444; color: #fca5a5; }

/* Tabs com estilo orbital */
.stTabs [data-baseweb="tab-list"] {
    background: linear-gradient(90deg, #0c1528 0%, #101c30 100%);
    border-radius: 10px; padding: 4px; gap: 4px;
    border: 1px solid rgba(255,120,0,0.2);
}
.stTabs [data-baseweb="tab"] { border-radius: 8px; color: #a0b8d8; font-weight: 600; padding: 8px 20px; }
.stTabs [aria-selected="true"] {
    background: linear-gradient(90deg, #1a2a10 0%, #2a1a05 100%) !important;
    color: #ff9030 !important;
    border: 1px solid rgba(255,120,0,0.5) !important;
}

/* Títulos principais */
.main-title {
    font-family: 'Space Mono', monospace;
    font-size: 2rem; font-weight: 700;
    background: linear-gradient(90deg, #ff8c00, #ffb347, #4aa8ff);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    letter-spacing: -0.02em; margin-bottom: 0;
}
.sub-title { color: #7090b0; font-size: 0.85rem; letter-spacing: 0.12em; margin-top: 4px; text-transform: uppercase; }
.sidebar-title {
    font-family: 'Space Mono', monospace; font-size: 1.3rem; font-weight: 700;
    background: linear-gradient(90deg, #ff8c00, #4aa8ff);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
}

/* Card NDWI */
.ndwi-card {
    border-radius: 12px; padding: 16px 20px; margin: 8px 0; border-left: 4px solid;
    background: linear-gradient(135deg, #0d1220, #1a1005);
    border-color: #ff8c00; color: #ffcc80;
}

/* Separador laranja */
hr { border-color: rgba(255,120,0,0.25); }

/* Borda brilhante no topo da sidebar */
[data-testid="stSidebar"]::before {
    content: '';
    display: block;
    height: 3px;
    background: linear-gradient(90deg, #ff8c00, #4aa8ff, #ff8c00);
    margin-bottom: 8px;
}

/* Órbita decorativa no cabeçalho */
.orbit-badge {
    display: inline-block;
    border: 1px solid rgba(255,140,0,0.5);
    border-radius: 20px;
    padding: 3px 12px;
    font-size: 0.72rem;
    font-family: 'Space Mono', monospace;
    color: #ff9030;
    background: rgba(255,120,0,0.08);
    letter-spacing: 0.08em;
}
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# CARREGAMENTO DOS DADOS
# ─────────────────────────────────────────────
@st.cache_data
def carregar_dados():
    df = pd.read_csv("data/previsoes_ml.csv", parse_dates=["data_hora"])
    df["data"] = df["data_hora"].dt.date
    df["hora_dia"] = df["data_hora"].dt.hour
    df["dia_semana"] = df["data_hora"].dt.dayofweek
    df["cidade_label"] = df["cidade"].str.replace("_", " ")
    # Compatibilidade: renomeia risco_previsto → risco se necessário
    if "risco_previsto" in df.columns and "risco" not in df.columns:
        df = df.rename(columns={"risco_previsto": "risco"})
    # Cria coluna chovendo se não existir
    if "chovendo" not in df.columns:
        df["chovendo"] = (df["precipitacao"] > 0).astype(int)
    # Cria precipitacao_48h se não existir (rolling 48h a partir da 24h)
    if "precipitacao_48h" not in df.columns:
        df = df.sort_values(["cidade", "data_hora"])
        df["precipitacao_48h"] = (
            df.groupby("cidade")["precipitacao"]
            .transform(lambda x: x.rolling(48, min_periods=1).sum())
        )
    return df

@st.cache_data
def coordenadas_cidades():
    return {
        "Sao_Paulo":   {"lat": -23.5505, "lon": -46.6333, "label": "São Paulo"},
        "Guarulhos":   {"lat": -23.4543, "lon": -46.5333, "label": "Guarulhos"},
        "Santo_Andre": {"lat": -23.6618, "lon": -46.5289, "label": "Santo André"},
    }

def classificar_ndwi(val):
    if val >= 0.2:
        return "Água/Enchente", "#ef4444"
    elif val >= 0.0:
        return "Úmido", "#f97316"
    elif val >= -0.1:
        return "Transição", "#eab308"
    else:
        return "Seco/Vegetação", "#22c55e"


# ─────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("""
    <div style="text-align:center; padding: 12px 0 4px 0;">
        <div style="font-size:2.2rem;">🛰️</div>
        <p class="sidebar-title">FloodVision</p>
        <p class="sub-title" style="font-size:0.68rem; line-height:1.5;">
            DADOS ORBITAIS · INTELIGÊNCIA OPERACIONAL<br>GESTÃO DE DESASTRES
        </p>
        <div style="display:flex; justify-content:center; gap:6px; margin-top:6px;">
            <span style="font-size:0.8rem;">🌍</span>
            <span style="font-size:0.8rem;">🔭</span>
            <span style="font-size:0.8rem;">📡</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
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
    limiar_chuva   = st.slider("Precipitação crítica 24h (mm)", 0, 100, 20)
    limiar_umidade = st.slider("Umidade crítica (%)", 50, 100, 85)

    st.markdown("---")
    st.markdown("""
    <div style="background:linear-gradient(135deg,#1a0f00,#001a2a); border:1px solid rgba(255,140,0,0.3);
                border-radius:10px; padding:12px; text-align:center;">
        <div style="color:#ff9030; font-size:0.8rem; font-weight:700;">📡 DADOS REAIS</div>
        <div style="color:#7090b0; font-size:0.75rem; margin-top:4px;">INPE via OpenWeather</div>
        <div style="color:#7090b0; font-size:0.72rem;">São Paulo · Guarulhos · Santo André</div>
        <div style="color:#4aa8ff; font-size:0.7rem; margin-top:6px; font-family:'Space Mono',monospace;">
            🛰 NDWI via Satélite
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.caption("FloodVision v2.0 · FIAP Global Solution 2025")


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
    st.markdown("""
    <div style="display:flex; align-items:center; gap:14px;">
        <div style="font-size:2.8rem; filter:drop-shadow(0 0 8px rgba(255,140,0,0.6));">🛰️</div>
        <div>
            <h1 class="main-title">FloodVision</h1>
            <p class="sub-title">uma plataforma que transforma dados orbitais em inteligência operacional para gestão de desastres</p>
        </div>
    </div>
    <div style="display:flex; gap:8px; margin-top:10px; flex-wrap:wrap;">
        <span class="orbit-badge">🌍 LEO ORBIT</span>
        <span class="orbit-badge">📡 NDWI ATIVO</span>
        <span class="orbit-badge">🔭 SENSORIAMENTO REMOTO</span>
        <span class="orbit-badge">⚡ TEMPO REAL</span>
    </div>
    """, unsafe_allow_html=True)
with col_status:
    agora = datetime.now().strftime("%d/%m/%Y %H:%M")
    st.markdown(f"""
    <div style="text-align:right; padding-top:8px;">
        <span style="background:rgba(255,120,0,0.12); color:#ff9030; border:1px solid rgba(255,120,0,0.5);
                     border-radius:20px; padding:4px 12px; font-size:0.75rem; font-family:'Space Mono',monospace;">
            ● TRANSMISSÃO ATIVA
        </span>
        <br/><small style="color:#7090b0; font-family:'Space Mono',monospace;">{agora}</small>
        <br/><small style="color:#4aa8ff; font-size:0.7rem;">🛸 COBERTURA ORBITAL</small>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ─────────────────────────────────────────────
# MÉTRICAS TOPO
# ─────────────────────────────────────────────
total_registros  = len(df)
dias_chuva       = int(df[df["chovendo"] == 1]["data"].nunique())
chuva_max_24h    = df["precipitacao_24h"].max()
temp_media       = df["temperatura"].mean()
umidade_media    = df["umidade"].mean()
dias_risco_medio = int((df["risco"] == "Médio").sum())

m1, m2, m3, m4, m5 = st.columns(5)
m1.metric("📋 Registros",       f"{total_registros:,}",     f"{df['cidade'].nunique()} cidades")
m2.metric("🌧️ Dias com Chuva", f"{dias_chuva}",             "no período")
m3.metric("💧 Chuva Máx 24h",  f"{chuva_max_24h:.1f} mm",  "pico registrado")
m4.metric("🌡️ Temp. Média",    f"{temp_media:.1f} °C",      "média do período")
m5.metric("⚠️ Alertas Médio",  f"{dias_risco_medio}",        "registros de risco")

st.markdown("---")


# ─────────────────────────────────────────────
# TABS
# ─────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "🌍 Mapa Orbital",
    "📈 Séries Temporais",
    "🛰️ Índice NDWI",
    "🤖 Predição IA",
    "🚨 Central de Alertas",
    "💬 ChatBot"
])


# ══════════════════════════════════════════════
# TAB 1 — MAPA
# ══════════════════════════════════════════════
with tab1:
    st.subheader("🌍 Cobertura Orbital — Risco Hidrológico · Grande São Paulo")

    coords = coordenadas_cidades()
    resumo_cidade = (
        df.sort_values("data_hora")
          .groupby("cidade")
          .last()
          .reset_index()[["cidade", "temperatura", "umidade", "precipitacao_24h", "precipitacao_48h", "risco", "ndwi"]]
    )

    col_mapa, col_painel = st.columns([2, 1])
    COR_RISCO = {"Crítico": "#ef4444", "Alto": "#f97316", "Médio": "#eab308", "Baixo": "#22c55e"}

    with col_mapa:
        m = folium.Map(location=[-23.55, -46.60], zoom_start=11, tiles="CartoDB dark_matter")

        for _, row in resumo_cidade.iterrows():
            cidade_key = row["cidade"]
            if cidade_key not in coords:
                continue
            cor   = COR_RISCO.get(row["risco"], "#94a3b8")
            label = coords[cidade_key]["label"]
            ndwi_class, _ = classificar_ndwi(row["ndwi"])

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
                    NDWI: {row['ndwi']:.3f} ({ndwi_class})
                """, max_width=220),
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
            label  = coords[cidade_key]["label"]
            classe = {"Crítico": "alert-vermelho", "Alto": "alert-laranja",
                      "Médio": "alert-amarelo", "Baixo": "alert-verde"}.get(row["risco"], "alert-verde")
            emoji  = {"Crítico": "🔴", "Alto": "🟠", "Médio": "🟡", "Baixo": "🟢"}.get(row["risco"], "⚪")
            ndwi_class, ndwi_cor = classificar_ndwi(row["ndwi"])
            st.markdown(f"""
            <div class="alert-card {classe}">
                <b>{emoji} {label}</b><br>
                <small>🌡 {row['temperatura']:.1f}°C &nbsp;|&nbsp; 💧 {row['umidade']:.0f}%</small><br>
                <small>🌧 24h: {row['precipitacao_24h']:.1f}mm</small><br>
                <small>🛰 NDWI: <span style="color:{ndwi_cor}">{row['ndwi']:.3f} ({ndwi_class})</span></small>
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
    st.subheader("📡 Séries Temporais — Telemetria Orbital e Dados de Solo")

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
        "Sao Paulo":   "#ff8c00",
        "Guarulhos":   "#4aa8ff",
        "Santo Andre": "#ff4fa0",
    }
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

    # Heatmap hora × dia da semana
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
# TAB 3 — NDWI
# ══════════════════════════════════════════════
with tab3:
    st.subheader("🛰️ Índice NDWI — Sensoriamento Remoto de Umidade do Solo")

    st.markdown("""
    <div class="ndwi-card">
        <b>🔭 O que é o NDWI e por que usamos satélites?</b><br>
        O <b>Normalized Difference Water Index (NDWI)</b> é calculado a partir de imagens de satélites
        de observação terrestre (como Landsat e Sentinel). Ele detecta a presença de água na superfície
        e a umidade do solo com precisão — algo impossível apenas com sensores terrestres.
        Valores próximos de <b>+1</b> indicam corpos d'água ou enchentes; valores negativos indicam solo seco ou vegetação densa.
        <br><br>
        <b>🌌 Faixas de classificação:</b>
        &nbsp;<span style="color:#ef4444">■</span> ≥ 0,2 Água/Enchente
        &nbsp;<span style="color:#f97316">■</span> 0 a 0,2 Úmido
        &nbsp;<span style="color:#eab308">■</span> -0,1 a 0 Transição
        &nbsp;<span style="color:#22c55e">■</span> < -0,1 Seco/Vegetação
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # ── Métricas NDWI por cidade ──────────────────────────────────────────
    st.markdown("#### 📊 NDWI Atual por Cidade")
    resumo_ndwi = (
        df.sort_values("data_hora")
          .groupby("cidade")
          .last()
          .reset_index()[["cidade", "ndwi"]]
    )
    coords = coordenadas_cidades()
    cols_ndwi = st.columns(len(resumo_ndwi))
    for i, (_, row) in enumerate(resumo_ndwi.iterrows()):
        label = coords.get(row["cidade"], {}).get("label", row["cidade"])
        classe, cor = classificar_ndwi(row["ndwi"])
        with cols_ndwi[i]:
            st.markdown(f"""
            <div style="background:linear-gradient(135deg,#0d1b2e,#122040);
                        border:1px solid {cor}; border-radius:12px;
                        padding:20px; text-align:center;">
                <div style="color:{cor}; font-family:'Space Mono',monospace; font-size:1.8rem; font-weight:700;">
                    {row['ndwi']:.4f}
                </div>
                <div style="color:#94a3b8; font-size:0.8rem; margin-top:4px;">{label}</div>
                <div style="color:{cor}; font-size:0.85rem; margin-top:4px; font-weight:600;">{classe}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("---")

    # ── Série temporal NDWI ───────────────────────────────────────────────
    st.markdown("#### 📈 Evolução Temporal do NDWI")

    df_ndwi_diario = (
        df.groupby(["data", "cidade_label"])["ndwi"]
          .mean()
          .reset_index()
    )

    cor_cidades = {
        "Sao Paulo":   "#ff8c00",
        "Guarulhos":   "#4aa8ff",
        "Santo Andre": "#ff4fa0",
    }

    fig_ndwi_ts = px.line(
        df_ndwi_diario, x="data", y="ndwi", color="cidade_label",
        color_discrete_map=cor_cidades,
        labels={"ndwi": "NDWI Médio Diário", "data": "", "cidade_label": "Cidade"},
        title="NDWI Médio Diário por Cidade",
    )
    # Linhas de referência das faixas
    fig_ndwi_ts.add_hline(y=0.2,  line_dash="dot", line_color="#ef4444", line_width=1,
                          annotation_text="Limiar Água (0.2)",  annotation_position="bottom right")
    fig_ndwi_ts.add_hline(y=0.0,  line_dash="dot", line_color="#f97316", line_width=1,
                          annotation_text="Úmido (0.0)",        annotation_position="bottom right")
    fig_ndwi_ts.add_hline(y=-0.1, line_dash="dot", line_color="#eab308", line_width=1,
                          annotation_text="Transição (-0.1)",   annotation_position="bottom right")
    fig_ndwi_ts.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(13,20,36,0.8)",
        font=dict(color="#94a3b8"), height=320, margin=dict(l=0, r=0, t=40, b=0),
        legend=dict(bgcolor="rgba(0,0,0,0)"),
    )
    fig_ndwi_ts.update_xaxes(gridcolor="#1e2d4a")
    fig_ndwi_ts.update_yaxes(gridcolor="#1e2d4a")
    st.plotly_chart(fig_ndwi_ts, use_container_width=True)

    # ── NDWI vs Precipitação (scatter) ───────────────────────────────────
    col_scatter, col_dist = st.columns(2)

    with col_scatter:
        st.markdown("#### 🔵 NDWI × Precipitação 24h")
        fig_scatter = px.scatter(
            df.sample(min(2000, len(df))),  # amostra para performance
            x="precipitacao_24h", y="ndwi",
            color="cidade_label",
            color_discrete_map=cor_cidades,
            opacity=0.6,
            labels={
                "precipitacao_24h": "Precipitação 24h (mm)",
                "ndwi": "NDWI",
                "cidade_label": "Cidade",
            },
            title="Correlação NDWI × Precipitação",
        )
        fig_scatter.add_hline(y=0.0,  line_dash="dash", line_color="#f97316", line_width=1)
        fig_scatter.add_hline(y=0.2,  line_dash="dash", line_color="#ef4444", line_width=1)
        fig_scatter.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(13,20,36,0.8)",
            font=dict(color="#94a3b8"), height=320, margin=dict(l=0, r=0, t=40, b=0),
            legend=dict(bgcolor="rgba(0,0,0,0)"),
        )
        fig_scatter.update_xaxes(gridcolor="#1e2d4a")
        fig_scatter.update_yaxes(gridcolor="#1e2d4a")
        st.plotly_chart(fig_scatter, use_container_width=True)

    with col_dist:
        st.markdown("#### 📊 Distribuição NDWI por Cidade")
        fig_box = px.box(
            df, x="cidade_label", y="ndwi",
            color="cidade_label",
            color_discrete_map=cor_cidades,
            labels={"cidade_label": "Cidade", "ndwi": "NDWI"},
            title="Distribuição dos Valores NDWI",
        )
        fig_box.add_hline(y=0.0,  line_dash="dash", line_color="#f97316", line_width=1)
        fig_box.add_hline(y=0.2,  line_dash="dash", line_color="#ef4444", line_width=1)
        fig_box.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(13,20,36,0.8)",
            font=dict(color="#94a3b8"), height=320, margin=dict(l=0, r=0, t=40, b=0),
            showlegend=False,
        )
        fig_box.update_xaxes(gridcolor="#1e2d4a")
        fig_box.update_yaxes(gridcolor="#1e2d4a")
        st.plotly_chart(fig_box, use_container_width=True)

    # ── Heatmap NDWI hora × cidade ────────────────────────────────────────
    st.markdown("#### 🔥 Mapa de Calor — NDWI por Hora do Dia")
    heatmap_ndwi = (
        df.groupby(["cidade_label", "hora_dia"])["ndwi"]
          .mean()
          .reset_index()
          .pivot(index="cidade_label", columns="hora_dia", values="ndwi")
          .fillna(0)
    )
    fig_heat_ndwi = px.imshow(
        heatmap_ndwi,
        color_continuous_scale="RdYlGn_r",
        zmin=-0.5, zmax=0.5,
        labels=dict(x="Hora do Dia", y="Cidade", color="NDWI"),
        title="NDWI Médio por Hora do Dia × Cidade",
        aspect="auto",
    )
    fig_heat_ndwi.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(13,20,36,0.8)",
        font=dict(color="#94a3b8"), height=260, margin=dict(l=0, r=0, t=40, b=0),
    )
    st.plotly_chart(fig_heat_ndwi, use_container_width=True)

    # ── Tabela de estatísticas NDWI ───────────────────────────────────────
    st.markdown("#### 📋 Estatísticas NDWI por Cidade")
    stats_ndwi = (
        df.groupby("cidade_label")["ndwi"]
          .agg(["min", "max", "mean", "std"])
          .round(4)
          .reset_index()
    )
    stats_ndwi.columns = ["Cidade", "Mínimo", "Máximo", "Média", "Desvio Padrão"]
    stats_ndwi["Classificação Média"] = stats_ndwi["Média"].apply(
        lambda v: classificar_ndwi(v)[0]
    )
    st.dataframe(
        stats_ndwi,
        use_container_width=True,
        hide_index=True,
    )


# ══════════════════════════════════════════════
# TAB 4 — PREDIÇÃO IA
# ══════════════════════════════════════════════
with tab4:
    st.subheader("🤖 Predição de Risco — Modelo IA Alimentado por Dados Orbitais")
    st.info(
        "**Placeholder do modelo ML.** "
        "Substitua `prever_risco()` pelo modelo Random Forest treinado com Scikit-Learn. "
        "O NDWI orbital já está incluído como feature preditora."
    )

    st.markdown("#### Simule um cenário")
    col_a, col_b, col_c, col_d, col_e = st.columns(5)
    chuva_24h  = col_a.number_input("🌧️ Chuva 24h (mm)",  0.0, 200.0, float(df["precipitacao_24h"].mean()), step=1.0)
    chuva_48h  = col_b.number_input("🌧️ Chuva 48h (mm)",  0.0, 200.0, float(df["precipitacao_48h"].mean()), step=1.0)
    umidade    = col_c.number_input("💧 Umidade (%)",       0.0, 100.0, float(df["umidade"].mean()),          step=1.0)
    temp       = col_d.number_input("🌡️ Temperatura (°C)", 0.0,  45.0, float(df["temperatura"].mean()),      step=0.5)
    ndwi_input = col_e.number_input("🛰️ NDWI",            -1.0,   1.0, float(df["ndwi"].mean()),             step=0.01)

    def prever_risco(c24, c48, umid, tmp, ndwi):
        """
        SUBSTITUIR POR:
            modelo = joblib.load('modelo_rf.pkl')
            X = pd.DataFrame([[c24, c48, umid, tmp, ndwi]],
                              columns=['precipitacao_24h','precipitacao_48h','umidade','temperatura','ndwi'])
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
        if ndwi >= 0.2:  score += 3
        elif ndwi >= 0.0: score += 1

        classes = ["Baixo", "Médio", "Alto", "Crítico"]
        if score >= 6: idx, proba = 3, [0.05, 0.10, 0.15, 0.70]
        elif score >= 4: idx, proba = 2, [0.10, 0.20, 0.55, 0.15]
        elif score >= 2: idx, proba = 1, [0.20, 0.55, 0.20, 0.05]
        else:            idx, proba = 0, [0.75, 0.18, 0.05, 0.02]
        return classes[idx], proba

    resultado, probabilidades = prever_risco(chuva_24h, chuva_48h, umidade, temp, ndwi_input)
    COR   = {"Crítico": "#ef4444", "Alto": "#f97316", "Médio": "#eab308", "Baixo": "#22c55e"}
    EMOJI = {"Crítico": "🔴", "Alto": "🟠", "Médio": "🟡", "Baixo": "🟢"}
    cor   = COR[resultado]
    ndwi_classe, ndwi_cor = classificar_ndwi(ndwi_input)

    st.markdown(f"""
    <div style="background:linear-gradient(135deg,#0d1b2e,#122040); border:2px solid {cor};
                border-radius:16px; padding:28px 32px; text-align:center; margin:16px 0;">
        <div style="font-size:3.5rem">{EMOJI[resultado]}</div>
        <div style="font-family:'Space Mono',monospace; font-size:1.8rem; color:{cor}; font-weight:700;">
            RISCO {resultado.upper()}
        </div>
        <div style="color:#7fa8cc; margin-top:8px; font-size:0.9rem;">
            Chuva 24h: {chuva_24h}mm · 48h: {chuva_48h}mm · Umidade: {umidade:.0f}% · 
            Temp: {temp:.1f}°C · NDWI: <span style="color:{ndwi_cor}">{ndwi_input:.3f} ({ndwi_classe})</span>
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

    st.markdown("#### 📊 Valores de Referência do Dataset")
    col_r1, col_r2, col_r3, col_r4, col_r5 = st.columns(5)
    col_r1.metric("Chuva 24h máx", f"{df['precipitacao_24h'].max():.1f} mm")
    col_r2.metric("Chuva 48h máx", f"{df['precipitacao_48h'].max():.1f} mm")
    col_r3.metric("Umidade máx",   f"{df['umidade'].max():.0f}%")
    col_r4.metric("Temp mín/máx",  f"{df['temperatura'].min():.1f}/{df['temperatura'].max():.1f}°C")
    col_r5.metric("NDWI médio",    f"{df['ndwi'].mean():.4f}")


# ══════════════════════════════════════════════
# TAB 5 — CENTRAL DE ALERTAS
# ══════════════════════════════════════════════
with tab5:
    st.subheader("🚨 Central de Alertas — Inteligência Operacional para Gestão de Desastres")

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
                ndwi_classe, ndwi_cor = classificar_ndwi(row["ndwi"])
                st.markdown(f"""
                <div class="alert-card {classe}">
                    <b>{emoji} {cidade_label}</b> &nbsp;<small style="opacity:0.7">{dt_str}</small><br>
                    <small>🌧 24h: {row['precipitacao_24h']:.1f}mm &nbsp;|&nbsp; 💧 {row['umidade']:.0f}% &nbsp;|&nbsp; 🌡 {row['temperatura']:.1f}°C</small><br>
                    <small>🛰 NDWI: <span style="color:{ndwi_cor}">{row['ndwi']:.3f} ({ndwi_classe})</span></small><br>
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
# ══════════════════════════════════════════════
# TAB 6 — FLOODVISION COPILOT
# ══════════════════════════════════════════════

with tab6:

    st.subheader("💬 FloodVision Copilot")

    st.markdown("""
    Converse com os dados do sistema.

    Exemplos:

    • Qual cidade teve mais chuva?
    • Qual o risco atual de Guarulhos?
    • Qual cidade apresenta maior NDWI?
    • Quantos registros críticos existem?
    • Qual a temperatura média do período?
    """)

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    pergunta = st.chat_input(
        "Faça uma pergunta sobre os dados..."
    )

    if pergunta:

        st.session_state.chat_history.append(
            {
                "role": "user",
                "content": pergunta
            }
        )

        with st.chat_message("user"):
            st.markdown(pergunta)

        resumo_cidades = (
            df.sort_values("data_hora")
              .groupby("cidade")
              .last()
              .reset_index()
        )

        cidade_mais_chuva = (
            df.groupby("cidade")["precipitacao_24h"]
              .max()
              .sort_values(ascending=False)
        )

        ndwi_medio = (
            df.groupby("cidade")["ndwi"]
              .mean()
              .round(4)
        )

        distribuicao_risco = (
            df["risco"]
            .value_counts()
            .to_dict()
        )

        contexto = f"""
        TOTAL DE REGISTROS:
        {len(df)}

        MAIOR CHUVA POR CIDADE:
        {cidade_mais_chuva.to_string()}

        NDWI MÉDIO:
        {ndwi_medio.to_string()}

        DISTRIBUIÇÃO DE RISCO:
        {distribuicao_risco}

        ÚLTIMO STATUS DAS CIDADES:

        {resumo_cidades[['cidade',
                          'temperatura',
                          'umidade',
                          'precipitacao_24h',
                          'precipitacao_48h',
                          'ndwi',
                          'risco']].to_string(index=False)}
        """

        try:

            resposta = model.generate_content(
                f"""
            Você é o Chatbot do FloodVision.

            Especialista em:

            - meteorologia
            - enchentes
            - NDWI
            - monitoramento orbital
            - gestão de riscos

            Responda SOMENTE usando os dados fornecidos.

            {contexto}

            Pergunta:

            {pergunta}
            """
            )

            texto = resposta.text

        except Exception as e:

            texto = f"Erro ao consultar Gemini: {e}"

        with st.chat_message("assistant"):
            st.markdown(texto)

        st.session_state.chat_history.append(
            {
                "role": "assistant",
                "content": texto
            }
        )