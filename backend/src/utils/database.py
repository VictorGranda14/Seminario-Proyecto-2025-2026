import sqlite3
import os

class DBManager:
    def __init__(self, db_path="data/outputs/resultados_nlp.db"):
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.conn = sqlite3.connect(db_path)
        self._create_tables()

    def _create_tables(self):
        cursor = self.conn.cursor()
        # Tabla para guardar los resultados de PyABSA
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS aspect_results (
                comment_id TEXT,
                attraction_name TEXT,
                aspect TEXT,
                opinion TEXT,
                sentiment TEXT
            )
        ''')
        self.conn.commit()

    def save_aspects(self, comment_id, attraction, aspects_list):
        if not aspects_list: 
            return
            
        cursor = self.conn.cursor()
        for item in aspects_list:
            cursor.execute('''
                INSERT INTO aspect_results (comment_id, attraction_name, aspect, opinion, sentiment)
                VALUES (?, ?, ?, ?, ?)
            ''', (comment_id, attraction, item['aspect'], item['opinion'], item['sentiment']))
        self.conn.commit()

    def get_processed_ids(self):
        """Devuelve un set con los IDs que ya pasaron por el modelo para no repetirlos."""
        cursor = self.conn.cursor()
        cursor.execute('SELECT DISTINCT comment_id FROM aspect_results')
        return {row[0] for row in cursor.fetchall()}