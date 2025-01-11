# --- domain/audio_analysis.py ---
from pydantic import BaseModel
import parselmouth
from parselmouth.praat import call
import numpy as np
from scipy.fft import fft, fftfreq
from scipy.signal import find_peaks
import matplotlib.pyplot as plt
import pandas as pd


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

            # Jitter (ppq5) calculation
            jitter = call(point_process, "Get jitter (ppq5)", 0, 0, 0.0001, 0.02, 1.3) #parselmouth.praat.call(point_process, "Get jitter (local)", 0, 0, 0.0001, 0.02, 1.3)#, 0.0001, 0.02, 0.02, 1.3)

            # Shimmer (apq3) calculation
            shimmer = call([sound, point_process], "Get shimmer (apq3)", 0, 0, 0.0001, 0.02, 1.3, 1.6) #parselmouth.praat.call([sound, point_process], "Get shimmer (local)", 0, 0, 0.0001, 0.02, 1.3, 1.6)#, 0.0001, 0.02, 0.02, 1.3)

            # Fundamental frequency calculation
            f0 = sound.to_pitch().selected_array["frequency"].mean()

            # Harmonicidade (HNR)
            harmonicity = sound.to_harmonicity()

            # Calcular Harmonics-to-Noise Ratio (HNR)
            hnr = call(harmonicity, "Get mean", 0, 0)

            top10_freq = self.calculate_fft(audio_path)
            return AudioAnalysisResult(
                jitter=jitter,
                shimmer=shimmer,
                fundamental_frequency=f0,
                frequencies=top10_freq["frequencies"],
                amplitudes=top10_freq["amplitudes"]
            )
            #     frequencies=top10_freq["frequencies"].tolist(),
            #     amplitudes=top10_freq["amplitudes"].tolist()
            # )
        except Exception as e:
            raise ValueError(f"Error analyzing audio: {str(e)}")


    def calculate_fft(self, audio_path:str) -> dict:
        """Calcula e plota a FFT de um arquivo de áudio e retorna as frequências e amplitudes."""
        sound = parselmouth.Sound(audio_path)
        sampling_rate = sound.sampling_frequency
        audio_data = sound.values[0]
        n = len(audio_data)

        # FFT computation
        fft_values = np.fft.fft(audio_data)
        frequencies = np.fft.fftfreq(n, d=1/sampling_rate)

        # Focus on positive frequencies
        positive_frequencies = frequencies[:n // 2]
        positive_amplitudes = np.abs(fft_values[:n // 2])

        # # Find the 10 largest amplitudes and their corresponding frequencies
        # indices = np.argsort(positive_amplitudes)[-10:]  # Indices of the 10 largest amplitudes
        # top_amplitudes = positive_amplitudes[indices]
        # top_frequencies = positive_frequencies[indices]
        #
        # # Sort the results for better readability
        # sorted_indices = np.argsort(top_frequencies)
        # top_frequencies = top_frequencies[sorted_indices]
        # top_amplitudes = top_amplitudes[sorted_indices]
        #
        # # Display the results
        # print("Top 10 Frequencies and Amplitudes:")
        # for freq, amp in zip(top_frequencies, top_amplitudes):
        #     print(f"Frequency: {freq:.2f} Hz, Amplitude: {amp:.2f}")



        # Distância mínima para considerar como um único grupo
        distancia_minima = 5  # Em unidades de frequência

        # Filtrar apenas frequências até 1 kHz
        limite_frequencia = 1000  # 1 kHz
        mask = positive_frequencies <= limite_frequencia
        positive_frequencies = positive_frequencies[mask]
        positive_amplitudes = positive_amplitudes[mask]

        # Detectar máximos locais
        indices_picos, _ = find_peaks(positive_amplitudes)

        # Filtrar os picos com base na distância mínima
        picos_filtrados = []
        frequencias_filtradas = []
        magnitudes_filtradas = []

        for i in range(len(indices_picos)):
            freq_atual = positive_frequencies[indices_picos[i]]
            mag_atual  = positive_amplitudes[indices_picos[i]]

            # Verificar se está longe o suficiente dos picos já filtrados
            if not any(abs(freq_atual - f) < distancia_minima for f in frequencias_filtradas):
                picos_filtrados.append(indices_picos[i])
                frequencias_filtradas.append(freq_atual)
                magnitudes_filtradas.append(mag_atual)

        # Exibir os resultados
        for i, (freq, mag) in enumerate(zip(frequencias_filtradas, magnitudes_filtradas)):
            print(f"{i+1}: Frequência = {freq:.2f} Hz, Valor = {mag:.2f}")

        # Plot FFT with top frequencies highlighted
        plt.figure(figsize=(10, 6))
        plt.plot(frequencias_filtradas, magnitudes_filtradas, label="FFT")
        # plt.scatter(top_frequencies, top_amplitudes, color='red', label="Top Peaks")
        plt.title("FFT of the Audio Signal with Top Peaks")
        plt.xlabel("Frequency (Hz)")
        plt.ylabel("Amplitude")
        plt.legend()
        plt.grid()
        plt.show()
        plt.savefig("fft_plot.png")
        self.export_to_excel(positive_frequencies, positive_amplitudes, "fft_audio.csv")
        self.export_to_excel(frequencias_filtradas, magnitudes_filtradas, "fft_audio_filtrada.csv")

        return {"frequencies": frequencias_filtradas,"amplitudes": magnitudes_filtradas}

    def export_to_excel(self, freq:list, amp:list, filename:str) -> None:
        """Export two lists into an Excel file with two columns."""
        if len(freq) != len(amp):
            raise ValueError("Both lists must have the same length.")

        # Create a DataFrame from the two lists
        data = pd.DataFrame({"freq": freq, "amp": amp})

        # Export to an Excel file
        data.to_csv(filename, index=False)
        print(f"Excel file '{filename}' has been created successfully.")
        return


