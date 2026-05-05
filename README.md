# Stock vs Venta — Monitor de alertas

## Instalación (primera vez)

```bash
pip install -r requirements.txt
```

## Correr la app

```bash
streamlit run app.py
```
Se abre automáticamente en http://localhost:8501

## Conectar al cubo real

En `app.py`, dentro de la función `cargar_datos()`, reemplaza el bloque de datos de ejemplo por:

```python
import pyodbc

conn = pyodbc.connect(
    'DRIVER={ODBC Driver 17 for SQL Server};'
    'SERVER=nombre_de_tu_servidor_as;'
    'DATABASE=nombre_de_tu_cubo;'
    'Trusted_Connection=yes;'
)

query = """
    SELECT
        zona,
        edp,
        nombre_tienda   AS tienda,
        sku,
        nombre_sku,
        categoria,
        venta_acum      AS venta,
        stock_tienda,
        stock_bodega,
        pedido_pendiente AS pedido
    FROM tu_vista_o_tabla
"""
df = pd.read_sql(query, conn)
df["pedido"] = df["pedido"].astype(bool)
return df
```

## Despliegue para el equipo (red interna)

Opción más simple — correr en un PC siempre encendido:

```bash
streamlit run app.py --server.port 8501 --server.address 0.0.0.0
```

Los demás acceden desde el navegador con: `http://IP_DEL_PC:8501`

## Despliegue en Streamlit Community Cloud (gratis, acceso con login)

1. Sube este proyecto a un repositorio GitHub privado
2. Ve a https://streamlit.io/cloud y conecta tu cuenta
3. Despliega el repositorio — la URL queda protegida con login de Google/GitHub
