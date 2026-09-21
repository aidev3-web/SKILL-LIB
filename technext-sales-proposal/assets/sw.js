// Minimal service worker — required for the browser's install-app prompt to fire.
// Deliberately does no caching (this is a one-time sales proposal page, not an app
// that needs offline support); it only exists to satisfy PWA installability criteria.
self.addEventListener('install', () => self.skipWaiting());
self.addEventListener('activate', (e) => e.waitUntil(self.clients.claim()));
self.addEventListener('fetch', () => {}); // presence of a fetch handler is required
