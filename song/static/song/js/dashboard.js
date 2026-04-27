const STATUS_STYLES = {
  READY:      { label: 'Ready',      classes: 'bg-green-900/40 text-green-300 border border-green-800' },
  GENERATING: { label: 'Generating', classes: 'bg-yellow-900/40 text-yellow-300 border border-yellow-800' },
  FAILED:     { label: 'Failed',     classes: 'bg-red-900/40 text-red-300 border border-red-800' },
};

let pendingDeleteId = null;

function getAccessToken() { return sessionStorage.getItem('access'); }
function getUserId()      { return sessionStorage.getItem('user_id'); }
function getUsername()    { return sessionStorage.getItem('username'); }

function authHeaders() {
  return {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${getAccessToken()}`,
  };
}

function showError(msg) {
  const el = document.getElementById('error-banner');
  if (!el) return;
  el.textContent = msg;
  el.classList.remove('hidden');
}

function formatDate(iso) {
  return new Date(iso).toLocaleDateString('en-US', { year: 'numeric', month: 'short', day: 'numeric' });
}

function showState(state) {
  ['loading-state', 'empty-state', 'song-list'].forEach(id => {
    document.getElementById(id)?.classList.add('hidden');
  });
  document.getElementById(`${state === 'songs' ? 'song-list' : state + '-state'}`)?.classList.remove('hidden');
}

// ─── Render ───────────────────────────────────────────────────────────────────

function renderSongs(songs) {
  const list = document.getElementById('song-list');
  list.innerHTML = '';

  songs.forEach(song => {
    const template = document.getElementById('song-card-template');
    const card = template.content.cloneNode(true);
    const isReady = song.status === 'READY';
    const style = STATUS_STYLES[song.status] || STATUS_STYLES.FAILED;

    card.querySelector('.song-title').textContent = song.title;
    card.querySelector('.song-date').textContent = `Created ${formatDate(song.created_at)}`;

    const statusEl = card.querySelector('.song-status');
    statusEl.textContent = style.label;
    statusEl.className += ` ${style.classes}`;

    ['action-play', 'action-share', 'action-download'].forEach(cls => {
      const btn = card.querySelector(`.${cls}`);
      if (!isReady) {
        btn.disabled = true;
        btn.className = `p-2 text-gray-600 cursor-not-allowed`;
      }
    });

    card.querySelector('.action-play').addEventListener('click', () => {
      if (!isReady || !song.url) return;
      window.open(song.url, '_blank');
    });

    card.querySelector('.action-share').addEventListener('click', async () => {
      if (!isReady) return;
      try {
        const res = await fetch(`/api/songs/${song.id}/share/`, { headers: authHeaders() });
        const data = await res.json();
        if (res.ok) {
          await navigator.clipboard.writeText(data.share_url);
          alert('Share link copied to clipboard!');
        } else {
          showError(data.error || 'Failed to get share link.');
        }
      } catch { showError('Could not generate share link.'); }
    });

    card.querySelector('.action-download').addEventListener('click', async () => {
      if (!isReady) return;
      try {
        const res = await fetch(`/api/songs/${song.id}/share/`, { headers: authHeaders() });
        const data = await res.json();
        if (res.ok) {
          const token = data.share_url.split('/').filter(Boolean).pop();
          window.location.href = `/api/songs/download/${token}/`;
        } else {
          showError(data.error || 'Failed to get download link.');
        }
      } catch { showError('Could not generate download link.'); }
    });

    card.querySelector('.action-delete').addEventListener('click', () => {
      pendingDeleteId = song.id;
      document.getElementById('delete-modal').classList.remove('hidden');
    });

    list.appendChild(card);
  });
}


// ─── API ──────────────────────────────────────────────────────────────────────

async function fetchLibrary() {
  const userId = getUserId();
  const res = await fetch(`/api/users/${userId}/library/`, { headers: authHeaders() });
  if (!res.ok) throw new Error('Failed to fetch library.');
  return res.json();
}

async function deleteSong(songId) {
  const res = await fetch(`/api/songs/${songId}/`, {
    method: 'DELETE',
    headers: authHeaders(),
  });
  return res;
}

async function logout() {
  const refresh = sessionStorage.getItem('refresh');
  try {
    await fetch('/api/auth/logout/', {
      method: 'POST',
      headers: authHeaders(),
      body: JSON.stringify({ refresh }),
    });
  } finally {
    sessionStorage.clear();
    window.location.href = '/login/';
  }
}


// ─── Init ─────────────────────────────────────────────────────────────────────

function initDashboard() {
  if (!getAccessToken()) { window.location.href = '/login/'; return; }

  document.getElementById('nav-username').textContent = `Hi, ${getUsername()}`;

  document.getElementById('logout-btn').addEventListener('click', logout);

  document.getElementById('modal-cancel').addEventListener('click', () => {
    document.getElementById('delete-modal').classList.add('hidden');
    pendingDeleteId = null;
  });

  document.getElementById('modal-confirm').addEventListener('click', async () => {
    if (!pendingDeleteId) return;
    const res = await deleteSong(pendingDeleteId);
    document.getElementById('delete-modal').classList.add('hidden');
    pendingDeleteId = null;
    if (res.ok) {
      await loadLibrary();
    } else {
      showError('Failed to delete song. Please try again.');
    }
  });

  loadLibrary();
}

async function loadLibrary() {
  showState('loading');
  try {
    const songs = await fetchLibrary();
    if (songs.length === 0) {
      showState('empty');
    } else {
      renderSongs(songs);
      showState('songs');
    }
  } catch {
    showError('Failed to load your library. Please refresh the page.');
    showState('empty');
  }
}