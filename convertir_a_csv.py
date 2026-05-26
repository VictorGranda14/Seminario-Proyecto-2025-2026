import pandas as pd

def convertir():
    ruta_excel = "data/processed/Comentarios_en_Final.xlsx"
    ruta_csv = "data/processed/Comentarios_en_Final.csv"
    
    print(f"⏳ Cargando Excel a la memoria (esto puede tomar un momento)...")
    try:
        df = pd.read_excel(ruta_excel)
    except FileNotFoundError:
        print(f"❌ No se encontró el archivo en {ruta_excel}")
        return
        
    print(f"🔄 Convirtiendo {len(df)} filas a CSV...")
    # Usamos punto y coma (;) como separador para que las comas del texto en inglés no rompan las columnas
    df.to_csv(ruta_csv, index=False, sep=';', encoding='utf-8-sig')
    
    print(f"✅ ¡Conversión exitosa! Archivo guardado en {ruta_csv}")

if __name__ == "__main__":
    convertir()