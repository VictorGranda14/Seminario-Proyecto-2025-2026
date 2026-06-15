import pandas as pd

def fusionar_rubros(ruta_dataset: str, ruta_mapeo: str):
    print("Cargando archivos para el cruce...")
    
    # 1. Cargar ambos CSV
    df_principal = pd.read_csv(ruta_dataset)
    # Utilizamos una expresión regular (Regex) para separar las columnas 
    # tomando en cuenta ÚNICAMENTE la última coma de cada línea.
    df_mapeo = pd.read_csv(ruta_mapeo, sep=r',(?!.*,)', engine='python')
    
    # 2. Realizar el Left Join usando 'attraction_name' como llave
    df_cruzado = pd.merge(df_principal, df_mapeo, on='attraction_name', how='left')
    
    # 3. Reemplazar la columna temporal 'rubro' (que decía "Por definir") 
    # por el valor real del catálogo. Si no hay cruce, asigna "Otros".
    df_cruzado['rubro'] = df_cruzado['rubro_oficial'].fillna('Otros')
    
    # 4. Eliminar la columna 'rubro_oficial' sobrante para mantener la estructura limpia
    df_cruzado = df_cruzado.drop(columns=['rubro_oficial'])
    
    # 5. Sobrescribir el CSV principal
    df_cruzado.to_csv(ruta_dataset, index=False, encoding='utf-8')
    
    # Resumen de validación
    total_asignados = df_cruzado['rubro'].notna().sum()
    sin_asignar = (df_cruzado['rubro'] == 'Otros').sum()
    
    print("-" * 30)
    print("Fusión completada con éxito.")
    print(f"Reseñas con rubro asignado: {total_asignados - sin_asignar}")
    print(f"Reseñas sin mapeo (marcadas como 'Otros'): {sin_asignar}")
    print(f"Archivo actualizado: {ruta_dataset}")
    print("-" * 30)

if __name__ == "__main__":
    # Ajusta las rutas según donde hayas guardado tu catálogo
    ruta_csv_filtrado = "C:\\Users\\ramiro\\Seminario-Proyecto-2025-2026\\backend\\data\\processed\\Comentarios_Final.csv"
    ruta_catalogo = "C:\\Users\\ramiro\\Seminario-Proyecto-2025-2026\\backend\\data\\mapeo_rubros.csv"
    
    fusionar_rubros(ruta_csv_filtrado, ruta_catalogo)