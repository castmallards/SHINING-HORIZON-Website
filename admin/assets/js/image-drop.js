// Drag-and-drop onto .image-upload zones and gallery (files + browser image URLs).
// IMPORTANT: read dataTransfer synchronously inside the drop handler (no await first).
(function (global) {
    let windowDropGuardInstalled = false;

    function installWindowDropGuard() {
        if (windowDropGuardInstalled) return;
        windowDropGuardInstalled = true;
        ['dragenter', 'dragover', 'drop'].forEach((evt) => {
            document.addEventListener(
                evt,
                (e) => {
                    const types = e.dataTransfer?.types ? [...e.dataTransfer.types] : [];
                    const hasPayload =
                        types.includes('Files') ||
                        types.some((t) => /^text\//i.test(t) || t === 'URL');
                    if (hasPayload) e.preventDefault();
                },
                false
            );
        });
    }

    function normalizeUrl(raw) {
        if (!raw || typeof raw !== 'string') return null;
        let url = raw.trim().replace(/^<|>$/g, '');
        if (!url) return null;
        if (url.startsWith('//')) url = `https:${url}`;
        if (!/^https?:\/\//i.test(url)) return null;
        if (url.startsWith('data:')) return null;
        return url;
    }

    function isImageFile(file) {
        if (!file || !file.size) return false;
        if (file.type && file.type.startsWith('image/')) return true;
        const name = file.name || '';
        if (/\.(jpe?g|png|gif|webp|svg|avif|bmp)$/i.test(name)) return true;
        // Drags from Google Images / web pages often use an empty or generic MIME type.
        if (!file.type || file.type === 'application/octet-stream') return true;
        return false;
    }

    function isBlockedPageUrl(url) {
        return /google\.com\/(search|imgres)([?#]|$)/i.test(url);
    }

    function isLikelyFetchableImageUrl(url) {
        if (!url || isBlockedPageUrl(url)) return false;
        if (/\.(jpe?g|png|gif|webp|svg|avif|bmp)(\?|#|$)/i.test(url)) return true;
        if (/gstatic\.com|googleusercontent\.com|ggpht\.com|encrypted-tbn/i.test(url)) return true;
        if (/[?&](format|image|img|url)=/i.test(url)) return true;
        return false;
    }

    function pushUrl(urls, raw) {
        const url = normalizeUrl(raw);
        if (!url || isBlockedPageUrl(url)) return;
        if (!urls.includes(url)) urls.push(url);
    }

    function parseHtmlUrls(html) {
        const urls = [];
        if (!html) return urls;

        try {
            const doc = new DOMParser().parseFromString(html, 'text/html');
            doc.querySelectorAll('img[src], img[data-src]').forEach((img) => {
                pushUrl(urls, img.getAttribute('src') || img.getAttribute('data-src'));
                const srcset = img.getAttribute('srcset');
                if (srcset) {
                    srcset.split(',').forEach((part) => {
                        pushUrl(urls, part.trim().split(/\s+/)[0]);
                    });
                }
            });
            doc.querySelectorAll('a[href]').forEach((a) => {
                const href = a.getAttribute('href');
                if (href && isLikelyFetchableImageUrl(normalizeUrl(href))) pushUrl(urls, href);
            });
        } catch (e) {
            /* ignore */
        }

        const srcRe = /\bsrc\s*=\s*["']([^"']+)["']/gi;
        let match;
        while ((match = srcRe.exec(html))) pushUrl(urls, match[1]);

        const srcsetRe = /\bsrcset\s*=\s*["']([^"']+)["']/gi;
        while ((match = srcsetRe.exec(html))) {
            match[1].split(',').forEach((part) => pushUrl(urls, part.trim().split(/\s+/)[0]));
        }

        return urls;
    }

    function parseTextUrls(raw) {
        const urls = [];
        if (!raw) return urls;
        raw.split(/\r?\n/).forEach((line) => {
            const url = normalizeUrl(line);
            if (url && isLikelyFetchableImageUrl(url)) pushUrl(urls, url);
        });
        return urls;
    }

    function mergeUrlLists(...lists) {
        const merged = [];
        lists.forEach((list) => {
            list.forEach((u) => {
                if (!merged.includes(u)) merged.push(u);
            });
        });
        return merged;
    }

    function readAllSyncStrings(dataTransfer) {
        const html = [];
        const uri = [];
        const plain = [];
        const other = [];

        if (!dataTransfer) return { html, uri, plain, other };

        const types = dataTransfer.types ? [...dataTransfer.types] : [];
        for (const type of types) {
            try {
                const value = dataTransfer.getData(type);
                if (!value) continue;
                const t = type.toLowerCase();
                if (t === 'text/html') html.push(value);
                else if (t === 'text/uri-list' || t === 'url') uri.push(value);
                else if (t === 'text/plain' || t === 'text/x-moz-url') plain.push(value);
                else other.push(value);
            } catch (e) {
                /* ignore */
            }
        }

        return { html, uri, plain, other };
    }

    function dedupeImageFiles(files) {
        const out = [];
        const seen = new Set();
        files.forEach((file) => {
            if (!file || !isImageFile(file)) return;
            const key = `${file.size}|${file.lastModified}`;
            if (seen.has(key)) return;
            seen.add(key);
            out.push(file);
        });
        return out;
    }

    function dedupeImageUrls(urls) {
        const out = [];
        const seen = new Set();
        urls.forEach((url) => {
            let key = url;
            try {
                const p = new URL(url);
                key = `${p.origin}${p.pathname}`;
            } catch (e) {
                /* keep full url */
            }
            if (seen.has(key)) return;
            seen.add(key);
            out.push(url);
        });
        return out;
    }

    function collectFilesSync(dataTransfer) {
        const fromItems = [];
        if (dataTransfer?.items) {
            for (let i = 0; i < dataTransfer.items.length; i++) {
                const item = dataTransfer.items[i];
                if (item.kind === 'file') {
                    const file = item.getAsFile();
                    if (file) fromItems.push(file);
                }
            }
        }
        if (fromItems.length) return dedupeImageFiles(fromItems);

        return dedupeImageFiles([...(dataTransfer?.files || [])]);
    }

    function collectUrlsSync(dataTransfer) {
        const parts = readAllSyncStrings(dataTransfer);

        const fromHtml = mergeUrlLists(...parts.html.map(parseHtmlUrls));
        const fromUri = mergeUrlLists(...parts.uri.map(parseTextUrls));
        const fromPlain = mergeUrlLists(...parts.plain.map(parseTextUrls));

        const fromOther = [];
        parts.other.forEach((chunk) => {
            fromOther.push(...parseHtmlUrls(chunk));
            fromOther.push(...parseTextUrls(chunk));
            const httpRe = /https?:\/\/[^\s"'<>]+/gi;
            let m;
            while ((m = httpRe.exec(chunk))) {
                const url = normalizeUrl(m[0]);
                if (url && isLikelyFetchableImageUrl(url)) pushUrl(fromOther, url);
            }
        });

        return dedupeImageUrls(mergeUrlLists(fromHtml, fromUri, fromPlain, fromOther));
    }

    function extractDropPayloadSync(dataTransfer) {
        const files = collectFilesSync(dataTransfer);
        if (files.length) return { files, urls: [] };
        return { files: [], urls: collectUrlsSync(dataTransfer) };
    }

    async function processDropPayload(payload, { multiple, onFiles, onUrl }) {
        if (payload.files.length && typeof onFiles === 'function') {
            const files = dedupeImageFiles(payload.files);
            await onFiles(multiple ? files : [files[0]]);
            return;
        }

        if (payload.urls.length && typeof onUrl === 'function') {
            const urls = dedupeImageUrls(payload.urls);
            // One web drag often carries the same image as file + URL, or via srcset.
            const list = multiple ? urls.slice(0, 1) : [urls[0]];
            for (const url of list) {
                await onUrl(url);
            }
            return;
        }

        if (payload.urls.length) {
            if (typeof showToast === 'function') {
                showToast(
                    'Could not use that link. Try saving the image to your computer and dropping the file, or click to browse.',
                    'error'
                );
            }
            return;
        }

        if (typeof showToast === 'function') {
            showToast(
                'No image detected. Drag the thumbnail from Google Images, paste a URL below, or save the file and drop it here.',
                'error'
            );
        }
    }

    function wireImageDropZone(zoneEl, options = {}) {
        if (!zoneEl || zoneEl.dataset.dropWired === '1') return;
        zoneEl.dataset.dropWired = '1';
        installWindowDropGuard();

        const multiple = Boolean(options.multiple);
        const onFiles = options.onFiles;
        const onUrl = options.onUrl;
        if (typeof onFiles !== 'function' && typeof onUrl !== 'function') return;

        const prevent = (e) => {
            e.preventDefault();
            e.stopPropagation();
        };

        const highlight = (e) => {
            prevent(e);
            if (e.dataTransfer) e.dataTransfer.dropEffect = 'copy';
            zoneEl.classList.add('is-drag-over');
        };

        zoneEl.addEventListener('dragenter', highlight);
        zoneEl.addEventListener('dragover', highlight);
        zoneEl.addEventListener('dragleave', (e) => {
            prevent(e);
            if (!zoneEl.contains(e.relatedTarget)) zoneEl.classList.remove('is-drag-over');
        });
        let dropInProgress = false;
        zoneEl.addEventListener('drop', (e) => {
            prevent(e);
            zoneEl.classList.remove('is-drag-over');
            if (dropInProgress) return;
            const payload = extractDropPayloadSync(e.dataTransfer);
            dropInProgress = true;
            void processDropPayload(payload, { multiple, onFiles, onUrl }).finally(() => {
                dropInProgress = false;
            });
        });

        zoneEl.addEventListener('paste', (e) => {
            const items = e.clipboardData?.items;
            if (!items) return;
            const imageFiles = [];
            for (let i = 0; i < items.length; i++) {
                if (items[i].type.startsWith('image/')) {
                    const file = items[i].getAsFile();
                    if (file) imageFiles.push(file);
                }
            }
            if (!imageFiles.length) return;
            e.preventDefault();
            e.stopPropagation();
            void processDropPayload({ files: imageFiles, urls: [] }, { multiple, onFiles, onUrl });
        });
    }

    function wireImageUrlField(inputEl, { onUrl, onFiles } = {}) {
        if (!inputEl) return;
        inputEl.addEventListener('click', (e) => e.stopPropagation());
        inputEl.addEventListener('keydown', (e) => {
            if (e.key !== 'Enter') return;
            e.preventDefault();
            const url = normalizeUrl(inputEl.value);
            if (!url) {
                if (typeof showToast === 'function') showToast('Enter a valid image URL', 'error');
                return;
            }
            if (typeof onUrl === 'function') void onUrl(url);
        });
        inputEl.addEventListener('paste', (e) => {
            const items = e.clipboardData?.items;
            if (!items) return;
            const imageFiles = [];
            for (let i = 0; i < items.length; i++) {
                if (items[i].type.startsWith('image/')) {
                    const file = items[i].getAsFile();
                    if (file) imageFiles.push(file);
                }
            }
            if (!imageFiles.length) return;
            e.preventDefault();
            if (typeof onFiles === 'function') {
                void onFiles([imageFiles[0]]);
            }
        });
    }

    function imageUploadHint() {
        return '<p style="margin-top: 8px; color: #64748b; font-size: 0.875rem;">Click, drag, or paste an image (desktop file or from Google Images)</p>';
    }

    global.wireImageDropZone = wireImageDropZone;
    global.wireImageUrlField = wireImageUrlField;
    global.imageUploadHint = imageUploadHint;
    global.extractImageDropPayload = extractDropPayloadSync;
    global.dedupeImageFiles = dedupeImageFiles;
})(window);
