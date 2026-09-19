import streamlit as st
import pandas as pd

st.set_page_config(page_title="Gini Corrientes - Grupo 5", page_icon="📊", layout="wide")

GINI_2024 = 0.3305706743
GINI_2025 = 0.3358053924

deciles = list(range(1, 11))

ingreso_decil = {
    "Decil": deciles,
    "T4 2024": [101658, 113679, 137718, 173784, 221865, 281967, 354093, 438240, 534405, 642591],
    "T4 2025": [147776, 166090, 202725, 257674, 330944, 422523, 532426, 660640, 807178, 972022],
}
df_ingresos = pd.DataFrame(ingreso_decil).set_index("Decil")

lorenz = {
    "Decil": [0] + deciles,
    "T4 2024": [0.000000, 0.033886, 0.071779, 0.117685, 0.175613, 0.249568, 0.343557, 0.461588, 0.607668, 0.785803, 1.000000],
    "T4 2025": [0.000000, 0.032839, 0.069748, 0.114798, 0.172059, 0.245602, 0.339496, 0.457813, 0.604622, 0.783995, 1.000000],
    "Igualdad": [0.0] + [i / 10 for i in deciles],
}
df_lorenz = pd.DataFrame(lorenz).set_index("Decil")

def gini_trapezoidal(lorenz_values):
    y = pd.Series(lorenz_values, dtype="float64")
    area = ((y.iloc[:-1].values + y.iloc[1:].values) / 2).sum() / 10
    return 1 - 2 * area

gini_calculado_2024 = gini_trapezoidal(df_lorenz["T4 2024"])
gini_calculado_2025 = gini_trapezoidal(df_lorenz["T4 2025"])

brechas = pd.DataFrame({
    "Indicador": ["Ingreso promedio D10", "Ingreso promedio D1", "Brecha D10 / D1", "Diferencia absoluta D10 - D1", "Brecha D9 / D1"],
    "T4 2024": [df_ingresos.loc[10, "T4 2024"], df_ingresos.loc[1, "T4 2024"], df_ingresos.loc[10, "T4 2024"] / df_ingresos.loc[1, "T4 2024"], df_ingresos.loc[10, "T4 2024"] - df_ingresos.loc[1, "T4 2024"], df_ingresos.loc[9, "T4 2024"] / df_ingresos.loc[1, "T4 2024"]],
    "T4 2025": [df_ingresos.loc[10, "T4 2025"], df_ingresos.loc[1, "T4 2025"], df_ingresos.loc[10, "T4 2025"] / df_ingresos.loc[1, "T4 2025"], df_ingresos.loc[10, "T4 2025"] - df_ingresos.loc[1, "T4 2025"], df_ingresos.loc[9, "T4 2025"] / df_ingresos.loc[1, "T4 2025"]],
})

seccion = st.sidebar.radio("Secciones", ["Resumen general", "Curva de Lorenz", "Ingreso por decil", "Comparación con INDEC", "Metodología"])

st.title("📊 Desigualdad de ingresos — Aglomerado Corrientes")
st.caption("EPH-INDEC · Comparación T4 2024 vs T4 2025")

if seccion == "Resumen general":
    st.header("Resumen general")
    c1, c2, c3 = st.columns(3)
    c1.metric("Gini T4 2024", f"{GINI_2024:.10f}")
    c2.metric("Gini T4 2025", f"{GINI_2025:.10f}")
    c3.metric("Variación del Gini", f"{GINI_2025 - GINI_2024:+.10f}", delta=f"{((GINI_2025 / GINI_2024) - 1) * 100:+.2f}%")
    st.subheader("Brechas entre deciles")
    st.dataframe(brechas.style.format({"T4 2024":"{:,.2f}", "T4 2025":"{:,.2f}"}), use_container_width=True, hide_index=True)
    st.info("El coeficiente de Gini resume la desigualdad de la distribución del ingreso: cuanto más se aproxima a 0, mayor es la igualdad; cuanto más se aproxima a 1, mayor es la concentración.")

