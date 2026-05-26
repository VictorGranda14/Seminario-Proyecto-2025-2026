import pandas as pd

def load_data(filepath: str) -> pd.DataFrame:
    """
    Carga datos desde un archivo Excel en un DataFrame de pandas.
    Args:
        filepath (str): La ruta al archivo .xlsx.
    Returns:
        pd.DataFrame: Un DataFrame con los datos cargados, o None si el archivo no se encuentra.
    """
    try:
        df = pd.read_excel(filepath)
        print(f"Datos cargados exitosamente desde {filepath}")
        return df
    except FileNotFoundError:
        print(f"Error: El archivo no se encontró en la ruta '{filepath}'.")
        return None
    except Exception as e:
        print(f"Ocurrió un error inesperado al cargar el archivo: {e}")
        return None

def filter_by_attraction(df: pd.DataFrame, attraction_name: str, column_name: str = "attraction_name") -> pd.DataFrame:
    """
    Filtra un DataFrame para obtener solo los comentarios de una atracción específica.

    Args:
        df (pd.DataFrame): El DataFrame completo.
        attraction_name (str): El nombre de la atracción a filtrar.
        column_name (str, optional): El nombre de la columna que contiene los nombres de las atracciones.

    Returns:
        pd.DataFrame: Un nuevo DataFrame que contiene solo las filas de la atracción especificada.
    """
    print(f"Filtrando por la atracción: '{attraction_name}'...")
    filtered_df = df[df[column_name].str.lower() == attraction_name.lower()].copy()
    return filtered_df