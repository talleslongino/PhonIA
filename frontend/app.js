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

    const response = await fetch("/analyze-audio", {
        method: "POST",
        body: formData,
    });

    if (response.ok) {
        const data = await response.json();
        resultDiv.innerHTML = `<p>Jitter: ${data.jitter}</p>
                               <p>Shimmer: ${data.shimmer}</p>
                               <p>Fundamental Frequency: ${data.fundamental_frequency}</p>`;
        fftPlot.style.display = "block";
    } else {
        const error = await response.json();
        resultDiv.innerHTML = `<p>Error: ${error.detail}</p>`;
    }
});
