# --- application/services.py ---
from domain.audio_analysis import AudioAnalyzer, AudioAnalysisResult
import sqlite3
from typing import Optional
from utils.logger import logger
from datetime import datetime


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
                                timestamp TEXT,
                                audio_original BLOB,
                                audio_analisado BLOB,
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
        # self._save_to_database(result)
        logger.info("Análise concluída com sucesso.")
        return result

    def _save_to_database(self, result: AudioAnalysisResult, user_id: Optional[int] = None):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Carregar os arquivos binários
        with open(result.original_path, "rb") as f:
            original_blob = f.read()

        with open(result.analyzed_path, "rb") as f:
            analyzed_blob = f.read()

            timestamp = datetime.now().isoformat()

        cursor.execute("""
            INSERT INTO ANALISE (user_id, localJitter, localabsoluteJitter, rapJitter, 
            ppq5Jitter, ddpJitter, localShimmer, localdbShimmer, apq3Shimmer, apq5Shimmer, 
            apq11Shimmer, ddaShimmer, fundamental_frequency, hnr, timestamp, audio_original, audio_analisado)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
            result.hnr,
            timestamp,
            original_blob,
            analyzed_blob
        ))
        conn.commit()
        conn.close()
        logger.info(f"🧠 Análise salva com timestamp {timestamp}")

    def save_user_info(self, user_data: dict) -> int:
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS USUARIO (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT,
                email TEXT, 
                age TEXT,
                gender TEXT,
                native_language TEXT,
                country_origin TEXT,
                education_level TEXT,
                resp_condition TEXT,
                resp_condition_details TEXT,
                voice_discomfort TEXT,
                voice_discomfort_details TEXT,
                speech_therapy TEXT,
                diagnosed_vocal_problem TEXT,
                diagnosed_vocal_problem_details TEXT,
                hormonal_medication TEXT,
                hormonal_medication_details TEXT,
                smoking TEXT,
                smoking_years TEXT,
                alcohol TEXT,
                occupation TEXT,
                voice_use_intense TEXT,
                singing TEXT,
                singing_frequency TEXT,
                daily_speaking_time TEXT
            )
        """)
        cursor.execute("""
            INSERT INTO USUARIO (username, email, age, gender, native_language, country_origin, education_level, resp_condition, resp_condition_details, voice_discomfort, voice_discomfort_details, speech_therapy, diagnosed_vocal_problem, diagnosed_vocal_problem_details, hormonal_medication, hormonal_medication_details, smoking, smoking_years, alcohol, occupation, voice_use_intense, singing, singing_frequency, daily_speaking_time)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                    user_data.get("username"),
                    user_data.get("email"),
                    user_data.get("age"),
                    user_data.get("gender"),
                    user_data.get("native_language"),
                    user_data.get("country_origin"),
                    user_data.get("education_level"),
                    user_data.get("resp_condition"),
                    user_data.get("resp_condition_details"),
                    user_data.get("voice_discomfort"),
                    user_data.get("voice_discomfort_details"),
                    user_data.get("speech_therapy"),
                    user_data.get("diagnosed_vocal_problem"),
                    user_data.get("diagnosed_vocal_problem_details"),
                    user_data.get("hormonal_medication"),
                    user_data.get("hormonal_medication_details"),
                    user_data.get("smoking"),
                    user_data.get("smoking_years"),
                    user_data.get("alcohol"),
                    user_data.get("occupation"),
                    user_data.get("voice_use_intense"),
                    user_data.get("singing"),
                    user_data.get("singing_frequency"),
                    user_data.get("daily_speaking_time")
                ))
        user_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return user_id
