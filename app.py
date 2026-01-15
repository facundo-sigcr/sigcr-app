import streamlit as st
import pandas as pd

st.set_page_config(page_title="SIGCR", layout="centered")

st.title("SIGCR – Sistema Integral de Gestión de Carteras")

perfil = st.selectbox(
    "Seleccioná tu perfil de inversor:",
    ["Conservador", "Moderado", "Agresivo"]
)

tab1, tab2, tab3, tab4 = st.tabs([
    "📊 Cartera",
    "🇦🇷 Stress Test",
    "🛡️ RA Score",
    "🧠 Explicabilidad"
])

carteras = {
    "Conservador": {
        "TX26": 20, "TX28": 20, "AL30": 15, "GD30": 10,
        "SPY": 10, "Pesos": 15
    },
    "Moderado": {
        "TX26": 10, "TX28": 10, "AL30": 15, "GD30": 10,
        "YPF": 10, "GGAL": 5, "SPY": 15, "QQQ": 10, "Pesos": 5
    },
    "Agresivo": {
        "AL30": 10, "GD30": 10, "YPF": 15, "GGAL": 10, "PAMP": 5,
        "SPY": 20, "QQQ": 15, "EEM": 10, "Pesos": 5
    }
}

shocks = {
    "2001": {"Bonos": -0.7, "Acciones": -0.6, "ETF": 0.2, "Pesos": -0.8},
    "2018": {"Bonos": -0.5, "Acciones": -0.55, "ETF": 0.15, "Pesos": -0.6},
    "2023": {"Bonos": -0.4, "Acciones": -0.45, "ETF": 0.10, "Pesos": -0.5}
}

def tipo_activo(activo):
    if activo in ["TX26", "TX28", "AL30", "GD30"]:
        return "Bonos"
    if activo in ["YPF", "GGAL", "PAMP"]:
        return "Acciones"
    if activo in ["SPY", "QQQ", "EEM"]:
        return "ETF"
    return "Pesos"

data = carteras[perfil]

df = pd.DataFrame({
    "Activo": list(data.keys()),
    "Peso (%)": list(data.values()),
    "Tipo": [tipo_activo(a) for a in data.keys()]
})

# Calculo impactos
impactos = []
for crisis, shock in shocks.items():
    impacto = sum(
        row["Peso (%)"] / 100 * shock[row["Tipo"]]
        for _, row in df.iterrows()
    )
    impactos.append(impacto * 100)

impacto_promedio = sum(impactos) / len(impactos)
ra_score = max(0, round(100 + impacto_promedio))

protectores = df[df["Tipo"].isin(["ETF", "Bonos"])]["Peso (%)"].sum()
riesgosos = df[df["Tipo"].isin(["Acciones", "Pesos"])]["Peso (%)"].sum()

with tab1:
    st.dataframe(df)
    st.bar_chart(df.set_index("Activo")["Peso (%)"])

with tab2:
    df_stress = pd.DataFrame({
        "Crisis": list(shocks.keys()),
        "Impacto (%)": [round(i, 1) for i in impactos]
    })
    st.dataframe(df_stress)
    st.bar_chart(df_stress.set_index("Crisis"))

with tab3:
    st.metric("RA Score", ra_score)

with tab4:
    st.subheader("¿Por qué esta cartera?")
    st.write(f"Activos protectores: **{protectores}%**")
    st.write(f"Activos riesgosos: **{riesgosos}%**")

    if ra_score < 60:
        st.warning("RA bajo: alta exposición a riesgo argentino.")
        st.info("Sugerencia: aumentar ETFs globales o bonos hard dollar.")
    elif ra_score < 75:
        st.info("RA medio: cartera balanceada con riesgo controlado.")
    else:
        st.success("RA alto: buena protección frente a crisis argentinas.")
