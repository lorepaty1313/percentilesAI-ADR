

import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import scipy.stats as stats
from fpdf import FPDF
from io import BytesIO
import os

# --- CONFIGURACIÓN GENERAL ---
st.set_page_config(page_title="Evaluación AI + Imagen", layout="wide")

# --- AUTENTICACIÓN SIMPLE ---
clave = st.text_input("Ingresa  clave de acceso:", type="password")
if clave != "lourdeswalls":
    st.warning("Clave incorrecta.")
    st.stop()

# --- HEADER ---
st.markdown(
    """
    <div style='text-align: right;'>
        <img src='https://raw.githubusercontent.com/lorepaty1313/percentilesAI-ADR/main/logobueno.jpg' width='150'>
    </div>
    """,
    unsafe_allow_html=True
)

# --- PARÁMETROS LMS ---
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
        raise ValueError("Medida inválida: usa 'AI' o 'ADR'")
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

# --- ENTRADA DE DATOS ---

st.markdown("### Subir radiografías opcionales (JPEG, PNG)")

imagenes_subidas = st.file_uploader(
    "Puedes subir una o dos imágenes (radiografías) opcionalmente:",
    type=["jpg", "jpeg", "png"],
    accept_multiple_files=True
)
st.title("Evaluación AI y Curva de Imagen de Referencia")

sexo = st.selectbox("Sexo del paciente", ["femenino", "masculino"])
col1, col2 = st.columns(2)
with col1:
    años = st.number_input("Edad (años)", min_value=0, max_value=14, step=1, value=0)
with col2:
    meses = st.number_input("Edad (meses)", min_value=0, max_value=11, step=1, value=0)

edad = años + (meses / 12)
nombre = st.text_input("ID Paciente", "")

st.markdown("### Valores de referencia")
colN1, colN2 = st.columns(2)
with colN1:
    novais_der = st.number_input("IA-S derecho", min_value=0.0, format="%.2f")
with colN2:
    novais_izq = st.number_input("IA-S izquierdo", min_value=0.0, format="%.2f")
    
colT1, colT2 = st.columns(2)
with colT1:
    tonnis_der = st.number_input("IA-L derecho", min_value=0.0, format="%.2f")
with colT2:
    tonnis_izq = st.number_input("IA-L izquierdo", min_value=0.0, format="%.2f")
# col3, col4 = st.columns(2)
#with col3:
 #   angulo_izq = st.number_input("AI / Ángulo cadera izquierda", min_value=0.0, format="%.2f")
#with col4:
 #   angulo_der = st.number_input("AI / Ángulo cadera derecha", min_value=0.0, format="%.2f")
