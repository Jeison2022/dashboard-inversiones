import streamlit as st
import pandas as pd
import datetime
import io
import plotly.express as px

st.set_page_config(page_title="Dashboard de Inversiones", layout="wide")
st.title("📊 Dashboard de Inversiones en Acciones")

# Inicializar session_state si no existe
if "data" not in st.session_state:
    st.session_state.data = []

# Formulario de entrada
with st.form("registro_operacion"):
    st.subheader("Agregar operación")
    nombre_empresa = st.text_input("Nombre de la empresa")
    comision = st.number_input("Comisión (COP)", min_value=0.0, step=100.0)
    precio_compra = st.number_input("Precio de compra por acción (COP)", min_value=0.0, step=100.0)
    precio_venta = st.number_input("Precio de venta por acción (COP)", min_value=0.0, step=100.0)
    numero_acciones = st.number_input("Número de acciones", min_value=1, step=1)
    fecha_operacion = st.date_input("Fecha de la operación", value=datetime.date.today())
    submitted = st.form_submit_button("Agregar")

    if submitted:
        ganancia_bruta = (precio_venta - precio_compra) * numero_acciones
        ganancia_neta = ganancia_bruta - comision
        porcentaje_ganancia = (ganancia_neta / (precio_compra * numero_acciones)) * 100 if precio_compra > 0 else 0

        st.session_state.data.append({
            "Fecha": fecha_operacion,
            "Empresa": nombre_empresa,
            "Comisión (COP)": comision,
            "Precio Compra (COP)": precio_compra,
            "Precio Venta (COP)": precio_venta,
            "Acciones": numero_acciones,
            "Ganancia Neta (COP)": ganancia_neta,
            "% Ganancia": porcentaje_ganancia
        })

# Mostrar tabla con filtros
if st.session_state.data:
    df = pd.DataFrame(st.session_state.data)

    st.sidebar.header("Filtros")
    empresas = df["Empresa"].unique()
    empresa_filtrada = st.sidebar.multiselect("Filtrar por empresa", empresas, default=list(empresas))

    fechas = pd.to_datetime(df["Fecha"])
    fecha_min, fecha_max = fechas.min(), fechas.max()
    fecha_rango = st.sidebar.date_input("Filtrar por rango de fechas", [fecha_min, fecha_max])

    df_filtrado = df[
        df["Empresa"].isin(empresa_filtrada) &
        (df["Fecha"] >= pd.to_datetime(fecha_rango[0])) &
        (df["Fecha"] <= pd.to_datetime(fecha_rango[1]))
    ]

    st.subheader("📈 Registro de Operaciones Filtrado")
    st.dataframe(df_filtrado.style.format({
        "Comisión (COP)": "${:,.0f}",
        "Precio Compra (COP)": "${:,.0f}",
        "Precio Venta (COP)": "${:,.0f}",
        "Ganancia Neta (COP)": "${:,.0f}",
        "% Ganancia": "{:.2f}%"
    }))

    # Gráfico de Ganancia Neta por Fecha
    st.subheader("📉 Gráfico de Ganancia Neta por Fecha")
    fig = px.line(df_filtrado, x="Fecha", y="Ganancia Neta (COP)", color="Empresa", markers=True)
    st.plotly_chart(fig, use_container_width=True)

    # Exportar a Excel
    def exportar_excel(dataframe):
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            dataframe.to_excel(writer, index=False, sheet_name='Inversiones')
            workbook = writer.book
            worksheet = writer.sheets['Inversiones']
            worksheet.set_column('A:H', 20)
        return output.getvalue()

    st.download_button(
        label="📅 Exportar a Excel",
        data=exportar_excel(df_filtrado),
        file_name="registro_inversiones.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
else:
    st.info("Agrega tus operaciones para ver el dashboard.")
