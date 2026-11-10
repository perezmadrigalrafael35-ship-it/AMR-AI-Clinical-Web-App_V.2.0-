import streamlit as st
import pandas as pd
import joblib
import datetime
import random

# 1. Configurar la página web
st.set_page_config(page_title="AMR-AI Clinical Pipeline", page_icon="🧬", layout="wide")

st.title("🧬 AMR-AI: Clinical Decision Support System")
st.markdown("Sistema de apoyo a la decisión clínica basado en Inteligencia Artificial.")

# 2. Cargar AMBOS modelos (El Cerebro 1 y el Cerebro 2)
try:
    modelo_basico = joblib.load(r"C:\Users\perez\modelo_amr_real.pkl")
    modelo_genomico = joblib.load(r"C:\Users\perez\modelo_genomico.pkl")
except Exception as e:
    st.error(f"Error al cargar los modelos: {e}. Asegúrate de que ambos archivos .pkl estén en la ruta.")
    st.stop()

# 3. Base de datos de antibióticos
ANTIBIOTICOS = {
    "Meropenem": {"familia": "Carbapenémico", "tipo": "último recurso", "evitar_ctex": "Sí (BLEE)", "usar_ctex": "Amikacina", "usar_susceptible": "Meropenem"},
    "Ceftriaxona": {"familia": "Cefalosporina 3ra Gen", "tipo": "común", "evitar_ctex": "Sí (BLEE)", "usar_ctex": "Meropenem", "usar_susceptible": "Ceftriaxona"},
    "Cefotaxima": {"familia": "Cefalosporina 3ra Gen", "tipo": "común", "evitar_ctex": "Sí (BLEE)", "usar_ctex": "Meropenem", "usar_susceptible": "Cefotaxima"},
    "Ceftazidima": {"familia": "Cefalosporina 3ra Gen", "tipo": "común", "evitar_ctex": "Sí (BLEE)", "usar_ctex": "Meropenem", "usar_susceptible": "Ceftazidima"},
    "Ampicilina": {"familia": "Penicilina", "tipo": "primera línea", "evitar_ctex": "Sí", "usar_ctex": "Meropenem/Amikacina", "usar_susceptible": "Ampicilina"},
    "Amoxicilina": {"familia": "Penicilina", "tipo": "primera línea", "evitar_ctex": "Sí", "usar_ctex": "Meropenem/Amikacina", "usar_susceptible": "Amoxicilina"},
    "Amikacina": {"familia": "Aminoglucósido", "tipo": "alternativa", "evitar_ctex": "No", "usar_ctex": "Es la alternativa", "usar_susceptible": "Amikacina"},
    "Gentamicina": {"familia": "Aminoglucósido", "tipo": "alternativa", "evitar_ctex": "No", "usar_ctex": "Es la alternativa", "usar_susceptible": "Gentamicina"},
    "Ciprofloxacino": {"familia": "Fluoroquinolona", "tipo": "común", "evitar_ctex": "No", "usar_ctex": "Es la alternativa", "usar_susceptible": "Ciprofloxacino"},
    "Trimetoprima/Sulfametoxazol": {"familia": "Sulfonamida", "tipo": "primera línea", "evitar_ctex": "No", "usar_ctex": "Es la alternativa", "usar_susceptible": "Trimetoprima/Sulfametoxazol"}
}

# --- BARRA LATERAL: DATOS DEL PACIENTE ---
st.sidebar.header("📋 Registro del Paciente")
nombre = st.sidebar.text_input("Nombre completo del paciente:")
id_paciente = st.sidebar.text_input("ID / Expediente del hospital:")
edad = st.sidebar.number_input("Edad del paciente:", min_value=0, max_value=120, value=45)

st.sidebar.subheader("🧪 Prueba de Sensibilidad")
antibiotico_evaluado = st.sidebar.selectbox("Antibiótico a evaluar:", list(ANTIBIOTICOS.keys()))

st.sidebar.subheader("🔬 Capacidad del Laboratorio")
modo_lab = st.sidebar.radio(
    "¿Qué datos tiene disponibles?",
    ["Básico (Antibiograma/BLEE)", "Avanzado (Secuenciación/Genes)"]
)

st.sidebar.subheader("🧬 Marcadores y Resultados")
if modo_lab == "Básico (Antibiograma/BLEE)":
    st.sidebar.info("Modo Hospital Público MX: Usando pruebas fenotípicas.")
    tiene_blee = st.sidebar.checkbox("Prueba de BLEE Positiva (+)")
    tiene_kpc_fenotipico = st.sidebar.checkbox("Resistente a Carbapenémicos (Antibiograma)")
    tiene_ctex = False
    tiene_kpc = False
else:
    st.sidebar.success("Modo Laboratorio de Alta Especialidad: Usando genómica.")
    tiene_ctex = st.sidebar.checkbox("Gen blaCTX-M (BLEE) detectado")
    tiene_kpc = st.sidebar.checkbox("Gen blaKPC (Carbapenemasa) detectado")
    tiene_blee = tiene_ctex 
    tiene_kpc_fenotipico = tiene_kpc

# --- ÁREA PRINCIPAL ---
col1, col2 = st.columns([2, 1])

