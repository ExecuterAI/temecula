const CACHE = 'wine-oclock-v2';
const SHELL = [
  '/wine-oclock/',
  '/wine-oclock/app.css',
  '/wine-oclock/app.js',
  '/wine-oclock/manifest.webmanifest',
  '/wine-oclock/content/days.json',
  '/wine-oclock/content/varietals.json',
  '/wine-oclock/content/lessons.json',
  '/wine-oclock/content/pairings.json',
  '/wine-oclock/content/quotes.json',
  '/wine-oclock/apple-touch-icon.png',
  '/wine-oclock/icon-512.png',
  '/images/brand/logo-header-horizontal.png',
  '/wine-oclock/audio/cork.wav',
  '/wine-oclock/audio/jazz-lounge.wav',
  '/wine-oclock/audio/golden-hour.wav',
  '/wine-oclock/audio/fireside.wav',
  '/wine-oclock/audio/dinner-party.wav',
  '/wine-oclock/audio/quiet.wav',
  '/wine-oclock/audio/signature.wav'
];

self.addEventListener('install', (event) => {
  event.waitUntil(caches.open(CACHE).then((cache) => cache.addAll(SHELL)).then(() => self.skipWaiting()));
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) => Promise.all(keys.filter((key) => key !== CACHE).map((key) => caches.delete(key)))).then(() => self.clients.claim())
  );
});

self.addEventListener('fetch', (event) => {
  const url = new URL(event.request.url);
  if (url.origin !== self.location.origin) return;
  if (!url.pathname.startsWith('/wine-oclock/') && !url.pathname.startsWith('/images/brand/logo-header-horizontal.png')) return;
  event.respondWith(
    fetch(event.request)
      .then((response) => {
        if (response && response.ok) {
          const copy = response.clone();
          caches.open(CACHE).then((cache) => cache.put(event.request, copy));
        }
        return response;
      })
      .catch(() => caches.match(event.request).then((hit) => hit || caches.match('/wine-oclock/')))
  );
});
