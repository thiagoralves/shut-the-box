const CACHE_NAME = 'shut-the-box-v6';
const urlsToCache = [
    '/static/css/style.css',
    '/static/manifest.json',
    '/static/icons/icon-192.png',
    '/static/icons/icon-512.png'
];

self.addEventListener('install', function(event) {
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then(function(cache) {
                console.log('Opened cache');
                return cache.addAll(urlsToCache);
            })
            .catch(function(err) {
                console.log('Cache install failed:', err);
            })
    );
    self.skipWaiting();
});

self.addEventListener('fetch', function(event) {
    if (event.request.method !== 'GET') {
        return;
    }
    
    if (event.request.mode === 'navigate') {
        event.respondWith(fetch(event.request));
        return;
    }
    
    event.respondWith(
        fetch(event.request)
            .then(function(response) {
                if (!response || response.status !== 200 || response.type !== 'basic') {
                    return response;
                }
                
                var url = new URL(event.request.url);
                if (url.pathname.startsWith('/static/')) {
                    var responseToCache = response.clone();
                    caches.open(CACHE_NAME)
                        .then(function(cache) {
                            cache.put(event.request, responseToCache);
                        });
                }
                
                return response;
            })
            .catch(function() {
                return caches.match(event.request);
            })
    );
});

self.addEventListener('activate', function(event) {
    event.waitUntil(
        caches.keys().then(function(cacheNames) {
            return Promise.all(
                cacheNames.filter(function(cacheName) {
                    return cacheName !== CACHE_NAME;
                }).map(function(cacheName) {
                    return caches.delete(cacheName);
                })
            );
        })
    );
    self.clients.claim();
});
