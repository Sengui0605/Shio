const CACHE_NAME = 'shio-cache-v1';
const ASSETS = [
  '/app',
  '/static/app.html',
  '/static/landing.css',
  '/static/app.js',
  '/static/shio_icon_256.png',
  '/static/shio_icon_512.png'
];

self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME).then((cache) => {
      return cache.addAll(ASSETS);
    })
  );
});

self.addEventListener('fetch', (event) => {
  event.respondWith(
    caches.match(event.request).then((response) => {
      return response || fetch(event.request);
    })
  );
});
