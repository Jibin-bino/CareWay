const API_BASE_URL = (() => {
    if (typeof window !== 'undefined' && window.location) {
        const origin = window.location.origin;
        const port = window.location.port;
        if (port === '5500' || port === '3000' || port === '5173') {
            return 'http://localhost:8080/api';
        }
        if (origin && (origin.startsWith('http://') || origin.startsWith('https://'))) {
            return `${origin}/api`;
        }
    }
    return 'http://localhost:8080/api';
})();

// Auth State Management
const Auth = {
    setToken: (token) => localStorage.setItem('auth_token', token),
    getToken: () => localStorage.getItem('auth_token'),
    setUser: (user) => localStorage.setItem('user', JSON.stringify(user)),
    getUser: () => JSON.parse(localStorage.getItem('user') || 'null'),
    logout: () => {
        localStorage.removeItem('auth_token');
        localStorage.removeItem('user');
    },
    isAuthenticated: () => !!localStorage.getItem('auth_token')
};

// Reusable INR Currency Formatter (Requirement 11)
function formatINR(amount) {
    if (amount === null || amount === undefined || isNaN(Number(amount))) {
        return '₹500';
    }
    const num = Math.round(Number(amount));
    return '₹' + num.toLocaleString('en-IN');
}
window.formatINR = formatINR;

// Helper to get friendly display name from user object
function getDisplayName(user) {
    if (!user) return 'Patient';
    if (user.first_name && user.first_name.trim()) {
        return user.last_name ? `${user.first_name} ${user.last_name}`.trim() : user.first_name.trim();
    }
    if (user.name && user.name.trim()) return user.name.trim();
    const raw = (user.username || user.email || '').trim();
    if (raw.includes('@')) {
        const prefix = raw.split('@')[0];
        return prefix.replace(/[._\-+]/g, ' ')
                     .replace(/\b\w/g, c => c.toUpperCase());
    }
    if (raw) return raw.charAt(0).toUpperCase() + raw.slice(1);
    return 'Patient';
}
window.getDisplayName = getDisplayName;

// GLOBAL SHARED NAVBAR COMPONENT (Requirements 4, 5, 6, 7, 8, 16)
function renderGlobalNavbar() {
    const navbar = document.querySelector('.navbar');
    if (!navbar) return;

    const currentPath = window.location.pathname;
    const isHome = currentPath.endsWith('index.html') || currentPath === '/' || currentPath.endsWith('/') || currentPath === '';
    const isFind = currentPath.endsWith('find_doctor.html');
    const isBook = currentPath.endsWith('book_doctor.html') || currentPath.endsWith('doctor_profile.html') || currentPath.endsWith('appointment_confirmation.html');
    const isLib = currentPath.endsWith('library.html');
    const isDash = currentPath.endsWith('dashboard.html');
    const isLogin = currentPath.endsWith('login.html');
    const isRegister = currentPath.endsWith('register.html');

    const isAuth = Auth.isAuthenticated();
    const user = isAuth ? Auth.getUser() : null;
    const displayName = getDisplayName(user);
    const initial = displayName.charAt(0).toUpperCase() || 'P';

    navbar.innerHTML = `
        <div class="container navbar-container">
            <a href="index.html" class="navbar-brand" aria-label="CareWay Home">
                <span class="brand-logo-icon">
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor" stroke="none" xmlns="http://www.w3.org/2000/svg">
                        <rect x="9.5" y="2" width="5" height="20" rx="1.5"/>
                        <rect x="2" y="9.5" width="20" height="5" rx="1.5"/>
                    </svg>
                </span>
                <span class="brand-text">Care<span>Way</span></span>
            </a>

            <button class="navbar-toggler" id="navbar-toggler" aria-label="Toggle navigation" aria-expanded="false">
                <span class="toggler-bar"></span>
                <span class="toggler-bar"></span>
                <span class="toggler-bar"></span>
            </button>

            <nav class="main-nav" id="navbar-collapse">
                <a href="index.html" class="nav-link ${isHome ? 'active' : ''}">Home</a>
                <a href="find_doctor.html" class="nav-link ${isFind ? 'active' : ''}">Find a Doctor</a>
                <a href="book_doctor.html" class="nav-link ${isBook ? 'active' : ''}">Book a Doctor</a>
                <a href="library.html" class="nav-link ${isLib ? 'active' : ''}">Health Library</a>
                ${isAuth ? `<a href="dashboard.html" class="nav-link ${isDash ? 'active' : ''}">My Bookings</a>` : ''}
            </nav>

            <div class="auth-nav">
                ${isAuth ? `
                    <a href="dashboard.html" class="user-nav-badge" title="My Bookings">
                        <span class="user-avatar-pill">${initial}</span>
                        <span class="user-name-text">${displayName}</span>
                    </a>
                    <button onclick="handleLogout()" class="btn btn-outline nav-logout-btn" style="padding: 0.35rem 0.85rem; font-size: 0.85rem;">Logout</button>
                ` : `
                    <a href="login.html" class="nav-link nav-auth-link ${isLogin ? 'active' : ''}">Login</a>
                    <a href="register.html" class="btn btn-accent nav-register-btn" style="padding: 0.45rem 1.15rem; font-size: 0.875rem;">Register</a>
                `}
            </div>
        </div>
    `;

    // Hook up responsive toggler
    const toggler = document.getElementById('navbar-toggler');
    const collapse = document.getElementById('navbar-collapse');
    if (toggler && collapse) {
        toggler.onclick = (e) => {
            e.stopPropagation();
            const isOpen = collapse.classList.toggle('show');
            toggler.setAttribute('aria-expanded', isOpen ? 'true' : 'false');
        };

        // Close on outside click
        document.addEventListener('click', (e) => {
            if (!navbar.contains(e.target) && collapse.classList.contains('show')) {
                collapse.classList.remove('show');
                toggler.setAttribute('aria-expanded', 'false');
            }
        });
    }
}
window.renderGlobalNavbar = renderGlobalNavbar;
window.updateNavbar = renderGlobalNavbar; // Alias for backwards-compatibility

