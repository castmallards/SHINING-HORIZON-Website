// Cookie-session auth helpers (Phase 4.1).
// The session token is an httpOnly cookie set by POST /api/auth/login,
// so JS never sees it. We cache the user record in localStorage purely
// for UI rendering (header avatar, role-gated nav).

const ADMIN_USER_KEY = 'admin_user';
const ADMIN_LOGIN_PAGE = 'login.html';

function setCachedUser(user) {
    try { localStorage.setItem(ADMIN_USER_KEY, JSON.stringify(user || null)); }
    catch (e) { /* private mode etc. — ignore */ }
}

function getCachedUser() {
    try {
        const raw = localStorage.getItem(ADMIN_USER_KEY);
        return raw ? JSON.parse(raw) : null;
    } catch (e) { return null; }
}

function clearCachedUser() {
    try { localStorage.removeItem(ADMIN_USER_KEY); } catch (e) {}
}

// Backwards-compat shim — old pages call getCurrentUser().
function getCurrentUser() { return getCachedUser(); }

// True if a user record is cached. The real source of truth is the cookie,
// which we can't read; the API will return 401 and trigger redirectToLogin
// if the cookie is missing or expired.
function isLoggedIn() { return !!getCachedUser(); }

function requireAuth() {
    if (!isLoggedIn()) {
        redirectToLogin();
        return false;
    }
    return true;
}

function redirectToLogin() {
    if (!window.location.pathname.endsWith('/' + ADMIN_LOGIN_PAGE)) {
        window.location.href = ADMIN_LOGIN_PAGE;
    }
}

// CSRF cookie reader. The middleware writes ``csrf_token`` (non-httpOnly)
// on the first response; we echo it back on every mutating request.
function getCsrfToken() {
    const match = document.cookie.match(/(?:^|;\s*)csrf_token=([^;]+)/);
    return match ? decodeURIComponent(match[1]) : null;
}

// ── Role-aware permission helpers ─────────────────────────────────────
// Mirrors backend/app/services/permissions.py. Used by admin pages to
// hide controls a user's role isn't allowed to invoke. The backend remains
// authoritative — these helpers only improve UX by not showing dead buttons.

const ROLE_LABELS = {
    super_admin: 'Super Admin',
    admin: 'Admin',
    manager: 'Manager',
    data_entry: 'Data Entry',
};

function roleLabel(role) {
    return ROLE_LABELS[role] || role || 'Unknown';
}

function _role(user) { return (user || getCachedUser() || {}).role; }

function canPublish(user) {
    return ['super_admin', 'admin', 'manager'].includes(_role(user));
}
function canDelete(user) {
    return ['super_admin', 'admin'].includes(_role(user));
}
function canManageUsers(user) {
    return _role(user) === 'super_admin';
}
function canViewAudit(user) {
    return ['super_admin', 'admin'].includes(_role(user));
}

// Apply role-based visibility once after page load. Pages that render
// later (after a fetch) should call this again from their render fn.
function applyRoleGates(user) {
    user = user || getCachedUser();
    if (!user) return;

    // Hide elements with [data-role-required="<roles>"] when user.role isn't listed.
    document.querySelectorAll('[data-role-required]').forEach(el => {
        const allowed = el.getAttribute('data-role-required').split(',').map(s => s.trim());
        if (!allowed.includes(user.role)) el.style.display = 'none';
    });

    // Hide elements with [data-permission="publish|delete|users|audit"]
    document.querySelectorAll('[data-permission]').forEach(el => {
        const perm = el.getAttribute('data-permission');
        const ok = perm === 'publish' ? canPublish(user)
            : perm === 'delete' ? canDelete(user)
            : perm === 'users' ? canManageUsers(user)
            : perm === 'audit' ? canViewAudit(user)
            : true;
        if (!ok) el.style.display = 'none';
    });

    // Status dropdowns: lock to "draft" for users who can't publish.
    // The backend rejects non-draft writes from these roles anyway; this just
    // makes the UI consistent so the form can't be submitted with "published".
    if (!canPublish(user)) {
        document.querySelectorAll('select[name="status"]').forEach(sel => {
            sel.querySelectorAll('option').forEach(o => {
                if (o.value && o.value !== 'draft') o.disabled = true;
            });
            sel.value = 'draft';
            sel.title = 'Your role can only save as draft. An admin or manager can publish.';
        });
    }
}

// Show a small role badge in the header user-info block.
function renderRoleBadge() {
    const u = getCachedUser();
    if (!u) return;
    const slot = document.querySelector('.user-info .user-role');
    if (slot) slot.textContent = roleLabel(u.role);
    const name = document.querySelector('.user-info .user-name');
    if (name && u.full_name) name.textContent = u.full_name;
    const avatar = document.querySelector('.user-avatar');
    if (avatar) avatar.textContent = (u.full_name || u.username || '?').charAt(0).toUpperCase();
}