#fig1 = None
# --- CALCULO Y GRAFICADO ---
generar_segunda = False 
if st.button("Calcular y mostrar gráficas"):
    # Calcular percentiles
    L, M, S = lms_parameters(sexo, "AI", edad)
    z_izq = calculate_z_score(novais_izq, L, M, S)
    z_der = calculate_z_score(novais_der, L, M, S)
    p_izq = z_to_percentile(z_izq)
    p_der = z_to_percentile(z_der)

    st.success(f"AI - Edad: {edad:.2f} años")
    st.success(f"AI izquierda → Z: {z_izq:.2f} | Percentil: {p_izq:.2f}")
    st.success(f"AI derecha → Z: {z_der:.2f} | Percentil: {p_der:.2f}")


    # Gráfica 1: Curva LMS
    edades = np.linspace(0, 14, 120)
    percentiles = [1, 3, 10, 25, 50, 75, 90, 97, 99]
    z_scores = [stats.norm.ppf(p / 100) for p in percentiles]
    curves = {p: [] for p in percentiles}
    for e in edades:
        l, m, s = lms_parameters(sexo, "AI", e)
        for p, z in zip(percentiles, z_scores):
            curves[p].append(calculate_percentile_valor(l, m, s, z))

    color_vigilancia = "#f8bbd0" if sexo == "femenino" else "#bbdefb"
    color_critico = "#c2185b" if sexo == "femenino" else "#1976d2"
    color_linea = "#880e4f" if sexo == "femenino" else "#0d47a1"

    fig1, ax1 = plt.subplots(figsize=(10, 6))
    ax1.fill_between(edades, curves[1], curves[50], color="white", alpha=0.4, label="0–50: Normal")
    ax1.fill_between(edades, curves[50], curves[90], color=color_vigilancia, alpha=0.4, label="50–90: Vigilancia")
    ax1.fill_between(edades, curves[90], curves[99], color=color_critico, alpha=0.4, label="90–99: Crítico")
    for p in percentiles:
        ax1.plot(edades, curves[p], color=color_linea, alpha=0.6, linewidth=1)
    # Puntos de referencia Novais
    ax1.scatter(edad, novais_izq, color='black', marker='o', s=20, zorder=5, label="Izquierda")
    # ax1.annotate("Izq", (edad, novais_izq), textcoords="offset points", xytext=(-20, 12), fontsize=10, color='black')
    ax1.scatter(edad, novais_der, color='black', marker='s', s=20, zorder=5, label="Derecha")
    # ax1.annotate("Der", (edad, novais_der), textcoords="offset points", xytext=(10, 12), fontsize=10, color='black')
    
    ax1.set_title(f'AI - Curvas percentiles valores de Novais et al ({sexo.capitalize()}) - Paciente {nombre}')
    ax1.set_xlabel("Edad (años)")
    ax1.set_ylabel("AI (mm)")
    ax1.grid(True)
    ax1.legend()
    st.pyplot(fig1)

    # Gráfica 2: Imagen de fondo
    img = mpimg.imread("fondo11.png")
    edad_to_x = {
    "0 años 1 meses": 0.0,
    "0 años 2 meses": 0.475,
    "0 años 3 meses": 0.95,
    "0 años 4 meses": 1.405,
    "0 años 5 meses": 1.86,
    "0 años 6 meses": 2.32,
    "0 años 7 meses": 2.78,
    "0 años 8 meses": 3.08,
    "0 años 9 meses": 3.39,
    "0 años 10 meses": 3.7,
    "0 años 11 meses": 4.0066,
    "1 años 0 meses": 4.31,
    "1 años 1 meses": 4.58,
    "1 años 2 meses": 4.8866,
    "1 años 3 meses": 5.1932,
    "1 años 4 meses": 5.4998,
    "1 años 5 meses": 5.8064,
    "1 años 6 meses": 6.113,
    "1 años 7 meses": 6.4196,
    "1 años 8 meses": 6.6163,
    "1 años 9 meses": 6.813,
    "1 años 10 meses": 7.0097,
    "1 años 11 meses": 7.2064,
    "2 años 0 meses": 7.4031,
    "2 años 1 meses": 7.6,
    "2 años 2 meses": 7.7,
    "2 años 3 meses": 7.8,
    "2 años 4 meses": 7.9,
    "2 años 5 meses": 8.0,
    "2 años 6 meses": 8.1,
    "2 años 7 meses": 8.2,
    "2 años 8 meses": 8.3,
    "2 años 9 meses": 8.4,
    "2 años 10 meses": 8.5,
    "2 años 11 meses": 8.6,
    "3 años 0 meses": 8.7,
    "3 años 1 meses": 8.8, #ya
    "3 años 2 meses": (8.8+(.05*1)) ,
    "3 años 3 meses": (8.8+(.05*2)),
    "3 años 4 meses": (8.8+(.05*3)),
    "3 años 5 meses": (8.8+(.05*4)),
    "3 años 6 meses": (8.8+(.05*5)),
    "3 años 7 meses": (8.8+(.05*6)),
    "3 años 8 meses": (8.8+(.05*7)),
    "3 años 9 meses": (8.8+(.05*8)),
    "3 años 10 meses": (8.8+(.05*9)),
    "3 años 11 meses": (8.8+(.05*10)),
    "4 años 0 meses": 9.35, # ya
    "4 años 1 meses": (9.35+(0.05*1)),
    "4 años 2 meses": (9.35+(.05*2)) ,
    "4 años 3 meses": (9.35+(.05*3)),
    "4 años 4 meses": (9.35+(.05*4)),
    "4 años 5 meses": (9.35+(.05*5)),
    "4 años 6 meses": (9.35+(.05*6)),
    "4 años 7 meses": (9.35+(.05*7)),
    "4 años 8 meses": (9.35+(.05*8)),
    "4 años 9 meses": (9.35+(.05*9)),
    "4 años 10 meses": (9.35+(.05*10)),
    "4 años 11 meses": (9.35+(.05*11)),
    "5 años 0 meses": 9.95,
    "5 años 1 meses": 10,
    "5 años 2 meses": 10,
    "5 años 3 meses": 10,
    "5 años 4 meses": 10,
    "5 años 5 meses": 10,
    "5 años 6 meses": 10,
    "5 años 7 meses": 10,
    "5 años 8 meses": 10,
    "5 años 9 meses": 10,
    "5 años 10 meses": 10,
    "5 años 11 meses": 10,
    "6 años 0 meses": 10,
    "6 años 1 meses": 10,
    "6 años 2 meses": 10,
    "6 años 3 meses": 10,
    "6 años 4 meses": 10,
    "6 años 5 meses": 10,
    "6 años 6 meses": 10,
    "6 años 7 meses": 10,
    "6 años 8 meses": 10,
    "6 años 9 meses": 10,
    "6 años 10 meses": 10,
    "5 años 11 meses": 10,
    "7 años 0 meses": 10.0
        
    }
    edad_key = f"{int(años)} años {int(meses)} meses"
    x_val = edad_to_x.get(edad_key, None)
    generar_segunda = x_val is not None  # NUEVA VARIABLE DE CONTROL

    if generar_segunda:
        xticks = [0, .95, 1.86, 2.78, 3.7, 4.58, 5.48, 6.42, 7.6, 8.8, 10]
        etiquetas_xticks = [
            "1 - 2 meses", "3 - 4 meses", "5 - 6 meses", "7 - 9 meses", "10 - 12 meses",
            "1 año 1 mes - 1 año 3 meses", "1 año 4 meses -1 año 6 meses", "1 año 7 meses - 2 años",
            "2 años 1 mes - 3 años", "3 años 1 mes - 5 años", "5 años 1 mes - 7años"
        ]

    fig2, ax2 = plt.subplots(figsize=(22, 10))
    ax2.imshow(img, extent=[0, 10, -2.5, 42], aspect='auto')
    ax2.plot(x_val, tonnis_izq, 'ko', markersize=12)  # azul círculo
    # ax2.text(x_val + 0.2, tonnis_izq + 1.5, color='black', fontsize=14)
    
    # Puntos en la gráfica con labels para la leyenda
    ax2.plot(x_val, tonnis_izq, 'ko', markersize=12, label="Izquierda")  # verde redondo
    ax2.plot(x_val, tonnis_der, 'ks', markersize=12, label="Derecha")    # azul cuadrado
    
    # Ejes y detalles
    ax2.set_xticks(xticks)
    ax2.set_xticklabels(etiquetas_xticks, rotation=45, ha='right', fontsize=14)
    ax2.set_xlim(0, 10)
    ax2.set_ylim(0, 42)
    ax2.set_xlabel("Edad", fontsize=18)
    ax2.set_ylabel("Ángulo acetabular (°)", fontsize=18)
    ax2.set_title(f"Curvas estimadas sobre imagen de referencia (Tönnis et al) - Paciente {nombre}", fontsize=20)
    ax2.grid(True, linestyle='--', alpha=0.5)
    ax2.legend(fontsize=14)
    
    # Mostrar
    st.pyplot(fig2)
