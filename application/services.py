# --- application/services.py ---
from domain.audio_analysis import AudioAnalyzer, AudioAnalysisResult
import sqlite3
from typing import Optional
from utils.logger import logger


class AudioAnalysisService:
    def __init__(self, analyzer: AudioAnalyzer):
        self.analyzer = analyzer
        self.db_path = "DB_Phonia.db"
        self._initialize_database()

    def _initialize_database(self):
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute("""
                            CREATE TABLE IF NOT EXISTS ANALISE (
                                id INTEGER PRIMARY KEY AUTOINCREMENT,
                                user_id INTEGER,
                                localJitter REAL,
                                localabsoluteJitter REAL,
                                rapJitter REAL,
                                ppq5Jitter REAL,
                                ddpJitter REAL,
                                localShimmer REAL,
                                localdbShimmer REAL,
                                apq3Shimmer REAL,
                                apq5Shimmer REAL,
                                apq11Shimmer REAL,
                                ddaShimmer REAL,
                                fundamental_frequency REAL,
                                hnr REAL,
                                FOREIGN KEY (user_id) REFERENCES users(id)
                            )
                        """)
            conn.commit()
            conn.close()
            logger.info("Tabela 'ANALISE' verificada/criada.")
        except Exception as e:
            logger.error(f"Erro ao inicializar DB: {e}")
            raise
        finally:
            conn.close()

    def analyze_audio_file(self, file_path: str) -> AudioAnalysisResult:
        logger.info(f"Analisando áudio: {file_path}")
        result = self.analyzer.analyze(file_path)
        self._save_to_database(result)
        logger.info("Análise concluída com sucesso.")
        return result

    def _save_to_database(self, result: AudioAnalysisResult, user_id: Optional[int] = None):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO ANALISE (user_id, localJitter, localabsoluteJitter, rapJitter, 
            ppq5Jitter, ddpJitter, localShimmer, localdbShimmer, apq3Shimmer, apq5Shimmer, 
            apq11Shimmer, ddaShimmer, fundamental_frequency, hnr)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            user_id,
            result.localJitter,
            result.localabsoluteJitter,
            result.rapJitter,
            result.ppq5Jitter,
            result.ddpJitter,
            result.localShimmer,
            result.localdbShimmer,
            result.apq3Shimmer,
            result.apq5Shimmer,
            result.apq11Shimmer,
            result.ddaShimmer,
            result.fundamental_frequency,
            result.hnr
        ))
        conn.commit()
        conn.close()

    def save_user_info(self, user_data: dict) -> int:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS USUARIO (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT,
                email TEXT,
                problem TEXT,
                trata TEXT,
                age TEXT,
                occupation TEXT,
                voz_trabalho TEXT,
                pais TEXT
            )
        """)
        cursor.execute("""
            INSERT INTO USUARIO (username, email, problem, trata, age, occupation, voz_trabalho, pais)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                    user_data.get("username"),
                    user_data.get("email"),
                    user_data.get("problem"),
                    user_data.get("trata"),
                    user_data.get("age"),
                    user_data.get("occupation"),
                    user_data.get("voz_trabalho"),
                    user_data.get("pais")
                ))
        user_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return user_id
