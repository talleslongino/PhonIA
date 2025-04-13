//# --- frontend/audio-editor.js ---

let wavesurfer;
let region = null;

function initializeWaveSurfer(containerId) {
    wavesurfer = WaveSurfer.create({
        container: containerId,
        waveColor: "blue",
        progressColor: "purple",
        cursorColor: "navy",
        height: 150,
        responsive: true,
        plugins: [WaveSurfer.regions.create()]
    });

    return wavesurfer;
}

function loadAudio(file) {
    const reader = new FileReader();
    reader.onload = (event) => {
        wavesurfer.load(event.target.result);
        wavesurfer.on("ready", () => {
            createInitialRegion();
        });
    };
    reader.readAsDataURL(file);
}

function createInitialRegion() {
    region = wavesurfer.addRegion({
        start: 0,
        end: Math.min(5, wavesurfer.getDuration()),
        color: "rgba(0, 255, 0, 0.3)"
    });
}

function playRegion() {
    if (region) {
        wavesurfer.play(region.start, region.end);
    } else {
        alert("Nenhuma região selecionada.");
    }
}

async function cutAudio() {
    if (!region) {
        alert("Por favor, selecione uma região para cortar.");
        return;
    }

    const originalBuffer = wavesurfer.backend.buffer;
    const startSample = Math.floor(region.start * originalBuffer.sampleRate);
    const endSample = Math.floor(region.end * originalBuffer.sampleRate);
    const cutSamples = endSample - startSample;

    if (cutSamples <= 0) {
        alert("Região inválida. Certifique-se de que a região está corretamente definida.");
        return;
    }

    const newBuffer = wavesurfer.backend.ac.createBuffer(
        originalBuffer.numberOfChannels,
        cutSamples,
        originalBuffer.sampleRate
    );

    for (let channel = 0; channel < originalBuffer.numberOfChannels; channel++) {
        const channelData = originalBuffer.getChannelData(channel);
        newBuffer.copyToChannel(channelData.subarray(startSample, endSample), channel);
    }
    console.log(`🎧 Corte de áudio realizado`);
    console.log(`⏱️ Duração original: ${(originalBuffer.duration).toFixed(2)}s`);
    console.log(`✂️ Duração cortada: ${(cutSamples / originalBuffer.sampleRate).toFixed(2)}s`);
    await exportAudioBuffer(newBuffer);
}

async function exportAudioBuffer(audioBuffer) {
    const offlineContext = new OfflineAudioContext(
        audioBuffer.numberOfChannels,
        audioBuffer.length,
        audioBuffer.sampleRate
    );

    const source = offlineContext.createBufferSource();
    source.buffer = audioBuffer;
    source.connect(offlineContext.destination);
    source.start();

    const renderedBuffer = await offlineContext.startRendering();
    const wavBlob = bufferToWave(renderedBuffer);

    const link = document.createElement("a");
    link.href = URL.createObjectURL(wavBlob);
    link.download = "cut_audio.wav";
    link.click();
}

function bufferToWave(buffer) {
    const numChannels = buffer.numberOfChannels;
    const length = buffer.length * numChannels * 2 + 44;
    const result = new ArrayBuffer(length);
    const view = new DataView(result);

    writeUTFBytes(view, 0, "RIFF");
    view.setUint32(4, length - 8, true);
    writeUTFBytes(view, 8, "WAVE");
    writeUTFBytes(view, 12, "fmt ");
    view.setUint32(16, 16, true);
    view.setUint16(20, 1, true);
    view.setUint16(22, numChannels, true);
    view.setUint32(24, buffer.sampleRate, true);
    view.setUint32(28, buffer.sampleRate * 4, true);
    view.setUint16(32, numChannels * 2, true);
    view.setUint16(34, 16, true);
    writeUTFBytes(view, 36, "data");
    view.setUint32(40, length - 44, true);

    let offset = 44;
    for (let i = 0; i < buffer.length; i++) {
        for (let channel = 0; channel < numChannels; channel++) {
            const sample = buffer.getChannelData(channel)[i];
            const value = Math.max(-1, Math.min(1, sample)) * 32767;
            view.setInt16(offset, value, true);
            offset += 2;
        }
    }
    return new Blob([view], { type: "audio/wav" });
}

function writeUTFBytes(view, offset, string) {
    for (let i = 0; i < string.length; i++) {
        view.setUint8(offset + i, string.charCodeAt(i));
    }
}
