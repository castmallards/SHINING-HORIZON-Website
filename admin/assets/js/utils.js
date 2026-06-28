// Utility Functions

// Sidebar toggle
function toggleSidebar() {
    const sidebar = document.getElementById('admin-sidebar');
    const main = document.querySelector('.main-content');
    if (!sidebar) return;
    const collapsed = sidebar.classList.toggle('collapsed');
    if (main) main.classList.toggle('expanded', collapsed);
    document.body.classList.toggle('sidebar-collapsed', collapsed);
    try { localStorage.setItem('sidebarCollapsed', collapsed ? '1' : '0'); } catch(e) {}
}
(function initSidebar() {
    document.addEventListener('DOMContentLoaded', function () {
        // Inject the floating reopen button into the body
        const btn = document.createElement('button');
        btn.className = 'sidebar-reopen-btn';
        btn.setAttribute('aria-label', 'Open sidebar');
        btn.setAttribute('title', 'Open sidebar');
        btn.innerHTML = '<svg width="14" height="14" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2.5" d="M9 5l7 7-7 7"/></svg>';
        btn.onclick = toggleSidebar;
        document.body.appendChild(btn);

        try {
            if (localStorage.getItem('sidebarCollapsed') === '1') {
                const sidebar = document.getElementById('admin-sidebar');
                const main = document.querySelector('.main-content');
                if (sidebar) sidebar.classList.add('collapsed');
                if (main) main.classList.add('expanded');
                document.body.classList.add('sidebar-collapsed');
            }
        } catch(e) {}
    });
})();

