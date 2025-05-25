import streamlit as st
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# === CONFIGURACIÓN DE GOOGLE SHEETS ===
sheet_id = "1S8t3jDiwews5mjjwt1eyt5aDCEQaJjMnHh54feZWic0"
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]

creds = ServiceAccountCredentials.from_json_keyfile_name("credentials.json", scope)
client = gspread.authorize(creds)
sheet = client.open_by_key(sheet_id).sheet1  # Asume que es la primera hoja

# === INTERFAZ DE LA APP ===
st.title("📋 Registro de Actividad Física")

col1, col2, col3 = st.columns(3)
with col1:
    calorias = st.number_input("🔥 Calorías quemadas", min_value=0, step=10)
with col2:
    actividad = st.text_input("🏃 Actividad (ej. trote)")
with col3:
    duracion = st.number_input("⏱️ Duración (minutos)", min_value=0, step=1)

# === REGISTRO ===
if st.button("Registrar actividad"):
    if calorias > 0 and actividad and duracion > 0:
        fecha = datetime.now().strftime("%Y-%m-%d %H:%M")
        nueva_fila = pd.DataFrame([[fecha, calorias, actividad, duracion]],
                                  columns=["Fecha", "Calorías", "Actividad", "Duración (min)"])

        # Guardar en CSV local
        try:
            historial = pd.read_csv("registro_calorias.csv")
            historial = pd.concat([historial, nueva_fila], ignore_index=True)
        except FileNotFoundError:
            historial = nueva_fila
        historial.to_csv("registro_calorias.csv", index=False)

        # Guardar en Google Sheets
        try:
            result = sheet.append_row([fecha, calorias, actividad, duracion], value_input_option="USER_ENTERED")
            st.success("✅ Actividad registrada localmente y en Google Sheets.")
        except Exception as e:
            st.error("❌ Error al guardar en Google Sheets.")
            st.exception(e)
    else:
        st.warning("❗Completa todos los campos antes de registrar.")

# === HISTORIAL Y GRÁFICO ===
try:
    historial = pd.read_csv("registro_calorias.csv")
    st.subheader("📜 Historial de Actividades")
    st.dataframe(historial)

    historial['Fecha_solo_dia'] = pd.to_datetime(historial['Fecha']).dt.date
    resumen = historial.groupby('Fecha_solo_dia')['Calorías'].sum().reset_index()

    st.subheader("📊 Calorías por Día")
    fig, ax = plt.subplots()
    ax.bar(resumen['Fecha_solo_dia'], resumen['Calorías'])
    ax.set_xlabel("Fecha")
    ax.set_ylabel("Calorías")
    ax.set_title("Total de calorías por día")
    st.pyplot(fig)

except FileNotFoundError:
    st.info("No hay actividades registradas todavía.")

