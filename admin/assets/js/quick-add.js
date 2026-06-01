// Inline create category / subcategory / brand from product or subcategory forms.
(function (global) {
    let config = null;
    let pendingType = null;

    function defaultStatus() {
        const user = typeof getCachedUser === 'function' ? getCachedUser() : null;
        return user && typeof canPublish === 'function' && canPublish(user) ? 'published' : 'draft';
    }

    function ensureModal() {
        if (document.getElementById('quick-add-modal')) return;
        const overlay = document.createElement('div');
        overlay.className = 'modal-overlay';
        overlay.id = 'quick-add-modal';
        overlay.style.zIndex = '500';
        overlay.innerHTML = `
            <div class="modal" style="max-width: 480px; width: calc(100vw - 32px);">
                <div class="modal-header">
                    <h3 class="modal-title" id="quick-add-title">Quick add</h3>
                    <button type="button" class="modal-close" aria-label="Close" id="quick-add-close">
                        <svg width="16" height="16" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/></svg>
                    </button>
                </div>
                <form id="quick-add-form">
                    <div class="modal-body" id="quick-add-body"></div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" id="quick-add-cancel">Cancel</button>
                        <button type="submit" class="btn btn-primary" id="quick-add-save">Save</button>
                    </div>
                </form>
            </div>
        `;
        document.body.appendChild(overlay);
        overlay.querySelector('#quick-add-close').addEventListener('click', close);
        overlay.querySelector('#quick-add-cancel').addEventListener('click', close);
        overlay.addEventListener('click', (e) => {
            if (e.target === overlay) close();
        });
        overlay.querySelector('#quick-add-form').addEventListener('submit', submit);
    }

    function close() {
        const overlay = document.getElementById('quick-add-modal');
        if (overlay) overlay.classList.remove('active');
        pendingType = null;
    }

    function open(type) {
        ensureModal();
        pendingType = type;
        const body = document.getElementById('quick-add-body');
        const title = document.getElementById('quick-add-title');
        const status = defaultStatus();

        if (type === 'category') {
            title.textContent = 'New category';
            body.innerHTML = `
                <div class="form-group">
                    <label class="form-label">Name *</label>
                    <input type="text" id="qa-name" class="form-input" required autofocus>
                </div>
                <div class="form-group">
                    <label class="form-label">Type *</label>
                    <select id="qa-type" class="form-select">
                        <option value="simple">Simple (product list)</option>
                        <option value="detailed">Detailed (has subcategories)</option>
                    </select>
                </div>
                <div class="form-group">
                    <label class="form-label">Status</label>
                    <select id="qa-status" class="form-select">
                        <option value="draft"${status === 'draft' ? ' selected' : ''}>Draft</option>
                        <option value="published"${status === 'published' ? ' selected' : ''}>Published</option>
                    </select>
                </div>
            `;
        } else if (type === 'subcategory') {
            if (typeof config.getCategoriesList === 'function') {
                config.categories = config.getCategoriesList();
            }
            const catId = config.getCategoryId ? config.getCategoryId() : '';
            title.textContent = 'New subcategory';
            const catOptions = (config.categories || [])
                .filter((c) => c.type === 'detailed')
                .map((c) => `<option value="${c.id}"${String(c.id) === String(catId) ? ' selected' : ''}>${escapeHtml(c.name)}</option>`)
                .join('');
            body.innerHTML = `
                <div class="form-group">
                    <label class="form-label">Category *</label>
                    <select id="qa-category-id" class="form-select" required>${catOptions || '<option value="">— No detailed categories —</option>'}</select>
                </div>
                <div class="form-group">
                    <label class="form-label">Name *</label>
                    <input type="text" id="qa-name" class="form-input" required autofocus>
                </div>
                <div class="form-group">
                    <label class="form-label">Status</label>
                    <select id="qa-status" class="form-select">
                        <option value="draft"${status === 'draft' ? ' selected' : ''}>Draft</option>
                        <option value="published"${status === 'published' ? ' selected' : ''}>Published</option>
                    </select>
                </div>
            `;
        } else if (type === 'brand') {
            title.textContent = 'New brand';
            body.innerHTML = `
                <div class="form-group">
                    <label class="form-label">Name *</label>
                    <input type="text" id="qa-name" class="form-input" required autofocus>
                </div>
                <div class="form-group">
                    <label class="form-label">Status</label>
                    <select id="qa-status" class="form-select">
                        <option value="draft"${status === 'draft' ? ' selected' : ''}>Draft</option>
                        <option value="published"${status === 'published' ? ' selected' : ''}>Published</option>
                    </select>
                </div>
            `;
        }

        document.getElementById('quick-add-modal').classList.add('active');
        body.querySelector('#qa-name')?.focus();
    }

    async function submit(e) {
        e.preventDefault();
        const name = document.getElementById('qa-name')?.value?.trim();
        if (!name) {
            showToast('Name is required', 'error');
            return;
        }
        const status = document.getElementById('qa-status')?.value || defaultStatus();

        try {
            let created = null;
            if (pendingType === 'category') {
                const type = document.getElementById('qa-type')?.value || 'simple';
                created = await categoriesAPI.create({ name, type, status, is_active: true });
                if (config.reloadCategories) await config.reloadCategories();
                if (config.selects?.category) {
                    document.getElementById(config.selects.category).value = created.id;
                }
                if (config.onCategoryChange) await config.onCategoryChange();
                showToast('Category created');
            } else if (pendingType === 'subcategory') {
                const categoryId = document.getElementById('qa-category-id')?.value;
                if (!categoryId) {
                    showToast('Select a category first', 'error');
                    return;
                }
                created = await subcategoriesAPI.create({
                    name,
                    category_id: Number(categoryId),
                    status,
                    is_active: true,
                });
                if (config.reloadCategories) await config.reloadCategories();
                if (config.selects?.category) {
                    document.getElementById(config.selects.category).value = categoryId;
                }
                if (config.onCategoryChange) await config.onCategoryChange();
                if (config.selects?.subcategory) {
                    document.getElementById(config.selects.subcategory).value = created.id;
                }
                showToast('Subcategory created');
            } else if (pendingType === 'brand') {
                created = await brandsAPI.create({ name, status, is_active: true });
                if (config.reloadBrands) await config.reloadBrands();
                if (config.selects?.brand) {
                    document.getElementById(config.selects.brand).value = created.id;
                }
                showToast('Brand created');
            }
            close();
        } catch (err) {
            showToast(err.message || 'Failed to create', 'error');
        }
    }

    const QUICK_ADD_LABELS = {
        category: 'New Category',
        subcategory: 'New Subcategory',
        brand: 'New Brand',
    };

    function attachQuickAddButtons(root) {
        if (!root) return;
        root.querySelectorAll('.select-with-action[data-quick-add]').forEach((wrap) => {
            if (wrap.querySelector('.btn-quick-add')) return;
            const type = wrap.getAttribute('data-quick-add');
            if (!type) return;

            const label =
                wrap.getAttribute('data-quick-add-label') ||
                QUICK_ADD_LABELS[type] ||
                'New';

            const btn = document.createElement('button');
            btn.type = 'button';
            btn.className = 'btn-quick-add';
            btn.textContent = label;
            btn.title = label;
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                e.stopPropagation();
                open(type);
            });
            wrap.appendChild(btn);
        });
    }

    function init(options) {
        config = options || {};
        ensureModal();
        attachQuickAddButtons(config.root || document);
    }

    global.QuickAdd = { init, open, close };
})(window);