// GLOBAL SHARED FOOTER COMPONENT (Requirement 15)
function renderGlobalFooter() {
    const footer = document.querySelector('footer.footer, #app-footer');
    if (!footer) return;

    footer.innerHTML = `
        <div class="container">
            <div class="footer-col">
                <div style="display:inline-flex; align-items:center; gap:0.6rem; margin-bottom:1rem;">
                    <span style="width:32px; height:32px; border-radius:9px; background:linear-gradient(145deg, #10B981 0%, #059669 60%, #047857 100%); display:inline-flex; align-items:center; justify-content:center; color:#fff; box-shadow:0 4px 12px rgba(5,150,105,0.4); flex-shrink:0;">
                        <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor" stroke="none" xmlns="http://www.w3.org/2000/svg">
                            <rect x="9.5" y="2" width="5" height="20" rx="1.5"/>
                            <rect x="2" y="9.5" width="20" height="5" rx="1.5"/>
                        </svg>
                    </span>
                    <h4 style="font-weight:800; color:var(--white); font-size:1.3rem; margin:0; letter-spacing:-0.02em;">Care<span style="color:#10B981;">Way</span></h4>
                </div>
                <p style="color:rgba(255, 255, 255, 0.7); line-height:1.6; max-width:320px; margin:0;">
                    AI-assisted healthcare navigation and doctor appointment platform built for patients.
                </p>
            </div>
            <div class="footer-col">
                <h4>Quick Links</h4>
                <p><a href="find_doctor.html">Find a Doctor</a></p>
                <p><a href="book_doctor.html">Book a Doctor</a></p>
                <p><a href="library.html">Health Library</a></p>
                <p><a href="dashboard.html">Patient Dashboard</a></p>
            </div>
            <div class="footer-col">
                <h4>Support & Contact</h4>
                <p>Email: <a href="mailto:support@careway.health" style="color:rgba(255,255,255,0.7);">support@careway.health</a></p>
                <p>Toll-free Helpline: 1800-CARE-WAY</p>
                <p>Location: Chennai, India</p>
            </div>
        </div>
        <div class="footer-bottom">
            <p>&copy; 2026 CareWay Health Technologies. All rights reserved.</p>
        </div>
    `;
}
window.renderGlobalFooter = renderGlobalFooter;

async function handleLogout() {
    const token = Auth.getToken();
    if (token) {
        try {
            await fetch(`${API_BASE_URL}/auth/logout/`, {
                method: 'POST',
                headers: {
                    'Authorization': `Token ${token}`,
                    'Content-Type': 'application/json'
                }
            });
        } catch (e) {
            console.error(e);
        }
    }
    Auth.logout();
    window.location.href = 'index.html';
}
window.handleLogout = handleLogout;

function requireAuth() {
    if (!Auth.isAuthenticated()) {
        window.location.href = 'login.html?redirect=' + encodeURIComponent(window.location.pathname);
    }
}
window.requireAuth = requireAuth;

// Global initialization across all pages
document.addEventListener('DOMContentLoaded', () => {
    renderGlobalNavbar();
    renderGlobalFooter();
});
