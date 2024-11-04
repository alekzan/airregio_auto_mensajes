import streamlit as st
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials

# Import functions from airregio_mensajes_utilities.py
from airregio_mensajes_utilities import generar_oferta, generar_mensaje

# Access environment variables from Streamlit Secrets
google_sheets_url = st.secrets["GOOGLE_SHEETS_URL_MESSAGES"]

# Load the service account info directly from Streamlit secrets
service_account_info = st.secrets["SERVICE_ACCOUNT_FILE"]

# Authenticate and access Google Sheets
scope = [
    "https://spreadsheets.google.com/feeds",
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]
creds = ServiceAccountCredentials.from_json_keyfile_dict(service_account_info, scope)
client = gspread.authorize(creds)


# Función para cargar las primeras 5 filas (excluyendo el encabezado) de Google Sheets
def load_first_rows():
    # Abrir la hoja de cálculo y seleccionar la primera hoja
    spreadsheet = client.open_by_url(google_sheets_url)
    sheet = spreadsheet.sheet1  # Usar la primera hoja; cambia si es necesario

    # Obtener todos los datos y convertirlos en un DataFrame
    data = sheet.get_all_records()
    df = pd.DataFrame(data).head(5)  # Limitar a las primeras 5 filas
    return df


# NUEVA FUNCIÓN: Actualizar las columnas en Google Sheets
def update_google_sheet(df):
    # Abrir la hoja de cálculo y seleccionar la primera hoja
    spreadsheet = client.open_by_url(google_sheets_url)
    sheet = spreadsheet.sheet1  # Usar la primera hoja; cambia si es necesario

    # Escribir los datos de las columnas "Oferta a realizar" y "Mensaje personalizado" de vuelta a Google Sheets
    # Asumiendo que las columnas comienzan en la columna 10 (columna J) y 11 (columna K)
    # y que los datos comienzan en la fila 2 (después de los encabezados)

    # Obtener las listas de valores de las columnas
    ofertas = df["Oferta a realizar"].tolist()
    mensajes = df["Mensaje personalizado"].tolist()

    # Actualizar las celdas correspondientes en Google Sheets
    for idx, (oferta, mensaje) in enumerate(zip(ofertas, mensajes)):
        row_number = (
            idx + 2
        )  # Agregar 2 porque Google Sheets es 1-indexed y la primera fila es el encabezado
        # Actualizar la columna "Oferta a realizar" (columna J)
        sheet.update_cell(row_number, 10, oferta)
        # Actualizar la columna "Mensaje personalizado" (columna K)
        sheet.update_cell(row_number, 11, mensaje)


def main():
    st.title("Generador de Mensajes para Recompra")

    # Inicializar el estado de la sesión para almacenar el DataFrame
    if "df" not in st.session_state:
        st.session_state.df = None

    # Botón para cargar datos
    if st.button("Cargar Datos de Compradores"):
        df = load_first_rows()
        st.session_state.df = df
        st.write("Datos cargados:")
        st.dataframe(df)

    # Si el DataFrame está cargado, mostrar el botón para generar mensajes
    if st.session_state.df is not None:
        if st.button("Generar mensajes"):
            df = st.session_state.df.copy()
            # Iterar sobre cada fila para generar la oferta y el mensaje personalizado
            for index, row in df.iterrows():
                # Extraer parámetros para generar_oferta
                fecha_de_ultimo_servicio = str(row["Fecha de último servicio"])
                tipo_de_servicio = str(row["Tipo de Servicio"])
                tipo_de_propiedad = str(row["Tipo de Propiedad"])
                estado_de_garantia = str(row["Estado de garantía"])

                # Generar "Oferta a realizar"
                oferta = generar_oferta(
                    fecha_de_ultimo_servicio,
                    tipo_de_servicio,
                    tipo_de_propiedad,
                    estado_de_garantia,
                )

                # Actualizar "Oferta a realizar" en el DataFrame
                df.at[index, "Oferta a realizar"] = oferta

                # Extraer parámetros para generar_mensaje
                nombre = str(row["Nombre del Cliente"])
                fecha_de_ultimo_servicio = str(row["Fecha de último servicio"])

                # Generar "Mensaje personalizado"
                mensaje = generar_mensaje(oferta, nombre, fecha_de_ultimo_servicio)

                # Actualizar "Mensaje personalizado" en el DataFrame
                df.at[index, "Mensaje personalizado"] = mensaje

            # Actualizar el DataFrame en el estado de la sesión
            st.session_state.df = df

            st.write("Datos actualizados con mensajes generados:")
            st.dataframe(df)

            # Actualizar los datos en Google Sheets
            update_google_sheet(df)
            st.success("Los datos han sido actualizados en Google Sheets.")


if __name__ == "__main__":
    main()
