// ─── CSRF ─────────────────────────────────────────────────────────────────────

function getCsrfToken() {
  return document.cookie.split(';')
    .map(c => c.trim())
    .find(c => c.startsWith('csrftoken='))
    ?.split('=')[1] ?? '';
}

// ─── Token Helpers ────────────────────────────────────────────────────────────

function saveSession(data) {
  sessionStorage.setItem('access',   data.access);
  sessionStorage.setItem('refresh',  data.refresh);
  sessionStorage.setItem('user_id',  data.user_id);
  sessionStorage.setItem('username', data.username);
}

function clearSession() {
  sessionStorage.clear();
}

function getAccessToken() {
  return sessionStorage.getItem('access');
}

function isLoggedIn() {
  return !!sessionStorage.getItem('access');
}


// ─── UI Helpers ───────────────────────────────────────────────────────────────

function showError(message) {
  const banner = document.getElementById('error-banner');
  if (!banner) return;
  banner.textContent = message;
  banner.classList.remove('hidden');

  const success = document.getElementById('success-banner');
  if (success) success.classList.add('hidden');
}

function showSuccess() {
  const banner = document.getElementById('success-banner');
  if (!banner) return;
  banner.classList.remove('hidden');

  const error = document.getElementById('error-banner');
  if (error) error.classList.add('hidden');
}

function clearBanners() {
  document.getElementById('error-banner')?.classList.add('hidden');
  document.getElementById('success-banner')?.classList.add('hidden');
}

function showFieldError(fieldId, message) {
  const errorEl = document.getElementById(`${fieldId}-error`);
  const inputEl = document.getElementById(fieldId);
  if (errorEl) {
    errorEl.textContent = message;
    errorEl.classList.remove('hidden');
  }
  if (inputEl) {
    inputEl.classList.add('border-red-500');
    inputEl.classList.remove('border-surface-border');
  }
}

function clearFieldErrors() {
  ['username', 'email', 'password'].forEach(fieldId => {
    document.getElementById(`${fieldId}-error`)?.classList.add('hidden');
    const input = document.getElementById(fieldId);
    if (input) {
      input.classList.remove('border-red-500');
      input.classList.add('border-surface-border');
    }
  });
}

function setLoading(btnId, spinnerId, textId, loadingText) {
  const btn = document.getElementById(btnId);
  if (btn) { btn.disabled = true; btn.classList.add('opacity-50', 'cursor-not-allowed'); }
  document.getElementById(spinnerId)?.classList.remove('hidden');
  const text = document.getElementById(textId);
  if (text) text.textContent = loadingText;
}

function clearLoading(btnId, spinnerId, textId, originalText) {
  const btn = document.getElementById(btnId);
  if (btn) { btn.disabled = false; btn.classList.remove('opacity-50', 'cursor-not-allowed'); }
  document.getElementById(spinnerId)?.classList.add('hidden');
  const text = document.getElementById(textId);
  if (text) text.textContent = originalText;
}


// ─── Validation ───────────────────────────────────────────────────────────────

function validateLogin(username, password) {
  let valid = true;
  if (!username.trim()) { showFieldError('username', 'Username is required.'); valid = false; }
  if (!password)        { showFieldError('password', 'Password is required.'); valid = false; }
  return valid;
}

function validateRegister(username, email, password) {
  let valid = true;

  if (!username.trim()) {
    showFieldError('username', 'Username is required.'); valid = false;
  } else if (username.trim().length < 3) {
    showFieldError('username', 'Username must be at least 3 characters.'); valid = false;
  }

  if (!email.trim()) {
    showFieldError('email', 'Email is required.'); valid = false;
  } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)) {
    showFieldError('email', 'Please enter a valid email address.'); valid = false;
  }

  if (!password) {
    showFieldError('password', 'Password is required.'); valid = false;
  } else if (password.length < 8) {
    showFieldError('password', 'Password must be at least 8 characters.'); valid = false;
  }

  return valid;
}


// ─── API Error Parser ─────────────────────────────────────────────────────────

// DRF returns errors in different shapes, e.g.:
//   { "username": ["Already exists."] }  → field error
//   { "error": "Invalid credentials" }   → top banner
function parseAndShowErrors(errorData) {
  const knownFields = ['username', 'email', 'password'];

  for (const [key, value] of Object.entries(errorData)) {
    const message = Array.isArray(value) ? value[0] : value;
    if (knownFields.includes(key)) {
      showFieldError(key, message);
    } else {
      showError(message);
    }
  }
}


// ─── Login ────────────────────────────────────────────────────────────────────

