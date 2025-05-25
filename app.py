import streamlit as st
import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt

st.title("📋 Registro de Actividad Física")

col1, col2, col3 = st.columns(3)
with col1:
    calorias = st.number_input("🔥 Calorías quemadas", min_value=0, step=10)
with col2:
    actividad = st.text_input("🏃 Actividad (ej. trote)")
with col3:
    duracion = st.number_input("⏱️ Duración (minutos)", min_value=0, step=1)

if st.button("Registrar actividad"):
    if calorias > 0 and actividad and duracion > 0:
        fecha = datetime.now().strftime("%Y-%m-%d %H:%M")
        nueva_fila = pd.DataFrame([[fecha, calorias, actividad, duracion]],
                                  columns=["Fecha", "Calorías", "Actividad", "Duración (min)"])
        try:
            historial = pd.read_csv("registro_calorias.csv")
            historial = pd.concat([historial, nueva_fila], ignore_index=True)
        except FileNotFoundError:
            historial = nueva_fila
        historial.to_csv("registro_calorias.csv", index=False)
        st.success("✅ Actividad registrada localmente.")
    else:
        st.warning("❗Completa todos los campos antes de registrar.")

# Mostrar historial y gráfico
try:
    historial = pd.read_csv("registro_calorias.csv")
    st.subheader("📜 Historial de Actividades")
    st.dataframe(historial)

    # Botón de descarga
    csv = historial.to_csv(index=False).encode("utf-8")
    st.download_button("⬇️ Descargar CSV", csv, "registro_calorias.csv", "text/csv")

    historial['Fecha_solo_dia'] = pd.to_datetime(historial['Fecha']).dt.date
    resumen = historial.groupby('Fecha_solo_dia')['Calorías'].sum().reset_index()

    st.subheader("📊 Calorías por Día")
    fig, ax = plt.subplots()
    ax.bar(resumen['Fecha_solo_dia'], resumen['Calorías'])
    ax.set_xlabel("Fecha")
    ax.set_ylabel("Calorías")
    ax.set_title("Total de calorías por día")
    st.pyplot(fig)

    # === Bloque para eliminar registros ===
    st.subheader("🧹 Eliminar una entrada registrada")

    if not historial.empty:
        opciones = [f"{i}. {row['Fecha']} — {row['Actividad']} — {row['Duración (min)']} min"
                    for i, row in historial.iterrows()]
        seleccion = st.selectbox("Selecciona una fila para eliminar:", options=opciones)
        if st.button("Eliminar selección"):
            index = int(seleccion.split(".")[0])
            historial = historial.drop(index).reset_index(drop=True)
            historial.to_csv("registro_calorias.csv", index=False)
            st.success("✅ Entrada eliminada correctamente.")
            st.experimental_rerun()

except FileNotFoundError:
    st.info("No hay actividades registradas todavía.")