// Show toast notification
function showToast(message, type = 'success') {
    const container = document.getElementById('toast-container') || createToastContainer();
    
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.innerHTML = `
        <svg width="20" height="20" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            ${type === 'success' 
                ? '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"/>'
                : '<path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>'}
        </svg>
        <span>${message}</span>
    `;
    
    container.appendChild(toast);
    
    setTimeout(() => {
        toast.style.animation = 'slideIn 0.3s ease reverse';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

function createToastContainer() {
    const container = document.createElement('div');
    container.id = 'toast-container';
    container.className = 'toast-container';
    document.body.appendChild(container);
    return container;
}

// Show loading
function showLoading(container) {
    container.innerHTML = `
        <div class="loading">
            <div class="spinner"></div>
        </div>
    `;
}

// Show empty state
function showEmptyState(container, message = 'No items found') {
    container.innerHTML = `
        <tr>
            <td colspan="20">
                <div class="empty-state">
                    <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4"/>
                    </svg>
                    <h3>${message}</h3>
                    <p>Click the button above to add a new item</p>
                </div>
            </td>
        </tr>
    `;
}

// Open modal
function openModal(modalId) {
    document.getElementById(modalId).classList.add('active');
}

// Close modal
function closeModal(modalId) {
    document.getElementById(modalId).classList.remove('active');
}

// Confirm dialog
function confirmDialog(message) {
    return new Promise((resolve) => {
        const result = confirm(message);
        resolve(result);
    });
}

// Format date
function formatDate(dateString) {
    if (!dateString) return '-';
    const date = new Date(dateString);
    return date.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric',
    });
}

// Truncate text
function truncateText(text, maxLength = 50) {
    if (!text) return '';
    if (text.length <= maxLength) return text;
    return text.substring(0, maxLength) + '...';
}

// Escape HTML
function escapeHtml(text) {
    if (!text) return '';
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Debounce function
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

// Update page title
function setPageTitle(title) {
    document.title = `${title} - Shining Horizon Admin`;
    const headerTitle = document.querySelector('.header-title');
    if (headerTitle) headerTitle.textContent = title;
}

// Initialize user info in header
function initUserInfo() {
    const user = getCurrentUser();
    if (user) {
        const userNameEl = document.querySelector('.user-name');
        const userRoleEl = document.querySelector('.user-role');
        const userAvatarEl = document.querySelector('.user-avatar');

        if (userNameEl) userNameEl.textContent = user.full_name || user.username;
        if (userRoleEl) userRoleEl.textContent = (typeof roleLabel === 'function') ? roleLabel(user.role) : user.role;
        if (userAvatarEl) userAvatarEl.textContent = (user.full_name || user.username).charAt(0).toUpperCase();
    }
}

// Handle image upload preview
function handleImageUpload(inputId, previewId, callback) {
    const input = document.getElementById(inputId);
    const preview = document.getElementById(previewId);
    
    input.addEventListener('change', async (e) => {
        const file = e.target.files[0];
        if (!file) return;
        
        // Show preview
        const reader = new FileReader();
        reader.onload = (e) => {
            preview.innerHTML = `<img src="${e.target.result}" class="image-preview" alt="Preview">`;
        };
        reader.readAsDataURL(file);
        
        // Call callback if provided
        if (callback) {
            callback(file);
        }
    });
}

// Translate a stored image base path into a public preview URL. Mirrors the
// server-side variant_url() so legacy v1 paths and new v2 base paths both work.
function adminImageUrl(path, size = 'card') {
    if (!path) return null;
    const p = String(path).trim();
    if (/^(https?:|data:)/.test(p)) return p;
    if (p.startsWith('/')) return p;
    if (/\.(png|jpe?g|gif|webp|svg)$/i.test(p)) return '/' + p.replace(/^backend\//, '');
    const noPrefix = p.replace(/^uploads\//, '');
    const parts = noPrefix.split('/');
    if (parts.length >= 2) {
        const folder = parts[0];
        const id = parts.slice(1).join('/');
        return `/uploads/${folder}/${size}/${id}.webp`;
    }
    return '/' + p.replace(/^backend\//, '');
}

// Render the v2 status pill (Phase 4.3 / 4.4 helpers).
function renderStatusPill(status, isActive) {
    const s = (status || (isActive ? 'published' : 'draft')).toLowerCase();
    const klass = s === 'published' ? 'published' : 'draft';
    const label = s === 'published' ? 'Published' : 'Draft';
    return `<span class="status-pill ${klass}">${label}</span>`;
}

// Open the public-facing URL of an entity in a new tab (Phase 4.11).
function previewUrl(entity_type, slug, status) {
    if (!slug) return null;
    let path = null;
    if (entity_type === 'product') path = `/product/${slug}`;
    else if (entity_type === 'category' || entity_type === 'subcategory') path = `/category/${slug}`;
    else if (entity_type === 'brand') path = `/brand/${slug}`;
    if (!path) return null;
    // Drafts are 404 to anonymous visitors — append ?preview=1 so the public
    // route lets the authenticated admin through and shows a "PREVIEW MODE" banner.
    if (status && status !== 'published') path += '?preview=1';
    return path;
}

function sanitizeRichHtml(html) {
    if (!html) return html;
    const tmp = document.createElement('div');
    tmp.innerHTML = html;
    tmp.querySelectorAll('[style]').forEach((el) => {
        el.style.removeProperty('background-color');
        el.style.removeProperty('color');
        if (!el.getAttribute('style').trim()) el.removeAttribute('style');
    });
    return tmp.innerHTML;
}

function listRowNumber(pageSkip, index) {
    return pageSkip + index + 1;
}

/** Normalize list API responses ({ items, total } or legacy array). */
function unwrapListResponse(res) {
    if (Array.isArray(res)) return { items: res, total: res.length, skip: 0, limit: res.length };
    return {
        items: res.items || [],
        total: typeof res.total === 'number' ? res.total : (res.items || []).length,
        skip: res.skip || 0,
        limit: res.limit || (res.items || []).length,
    };
}

function renderListPagination({ total, pageSkip, pageSize }) {
    const info = document.getElementById('pagination-info');
    const pageEl = document.getElementById('pagination-page');
    const prev = document.getElementById('pg-prev');
    const next = document.getElementById('pg-next');
    if (!info) return;
    const start = total ? pageSkip + 1 : 0;
    const end = Math.min(pageSkip + pageSize, total);
    const totalPages = total ? Math.ceil(total / pageSize) : 1;
    const currentPage = total ? Math.floor(pageSkip / pageSize) + 1 : 1;
    info.textContent = total ? `Showing ${start.toLocaleString()}–${end.toLocaleString()} of ${total.toLocaleString()}` : '';
    if (pageEl) pageEl.textContent = total ? `Page ${currentPage} of ${totalPages}` : '';
    if (prev) prev.disabled = pageSkip <= 0;
    if (next) next.disabled = end >= total;
}

function readFocusParam() {
    const focus = new URLSearchParams(window.location.search).get('focus');
    if (!focus) return null;
    const id = parseInt(focus, 10);
    return Number.isNaN(id) ? null : id;
}

function clearFocusFromUrl() {
    const params = new URLSearchParams(window.location.search);
    if (!params.has('focus')) return;
    params.delete('focus');
    const qs = params.toString();
    history.replaceState({}, '', qs ? `${window.location.pathname.split('/').pop()}?${qs}` : window.location.pathname.split('/').pop());
}

function highlightEntityRow(entityId, attr = 'data-entity-id') {
    document.querySelectorAll('tr.row-focused').forEach((row) => row.classList.remove('row-focused'));
    const row = document.querySelector(`tr[${attr}="${entityId}"]`);
    if (row) {
        row.classList.add('row-focused');
        row.scrollIntoView({ block: 'nearest', behavior: 'smooth' });
    }
}

function adminEntityUrl(entityType, entityId) {
    if (!entityId) return null;
    const map = {
        product: 'products.html',
        category: 'categories.html',
        brand: 'brands.html',
        subcategory: 'subcategories.html',
    };
    const page = map[entityType];
    return page ? `${page}?focus=${entityId}` : null;
}

function formatAuditUser(entry) {
    if (!entry.username && !entry.full_name) return '—';
    if (entry.full_name && entry.username) {
        return `${entry.full_name} (@${entry.username})`;
    }
    return entry.full_name || entry.username || '—';
}

const AUDIT_FIELD_LABELS = {
    name: 'Name',
    slug: 'Slug',
    part_number: 'Part number',
    category_id: 'Category',
    subcategory_id: 'Subcategory',
    brand_id: 'Brand',
    status: 'Status',
    is_active: 'Active',
    is_featured: 'Featured',
    image: 'Image',
    datasheet_url: 'Datasheet',
    display_order: 'Display order',
    short_description: 'Short description',
    meta_title: 'Meta title',
    meta_description: 'Meta description',
    description: 'Description',
    type: 'Type',
    show_on_home: 'Show on home',
    logo: 'Logo',
    website_url: 'Website',
    country: 'Country',
};

function auditFieldLabel(key) {
    return AUDIT_FIELD_LABELS[key] || key.replace(/_/g, ' ');
}

// Set active nav item
function setActiveNav(page) {
    document.querySelectorAll('.nav-item').forEach(item => {
        item.classList.remove('active');
        if (item.dataset.page === page) {
            item.classList.add('active');
        }
    });
}

// Populate select with options
function populateSelect(selectId, items, valueKey = 'id', labelKey = 'name', placeholder = 'Select...') {
    const select = document.getElementById(selectId);
    if (!select) return;
    
    select.innerHTML = `<option value="">${placeholder}</option>`;
    items.forEach(item => {
        select.innerHTML += `<option value="${item[valueKey]}">${escapeHtml(item[labelKey])}</option>`;
    });
}

// Get form data as object
function getFormData(formId) {
    const form = document.getElementById(formId);
    const data = {};

    // FormData only iterates CHECKED checkboxes — unchecked ones disappear
    // entirely, so we'd never send `false` to the API. Walk the form's own
    // elements instead so every named field shows up exactly once.
    Array.from(form.elements).forEach(el => {
        if (!el.name || el.disabled) return;

        if (el.type === 'checkbox') {
            data[el.name] = el.checked;
            return;
        }
        if (el.type === 'radio') {
            if (el.checked) data[el.name] = el.value;
            return;
        }
        if (el.type === 'submit' || el.type === 'button' || el.type === 'reset') return;

        const raw = el.value;
        if (el.type === 'number') {
            // Empty number → omit (let the backend keep the previous value);
            // "0" must round-trip as 0, not be dropped.
            if (raw === '' || raw === null) return;
            const n = Number(raw);
            data[el.name] = Number.isFinite(n) ? n : raw;
            return;
        }
        if (raw === '') return;
        data[el.name] = raw;
    });

    return data;
}

// Reset form
function resetForm(formId) {
    const form = document.getElementById(formId);
    if (form) form.reset();
}

// Fill form with data
function fillForm(formId, data) {
    const form = document.getElementById(formId);
    if (!form) return;

    Object.keys(data).forEach(key => {
        const element = form.elements[key];
        if (!element) return;

        if (element.type === 'checkbox') {
            element.checked = !!data[key];
            return;
        }
        // Use nullish coalescing so 0, false and '' all round-trip correctly
        // (the previous `data[key] || ''` turned display_order=0 into blank).
        const v = data[key];
        element.value = v === null || v === undefined ? '' : v;
    });
}