with col1:
    st.subheader("Análisis de Laboratorio")
    if st.button("🔬 Ejecutar Diagnóstico IA", type="primary"):
        if not nombre or not id_paciente:
            st.warning("Por favor, ingrese el nombre y el ID del paciente.")
        else:
            st.session_state['analizado'] = True
            st.session_state['datos_paciente'] = {
                "nombre": nombre,
                "id": id_paciente,
                "edad": edad,
                "antibiotico": antibiotico_evaluado,
                "fecha": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "folio": f"AMR-{random.randint(1000, 9999)}"
            }

with col2:
    st.subheader("Información del Sistema")
    st.info("Sistema experto para predicción de resistencia. Evaluando farmacología clínica basada en genómica.")

# --- GENERACIÓN DEL REPORTE CLÍNICO ---
if st.session_state.get('analizado', False):
    st.markdown("---")
    datos = st.session_state['datos_paciente']
    info_ab = ANTIBIOTICOS[datos['antibiotico']]
    
    st.header("📄 Reporte Clínico Automatizado")
    
    with st.container(border=True):
        st.markdown(f"**Folio:** {datos['folio']} | **Fecha de Emisión:** {datos['fecha']}")
        st.markdown(f"**Paciente:** {datos['nombre']} (ID: {datos['id']}) | **Edad:** {datos['edad']} años")
        st.markdown(f"**Antibiótico Evaluado:** {datos['antibiotico']} ({info_ab['familia']})")
        st.divider()
        
        # Lógica de decisión clínica ADAPTATIVA
        if tiene_blee or tiene_kpc or tiene_kpc_fenotipico:
            st.error(f"⚠️ **RESULTADO: CEPA RESISTENTE a {datos['antibiotico']}.**")
            
            if tiene_blee:
                st.markdown(f"**Justificación:** Se ha detectado un mecanismo de **Betalactamasa de Espectro Extendido (BLEE)**.")
                st.markdown(f"❌ **Contraindicado:** Penicilinas y Cefalosporinas de 3ra generación.")
                st.success(f"✅ **Alternativa (Cuadro Básico):** Meropenem o Amikacina.")
            
            if tiene_kpc or tiene_kpc_fenotipico:
                st.markdown(f"**Justificación:** Se ha detectado **resistencia a Carbapenémicos**.")
                st.warning("⚠️ **Alerta de Salud Pública:** Cepa multirresistente.")
                st.success("✅ **Opciones de Tratamiento (Último Recurso):**")
                st.markdown("- **Polimixina B**")
                st.markdown("- **Tigeciclina**")
        
        else:
            # EL SISTEMA DE DOS CEREBROS
            if modo_lab == "Básico (Antibiograma/BLEE)":
                # Cerebro 1 (Datos Fenotípicos)
                paciente = {'Genome ID': 562, 'Laboratory Typing Method': 'Disk diffusion'}
                df_paciente = pd.DataFrame([paciente])
                df_dummies = pd.get_dummies(df_paciente)
                for col in modelo_basico.feature_names_in_:
                    if col not in df_dummies.columns:
                        df_dummies[col] = 0
                df_final = df_dummies[modelo_basico.feature_names_in_]
                prediccion = modelo_basico.predict(df_final)[0]
                
                if prediccion == 1:
                    st.warning(f"⚠️ **RESULTADO: CEPA RESISTENTE (Predicción IA Fenotípica).**")
                    st.success(f"✅ **Tratamiento sugerido:** {info_ab['usar_ctex']}")
                else:
                    st.success(f"✅ **RESULTADO: CEPA SUSCEPTIBLE.**")
                    st.info(f"💡 **Tratamiento sugerido:** {info_ab['usar_susceptible']}")
            
            else:
                # Cerebro 2 (Datos Genómicos)
                st.info("🧬 Analizando perfil genómico con el Cerebro 2 (Modo Avanzado)...")
                
                genes_paciente = {
                    'gene_CTX-M-15': 1 if tiene_ctex else 0,
                    'gene_KPC-1': 1 if tiene_kpc else 0,
                }
                
                df_gen = pd.DataFrame([genes_paciente])
                for col in modelo_genomico.feature_names_in_:
                    if col not in df_gen.columns:
                        df_gen[col] = 0
                
                df_gen_final = df_gen[modelo_genomico.feature_names_in_]
                prediccion_gen = modelo_genomico.predict(df_gen_final)[0]
                
                if prediccion_gen == 1:
                    st.warning(f"⚠️ **RESULTADO: CEPA RESISTENTE (Predicción IA Genómica).**")
                    st.success(f"✅ **Tratamiento sugerido:** {info_ab['usar_ctex']}")
                else:
                    st.success(f"✅ **RESULTADO: CEPA SUSCEPTIBLE (Predicción IA Genómica).**")
                    st.info(f"💡 **Tratamiento sugerido:** {info_ab['usar_susceptible']}")
        
        st.divider()
        st.caption("Firma del responsable: ___________________________ (Validación médica requerida)")
        st.caption("Este es un reporte generado por IA y no sustituye el juicio clínico de un profesional de la salud.")