function initLogin() {
  if (isLoggedIn()) { window.location.href = '/dashboard/'; return; }

  if (new URLSearchParams(window.location.search).get('error') === 'google_failed') {
    showError('Google sign-in failed. Please try again.');
  }

  document.getElementById('login-form')?.addEventListener('submit', async function (e) {
    e.preventDefault();
    clearBanners();
    clearFieldErrors();

    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;

    if (!validateLogin(username, password)) return;

    setLoading('login-btn', 'login-spinner', 'login-btn-text', 'Signing in...');

    try {
      const response = await fetch('/api/auth/login/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCsrfToken() },
        body: JSON.stringify({ username, password }),
      });

      const data = await response.json();

      if (response.ok) {
        saveSession(data);
        window.location.href = '/dashboard/';
      } else {
        parseAndShowErrors(data);
      }
    } catch {
      showError('Unable to connect to the server. Please check your connection.');
    } finally {
      clearLoading('login-btn', 'login-spinner', 'login-btn-text', 'Sign in');
    }
  });
}


// ─── Forgot Password ──────────────────────────────────────────────────────────

function initForgotPassword() {
  document.getElementById('forgot-form')?.addEventListener('submit', async function (e) {
    e.preventDefault();
    clearBanners();

    const email = document.getElementById('email').value.trim();
    if (!email) {
      showFieldError('email', 'Email is required.');
      return;
    }

    setLoading('forgot-btn', 'forgot-spinner', 'forgot-btn-text', 'Sending…');

    try {
      const response = await fetch('/api/auth/forgot-password/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCsrfToken() },
        body: JSON.stringify({ email }),
      });

      if (response.ok) {
        showSuccess();
        document.getElementById('forgot-form').classList.add('hidden');
      } else {
        const data = await response.json();
        showError(data.error || 'Something went wrong. Please try again.');
      }
    } catch {
      showError('Unable to connect to the server. Please check your connection.');
    } finally {
      clearLoading('forgot-btn', 'forgot-spinner', 'forgot-btn-text', 'Send reset link');
    }
  });
}


// ─── Reset Password ───────────────────────────────────────────────────────────

function initResetPassword() {
  const token = new URLSearchParams(window.location.search).get('token');
  if (!token) {
    showError('Invalid or missing reset token. Please request a new reset link.');
    document.getElementById('reset-form')?.classList.add('hidden');
    return;
  }

  document.getElementById('reset-form')?.addEventListener('submit', async function (e) {
    e.preventDefault();
    clearBanners();

    const password        = document.getElementById('password').value;
    const confirmPassword = document.getElementById('confirm-password').value;

    let valid = true;
    if (!password || password.length < 8) {
      document.getElementById('password-error').textContent = 'Password must be at least 8 characters.';
      document.getElementById('password-error').classList.remove('hidden');
      document.getElementById('password').classList.add('border-red-500');
      valid = false;
    } else {
      document.getElementById('password-error').classList.add('hidden');
      document.getElementById('password').classList.remove('border-red-500');
    }

    if (password !== confirmPassword) {
      document.getElementById('confirm-password-error').textContent = 'Passwords do not match.';
      document.getElementById('confirm-password-error').classList.remove('hidden');
      document.getElementById('confirm-password').classList.add('border-red-500');
      valid = false;
    } else {
      document.getElementById('confirm-password-error').classList.add('hidden');
      document.getElementById('confirm-password').classList.remove('border-red-500');
    }

    if (!valid) return;

    setLoading('reset-btn', 'reset-spinner', 'reset-btn-text', 'Resetting…');

    try {
      const response = await fetch('/api/auth/reset-password/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCsrfToken() },
        body: JSON.stringify({ token, new_password: password }),
      });

      const data = await response.json();

      if (response.ok) {
        showSuccess();
        document.getElementById('reset-form').classList.add('hidden');
        setTimeout(() => { window.location.href = '/login/'; }, 2000);
      } else {
        showError(data.error || 'Something went wrong. Please try again.');
      }
    } catch {
      showError('Unable to connect to the server. Please check your connection.');
    } finally {
      clearLoading('reset-btn', 'reset-spinner', 'reset-btn-text', 'Reset password');
    }
  });
}


// ─── Register ─────────────────────────────────────────────────────────────────

function initRegister() {
  if (isLoggedIn()) { window.location.href = '/dashboard/'; return; }

  document.getElementById('register-form')?.addEventListener('submit', async function (e) {
    e.preventDefault();
    clearBanners();
    clearFieldErrors();

    const username = document.getElementById('username').value;
    const email    = document.getElementById('email').value;
    const password = document.getElementById('password').value;

    if (!validateRegister(username, email, password)) return;

    setLoading('register-btn', 'register-spinner', 'register-btn-text', 'Creating...');

    try {
      const response = await fetch('/api/users/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-CSRFToken': getCsrfToken() },
        body: JSON.stringify({ username, email, password }),
      });

      const data = await response.json();

      if (response.status === 201) {
        showSuccess();
        setTimeout(() => { window.location.href = '/login/'; }, 1500);
      } else {
        parseAndShowErrors(data);
      }
    } catch {
      showError('Unable to connect to the server. Please check your connection.');
    } finally {
      clearLoading('register-btn', 'register-spinner', 'register-btn-text', 'Create account');
    }
  });
}