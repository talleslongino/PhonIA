//# --- frontend/service-worker.js ---
const CACHE_NAME = "audio-tool-cache-v1";
const urlsToCache = [
    "/",
    "/static/styles.css",
    "/static/app.js",
    "/static/assets/logo-192x192.png",
    "/static/assets/logo-512x512.png"
];

// Instala o Service Worker e adiciona os arquivos ao cache
self.addEventListener("install", (event) => {
    event.waitUntil(
        caches.open(CACHE_NAME).then((cache) => {
            return cache.addAll(urlsToCache);
        })
    );
});

// Responde às requisições com o cache, se disponível
self.addEventListener("fetch", (event) => {
    event.respondWith(
        caches.match(event.request).then((response) => {
            return response || fetch(event.request);
        })
    );
});

// Atualiza o cache quando o Service Worker é ativado
self.addEventListener("activate", (event) => {
    const cacheWhitelist = [CACHE_NAME];
    event.waitUntil(
        caches.keys().then((cacheNames) => {
            return Promise.all(
                cacheNames.map((cacheName) => {
                    if (!cacheWhitelist.includes(cacheName)) {
                        return caches.delete(cacheName);
                    }
                })
            );
        })
    );
});