else:
    st.warning("No se encontró la edad en el diccionario para graficar sobre imagen.")
try: 
  st.markdown("---")
  st.markdown(
    	"""
         **Referencia:**

    	Novais EN, Pan Z, Autruong PT, Meyers ML, Chang FM.  
    	*Normal Percentile Reference Curves and Correlation of Acetabular Index and Acetabular Depth Ratio in Children.*  
    	J Pediatr Orthop. 2018 Mar;38(3):163–169.  
    	doi: [10.1097/BPO.0000000000000791](https://doi.org/10.1097/BPO.0000000000000791)  
    	PMID: [27261963](https://pubmed.ncbi.nlm.nih.gov/27261963/)

    	*Tönnis D. Normal values of the hip joint for the evaluation of X-rays in children and adults.*  
   	 Clin Orthop Relat Res. 1976;119:39–47
    	""",
   	 unsafe_allow_html=True
)

except Exception as e:
        st.error(f"Ocurrió un error: {e}")



# Guardar las gráficas como imágenes en memoria
from PIL import Image

# Guardar las gráficas como imágenes en memoria solo si se generaron
buf1, buf2 = None, None

if 'fig1' in locals():
    buf1 = BytesIO()
    fig1.savefig(buf1, format="png", bbox_inches='tight')
    buf1.seek(0)

