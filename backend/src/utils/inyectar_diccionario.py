import sqlite3
import pandas as pd

def inyectar_mapeo_local(ruta_db, ruta_csv):
    print("1. Cargando el diccionario desde el CSV...")
    df_mapeo = pd.read_csv(ruta_csv)
    
    conexion = sqlite3.connect(ruta_db)
    cursor = conexion.cursor()
    
    print("2. Creando tabla temporal en memoria...")
    df_mapeo.to_sql('tabla_temp_mapeo', conexion, if_exists='replace', index=False)
    
    print("3. Creando índices de aceleración (esto evita el cuello de botella)...")
    # Al crear estos índices, convertimos una búsqueda secuencial (lenta) en una búsqueda binaria (instantánea)
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_temp_aspecto ON tabla_temp_mapeo(aspecto_detectado);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_crudo_aspecto ON analisis_crudo(aspecto_detectado);")
    
    print("4. Inyectando categorías a la base principal (esto tomará solo unos segundos)...")
    # Utilizamos la sintaxis UPDATE FROM que es inmensamente más rápida
    cursor.execute("""
        UPDATE analisis_crudo
        SET 
            aspecto_consolidado = tabla_temp_mapeo.aspecto_consolidado,
            categoria_oficial = tabla_temp_mapeo.categoria_oficial
        FROM tabla_temp_mapeo
        WHERE analisis_crudo.aspecto_detectado = tabla_temp_mapeo.aspecto_detectado;
    """)
    
    filas_afectadas = cursor.rowcount
    conexion.commit()
    
    print("5. Limpiando archivos temporales...")
    cursor.execute("DROP TABLE tabla_temp_mapeo")
    cursor.execute("DROP INDEX IF EXISTS idx_crudo_aspecto")
    conexion.close()
    
    print("=====================================================")
    print(f"¡Éxito! Se actualizaron {filas_afectadas} filas instantáneamente.")
    print("=====================================================")

if __name__ == "__main__":
    # Asegúrate de que las rutas estén correctas
    base_de_datos = r"C:\Users\ramiro\Seminario-Proyecto-2025-2026\backend\data\turismo.sqlite"
    archivo_csv = r"C:\Users\ramiro\Seminario-Proyecto-2025-2026\backend\data\diccionario_mapeo_llm.csv"
    
    inyectar_mapeo_local(base_de_datos, archivo_csv)