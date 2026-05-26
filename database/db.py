import sqlite3
from datetime import datetime


class Database:
    """Maneja la base de datos SQLite para guardar análisis."""

    def __init__(self, db_name="fps_analyzer.db"):
        self.db_name = db_name
        self.conn = sqlite3.connect(db_name)
        self.create_tables()

    def create_tables(self):
        """Crea las tablas necesarias."""
        
        cursor = self.conn.cursor()

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS analyses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            video_name TEXT NOT NULL,
            fps REAL,
            duration REAL,
            avg_motion REAL,
            max_motion REAL,
            stability REAL,
            flicks INTEGER,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """)

        self.conn.commit()

    def save_analysis(self, data, video_name):
        """Guarda un análisis en la base de datos."""
        
        cursor = self.conn.cursor()

        cursor.execute("""
        INSERT INTO analyses
        (
            video_name,
            fps,
            duration,
            avg_motion,
            max_motion,
            stability,
            flicks
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            video_name,
            data["fps"],
            data["duration"],
            data["avg_motion"],
            data["max_motion"],
            data["stability"],
            data["flicks"]
        ))

        self.conn.commit()

    def get_all_analyses(self):
        """Obtiene todos los análisis guardados."""
        
        cursor = self.conn.cursor()

        cursor.execute("""
        SELECT *
        FROM analyses
        ORDER BY created_at DESC
        """)

        return cursor.fetchall()

    def delete_analysis(self, analysis_id):
        """Elimina un análisis por ID."""
        
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM analyses WHERE id = ?", (analysis_id,))
        self.conn.commit()

    def close(self):
        """Cierra la conexión con la base de datos."""
        self.conn.close()
