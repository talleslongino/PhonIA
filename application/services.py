# --- application/services.py ---
from domain.audio_analysis import AudioAnalyzer, AudioAnalysisResult
import sqlite3

class AudioAnalysisService:
    def __init__(self, analyzer: AudioAnalyzer):
        self.analyzer = analyzer
        self.db_path = "DB_Phonia.db"
        self._initialize_database()

    def _initialize_database(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS analysis (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                jitter REAL,
                shimmer REAL,
                fundamental_frequency REAL
            )
        """)
        conn.commit()
        conn.close()

    def analyze_audio_file(self, file_path: str) -> AudioAnalysisResult:
        result = self.analyzer.analyze(file_path)
        self._save_to_database(result)
        return result

    def _save_to_database(self, result: AudioAnalysisResult):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO analysis (jitter, shimmer, fundamental_frequency)
            VALUES (?, ?, ?)
        """, (result.jitter, result.shimmer, result.fundamental_frequency))
        conn.commit()
        conn.close()
