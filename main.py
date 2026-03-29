import pandas as pd
from src.models.aspect_miner import AspectMinerLocal
from src.utils.database import DBManager

# --- CONFIGURACIÓN DE EJECUCIÓN ---
# Si quieres procesar todo, déjalo como None.
# Si quieres procesar una atracción específica, pon su nombre exacto, ej: "Viña Santa Rita"
ATRACCION_OBJETIVO = "Viña Santa Rita" 

def main():
    print("Iniciando Orquestador Principal...")
    
    # 1. Cargar datos limpios
    data_path = "data/processed/Dataset_Limpio_Final.csv"
    try:
        df = pd.read_csv(data_path, sep=';') 
    except FileNotFoundError:
        print(f"No se encontró el dataset en {data_path}.")
        return

    # 2. Aplicar filtro de atracción (si está configurado)
    if ATRACCION_OBJETIVO:
        df = df[df['attraction_name'] == ATRACCION_OBJETIVO].copy()
        print(f"Modo Filtrado: Procesando solo '{ATRACCION_OBJETIVO}' ({len(df)} comentarios).")
    else:
        print(f"Modo Masivo: Procesando TODO el dataset ({len(df)} comentarios).")

    # 3. Inicializar Base de Datos y revisar progreso
    db = DBManager()
    procesados = db.get_processed_ids()
    
    # Descartar los comentarios que ya están en SQLite
    df_a_procesar = df[~df['Comment_ID'].isin(procesados)]
    print(f"Comentarios pendientes en esta ejecución: {len(df_a_procesar)}")

    if len(df_a_procesar) == 0:
        print("No hay comentarios nuevos por procesar.")
        return

    # 4. Inicializar el Minero de Aspectos (PyABSA)
    miner = AspectMinerLocal()

    # 5. Bucle de procesamiento
    print("Extrayendo aspectos y opiniones...")
    for index, row in df_a_procesar.iterrows():
        c_id = row['Comment_ID']
        attraction = row['attraction_name']
        text = str(row['review_text'])

        if text.strip() == "" or text.lower() == "nan":
            continue

        aspectos = miner.extract_aspects(text)
        db.save_aspects(c_id, attraction, aspectos)

        # Contador cada 50 comentarios
        if (index + 1) % 50 == 0:
            print(f"Procesados {index + 1} comentarios...")

    print("Procesamiento finalizado.")

if __name__ == "__main__":
    main()