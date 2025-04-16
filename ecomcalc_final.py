import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
from io import BytesIO
from fpdf import FPDF
import base64

st.set_page_config(page_title='EcomCalc - Simulador E-commerce', layout='wide')

# Logo y encabezado
st.image("perfil_pato.png", width=180)
st.markdown("<h2 style='text-align: center;'>EcomCalc - Simula. Compara. Invierte con inteligencia.</h2>", unsafe_allow_html=True)

st.sidebar.header("📋 Parámetros del Producto")

# Entradas
precio_venta = st.sidebar.number_input("Precio de venta ($)", value=29990)
costo_producto = st.sidebar.number_input("Costo del producto ($)", value=10000)
envio = st.sidebar.number_input("Costo de envío ($)", value=2000)
comision = st.sidebar.number_input("Comisión plataforma (%)", value=10.0) / 100
publicidad = st.sidebar.number_input("Costo de publicidad ($)", value=5000)
otros_costos = st.sidebar.number_input("Otros costos variables ($)", value=1000)

# Cálculos
comision_valor = precio_venta * comision
costo_total = costo_producto + envio + comision_valor + publicidad + otros_costos
ganancia = precio_venta - costo_total
margen = (ganancia / precio_venta) * 100 if precio_venta != 0 else 0
punto_equilibrio = costo_total / (precio_venta - costo_total) if (precio_venta - costo_total) > 0 else float('inf')

# Evaluación automática
if ganancia < 0:
    evaluacion = "🔴 Este producto genera pérdidas. Revisa tus costos."
elif margen < 15:
    evaluacion = "🟡 Producto con baja rentabilidad. Podrías ajustar precio o reducir costos."
else:
    evaluacion = "🟢 Producto rentable. ¡Puedes escalarlo!"

# Resultados
st.markdown("## 📊 Resultados de la Simulación")
col1, col2, col3 = st.columns(3)
col1.metric("💰 Ganancia por unidad", f"${ganancia:,.0f}")
col2.metric("📈 Margen de utilidad", f"{margen:.2f}%")
col3.metric("⚖️ Punto de equilibrio (aprox. unidades)", f"{round(punto_equilibrio, 1)}" if punto_equilibrio != float('inf') else "No rentable")

# Evaluación tipo semáforo
st.markdown("### 🚦 Evaluación del Producto")
st.info(evaluacion)

# Gráfico de componentes (%)
st.markdown("### 🧮 Distribución de Costos y Ganancia (% del precio de venta)")
componentes = {
    "Costo Producto": costo_producto,
    "Envío": envio,
    "Comisión": comision_valor,
    "Publicidad": publicidad,
    "Otros": otros_costos,
    "Ganancia": ganancia
}
labels = list(componentes.keys())
valores = list(componentes.values())

fig1, ax1 = plt.subplots()
ax1.pie(valores, labels=labels, autopct='%1.1f%%', startangle=140)
ax1.axis('equal')
st.pyplot(fig1)

# Historial de simulaciones
if "historial_ecomcalc" not in st.session_state:
    st.session_state.historial_ecomcalc = []

sim_actual = {
    "Precio Venta": precio_venta,
    "Costo Total": costo_total,
    "Ganancia": ganancia,
    "Margen %": round(margen, 2),
    "Pto. Equilibrio": round(punto_equilibrio, 1) if punto_equilibrio != float('inf') else "No rentable"
}

if sim_actual not in st.session_state.historial_ecomcalc:
    st.session_state.historial_ecomcalc.insert(0, sim_actual)

st.markdown("### 🧾 Historial de Simulaciones (últimas 5)")
for i, h in enumerate(st.session_state.historial_ecomcalc[:5]):
    st.markdown(f"- 💰 Precio: ${h['Precio Venta']} | Ganancia: ${h['Ganancia']:,.0f} | Margen: {h['Margen %']}% | Punto Equilibrio: {h['Pto. Equilibrio']}")

# Exportar Excel
df_export = pd.DataFrame([sim_actual])
excel_buffer = BytesIO()
with pd.ExcelWriter(excel_buffer, engine='xlsxwriter') as writer:
    df_export.to_excel(writer, index=False)

st.download_button(
    label="📊 Descargar Excel",
    data=excel_buffer.getvalue(),
    file_name="simulacion_ecomcalc.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

# Exportar PDF
def generar_pdf():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(200, 10, txt="Reporte EcomCalc - Simulador Ecommerce", ln=True, align='C')
    pdf.ln(10)
    for k, v in sim_actual.items():
        pdf.cell(200, 10, txt=f"{k}: {v}", ln=True)
    pdf.multi_cell(200, 10, txt=f"Evaluación: {evaluacion}")
    return pdf.output(dest="S").encode("latin-1")

if st.button("📄 Descargar PDF"):
    pdf_bytes = generar_pdf()
    b64 = base64.b64encode(pdf_bytes).decode()
    href = f'<a href="data:application/octet-stream;base64,{b64}" download="reporte_ecomcalc.pdf">Haz clic aquí para descargar PDF 📄</a>'
    st.markdown(href, unsafe_allow_html=True)
