/* ==========================================================================
   Clean & Safe India - PWA Service Worker (v1.0.0)
   Provides Offline Support, Asset Caching, Push Notifications & Background Sync
   ========================================================================== */

const CACHE_NAME = 'clean-safe-india-v17.0.0';
const STATIC_ASSETS = [
  './',
  './index.html',
  './manifest.json',
  './css/main.css',
  './css/responsive.css',
  './css/components.css',
  './css/auth.css',
  './css/command-center.css',
  './css/electricity.css',
  './css/iot-simulation.css',
  './assets/logo.png',
  './assets/icon-192.png',
  './assets/icon-512.png',
  './assets/maskable-icon.png',
  './assets/apple-touch-icon.png'
];

// Install Event: Pre-cache core application shell
self.addEventListener('install', (event) => {
  self.skipWaiting();
});

// Activate Event: Clean up legacy caches immediately
self.addEventListener('activate', (event) => {
  event.waitUntil(
    caches.keys().then((keys) => {
      return Promise.all(
        keys.map((key) => {
          if (key !== CACHE_NAME) {
            console.log('[ServiceWorker] Removing legacy cache:', key);
            return caches.delete(key);
          }
        })
      );
    })
  );
  self.clients.claim();
});

// Fetch Event: Network-First with Cache Fallback for instant updates
self.addEventListener('fetch', (event) => {
  // Never intercept or cache API endpoints or JS bundles
  if (event.request.url.includes('/api/') || event.request.url.includes('bundle.js')) return;
  if (event.request.method !== 'GET') return;

  event.respondWith(
    fetch(event.request)
      .then((networkResponse) => {
        // If valid response, clone and update cache in background
        if (networkResponse && networkResponse.status === 200) {
          const responseClone = networkResponse.clone();
          caches.open(CACHE_NAME).then((cache) => {
            cache.put(event.request, responseClone);
          });
        }
        return networkResponse;
      })
      .catch(() => {
        // Fallback to cache if network is unavailable (offline mode)
        return caches.match(event.request).then((cachedResponse) => {
          if (cachedResponse) {
            return cachedResponse;
          }
          if (event.request.mode === 'navigate') {
            return caches.match('./index.html');
          }
        });
      })
  );
});

// Push Notifications Event
self.addEventListener('push', (event) => {
  let data = { title: 'Smart Civic Alert', body: 'New update from Clean & Safe India', icon: './assets/icon-192.png' };
  if (event.data) {
    try {
      data = event.data.json();
    } catch (e) {
      data.body = event.data.text();
    }
  }

  const options = {
    body: data.body,
    icon: data.icon || './assets/icon-192.png',
    badge: './assets/icon-192.png',
    vibrate: [200, 100, 200],
    data: data.url || './index.html',
    actions: [
      { action: 'open', title: 'Open App 🚀' },
      { action: 'dismiss', title: 'Dismiss' }
    ]
  };

  event.waitUntil(
    self.registration.showNotification(data.title, options)
  );
});

// Notification Click Event
self.addEventListener('notificationclick', (event) => {
  event.notification.close();
  const urlToOpen = event.notification.data || './index.html';

  event.waitUntil(
    clients.matchAll({ type: 'window', includeUncontrolled: true }).then((windowClients) => {
      for (let client of windowClients) {
        if (client.url === urlToOpen && 'focus' in client) {
          return client.focus();
        }
      }
      if (clients.openWindow) {
        return clients.openWindow(urlToOpen);
      }
    })
  );
});
