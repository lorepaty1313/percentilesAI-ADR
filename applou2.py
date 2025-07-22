import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as stats

#clave
clave = st.text_input("Ingresa  clave de acceso:", type="password")
if clave != "lourdeswalls":
    st.warning("Clave incorrecta.")
    st.stop()

# original

def lms_parameters(sexo: str, medida: str, edad: float):
    if medida.lower() == "ai":
        if sexo.lower() == "femenino":
            L = 0.279 - 0.029 * edad
            M = 26.289 - 2.415 * edad + 0.188 * edad**2 - 0.008 * edad**3
            S = 0.150 + 0.011 * edad - 0.0006 * edad**2
        else:
            L = 0.834 - 0.028 * edad
            M = 25.297 - 2.721 * edad + 0.201 * edad**2 - 0.006 * edad**3
            S = 0.128 + 0.030 * edad - 0.001 * edad**2
    elif medida.lower() == "adr":
        if sexo.lower() == "femenino":
            L = 1.139 - 0.057 * edad
            M = 14.904 + 3.030 * edad - 0.246 * edad**2 + 0.008 * edad**3
            S = 0.127 - 0.002 * edad
        else:
            L = 1.163 - 0.044 * edad
            M = 15.825 + 2.464 * edad - 0.189 * edad**2 + 0.006 * edad**3
            S = 0.129 - 0.003 * edad
    else:
        raise ValueError("Invalido, indica 'AI' o 'ADR'.")
    return L, M, S

def calculate_z_score(X, L, M, S):
    if L == 0:
        return np.log(X / M) / S
    return ((X / M)**L - 1) / (L * S)

def z_to_percentile(z):
    return stats.norm.cdf(z) * 100

def calculate_percentile_valor(L, M, S, z):
    if L == 0:
        return M * np.exp(S * z)
    return M * (1 + L * S * z) ** (1 / L)

def plot_percentile_curve(sexo, medida, edad_obs, valor_obs):
    edades = np.linspace(0, 14, 100)
    percentiles = [3, 10, 25, 50, 75, 90, 97]
    z_scores = [stats.norm.ppf(p / 100) for p in percentiles]
    curves = {p: [] for p in percentiles}

    for edad in edades:
        L, M, S = lms_parameters(sexo, medida, edad)
        for p, z in zip(percentiles, z_scores):
            valor = calculate_percentile_valor(L, M, S, z)
            curves[p].append(valor)

    fig, ax = plt.subplots(figsize=(10, 6))
    for p in percentiles:
        ax.plot(edades, curves[p], label=f'P{p}')
    
    ax.scatter(edad_obs, valor_obs, color='red', label='Valor observado', zorder=5)
    ax.set_title(f'{medida.upper()} - Curvas percentiles ({sexo.capitalize()})')
    ax.set_xlabel("Edad (años)")
    ax.set_ylabel(f"{medida.upper()} valor")
    ax.legend()
    ax.set_xticks(np.arange(0, 15, 1))
    ax.grid(True)
    return fig

# Pa streamline

st.set_page_config(page_title="Percentiles AI/ADR", layout="centered")
st.title("Calculadora de percentiles AI / ADR")
st.markdown("Selecciona los valores para calcular el percentil y visualizar la curva correspondiente.")

sexo = st.selectbox("Sexo", ["femenino", "masculino"])
medida = st.selectbox("Medida", ["AI", "ADR"])


col1, col2 = st.columns(2)
with col1:
    años = st.number_input("Edad (años)", min_value=0, max_value=14, step=1, value=0)
with col2:
    meses = st.number_input("Edad (meses)", min_value=0, max_value=11, step=1, value=0)

edad = años + (meses / 12)  

valor = st.number_input("Valor observado", min_value=0.0, format="%.2f", value=20.0)

if st.button("Calcular"):
    try:
        L, M, S = lms_parameters(sexo, medida, edad)
        z = calculate_z_score(valor, L, M, S)
        percentile = z_to_percentile(z)

        st.success(f"Edad: {edad:.2f} años")
        st.success(f"Z-score: {z:.2f}")
        st.success(f"Percentil estimado: {percentile:.2f}")

        fig = plot_percentile_curve(sexo, medida, edad, valor)
        st.pyplot(fig)
    except Exception as e:
        st.error(f"Ocurrió un error: {e}")
