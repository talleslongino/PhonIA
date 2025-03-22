//# --- frontend/app.js ---

// Lógica para enviar o arquivo de áudio e exibir os resultados diretamente
const form = document.getElementById("upload-form");
const resultDiv = document.getElementById("result");
const fftPlot = document.getElementById("fft-plot");
const fftPlotly = document.getElementById("fft-plotly");



// Verifica se o termo de consentimento foi aceito
if (!localStorage.getItem("consentGiven")) {
  alert("Você precisa aceitar o termo de consentimento para continuar.");
  window.location.href = "/consent";
  sessionStorage.setItem("pendingRedirect", link.href);
}

form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const fileInput = document.getElementById("audio-file");
    const file = fileInput.files[0];

    if (!file) return;

    const formData = new FormData();
    formData.append("file", file);

    // Envia o arquivo para análise e exibe os resultados
    try {
        const response = await fetch("/start-analysis", {
            method: "POST",
            body: formData,
        });

        if (response.ok) {
            const data = await response.json();
            resultDiv.innerHTML = `<p>Jitter (local): ${data.localJitter}</p>
                                    <p>Jitter (local, absolute): ${data.localabsoluteJitter}</p>
                                    <p>Jitter (rap): ${data.rapJitter}</p>
                                    <p>Jitter (ppq5): ${data.ppq5Jitter}</p>
                                    <p>Jitter (ddp): ${data.ddpJitter}</p>
                                    <p>Shimmer (local): ${data.localShimmer}</p>
                                    <p>Shimmer (local, dB): ${data.localdbShimmer}</p>
                                    <p>Shimmer (apq3): ${data.apq3Shimmer}</p>
                                    <p>Shimmer (apq5): ${data.apq5Shimmer}</p>
                                    <p>Shimmer (apq11): ${data.apq11Shimmer}</p>
                                    <p>Shimmer (dda): ${data.ddaShimmer}</p>
                                    <p>Fundamental Frequency: ${data.fundamental_frequency}</p>
                                    <p>HNR: ${data.hnr}</p>`;
            fftPlot.style.display = "block";
            fftPlotly.style.display = "block";

            const results = [
            { freq: "Jitter (ppq5)", amp: 1.11 },
            { freq: "Shimmer (apq3)", amp: 2.22 },
            { freq: "Frequência Fundamental (Hz)", amp: 3.33 },
            { freq: "HNR (Harmonic-to-Noise Ratio)", amp: 4.44 }
            ];

            const results2 = [
            { metrica: "Jitter (ppq5)", valor: data.jitter },
            { metrica: "Shimmer (apq3)", valor: data.shimmer },
            { metrica: "Frequência Fundamental (Hz)", valor: data.fundamental_frequency },
            { metrica: "HNR (Harmonic-to-Noise Ratio)", valor: data.hnr }
            ];

//            // Verificar se as listas têm o mesmo tamanho
//            if (data.frequencies.length !== data.amplitudes.length) {
//                console.error("As listas de frequências e amplitudes têm tamanhos diferentes!");
//            } else {
//                // Criar um dicionário combinando os itens das listas
//                const results = data.frequencies.map((freq, index) => {
//                    return {
//                        freq: freq,
//                        amp: data.amplitudes[index]
//                    };
//                });
//
//            console.log(results);

            // Chama a função para criar a tabela com os dados
            criarTabela(results);
            criarTabela_fft(results2);

        } else {
            const error = await response.json();
            resultDiv.innerHTML = `<p>Error: ${error.detail}</p>`;
        }
    } catch (error) {
        resultDiv.innerHTML = `<p>Error: ${error.message}</p>`;
    }
});


        // Função para criar e inserir a tabela
        function criarTabela(dados) {
            // Cria o elemento da tabela
            const tabela = document.createElement("table");

            // Cabeçalho da tabela
            const thead = document.createElement("thead");
            thead.innerHTML = `
                <tr>
                    <th>Frequência [Hz]</th>
                    <th>Amplitude</th>
                </tr>
            `;
            tabela.appendChild(thead);

            // Corpo da tabela
            const tbody = document.createElement("tbody");
            dados.forEach((item) => {
                const row = document.createElement("tr");
                row.innerHTML = `
                    <td>${item.freq}</td>
                    <td>${item.amp}</td>
                `;
                tbody.appendChild(row);
            });
            tabela.appendChild(tbody);

            // Insere a tabela no contêiner
            document.getElementById("tabela-resultados").appendChild(tabela);
        }

                // Função para criar e inserir a tabela
        function criarTabela_fft(dados) {
            // Cria o elemento da tabela
            const tabela = document.createElement("table");

            // Cabeçalho da tabela
            const thead = document.createElement("thead");
            thead.innerHTML = `
                <tr>
                    <th>Métrica2</th>
                    <th>Valor2</th>
                </tr>
            `;
            tabela.appendChild(thead);

            // Corpo da tabela
            const tbody = document.createElement("tbody");
            dados.forEach((item) => {
                const row = document.createElement("tr");
                row.innerHTML = `
                    <td>${item.metrica}</td>
                    <td>${item.valor}</td>
                `;
                tbody.appendChild(row);
            });
            tabela.appendChild(tbody);

            // Insere a tabela no contêiner
            document.getElementById("tabela-resultados_fft").appendChild(tabela);
        }
