// Specifications key/value builder (Phase 4.7).
// Backs a hidden input with a JSON array of {key, value} rows.

(function () {
    function mount({ inputId, containerId, addLabel = 'Add specification' }) {
        const input = document.getElementById(inputId);
        const container = document.getElementById(containerId);
        if (!input || !container) return null;

        let rows = [];
        try {
            const parsed = JSON.parse(input.value || '[]');
            rows = Array.isArray(parsed)
                ? parsed.map(r => ({ key: r.key || '', value: r.value || '' }))
                : [];
        } catch (e) { rows = []; }

        const list = document.createElement('div');
        list.className = 'specs-list';
        container.appendChild(list);

        const addBtn = document.createElement('button');
        addBtn.type = 'button';
        addBtn.className = 'btn btn-secondary btn-sm specs-add';
        addBtn.innerHTML = `
            <svg width="14" height="14" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4"/>
            </svg>
            ${addLabel}
        `;
        addBtn.addEventListener('click', () => {
            rows.push({ key: '', value: '' });
            persist();
            render(true);
        });
        container.appendChild(addBtn);

        function persist() {
            const cleaned = rows
                .map(r => ({ key: (r.key || '').trim(), value: (r.value || '').trim() }))
                .filter(r => r.key !== '' || r.value !== '');
            input.value = JSON.stringify(cleaned);
        }

        function render(focusLast = false) {
            list.innerHTML = rows.map((r, i) => `
                <div class="specs-row" data-index="${i}">
                    <input type="text" class="form-input specs-key" placeholder="Field" value="${escapeAttr(r.key)}">
                    <input type="text" class="form-input specs-value" placeholder="Value" value="${escapeAttr(r.value)}">
                    <button type="button" class="specs-remove" title="Remove" aria-label="Remove">
                        <svg width="16" height="16" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
                    </button>
                </div>
            `).join('');

            list.querySelectorAll('.specs-row').forEach(row => {
                const i = Number(row.getAttribute('data-index'));
                row.querySelector('.specs-key').addEventListener('input', (e) => {
                    rows[i].key = e.target.value;
                    persist();
                });
                row.querySelector('.specs-value').addEventListener('input', (e) => {
                    rows[i].value = e.target.value;
                    persist();
                });
                row.querySelector('.specs-remove').addEventListener('click', () => {
                    rows.splice(i, 1);
                    persist();
                    render();
                });
            });

            if (focusLast) {
                const last = list.querySelector('.specs-row:last-child .specs-key');
                if (last) last.focus();
            }
        }

        function escapeAttr(s) { return String(s == null ? '' : s).replace(/"/g, '&quot;'); }

        function setValue(value) {
            rows = Array.isArray(value)
                ? value.map(r => ({ key: r.key || '', value: r.value || '' }))
                : [];
            persist();
            render();
        }

        render();
        return { setValue, getValue: () => rows.map(r => ({ key: r.key, value: r.value })) };
    }

    window.SpecsWidget = { mount };
})();