elif seccion == "Curva de Lorenz":
    st.header("Curva de Lorenz")
    st.write("Porcentaje acumulado del ingreso según porcentaje acumulado de la población, ordenada por IPCF.")
    st.line_chart(df_lorenz, x_label="Decil poblacional acumulado", y_label="Ingreso acumulado (proporción)")
    st.caption("La línea de igualdad representa el escenario en el que cada proporción de la población recibe exactamente la misma proporción del ingreso.")
    c1, c2 = st.columns(2)
    c1.metric("Gini por fórmula trapezoidal — T4 2024", f"{gini_calculado_2024:.10f}")
    c2.metric("Gini por fórmula trapezoidal — T4 2025", f"{gini_calculado_2025:.10f}")

elif seccion == "Ingreso por decil":
    st.header("Ingreso promedio IPCF por decil")
    st.write("Ingreso promedio de la población de cada decil del aglomerado Corrientes.")
    st.bar_chart(df_ingresos, x_label="Decil", y_label="Ingreso promedio IPCF ($)")
    tabla = df_ingresos.copy()
    tabla.index = [f"D{i}" for i in tabla.index]
    st.dataframe(tabla.style.format("{:,.0f}"), use_container_width=True)

elif seccion == "Comparación con INDEC":
    st.header("Comparación con INDEC")
    comparacion = pd.DataFrame([
        {"Referencia": "Aglomerado Corrientes — cálculo del proyecto", "Período": "T4 2024", "Gini": GINI_2024},
        {"Referencia": "Aglomerado Corrientes — cálculo del proyecto", "Período": "T4 2025", "Gini": GINI_2025},
        {"Referencia": "INDEC — total nacional oficial", "Período": "T4 2024", "Gini": 0.430},
        {"Referencia": "INDEC — total nacional oficial", "Período": "T4 2025", "Gini": 0.427},
        {"Referencia": "Corrientes — EPH Total Urbano", "Período": "2023", "Gini": 0.421},
        {"Referencia": "Corrientes — EPH Total Urbano", "Período": "2025", "Gini": 0.351},
    ])
    st.dataframe(comparacion.style.format({"Gini": "{:.3f}"}), use_container_width=True, hide_index=True)
    st.warning("Advertencia: los valores no son 100% comparables por diferencias de cobertura geográfica y trimestre. El cálculo del proyecto corresponde al aglomerado Corrientes y a T4 de la EPH; el Gini nacional refiere al total nacional y el dato provincial corresponde al informe EPH Total Urbano.")

elif seccion == "Metodología":
    st.header("Metodología")
    st.subheader("Variables")
    st.markdown("- **IPCF:** ingreso per cápita familiar, utilizado para ordenar a la población por nivel de ingreso.\n- **PONDIH:** ponderador de hogares de la EPH.\n- **AGLOMERADO = 12:** filtro utilizado para seleccionar el aglomerado Corrientes.")
    st.subheader("Deciles locales")
    st.write("Los deciles se recalculan localmente para el aglomerado Corrientes en cada período, ordenando la población según IPCF y dividiéndola en diez grupos de igual tamaño poblacional.")
    st.subheader("Fórmula trapezoidal del Gini")
    st.latex("G = 1 - 2A,   A = (1/n) * sum((L(i-1) + L(i)) / 2)")
    st.write("A es el área bajo la curva de Lorenz, n=10 es la cantidad de intervalos y L(i) es el ingreso acumulado hasta el decil i.")

st.sidebar.markdown("---")
st.sidebar.caption("Proyecto Final - Grupo 5: Andrea Celeste Coronel & Gisela Alejandra Romero")
st.markdown("---")
st.caption("Proyecto Final - Grupo 5: Andrea Celeste Coronel & Gisela Alejandra Romero")
