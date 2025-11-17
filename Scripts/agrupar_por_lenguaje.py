import os
import pandas as pd

def main():
    print("=== Agrupar registros por idioma ===\n")

    # Pedir ruta del archivo Excel
    ruta_archivo = input("Ingresa la ruta del archivo Excel (por ejemplo: C:\\Users\\TuNombre\\Documentos\\datos.xlsx):\n> ").strip()

    if not os.path.isfile(ruta_archivo):
        print("No se encontró el archivo en la ruta especificada.")
        return

    # Leer archivo
    try:
        df = pd.read_excel(ruta_archivo)
        print(f"\nArchivo cargado correctamente: {os.path.basename(ruta_archivo)}")
    except Exception as e:
        print(f"Error al leer el archivo: {e}")
        return

    # Verificar columna 'language'
    if 'language' not in df.columns:
        print("No se encontró la columna 'language' en el archivo.")
        return

    # Agrupar por idioma
    grupos = df.groupby('language')

    print("\nCantidad de registros por idioma:")
    print(grupos.size())

    # Crear carpeta de salida
    carpeta_salida = "data"
    os.makedirs(carpeta_salida, exist_ok=True)

    # Guardar cada grupo en su archivo Excel
    for idioma, grupo in grupos:
        nombre_salida = os.path.join(carpeta_salida, f"{idioma}_records.xlsx")
        grupo.to_excel(nombre_salida, index=False)
        print(f"Grupo '{idioma}' guardado en: {nombre_salida}")

    print("\nProceso completado con éxito.")

if __name__ == "__main__":
    main()
