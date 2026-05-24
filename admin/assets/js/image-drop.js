// Drag-and-drop onto .image-upload zones (primary image / logo).
(function (global) {
    function wireImageDropZone(zoneEl, options = {}) {
        if (!zoneEl || zoneEl.dataset.dropWired === '1') return;
        zoneEl.dataset.dropWired = '1';

        const multiple = Boolean(options.multiple);
        const onFiles = options.onFiles;
        if (typeof onFiles !== 'function') return;

        const prevent = (e) => {
            e.preventDefault();
            e.stopPropagation();
        };

        zoneEl.addEventListener('dragenter', (e) => {
            prevent(e);
            zoneEl.classList.add('is-drag-over');
        });
        zoneEl.addEventListener('dragover', (e) => {
            prevent(e);
            zoneEl.classList.add('is-drag-over');
        });
        zoneEl.addEventListener('dragleave', (e) => {
            prevent(e);
            if (!zoneEl.contains(e.relatedTarget)) zoneEl.classList.remove('is-drag-over');
        });
        zoneEl.addEventListener('drop', (e) => {
            prevent(e);
            zoneEl.classList.remove('is-drag-over');
            const files = [...(e.dataTransfer?.files || [])].filter((f) => f.type.startsWith('image/'));
            if (!files.length) return;
            onFiles(multiple ? files : [files[0]]);
        });
    }

    function imageUploadHint() {
        return '<p style="margin-top: 8px; color: #64748b; font-size: 0.875rem;">Click or drag image here</p>';
    }

    global.wireImageDropZone = wireImageDropZone;
    global.imageUploadHint = imageUploadHint;
})(window);
