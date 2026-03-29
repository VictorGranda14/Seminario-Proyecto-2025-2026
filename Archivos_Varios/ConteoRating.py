import pandas as pd
import os

# --- CONFIGURACIÓN ---
INPUT_FILE = "data/processed/Comentarios_en_Final.xlsx"
ATTRACTION_NAME = "Centro Artesanal Pueblito Los Dominicos" 

def main():
    if not os.path.exists(INPUT_FILE):
        print(f"❌ Error: No se encontró el archivo {INPUT_FILE}")
        return

    print(f"Cargando datos...")
    df = pd.read_excel(INPUT_FILE)

    # 1. Filtrar por atracción
    # Usamos str.lower() para evitar problemas de mayúsculas/minúsculas
    df_attraction = df[df['attraction_name'].str.lower() == ATTRACTION_NAME.lower()]

    if df_attraction.empty:
        print(f"❌ No se encontraron comentarios para la atracción: '{ATTRACTION_NAME}'")
        return

    print(f"✅ Analizando {len(df_attraction)} comentarios para '{ATTRACTION_NAME}'...\n")

    # 2. Clasificar según el Rating (1-5)
    # Criterio: 
    #   Positivo: 3, 4, 5
    #   Negativo: 1, 2
    
    # Filtramos y contamos
    positivos = df_attraction[df_attraction['rating_review'] >= 3]
    negativos = df_attraction[df_attraction['rating_review'] <= 2]

    count_pos = len(positivos)
    count_neg = len(negativos)
    total = count_pos + count_neg

    # 3. Calcular porcentajes
    pct_pos = (count_pos / total * 100) if total > 0 else 0
    pct_neg = (count_neg / total * 100) if total > 0 else 0

    # 4. Mostrar Resultados
    print("--- RESULTADOS BASADOS EN ESTRELLAS (RATING) ---")
    print(f"Total Evaluados: {total}")
    print("-" * 40)
    print(f"👍 Positivos (3-5 estrellas): {count_pos} ({pct_pos:.1f}%)")
    print(f"👎 Negativos (1-2 estrellas): {count_neg} ({pct_neg:.1f}%)")
    print("-" * 40)

if __name__ == "__main__":
    main()