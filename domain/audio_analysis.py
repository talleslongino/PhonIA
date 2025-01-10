# --- domain/audio_analysis.py ---
from pydantic import BaseModel
import parselmouth
from parselmouth.praat import call
import numpy as np
from scipy.fft import fft, fftfreq
import matplotlib.pyplot as plt


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

            # Jitter (ppq5) calculation with correct parameters
            jitter = call(point_process, "Get jitter (ppq5)", 0, 0, 0.0001, 0.02, 1.3) #parselmouth.praat.call(point_process, "Get jitter (local)", 0, 0, 0.0001, 0.02, 1.3)#, 0.0001, 0.02, 0.02, 1.3)

            # Shimmer (apq3) calculation with correct parameters
            shimmer = call([sound, point_process], "Get shimmer (apq3)", 0, 0, 0.0001, 0.02, 1.3, 1.6) #parselmouth.praat.call([sound, point_process], "Get shimmer (local)", 0, 0, 0.0001, 0.02, 1.3, 1.6)#, 0.0001, 0.02, 0.02, 1.3)

            # Fundamental frequency calculation
            f0 = sound.to_pitch().selected_array["frequency"].mean()

            # Harmonicidade (HNR)
            harmonicity = sound.to_harmonicity()

            # Calcular Harmonics-to-Noise Ratio (HNR)
            hnr = call(harmonicity, "Get mean", 0, 0)

            # FFT calculation
            signal = sound.values[0]  # Get the mono signal
            sampling_rate = sound.sampling_frequency
            n = len(signal)
            yf = fft(signal)
            xf = fftfreq(n, 1 / sampling_rate)

            # Filter frequencies up to 2000 Hz
            mask = xf > 0
            xf = xf[mask]
            yf = 2.0 / n * np.abs(yf[mask])
            filtered_xf = xf[xf <= 2000]
            filtered_yf = yf[:len(filtered_xf)]

            # Plot FFT
            plt.figure(figsize=(10, 6))
            plt.plot(filtered_xf, filtered_yf, label="FFT")
            plt.title("FFT Analysis (up to 2000 Hz)")
            plt.xlabel("Frequency (Hz)")
            plt.ylabel("Amplitude")
            plt.grid()
            plt.legend()
            plt.savefig("fft_plot.png")

            return AudioAnalysisResult(
                jitter=jitter,
                shimmer=shimmer,
                fundamental_frequency=f0,
                frequencies=filtered_xf.tolist(),
                amplitudes=filtered_yf.tolist()
            )
        except Exception as e:
            raise ValueError(f"Error analyzing audio: {str(e)}")
