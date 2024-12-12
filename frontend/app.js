const form = document.getElementById("upload-form");
const resultDiv = document.getElementById("result");
const fftPlot = document.getElementById("fft-plot");

form.addEventListener("submit", async (e) => {
    e.preventDefault();
    const fileInput = document.getElementById("audio-file");
    const file = fileInput.files[0];

    if (!file) return;

    const formData = new FormData();
    formData.append("file", file);

    // Inicia a análise e obtém o ID da tarefa
    let response = await fetch("/start-analysis", {
        method: "POST",
        body: formData,
    });

    if (response.ok) {
        const data = await response.json();
        const taskId = data.task_id;
        await checkTaskStatus(taskId);
    } else {
        const error = await response.json();
        resultDiv.innerHTML = `<p>Error: ${error.detail}</p>`;
    }
});

// Função para verificar o status da tarefa
async function checkTaskStatus(taskId) {
    while (true) {
        const response = await fetch(`/task-status/${taskId}`);
        const data = await response.json();

        if (data.status === "completed") {
            resultDiv.innerHTML = `<p>Jitter: ${data.result.jitter}</p>
                                   <p>Shimmer: ${data.result.shimmer}</p>
                                   <p>Fundamental Frequency: ${data.result.fundamental_frequency}</p>`;
            fftPlot.style.display = "block";
            break;
        } else if (data.status === "failed") {
            resultDiv.innerHTML = `<p>Error: ${data.error}</p>`;
            break;
        }

        // Espera antes de verificar novamente
        await new Promise(resolve => setTimeout(resolve, 1000));
    }
}
