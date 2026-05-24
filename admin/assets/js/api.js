// Admin API client (Phase 4.1 + 4.2).
// All endpoints live under /api/* on the same origin as the admin SPA,
// so cookies are sent automatically. Mutating requests carry the
// double-submit CSRF header read from the csrf_token cookie.

const API_BASE = '/api';
const MUTATING_METHODS = new Set(['POST', 'PUT', 'PATCH', 'DELETE']);

async function apiRequest(endpoint, options = {}) {
    const method = (options.method || 'GET').toUpperCase();
    const headers = { 'Content-Type': 'application/json', ...(options.headers || {}) };

    if (MUTATING_METHODS.has(method)) {
        const token = getCsrfToken();
        if (token) headers['X-CSRF-Token'] = token;
    }

    const response = await fetch(`${API_BASE}${endpoint}`, {
        ...options,
        method,
        headers,
        credentials: 'same-origin',
    });

    // Auto-redirect to login on session expiry. Skip for /auth/login itself
    // so the login form can surface the error inline.
    if (response.status === 401 && !endpoint.startsWith('/auth/login')) {
        clearCachedUser();
        if (typeof redirectToLogin === 'function') redirectToLogin();
        throw new Error('Session expired. Please sign in again.');
    }

    let data = null;
    if (response.status !== 204) {
        try { data = await response.json(); }
        catch (e) { data = null; }
    }

    if (!response.ok) {
        const detail = (data && (data.detail || data.message)) || `Request failed (${response.status})`;
        throw new Error(typeof detail === 'string' ? detail : JSON.stringify(detail));
    }
    return data;
}

// ─── Auth ──────────────────────────────────────────────────────────────

const authAPI = {
    async login(username, password) {
        const data = await apiRequest('/auth/login', {
            method: 'POST',
            body: JSON.stringify({ username, password }),
        });
        if (data && data.user) setCachedUser(data.user);
        return data;
    },
    async logout() {
        try { await apiRequest('/auth/logout', { method: 'POST' }); }
        catch (e) { /* ignore — cookie may already be gone */ }
        clearCachedUser();
        window.location.href = ADMIN_LOGIN_PAGE;
    },
    getMe: () => apiRequest('/auth/me'),
};

// ─── Resources ────────────────────────────────────────────────────────

function buildQuery(params) {
    const q = new URLSearchParams();
    Object.entries(params || {}).forEach(([k, v]) => {
        if (v !== undefined && v !== null && v !== '') q.append(k, v);
    });
    const s = q.toString();
    return s ? `?${s}` : '';
}

const categoriesAPI = {
    getAll: (params = {}) => apiRequest(`/categories/${buildQuery({ include_inactive: true, ...params })}`),
    getById: (id) => apiRequest(`/categories/${id}`),
    create: (data) => apiRequest('/categories/', { method: 'POST', body: JSON.stringify(data) }),
    update: (id, data) => apiRequest(`/categories/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
    delete: (id) => apiRequest(`/categories/${id}`, { method: 'DELETE' }),
};

const subcategoriesAPI = {
    getAll: (categoryId = null, params = {}) =>
        apiRequest(`/subcategories/${buildQuery({ include_inactive: true, category_id: categoryId, ...params })}`),
    getById: (id) => apiRequest(`/subcategories/${id}`),
    create: (data) => apiRequest('/subcategories/', { method: 'POST', body: JSON.stringify(data) }),
    update: (id, data) => apiRequest(`/subcategories/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
    delete: (id) => apiRequest(`/subcategories/${id}`, { method: 'DELETE' }),
};

const brandsAPI = {
    getAll: (params = {}) => apiRequest(`/brands/${buildQuery({ include_inactive: true, ...params })}`),
    getById: (id) => apiRequest(`/brands/${id}`),
    create: (data) => apiRequest('/brands/', { method: 'POST', body: JSON.stringify(data) }),
    update: (id, data) => apiRequest(`/brands/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
    delete: (id) => apiRequest(`/brands/${id}`, { method: 'DELETE' }),
};

const productsAPI = {
    // Returns { items, total, skip, limit }. Pass {category_id, subcategory_id,
    // brand_id, status, search, skip, limit, include_inactive} to filter.
    getAll: (params = {}) => apiRequest(`/products/${buildQuery({ include_inactive: true, limit: 50, ...params })}`),
    getById: (id) => apiRequest(`/products/${id}`),
    create: (data) => apiRequest('/products/', { method: 'POST', body: JSON.stringify(data) }),
    update: (id, data) => apiRequest(`/products/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
    delete: (id) => apiRequest(`/products/${id}`, { method: 'DELETE' }),
    bulk: (ids, action) => apiRequest('/products/bulk', { method: 'POST', body: JSON.stringify({ ids, action }) }),
    validation: () => apiRequest('/products/validation'),
    checkPartNumber: (partNumber, excludeId = null) =>
        apiRequest(
            `/products/check-part-number${buildQuery({
                part_number: partNumber,
                exclude_id: excludeId,
            })}`
        ),
};

const usersAPI = {
    getAll: () => apiRequest('/users/'),
    getById: (id) => apiRequest(`/users/${id}`),
    create: (data) => apiRequest('/users/', { method: 'POST', body: JSON.stringify(data) }),
    update: (id, data) => apiRequest(`/users/${id}`, { method: 'PUT', body: JSON.stringify(data) }),
    delete: (id) => apiRequest(`/users/${id}`, { method: 'DELETE' }),
};

const auditAPI = {
    list: (params = {}) => apiRequest(`/audit/${buildQuery(params)}`),
};

const uploadAPI = {
    uploadImage: async (file, folder) => {
        const formData = new FormData();
        formData.append('file', file);
        const headers = {};
        const token = getCsrfToken();
        if (token) headers['X-CSRF-Token'] = token;

        const response = await fetch(`${API_BASE}/upload/image/${folder}`, {
            method: 'POST',
            credentials: 'same-origin',
            headers,
            body: formData,
        });
        if (response.status === 401) {
            clearCachedUser();
            redirectToLogin();
            throw new Error('Session expired. Please sign in again.');
        }
        if (!response.ok) {
            const error = await response.json().catch(() => ({}));
            throw new Error(error.detail || 'Upload failed');
        }
        return response.json();
    },
    uploadImageFromUrl: async (url, folder) => {
        return apiRequest(`/upload/image-from-url/${folder}`, {
            method: 'POST',
            body: JSON.stringify({ url }),
        });
    },
};

const importAPI = {
    importCategories: (file) => importFile('/import/categories', file),
    importSubcategories: (file) => importFile('/import/subcategories', file),
    importBrands: (file) => importFile('/import/brands', file),
    importProducts: (file) => importFile('/import/products', file),
};

async function importFile(endpoint, file) {
    const formData = new FormData();
    formData.append('file', file);
    const headers = {};
    const token = getCsrfToken();
    if (token) headers['X-CSRF-Token'] = token;
    const response = await fetch(`${API_BASE}${endpoint}`, {
        method: 'POST',
        credentials: 'same-origin',
        headers,
        body: formData,
    });
    if (!response.ok) {
        const error = await response.json().catch(() => ({}));
        throw new Error(error.detail || 'Import failed');
    }
    return response.json();
}
