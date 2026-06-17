const CACHE_NAME = 'eorder-kasir-v1';
const CACHE_URLS = [
    '/kasir/dashboard/',
    '/kasir/login/',
    '/static/manifest.json',
    '/static/img/icons/icon-192.png',
    '/static/img/icons/icon-512.png',
];

self.addEventListener('install', event => {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(cache => cache.addAll(CACHE_URLS))
            .then(() => self.skipWaiting())
    );
});

self.addEventListener('activate', event => {
    event.waitUntil(
        caches.keys().then(keys =>
            Promise.all(
                keys.filter(k => k !== CACHE_NAME)
                    .map(k => caches.delete(k))
            )
        ).then(() => self.clients.claim())
    );
});

self.addEventListener('fetch', event => {
    if (event.request.method !== 'GET') return;
    const url = new URL(event.request.url);
    if (!url.pathname.startsWith('/kasir/')
            && !url.pathname.startsWith('/static/')) return;
    if (url.pathname.includes('/api/')) return;
    if (url.pathname.includes('/update-status/')) return;

    event.respondWith(
        fetch(event.request)
            .then(response => {
                if (response && response.status === 200) {
                    const clone = response.clone();
                    caches.open(CACHE_NAME).then(cache => {
                        cache.put(event.request, clone);
                    });
                }
                return response;
            })
            .catch(() => caches.match(event.request))
    );
});


// ==============================
// ✅ PUSH NOTIFICATION HANDLER
// ==============================
self.addEventListener('push', event => {
    let data = {
        title : '🔔 E-Order Kasir',
        body  : 'Ada pesanan baru!',
        url   : '/kasir/dashboard/',
        icon  : '/static/img/icons/icon-192.png',
        badge : '/static/img/icons/icon-72.png',
    };

    if (event.data) {
        try {
            data = { ...data, ...event.data.json() };
        } catch(e) {
            data.body = event.data.text();
        }
    }

    const options = {
        body   : data.body,
        icon   : data.icon,
        badge  : data.badge,
        vibrate: [200, 100, 200],
        tag    : 'eorder-pesanan-baru',
        renotify: true,
        data   : { url: data.url },
        actions: [
            {
                action: 'buka',
                title : '📊 Buka Dashboard',
            },
            {
                action: 'tutup',
                title : 'Tutup',
            }
        ]
    };

    event.waitUntil(
        self.registration.showNotification(data.title, options)
    );
});


// ==============================
// ✅ KLIK NOTIFIKASI
// ==============================
self.addEventListener('notificationclick', event => {
    event.notification.close();

    if (event.action === 'tutup') return;

    const url = event.notification.data?.url || '/kasir/dashboard/';

    event.waitUntil(
        clients.matchAll({ type: 'window', includeUncontrolled: true })
            .then(windowClients => {
                // Jika tab kasir sudah terbuka → focus
                for (const client of windowClients) {
                    if (client.url.includes('/kasir/') && 'focus' in client) {
                        client.navigate(url);
                        return client.focus();
                    }
                }
                // Jika belum ada tab → buka baru
                if (clients.openWindow) {
                    return clients.openWindow(url);
                }
            })
    );
});