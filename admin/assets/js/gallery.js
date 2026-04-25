// Multi-image gallery widget (Phase 4.6).
// Backs a hidden input with a JSON array of image base paths. Supports
// drag-and-drop reordering (HTML5), per-tile delete, and click-to-upload.

(function () {
    function mount({ inputId, containerId, folder = 'products', onChange = null }) {
        const input = document.getElementById(inputId);
        const container = document.getElementById(containerId);
        if (!input || !container) return null;

        let items = [];
        try { items = JSON.parse(input.value || '[]'); }
        catch (e) { items = []; }

        const fileInput = document.createElement('input');
        fileInput.type = 'file';
        fileInput.accept = 'image/*';
        fileInput.multiple = true;
        fileInput.style.display = 'none';
        container.appendChild(fileInput);

        const grid = document.createElement('div');
        grid.className = 'gallery-grid';
        container.appendChild(grid);

        const addTile = document.createElement('button');
        addTile.type = 'button';
        addTile.className = 'gallery-add';
        addTile.innerHTML = `
            <svg width="22" height="22" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/>
            </svg>
            <span>Add images</span>
        `;
        addTile.addEventListener('click', () => fileInput.click());
        container.appendChild(addTile);

        function persist() {
            input.value = JSON.stringify(items);
            if (typeof onChange === 'function') onChange(items);
        }

        function render() {
            grid.innerHTML = items.map((path, i) => `
                <div class="gallery-tile" draggable="true" data-index="${i}">
                    <img src="/uploads/${path.replace(/^uploads\//, '').replace(/\.(png|jpg|jpeg|gif|webp)$/i, '')}/card/${''}" data-path="${escapeAttr(path)}" alt="Image ${i + 1}">
                    <button type="button" class="gallery-remove" data-index="${i}" title="Remove">×</button>
                </div>
            `).join('');
            // Use the original path verbatim — keep things working even for legacy
            // paths that already include extensions.
            grid.querySelectorAll('img').forEach(img => {
                const path = img.getAttribute('data-path') || '';
                img.src = pickPreviewUrl(path);
            });
            wireDnD();
            grid.querySelectorAll('.gallery-remove').forEach(btn => {
                btn.addEventListener('click', () => {
                    const i = Number(btn.getAttribute('data-index'));
                    items.splice(i, 1);
                    persist();
                    render();
                });
            });
        }

        function pickPreviewUrl(path) {
            if (!path) return '';
            const p = String(path).trim();
            if (/^https?:|^data:|^\//.test(p)) return p.startsWith('/') ? p : p;
            if (/\.(png|jpe?g|gif|webp|svg)$/i.test(p)) return '/' + p.replace(/^backend\//, '');
            // Modern v2 base path → ask for the card-size variant.
            const noPrefix = p.replace(/^uploads\//, '');
            const parts = noPrefix.split('/');
            if (parts.length >= 2) {
                const folder = parts[0];
                const id = parts.slice(1).join('/');
                return `/uploads/${folder}/card/${id}.webp`;
            }
            return '/' + p.replace(/^backend\//, '');
        }

        function escapeAttr(s) { return String(s).replace(/"/g, '&quot;'); }

        // Drag and drop reordering
        let dragSrc = null;
        function wireDnD() {
            grid.querySelectorAll('.gallery-tile').forEach(tile => {
                tile.addEventListener('dragstart', (e) => {
                    dragSrc = Number(tile.getAttribute('data-index'));
                    tile.classList.add('is-dragging');
                    e.dataTransfer.effectAllowed = 'move';
                });
                tile.addEventListener('dragend', () => tile.classList.remove('is-dragging'));
                tile.addEventListener('dragover', (e) => { e.preventDefault(); tile.classList.add('is-drop-target'); });
                tile.addEventListener('dragleave', () => tile.classList.remove('is-drop-target'));
                tile.addEventListener('drop', (e) => {
                    e.preventDefault();
                    tile.classList.remove('is-drop-target');
                    const dst = Number(tile.getAttribute('data-index'));
                    if (dragSrc == null || dragSrc === dst) return;
                    const [moved] = items.splice(dragSrc, 1);
                    items.splice(dst, 0, moved);
                    dragSrc = null;
                    persist();
                    render();
                });
            });
        }

        fileInput.addEventListener('change', async () => {
            const files = Array.from(fileInput.files || []);
            fileInput.value = '';
            for (const f of files) {
                try {
                    const result = await uploadAPI.uploadImage(f, folder);
                    items.push(result.path);
                    persist();
                    render();
                } catch (err) {
                    if (typeof showToast === 'function') showToast(err.message, 'error');
                    else alert(err.message);
                }
            }
        });

        function setValue(value) {
            items = Array.isArray(value) ? [...value] : [];
            persist();
            render();
        }

        render();
        return { setValue, getValue: () => [...items] };
    }

    window.GalleryWidget = { mount };
})();
