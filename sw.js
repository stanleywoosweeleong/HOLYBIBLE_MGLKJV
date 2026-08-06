/* Ариун Библи — service worker
   Rewritten by build.py on every build. Never edit by hand.

   Two caches, on purpose:
     SHELL — timestamped, replaced on every build (HTML, icons, manifest: ~110 KB)
     DATA  — keyed by the scripture filename, replaced ONLY when the text changes
   A UI fix therefore costs a small download; the 1.66 MB Bible is refetched only
   when the text itself has actually been corrected. */
const SHELL_CACHE = "mnbible-shell-20260806-1622";
const DATA_CACHE  = "mnbible-text-v1.0.1";
const SHELL_ASSETS = [
  "./",
  "./index.html",
  "./manifest.webmanifest",
  "./favicon.ico",
  "./icons/apple-touch-icon-152.png",
  "./icons/apple-touch-icon-167.png",
  "./icons/apple-touch-icon.png",
  "./icons/favicon-16.png",
  "./icons/favicon-32.png",
  "./icons/icon-192.png",
  "./icons/icon-256.png",
  "./icons/icon-384.png",
  "./icons/icon-512.png",
  "./icons/maskable-192.png",
  "./icons/maskable-512.png"
];
const DATA_ASSET   = "./data/bible-1.0.1.bin";

async function fillCache(cacheName, urls) {
  const c = await caches.open(cacheName);
  const failed = [];
  await Promise.all(urls.map(async u => {
    if (await c.match(u)) return;                 // already held - do not refetch
    try {
      const r = await fetch(u, { cache: "reload" });
      if (!r.ok) throw new Error(r.status);
      await c.put(u, r);
    } catch (err) { failed.push(u + " (" + err.message + ")"); }
  }));
  if (failed.length) throw new Error("precache incomplete: " + failed.join(", "));
}

self.addEventListener("install", e => {
  e.waitUntil((async () => {
    await fillCache(DATA_CACHE, [DATA_ASSET]);    // survives shell-only updates
    await fillCache(SHELL_CACHE, SHELL_ASSETS);
  })());
});

self.addEventListener("activate", e => {
  e.waitUntil((async () => {
    const keep = new Set([SHELL_CACHE, DATA_CACHE]);
    const keys = await caches.keys();
    await Promise.all(keys.filter(k => !keep.has(k)).map(k => caches.delete(k)));
    await self.clients.claim();
  })());
});

self.addEventListener("message", e => {
  if (e.data === "skipWaiting") self.skipWaiting();
});

self.addEventListener("fetch", e => {
  const req = e.request;
  if (req.method !== "GET") return;
  const url = new URL(req.url);
  if (url.origin !== location.origin) return;
  // The optional English text lives in IndexedDB; never duplicate it here.
  if (url.pathname.endsWith("/kjv.bin")) return;

  e.respondWith((async () => {
    const cached = await caches.match(req);
    if (cached) return cached;
    try {
      const res = await fetch(req);
      if (res.ok && res.type === "basic") {
        const c = await caches.open(SHELL_CACHE);
        c.put(req, res.clone());
      }
      return res;
    } catch (err) {
      if (req.mode === "navigate") {
        const shell = await caches.match("./index.html");
        if (shell) return shell;
      }
      throw err;
    }
  })());
});
