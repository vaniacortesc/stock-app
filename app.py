import streamlit as st
import pandas as pd
import numpy as np
import random
from collections import defaultdict

st.set_page_config(
    page_title="Stock vs Venta",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── ESTILOS ────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@300;400;500;600&family=DM+Mono:wght@400;500&display=swap');

html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }

.block-container { padding: 1.5rem 2rem 2rem; max-width: 1400px; }

/* Header */
.app-header {
    background: #0F172A;
    border-radius: 12px;
    padding: 1.4rem 2rem;
    margin-bottom: 1.5rem;
    display: flex;
    align-items: center;
    justify-content: space-between;
}
.app-title { color: #F8FAFC; font-size: 1.25rem; font-weight: 600; margin: 0; }
.app-sub   { color: #64748B; font-size: 0.8rem; margin: 0; font-family: 'DM Mono', monospace; }

/* KPI cards */
.kpi-grid { display: grid; grid-template-columns: repeat(5,1fr); gap: 10px; margin-bottom: 1.5rem; }
.kpi { border-radius: 10px; padding: 0.9rem 1rem; border: 1px solid rgba(0,0,0,0.06); }
.kpi-label { font-size: 0.7rem; font-weight: 600; text-transform: uppercase; letter-spacing: .07em; margin-bottom: 4px; }
.kpi-val   { font-size: 1.6rem; font-weight: 600; font-family: 'DM Mono', monospace; line-height: 1; }
.kpi-red    { background:#FEF2F2; } .kpi-red    .kpi-label { color:#B91C1C; } .kpi-red    .kpi-val { color:#DC2626; }
.kpi-orange { background:#FFF7ED; } .kpi-orange .kpi-label { color:#C2410C; } .kpi-orange .kpi-val { color:#EA580C; }
.kpi-amber  { background:#FFFBEB; } .kpi-amber  .kpi-label { color:#B45309; } .kpi-amber  .kpi-val { color:#D97706; }
.kpi-green  { background:#F0FDF4; } .kpi-green  .kpi-label { color:#15803D; } .kpi-green  .kpi-val { color:#16A34A; }
.kpi-slate  { background:#F8FAFC; } .kpi-slate  .kpi-label { color:#475569; } .kpi-slate  .kpi-val { color:#64748B; }

/* Tabla */
.stDataFrame { border-radius: 10px; overflow: hidden; }
thead tr th { background: #0F172A !important; color: white !important; font-size: 0.75rem !important; }

/* Badges alerta */
.badge {
    display: inline-block; padding: 2px 10px; border-radius: 20px;
    font-size: 0.72rem; font-weight: 600; white-space: nowrap;
}
.badge-quiebre   { background:#FEE2E2; color:#991B1B; }
.badge-riesgo    { background:#FFEDD5; color:#9A3412; }
.badge-sobre     { background:#FEF3C7; color:#92400E; }
.badge-atencion  { background:#FEF9C3; color:#854D0E; }
.badge-ok        { background:#DCFCE7; color:#166534; }
.badge-sin       { background:#F1F5F9; color:#475569; }

/* Sidebar */
section[data-testid="stSidebar"] { background: #0F172A; }
section[data-testid="stSidebar"] * { color: #CBD5E1 !important; }
section[data-testid="stSidebar"] .stMultiSelect div { background: #1E293B !important; }
section[data-testid="stSidebar"] label { color: #94A3B8 !important; font-size: 0.78rem !important; font-weight: 600 !important; text-transform: uppercase; letter-spacing: .06em; }

/* Tabs */
.stTabs [data-baseweb="tab-list"] { gap: 4px; background: #F8FAFC; padding: 4px; border-radius: 10px; }
.stTabs [data-baseweb="tab"] { border-radius: 8px; font-size: 0.85rem; font-weight: 500; padding: 6px 18px; }
.stTabs [aria-selected="true"] { background: #0F172A !important; color: white !important; }

/* Acción urgente */
.accion-urgente { background: #FEF2F2; border-left: 3px solid #DC2626; border-radius: 0 8px 8px 0; padding: 0.5rem 0.8rem; font-size: 0.82rem; color: #991B1B; font-weight: 600; }
.accion-normal  { font-size: 0.82rem; color: #334155; }

/* Traspaso card */
.traspaso-card {
    background: white; border: 1px solid #E2E8F0; border-radius: 12px;
    padding: 1rem 1.25rem; margin-bottom: 10px;
    display: flex; align-items: center; gap: 1rem;
}
.t-zona  { font-size: 0.7rem; color: #64748B; font-weight: 600; text-transform: uppercase; letter-spacing:.05em; margin-bottom: 2px; }
.t-sku   { font-size: 0.9rem; font-weight: 600; color: #0F172A; }
.t-arrow { color: #64748B; font-size: 1.2rem; }
.t-units { font-size: 1.4rem; font-weight: 700; color: #2563EB; font-family: 'DM Mono', monospace; }
.t-ulabel{ font-size: 0.7rem; color: #64748B; }
</style>
""", unsafe_allow_html=True)

# ── DATOS ─────────────────────────────────────────────────────────
@st.cache_data
def cargar_datos():
    """
    CONEXIÓN REAL → reemplaza este bloque con:
    
    import pyodbc
    conn = pyodbc.connect(
        'DRIVER={ODBC Driver 17 for SQL Server};'
        'SERVER=tu_servidor;DATABASE=tu_cubo;Trusted_Connection=yes;'
    )
    query = \"\"\"
        SELECT zona, edp, tienda, sku, nombre_sku, categoria,
               venta_acum, stock_tienda, stock_bodega, pedido_pendiente
        FROM tu_vista_o_tabla
    \"\"\"
    df = pd.read_sql(query, conn)
    return df
    """
    random.seed(42)
    zonas = {
        "Zona Centro":   [(695,"BATA WOMAN"),(301,"ESTADO SANTIAGO 1"),(308,"IRARRAZAVAL"),(309,"PORTAL ÑUÑOA")],
        "Zona Sur":      [(354,"SAN BERNARDO MALL"),(258,"MAIPU SOC S&S"),(312,"PUENTE ALTO CALLE"),(305,"FLORIDA CENTER")],
        "Zona Oriente":  [(319,"MALL PLAZA TOBALABA"),(341,"SANTIAGO 41 MALL"),(276,"MALL VIVO EL CENTRO")],
        "Zona Poniente": [(352,"ESPACIO URBANO GRAN AV."),(335,"MALL QUILIN"),(348,"MALL EGAÑA")],
    }
    skus = [
        ("SKU-001","Zapato mujer T38","Calzado Dama"),
        ("SKU-002","Bota hombre T42","Calzado Hombre"),
        ("SKU-003","Sandalia infantil","Calzado Niño"),
        ("SKU-004","Zapatilla deportiva","Deportivo"),
        ("SKU-005","Mocasín cuero","Calzado Hombre"),
    ]
    rows = []
    for zona, tiendas in zonas.items():
        for edp, tienda in tiendas:
            for sku_cod, sku_nom, cat in skus:
                venta   = random.randint(0, 14)
                stock_t = random.randint(0, 12)
                stock_b = random.randint(0, 20)
                pedido  = random.choice([True, False, False])
                rows.append({
                    "zona": zona, "edp": edp, "tienda": tienda,
                    "sku": sku_cod, "nombre_sku": sku_nom, "categoria": cat,
                    "venta": venta, "stock_tienda": stock_t,
                    "stock_bodega": stock_b, "pedido": pedido,
                })
    return pd.DataFrame(rows)

SEMANAS    = 18
QUIEBRE_U  = 2
SOBRE_SEM  = 8
VENTA_MIN  = 1

def calcular_alertas(df):
    df = df.copy()
    df["cobertura"] = df.apply(
        lambda r: round(r["stock_tienda"] / r["venta"] * SEMANAS, 1) if r["venta"] > 0 else 999, axis=1
    )
    def alerta(r):
        v, st, sb, p, cob = r["venta"], r["stock_tienda"], r["stock_bodega"], r["pedido"], r["cobertura"]
        if v == 0 and st == 0 and sb == 0: return "SIN MOVIMIENTO", 0
        if v >= VENTA_MIN and st <= QUIEBRE_U and not sb and not p: return "QUIEBRE", 4
        if v >= VENTA_MIN and st <= QUIEBRE_U: return "RIESGO QUIEBRE", 3
        if v < VENTA_MIN and st > 5: return "SOBRESTOCK", 3
        if cob >= SOBRE_SEM: return "SOBRESTOCK", 3
        if cob >= SOBRE_SEM / 2: return "ATENCIÓN", 2
        return "OK", 1
    df[["alerta","prioridad"]] = df.apply(alerta, axis=1, result_type="expand")
    return df

def accion(r):
    a, st, sb, p, v = r["alerta"], r["stock_tienda"], r["stock_bodega"], r["pedido"], r["venta"]
    if a == "QUIEBRE":
        if sb > 0:   return f"Enviar {min(sb,5)} u. desde bodega", False
        elif p:      return "Esperar pedido pendiente", False
        else:        return "⚠ URGENTE: generar OC o traspaso", True
    if a == "RIESGO QUIEBRE":
        return (f"Reponer desde bodega ({sb} u. disp.)" if sb > 0 else "Buscar traspaso en zona"), False
    if a == "SOBRESTOCK":
        return ("Cancelar/pausar pedido pendiente" if p else "Evaluar traspaso a tienda con quiebre"), False
    if a == "ATENCIÓN":
        return "Monitorear próxima semana", False
    return "", False

def traspasos(df):
    result = []
    for (zona, sku, nom), grp in df.groupby(["zona","sku","nombre_sku"]):
        sobre  = grp[grp["alerta"] == "SOBRESTOCK"].copy()
        quiebre = grp[grp["alerta"].isin(["QUIEBRE","RIESGO QUIEBRE"])].copy()
        for _, s_row in sobre.iterrows():
            for _, q_row in quiebre.iterrows():
                exceso = s_row["stock_tienda"] - 3
                necesidad = QUIEBRE_U + 2 - q_row["stock_tienda"]
                unidades = max(1, min(exceso, necesidad, s_row["stock_tienda"]))
                result.append({
                    "zona": zona, "sku": sku, "nombre_sku": nom,
                    "origen": s_row["tienda"], "destino": q_row["tienda"],
                    "unidades": int(unidades),
                    "stock_origen": int(s_row["stock_tienda"]),
                    "stock_destino": int(q_row["stock_tienda"]),
                })
    return pd.DataFrame(result)

# ── CARGA ──────────────────────────────────────────────────────────
df_raw = cargar_datos()
df = calcular_alertas(df_raw)

# ── SIDEBAR ────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 📦 Filtros")
    st.markdown("---")
    zonas_disp = sorted(df["zona"].unique())
    zonas_sel = st.multiselect("Zona", zonas_disp, default=zonas_disp, label_visibility="visible")
    st.markdown(" ")
    skus_disp = sorted(df["sku"].unique())
    skus_sel = st.multiselect("SKU", skus_disp, default=skus_disp)
    st.markdown(" ")
    alertas_disp = ["QUIEBRE","RIESGO QUIEBRE","SOBRESTOCK","ATENCIÓN","OK","SIN MOVIMIENTO"]
    alertas_sel = st.multiselect("Alerta", alertas_disp, default=alertas_disp)
    st.markdown("---")
    st.markdown("### ⚙️ Umbrales")
    q_u = st.slider("Umbral quiebre (unid.)", 1, 5, QUIEBRE_U)
    s_s = st.slider("Umbral sobrestock (sem.)", 4, 16, SOBRE_SEM)
    sem = st.slider("Semanas del período", 1, 52, SEMANAS)
    if st.button("Recalcular"):
        QUIEBRE_U = q_u; SOBRE_SEM = s_s; SEMANAS = sem
        df = calcular_alertas(df_raw)

# ── FILTRO ─────────────────────────────────────────────────────────
mask = (
    df["zona"].isin(zonas_sel) &
    df["sku"].isin(skus_sel) &
    df["alerta"].isin(alertas_sel)
)
dff = df[mask].copy()

# ── HEADER ─────────────────────────────────────────────────────────
st.markdown(f"""
<div class="app-header">
  <div>
    <p class="app-title">📦 Stock vs Venta — Monitor de alertas</p>
    <p class="app-sub">Semana {SEMANAS} acumulada · {len(dff):,} combinaciones tienda/SKU visibles</p>
  </div>
</div>
""", unsafe_allow_html=True)

# ── KPIs ───────────────────────────────────────────────────────────
cnts = dff["alerta"].value_counts()
def cnt(k): return int(cnts.get(k, 0))

st.markdown(f"""
<div class="kpi-grid">
  <div class="kpi kpi-red">
    <div class="kpi-label">Quiebres</div>
    <div class="kpi-val">{cnt("QUIEBRE")}</div>
  </div>
  <div class="kpi kpi-orange">
    <div class="kpi-label">Riesgo quiebre</div>
    <div class="kpi-val">{cnt("RIESGO QUIEBRE")}</div>
  </div>
  <div class="kpi kpi-amber">
    <div class="kpi-label">Sobrestock</div>
    <div class="kpi-val">{cnt("SOBRESTOCK")}</div>
  </div>
  <div class="kpi kpi-green">
    <div class="kpi-label">OK</div>
    <div class="kpi-val">{cnt("OK")}</div>
  </div>
  <div class="kpi kpi-slate">
    <div class="kpi-label">Sin movimiento</div>
    <div class="kpi-val">{cnt("SIN MOVIMIENTO")}</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── TABS ───────────────────────────────────────────────────────────
tab1, tab2, tab3 = st.tabs(["📊  Dashboard", "🚨  Acciones del día", "🔄  Traspasos sugeridos"])

BADGE = {
    "QUIEBRE":       "badge-quiebre",
    "RIESGO QUIEBRE":"badge-riesgo",
    "SOBRESTOCK":    "badge-sobre",
    "ATENCIÓN":      "badge-atencion",
    "OK":            "badge-ok",
    "SIN MOVIMIENTO":"badge-sin",
}

# TAB 1 — DASHBOARD
with tab1:
    dff_sorted = dff.sort_values(["prioridad","zona","tienda"], ascending=[False,True,True])

    def badge(a): return f'<span class="badge {BADGE.get(a,"")}">{"⬆" if a=="QUIEBRE" else ""} {a}</span>'

    display = dff_sorted[[
        "zona","tienda","nombre_sku","sku","categoria",
        "venta","stock_tienda","stock_bodega","pedido","cobertura","alerta"
    ]].copy()
    display.columns = ["Zona","Tienda","SKU","Cód.","Categoría","Venta","Stock tienda","Stock bodega","Pedido pend.","Cobertura (sem.)","Alerta"]
    display["Pedido pend."] = display["Pedido pend."].map({True:"Sí", False:"No"})
    display["Cobertura (sem.)"] = display["Cobertura (sem.)"].apply(lambda x: "—" if x >= 99 else x)

    def color_alerta(val):
        colores = {
            "QUIEBRE":        "background-color:#FEE2E2;color:#991B1B;font-weight:600",
            "RIESGO QUIEBRE": "background-color:#FFEDD5;color:#9A3412;font-weight:600",
            "SOBRESTOCK":     "background-color:#FEF3C7;color:#92400E;font-weight:600",
            "ATENCIÓN":       "background-color:#FEF9C3;color:#854D0E;font-weight:600",
            "OK":             "background-color:#DCFCE7;color:#166534",
            "SIN MOVIMIENTO": "background-color:#F1F5F9;color:#475569",
        }
        return colores.get(val, "")

    styled = display.style.applymap(color_alerta, subset=["Alerta"])
    st.dataframe(styled, use_container_width=True, hide_index=True, height=520)

# TAB 2 — ACCIONES
with tab2:
    activas = dff[dff["alerta"].isin(["QUIEBRE","RIESGO QUIEBRE","SOBRESTOCK","ATENCIÓN"])].copy()
    activas = activas.sort_values("prioridad", ascending=False)

    if activas.empty:
        st.success("✅ Sin alertas activas para los filtros seleccionados.")
    else:
        cols = st.columns([1.2, 2.5, 1.5, 1, 1, 1, 1, 3])
        for h in ["Zona","Tienda / SKU","Alerta","Venta","St. tienda","St. bodega","Pedido","Acción sugerida"]:
            cols[["Zona","Tienda / SKU","Alerta","Venta","St. tienda","St. bodega","Pedido","Acción sugerida"].index(h)].markdown(
                f"<span style='font-size:0.7rem;font-weight:600;color:#64748B;text-transform:uppercase;letter-spacing:.05em'>{h}</span>",
                unsafe_allow_html=True
            )
        st.markdown("<hr style='margin:4px 0 8px;border-color:#E2E8F0'>", unsafe_allow_html=True)

        for _, r in activas.iterrows():
            accion_txt, urgente = accion(r)
            cols = st.columns([1.2, 2.5, 1.5, 1, 1, 1, 1, 3])
            cols[0].markdown(f"<span style='font-size:0.8rem;color:#334155'>{r['zona']}</span>", unsafe_allow_html=True)
            cols[1].markdown(f"<span style='font-size:0.82rem;font-weight:500;color:#0F172A'>{r['tienda']}</span><br><span style='font-size:0.75rem;color:#64748B'>{r['nombre_sku']}</span>", unsafe_allow_html=True)
            cols[2].markdown(f"<span class='badge {BADGE.get(r[\"alerta\"],\"\")}'>{r['alerta']}</span>", unsafe_allow_html=True)
            cols[3].markdown(f"<span style='font-size:0.9rem;font-family:DM Mono,monospace;color:#0F172A'>{r['venta']}</span>", unsafe_allow_html=True)
            cols[4].markdown(f"<span style='font-size:0.9rem;font-family:DM Mono,monospace;color:#0F172A'>{r['stock_tienda']}</span>", unsafe_allow_html=True)
            cols[5].markdown(f"<span style='font-size:0.9rem;font-family:DM Mono,monospace;color:#0F172A'>{r['stock_bodega']}</span>", unsafe_allow_html=True)
            cols[6].markdown(f"<span style='font-size:0.8rem;color:#0F172A'>{'Sí' if r['pedido'] else 'No'}</span>", unsafe_allow_html=True)
            if urgente:
                cols[7].markdown(f"<div class='accion-urgente'>{accion_txt}</div>", unsafe_allow_html=True)
            else:
                cols[7].markdown(f"<div class='accion-normal'>{accion_txt}</div>", unsafe_allow_html=True)
            st.markdown("<hr style='margin:2px 0;border-color:#F1F5F9'>", unsafe_allow_html=True)

# TAB 3 — TRASPASOS
with tab3:
    df_tr = traspasos(dff)
    if df_tr.empty:
        st.info("No hay traspasos sugeridos para los filtros actuales.")
    else:
        st.markdown(f"**{len(df_tr)} traspasos identificados** dentro de la misma zona — tiendas con sobrestock → tiendas con quiebre del mismo SKU.")
        st.markdown(" ")
        for _, r in df_tr.iterrows():
            st.markdown(f"""
            <div class="traspaso-card">
              <div style="flex:1.2">
                <div class="t-zona">{r['zona']}</div>
                <div class="t-sku">{r['nombre_sku']} <span style="font-size:0.75rem;color:#94A3B8">· {r['sku']}</span></div>
              </div>
              <div style="flex:1.5">
                <div style="font-size:0.7rem;color:#EA580C;font-weight:600;text-transform:uppercase;letter-spacing:.05em">Origen (sobrestock)</div>
                <div style="font-size:0.9rem;font-weight:500;color:#0F172A">{r['origen']}</div>
                <div style="font-size:0.75rem;color:#64748B">{r['stock_origen']} u. en tienda</div>
              </div>
              <div class="t-arrow">→</div>
              <div style="flex:1.5">
                <div style="font-size:0.7rem;color:#DC2626;font-weight:600;text-transform:uppercase;letter-spacing:.05em">Destino (quiebre)</div>
                <div style="font-size:0.9rem;font-weight:500;color:#0F172A">{r['destino']}</div>
                <div style="font-size:0.75rem;color:#64748B">{r['stock_destino']} u. en tienda</div>
              </div>
              <div style="text-align:center;min-width:80px">
                <div class="t-units">{r['unidades']}</div>
                <div class="t-ulabel">unidades a mover</div>
              </div>
            </div>
            """, unsafe_allow_html=True)
