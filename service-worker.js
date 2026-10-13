/* ========================================================
   SERVICE WORKER — FIXED FOR API + CACHING + PUSH
======================================================== */

const CACHE_NAME = 'ocean-hydration-v1';
const ASSETS = [
  '/index.html',
  '/manifest.json'
  // DO NOT add mp3 or API URLs here
];

/* ===========================
   INSTALL — Cache STATIC files only
=========================== */
self.addEventListener('install', (event) => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => cache.addAll(ASSETS))
      .catch(() => {})
  );
  self.skipWaiting();
});

/* ===========================
   ACTIVATE
=========================== */
self.addEventListener('activate', (event) => {
  event.waitUntil(self.clients.claim());
});

/* ===========================
   FETCH — IMPORTANT FIX!
   Do NOT intercept API calls to 127.0.0.1:3000
=========================== */
self.addEventListener('fetch', (event) => {
  const url = event.request.url;

  // 🚫 Bypass all requests to your push server API
  if (url.includes('127.0.0.1:3000') || url.includes('localhost:3000')) {
    return; // Let network handle it
  }

  // 🚫 Bypass mp3 or other dynamic assets
  if (url.endsWith('.mp3') || url.endsWith('.ico')) {
    return fetch(event.request);
  }

  // ✔ Cache-first for static PWA files only
  event.respondWith(
    caches.match(event.request)
      .then(resp => resp || fetch(event.request))
  );
});

/* ===========================
   PUSH — Show notification
=========================== */
self.addEventListener('push', (event) => {
  let payload = {
    title: '🐬 Hydration Reminder',
    body: 'Take a sip of water!',
    icon: 'https://cdn-icons-png.flaticon.com/512/2928/2928896.png',
    data: { url: '/' }
  };

  if (event.data) {
    try {
      payload = event.data.json();
    } catch (e) {
      payload.body = event.data.text();
    }
  }

  const options = {
    body: payload.body,
    icon: payload.icon,
    badge: payload.icon,
    data: payload.data,
    vibrate: [200, 100, 200],
    renotify: true
  };

  event.waitUntil(
    self.registration.showNotification(payload.title, options)
  );
});

/* ===========================
   NOTIFICATION CLICK
=========================== */
self.addEventListener('notificationclick', (event) => {
  event.notification.close();
  const url = event.notification.data?.url || '/';

  event.waitUntil(
    clients.matchAll({ type: 'window', includeUncontrolled: true })
      .then((windowClients) => {
        for (const client of windowClients) {
          if (client.url === url && 'focus' in client) {
            return client.focus();
          }
        }
        return clients.openWindow(url);
      })
  );
});
