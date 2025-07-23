import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import scipy.stats as stats
from PIL import Image
import base64


#clave
clave = st.text_input("Ingresa  clave de acceso:", type="password")
if clave != "lourdeswalls":
    st.warning("Clave incorrecta.")
    st.stop()

st.markdown(
    """
    <div style='text-align: right;'>
        <img src='https://raw.githubusercontent.com/lorepaty1313/percentilesAI-ADR/main/logobueno.jpg' width='200'>
    </div>
    """,
    unsafe_allow_html=True
)


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

def plot_percentile_curve(sexo, medida, edad_obs, valor_obs, nombre=""):
    edades = np.linspace(0, 14, 120)
    percentiles = [1, 3, 10, 25, 50, 75, 90, 97, 99]
    z_scores = [stats.norm.ppf(p / 100) for p in percentiles]
    curves = {p: [] for p in percentiles}

    for edad in edades:
        L, M, S = lms_parameters(sexo, medida, edad)
        for p, z in zip(percentiles, z_scores):
            valor = calculate_percentile_valor(L, M, S, z)
            curves[p].append(valor)

    # Colores según sexo
    if sexo.lower() == "femenino": 
        color_normal = "#ffffff"      # Blanco
        color_vigilancia = "#f8bbd0"  # rosa claro
        color_critico = "#c2185b"     # rosa fuerte
        line_color = "#880e4f"
    else:
        color_normal = "#ffffff"      # blanco
        color_vigilancia = "#bbdefb"  # azul claro
        color_critico = "#1976d2"     # azul fuerte
        line_color = "#0d47a1"

    fig, ax = plt.subplots(figsize=(10, 6))

    # Sombrear zonas por riesgo
    ax.fill_between(edades, curves[1], curves[50], color=color_normal, alpha=0.4, label="0–50: Normal")
    ax.fill_between(edades, curves[50], curves[90], color=color_vigilancia, alpha=0.4, label="50–90: Vigilancia")
    ax.fill_between(edades, curves[90], curves[99], color=color_critico, alpha=0.4, label="90–99: Crítico")

    # Dibujar curvas
    for p in percentiles:
        ax.plot(edades, curves[p], color=line_color, alpha=0.6, linewidth=1)

    # Punto observado
    ax.scatter(edad_obs, valor_obs, color='red', zorder=5)

    # Etiqueta con nombre
    if nombre:
        ax.annotate(nombre, (edad_obs, valor_obs),
                    textcoords="offset points", xytext=(0,10),
                    ha='center', fontsize=10, color='black', fontweight='bold')
    else:
        ax.annotate("Valor observado", (edad_obs, valor_obs),
                    textcoords="offset points", xytext=(0,10),
                    ha='center', fontsize=10, color='black')

    ax.set_title(f'{medida.upper()} - Curvas percentiles ({sexo.capitalize()})')
    ax.set_xlabel("Edad (años)")
    ax.set_ylabel(f"{medida.upper()} valor")
    ax.set_xticks(np.arange(0, 15, 1))
    ax.legend()
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
nombre = st.text_input("ID Paciente", "")
valor = st.number_input("Valor observado", min_value=0.0, format="%.2f", value=20.0)

if st.button("Calcular"):
    try:
        L, M, S = lms_parameters(sexo, medida, edad)
        z = calculate_z_score(valor, L, M, S)
        percentile = z_to_percentile(z)

        st.success(f"Edad: {edad:.2f} años")
        st.success(f"Z-score: {z:.2f}")
        st.success(f"Percentil estimado: {percentile:.2f}")

        fig = plot_percentile_curve(sexo, medida, edad, valor, nombre)
        st.pyplot(fig)

    except Exception as e:
        st.error(f"Ocurrió un error: {e}")

if st.button("Calcular"):
    try:
        L, M, S = lms_parameters(sexo, medida, edad)
        z = calculate_z_score(valor, L, M, S)
        percentile = z_to_percentile(z)

        st.success(f"Edad: {edad:.2f} años")
        st.success(f"Z-score: {z:.2f}")
        st.success(f"Percentil estimado: {percentile:.2f}")

        fig = plot_percentile_curve(sexo, medida, edad, valor, nombre)
        st.pyplot(fig)

    st.markdown("---")  

st.markdown(
    """
    **Referencia:**

    Novais EN, Pan Z, Autruong PT, Meyers ML, Chang FM.  
    *Normal Percentile Reference Curves and Correlation of Acetabular Index and Acetabular Depth Ratio in Children.*  
    J Pediatr Orthop. 2018 Mar;38(3):163–169.  
    doi: [10.1097/BPO.0000000000000791](https://doi.org/10.1097/BPO.0000000000000791)  
    PMID: [27261963](https://pubmed.ncbi.nlm.nih.gov/27261963/)
    """,
    unsafe_allow_html=True
)
    except Exception as e:
        st.error(f"Ocurrió un error: {e}")