if 'fig2' in locals() and generar_segunda:
    buf2 = BytesIO()
    fig2.savefig(buf2, format="png", bbox_inches='tight')
    buf2.seek(0)

# Crear el PDF con fpdf
# Crear el PDF con fpdf
pdf = FPDF()
pdf.add_page()

# Título
pdf.set_font("Arial", 'B', 13)
pdf.cell(0, 10, f"Evaluación radiográfica de caderas - {nombre}", ln=True)

# Edad
pdf.set_font("Arial", '', 11)
pdf.cell(0, 10, f"Edad: {int(años)} años {int(meses)} meses", ln=True)
pdf.ln(5)

# Valores en dos columnas
pdf.set_font("Arial", 'B', 11)
pdf.cell(0, 10, "Valores de Índice Acetabular:", ln=True)

pdf.set_font("Arial", '', 11)
pdf.cell(95, 10, f"IA-S Derecha: {novais_der:.2f}°", ln=False)
pdf.cell(95, 10, f"IA-S Izquierda: {novais_izq:.2f}°", ln=False)
pdf.cell(95, 10, f"IA-L Derecha: {tonnis_der:.2f}°", ln=True)
pdf.cell(95, 10, f"IA-L Izquierda: {tonnis_izq:.2f}°", ln=True)
pdf.ln(5)

# Insertar primera imagen (fig1)
if buf1:
    img1 = Image.open(buf1)
    img1_path = "/tmp/fig1.png"
    img1.save(img1_path)
    pdf.image(img1_path, x=9, w=130) 
    pdf.ln(5)# Gráfica 1 (Novais)

# Insertar segunda imagen (fig2)
if generar_segunda and buf2:
    img2 = Image.open(buf2)
    img2_path = "/tmp/fig2.png"
    img2.save(img2_path)
    pdf.image(img2_path, x=9, w=130)  # Gráfica 2 (Tönnis)

# Agregar nueva página para radiografías
if imagenes_subidas:
    pdf.add_page()
    pdf.set_font("Arial", 'B', 11)
    pdf.cell(0, 10, "Mediciones Radiográficas:", ln=True)
    for i, archivo in enumerate(imagenes_subidas):
        img_rdg = Image.open(archivo)
        img_path = f"/tmp/radiografia_{i}.png"
        img_rdg.save(img_path)
        pdf.image(img_path, w=130)
        pdf.ln(5)

# Referencias al final
pdf.set_font("Arial", 'B', 9)
pdf.cell(0, 10, "Referencias:", ln=True)
pdf.set_font("Arial", '', 8)
pdf.multi_cell(0, 5,
    "Novais EN, Pan Z, Autruong PT, Meyers ML, Chang FM. "
    "Normal Percentile Reference Curves and Correlation of Acetabular Index and Acetabular Depth Ratio in Children. "
    "J Pediatr Orthop. 2018 Mar;38(3):163-169. doi:10.1097/BPO.0000000000000791\n\n"
    "Tönnis D. Normal values of the hip joint for the evaluation of X-rays in children and adults. "
    "Clin Orthop Relat Res.1976;119:39-47"
)

# Exportar PDF
pdf_output = BytesIO()
pdf_bytes = pdf.output(dest='S').encode('latin1')  # 'S' = return as string
pdf_output = BytesIO(pdf_bytes)
pdf_output.seek(0)

# Botón de descarga
st.download_button(
    label="📥 Descargar PDF",
    data=pdf_output,
    file_name=f"evaluacion_AI_{nombre.replace(' ', '_')}.pdf",
    mime="application/pdf"
)

