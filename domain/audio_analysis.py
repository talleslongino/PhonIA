# --- domain/audio_analysis.py ---
from pydantic import BaseModel
import parselmouth
from parselmouth.praat import call
import numpy as np
from scipy.signal import find_peaks
import matplotlib.pyplot as plt
import pandas as pd
import plotly.graph_objects as go


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
            jitter = call(point_process, "Get jitter (ppq5)", 0, 0, 0.0001, 0.02, 1.3)
            # parselmouth.praat.call(point_process, "Get jitter (local)", 0, 0, 0.0001, 0.02, 1.3)#, 0.0001, 0.02, 0.02, 1.3)

            # Shimmer (apq3) calculation
            shimmer = call([sound, point_process], "Get shimmer (apq3)", 0, 0, 0.0001, 0.02, 1.3, 1.6)
            # parselmouth.praat.call([sound, point_process], "Get shimmer (local)", 0, 0, 0.0001, 0.02, 1.3, 1.6)#, 0.0001, 0.02, 0.02, 1.3)

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

        except Exception as e:
            raise ValueError(f"Error analyzing audio: {str(e)}")

    def calculate_fft(self, audio_path: str) -> dict:
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

        # Distância mínima para considerar como um único grupo
        distancia_minima = 50  # Em unidades de frequência

        # Filtrar apenas frequências até 1 kHz
        limite_frequencia = 1000  # 1 kHz
        mask = positive_frequencies <= limite_frequencia
        freq_filter_freq = positive_frequencies[mask]
        amp_filter_freq = positive_amplitudes[mask]

        # Detectar picos com distância mínima de 2mil amostras
        indices_picos, _ = find_peaks(amp_filter_freq, distance=2000)

        # Filtrar os picos com base na distância mínima
        picos_filtrados = []
        frequencias_filtradas = []
        magnitudes_filtradas = []

        for i in range(len(indices_picos)):
            freq_atual = freq_filter_freq[indices_picos[i]]
            mag_atual = amp_filter_freq[indices_picos[i]]

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
        plt.plot(freq_filter_freq, amp_filter_freq, label="FFT")
        plt.scatter(frequencias_filtradas, magnitudes_filtradas, color='red', label="Top Peaks")
        plt.title("FFT of the Audio Signal with Top Peaks")
        plt.xlabel("Frequency (Hz)")
        plt.ylabel("Amplitude")
        plt.legend()
        plt.grid()
        plt.savefig("fft_plot.png")

        self.create_plot_fft(freq_filter_freq, amp_filter_freq, frequencias_filtradas, magnitudes_filtradas)
        self.export_to_excel(positive_frequencies, positive_amplitudes, "fft_audio.csv")
        self.export_to_excel(frequencias_filtradas, magnitudes_filtradas, "fft_audio_filtrada.csv")

        return {"frequencies": frequencias_filtradas, "amplitudes": magnitudes_filtradas}

    def create_plot_fft(self, freq_filter_freq, amp_filter_freq, frequencias_filtradas, magnitudes_filtradas) -> None:
        """Create a iterative plot in html form"""

        # Criando o gráfico interativo
        fig = go.Figure()

        fig.add_trace(go.Scatter(x=freq_filter_freq, y=amp_filter_freq, mode='lines', name='FFT'))
        fig.add_trace(go.Scatter(x=frequencias_filtradas, y=magnitudes_filtradas, mode='markers', name='Maiores Picos'))

        # Configuração do layout
        fig.update_layout(
            title=dict(text="Gráfico Interativo - FFT do Sinal de Áudio e Maiores Picos",
                       x=0.5, xanchor="center",
                       font=dict(family="Arial, sans-serif", size=20, color="black", weight="bold")),
            xaxis_title=dict(text="Frequência (Hz)",font=dict(size=16, color="black", weight="bold")),
            yaxis_title=dict(text="Amplitude",font=dict(size=16, color="black", weight="bold")),
            xaxis=dict(tickfont=dict(size=12, weight="bold")),
            yaxis=dict(tickfont=dict(size=12, weight="bold")),
            plot_bgcolor='whitesmoke', #determina a cor do fundo
            template='plotly_white', #"plotly_dark"  # Opção de tema
            legend=dict(x=0.5, y=1.1, xanchor="center", orientation="h")
        )

        # Determina a cor do eixo x e a cor do grid
        fig.update_xaxes(showgrid=True, gridwidth=1, gridcolor='lightgray',
        showline=True, linewidth=1, linecolor='black')

        # Determina a cor do eixo y e a cor do grid
        fig.update_yaxes(showgrid=True, gridwidth=1, gridcolor='lightgray',
        showline=True, linewidth=1, linecolor='black')

        # Salvar como HTML
        fig.write_html("frontend/assets/grafico_interativo.html")
        print("Gráfico salvo como 'grafico_interativo.html'.")

        return

    def export_to_excel(self, freq: list, amp: list, filename: str) -> None:
        """Export two lists into an Excel file with two columns."""
        if len(freq) != len(amp):
            raise ValueError("Both lists must have the same length.")

        # Create a DataFrame from the two lists
        data = pd.DataFrame({"freq": freq, "amp": amp})

        # Export to an Excel file
        data.to_csv(filename, index=False)
        print(f"Excel file '{filename}' has been created successfully.")
        return
