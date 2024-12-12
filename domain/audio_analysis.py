# --- domain/audio_analysis.py ---
from pydantic import BaseModel
import parselmouth
import numpy as np
from scipy.fft import fft, fftfreq


class AudioAnalysisResult(BaseModel):
    jitter: float
    shimmer: float
    fundamental_frequency: float
    frequencies: list
    amplitudes: list

class AudioAnalyzer:
    def analyze(self, audio_path: str) -> AudioAnalysisResult:
        try:
            sound = parselmouth.Sound(audio_path)
            point_process = parselmouth.praat.call(sound, "To PointProcess (periodic, cc)", 75, 500)

            # Updated jitter calculation with correct parameters
            jitter = parselmouth.praat.call(point_process, "Get jitter (local)", 0, 0, 0.0001, 0.02, 1.3)#, 0.0001, 0.02, 0.02, 1.3)

            # Updated shimmer calculation with correct parameters
            shimmer = parselmouth.praat.call([sound, point_process], "Get shimmer (local)", 0, 0, 0.0001, 0.02, 1.3, 1.6)#, 0.0001, 0.02, 0.02, 1.3)

            # Fundamental frequency calculation
            f0 = sound.to_pitch().selected_array["frequency"].mean()

            # FFT calculation
            signal = sound.values[0]  # Get the mono signal
            sampling_rate = sound.sampling_frequency
            n = len(signal)
            yf = fft(signal)
            xf = fftfreq(n, 1 / sampling_rate)

            # Return only positive frequencies
            positive_frequencies = xf[:n // 2]
            amplitudes = 2.0 / n * np.abs(yf[:n // 2])

            return AudioAnalysisResult(
                jitter=jitter,
                shimmer=shimmer,
                fundamental_frequency=f0,
                frequencies=positive_frequencies.tolist(),
                amplitudes=amplitudes.tolist()
            )
        except Exception as e:
            raise ValueError(f"Error analyzing audio: {str(e)}")
