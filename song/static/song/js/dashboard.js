const STATUS_STYLES = {
  READY:      { label: 'Ready',      classes: 'bg-green-900/40 text-green-300 border border-green-800' },
  GENERATING: { label: 'Generating', classes: 'bg-yellow-900/40 text-yellow-300 border border-yellow-800' },
  FAILED:     { label: 'Failed',     classes: 'bg-red-900/40 text-red-300 border border-red-800' },
};

let pendingDeleteId  = null;
let activeSidebarSong = null;

// ─── Player state ─────────────────────────────────────────────────────────────
let allSongs         = [];
let currentSongIndex = -1;
const audio          = new Audio();

function getAccessToken() { return sessionStorage.getItem('access'); }
function getUserId()      { return sessionStorage.getItem('user_id'); }
function getUsername()    { return sessionStorage.getItem('username'); }

function authHeaders() {
  return {
    'Content-Type': 'application/json',
    'Authorization': `Bearer ${getAccessToken()}`,
  };
}

let toastTimer = null;
function showToast() {
  const toast = document.getElementById('copy-toast');
  toast.classList.remove('opacity-0');
  toast.classList.add('opacity-100');
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => {
    toast.classList.remove('opacity-100');
    toast.classList.add('opacity-0');
  }, 2500);
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

function formatTime(secs) {
  if (!isFinite(secs)) return '0:00';
  const m = Math.floor(secs / 60);
  const s = Math.floor(secs % 60).toString().padStart(2, '0');
  return `${m}:${s}`;
}

function showState(state) {
  ['loading-state', 'empty-state', 'song-list'].forEach(id => {
    document.getElementById(id)?.classList.add('hidden');
  });
  document.getElementById(`${state === 'songs' ? 'song-list' : state + '-state'}`)?.classList.remove('hidden');
}


// ─── Music Player ─────────────────────────────────────────────────────────────

function showPlayer() {
  document.getElementById('music-player').classList.remove('hidden');
  // Keep sidebar above player
  document.getElementById('detail-sidebar').style.bottom = '4rem';
  // Add bottom padding so content isn't hidden behind player
  document.querySelector('main').style.paddingBottom = '4rem';
}

function setPlayerIcons(playing) {
  document.getElementById('player-play-icon').classList.toggle('hidden', playing);
  document.getElementById('player-pause-icon').classList.toggle('hidden', !playing);
}

function playSong(index) {
  const song = allSongs[index];
  if (!song || song.status !== 'READY' || !song.url) return;

  currentSongIndex = index;
  audio.src = song.url;
  audio.load();
  audio.play().catch(console.warn);

  document.getElementById('player-title').textContent = song.title;
  document.getElementById('player-sub').textContent   = 'Now playing';
  showPlayer();

  // Highlight active card
  document.querySelectorAll('.song-card').forEach((c, i) => {
    c.classList.toggle('border-brand', i === index);
  });
}

function playPrev() {
  if (allSongs.length === 0) return;
  // Walk backwards to find a READY song
  let idx = currentSongIndex - 1;
  while (idx >= 0 && allSongs[idx].status !== 'READY') idx--;
  if (idx >= 0) playSong(idx);
}

function playNext() {
  if (allSongs.length === 0) return;
  // Walk forwards to find a READY song
  let idx = currentSongIndex + 1;
  while (idx < allSongs.length && allSongs[idx].status !== 'READY') idx++;
  if (idx < allSongs.length) playSong(idx);
}

function initPlayerControls() {
  document.getElementById('player-playpause').addEventListener('click', () => {
    if (audio.paused) audio.play(); else audio.pause();
  });

  document.getElementById('player-prev').addEventListener('click', playPrev);
  document.getElementById('player-next').addEventListener('click', playNext);

  document.getElementById('player-seek').addEventListener('input', e => {
    if (audio.duration) audio.currentTime = (e.target.value / 100) * audio.duration;
  });

  document.getElementById('player-volume').addEventListener('input', e => {
    audio.volume = e.target.value;
  });

  audio.addEventListener('play',  () => setPlayerIcons(true));
  audio.addEventListener('pause', () => setPlayerIcons(false));

  audio.addEventListener('timeupdate', () => {
    if (!audio.duration) return;
    document.getElementById('player-seek').value    = (audio.currentTime / audio.duration) * 100;
    document.getElementById('player-current').textContent  = formatTime(audio.currentTime);
    document.getElementById('player-duration').textContent = formatTime(audio.duration);
  });

  audio.addEventListener('ended', playNext);

  document.addEventListener('keydown', e => {
    if (e.code !== 'Space') return;
    const tag = document.activeElement?.tagName;
    if (tag === 'INPUT' || tag === 'TEXTAREA') return;
    if (document.getElementById('music-player').classList.contains('hidden')) return;
    e.preventDefault();
    if (audio.paused) audio.play().catch(console.warn); else audio.pause();
  });
}


// ─── Render ───────────────────────────────────────────────────────────────────

function renderSongs(songs) {
  allSongs = songs;
  const list = document.getElementById('song-list');
  list.innerHTML = '';

  songs.forEach((song, index) => {
    const template = document.getElementById('song-card-template');
    const card     = template.content.cloneNode(true);
    const isReady  = song.status === 'READY';
    const style    = STATUS_STYLES[song.status] || STATUS_STYLES.FAILED;

    card.querySelector('.song-title').textContent = song.title;
    card.querySelector('.song-date').textContent  = `Created ${formatDate(song.created_at)}`;

    const statusEl = card.querySelector('.song-status');
    statusEl.textContent = style.label;
    statusEl.className  += ` ${style.classes}`;

    // Play button
    const playBtn = card.querySelector('.action-play');
    if (isReady) {
      playBtn.addEventListener('click', () => playSong(index));
    } else {
      playBtn.disabled  = true;
      playBtn.className = 'action-play flex-shrink-0 w-9 h-9 rounded-full bg-surface-border flex items-center justify-center cursor-not-allowed opacity-40';
    }

    // Share / Download / Detail: disabled unless READY
    ['action-share', 'action-download', 'action-detail'].forEach(cls => {
      const btn = card.querySelector(`.${cls}`);
      if (!isReady) {
        btn.disabled  = true;
        btn.className = `${cls} w-8 h-8 rounded-lg flex items-center justify-center text-gray-600 cursor-not-allowed opacity-40`;
      }
    });

    card.querySelector('.action-share').addEventListener('click', async () => {
      if (!isReady) return;
      try {
        const res  = await fetch(`/api/songs/${song.id}/share/`, { headers: authHeaders() });
        const data = await res.json();
        if (res.ok) {
          await navigator.clipboard.writeText(data.share_url);
          showToast();
        } else {
          showError(data.error || 'Failed to get share link.');
        }
      } catch { showError('Could not generate share link.'); }
    });

    card.querySelector('.action-download').addEventListener('click', async () => {
      if (!isReady) return;
      try {
        const res  = await fetch(`/api/songs/${song.id}/share/`, { headers: authHeaders() });
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

    card.querySelector('.action-detail').addEventListener('click', () => {
      if (!isReady) return;
      openSidebar(song);
    });

    list.appendChild(card);
  });
}


// ─── API ──────────────────────────────────────────────────────────────────────

async function fetchLibrary() {
  const res = await fetch(`/api/users/${getUserId()}/library/`, { headers: authHeaders() });
  if (!res.ok) throw new Error('Failed to fetch library.');
  return res.json();
}

async function deleteSong(songId) {
  return fetch(`/api/songs/${songId}/`, { method: 'DELETE', headers: authHeaders() });
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

  document.getElementById('sidebar-close')?.addEventListener('click', closeSidebar);

  document.getElementById('sd-delete-btn')?.addEventListener('click', () => {
    if (!activeSidebarSong) return;
    pendingDeleteId = activeSidebarSong.id;
    closeSidebar();
    document.getElementById('delete-modal').classList.remove('hidden');
  });

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
      // Stop player if the deleted song was playing
      if (allSongs[currentSongIndex]?.id === pendingDeleteId) {
        audio.pause();
        audio.src = '';
      }
      await loadLibrary();
    } else {
      showError('Failed to delete song. Please try again.');
    }
  });

  initPlayerControls();
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


// ─── Detail Sidebar ───────────────────────────────────────────────────────────

function openSidebar(song) {
  activeSidebarSong = song;
  const sidebar = document.getElementById('detail-sidebar');

  document.getElementById('sd-title').textContent    = song.title || '—';
  document.getElementById('sd-occasion').textContent = song.prompt?.occasion   || '—';
  document.getElementById('sd-genre').textContent    = song.prompt?.genre      || '—';
  document.getElementById('sd-mood').textContent     = song.prompt?.mood       || '—';
  document.getElementById('sd-voice').textContent    = song.prompt?.voice_type || '—';
  document.getElementById('sd-lyrics').textContent   = song.prompt?.lyrics     || 'No lyrics provided.';
  document.getElementById('sd-created').textContent  = formatDate(song.created_at);
  document.getElementById('sd-updated').textContent  = formatDate(song.updated_at || song.created_at);

  const statusEl = document.getElementById('sd-status');
  const style    = STATUS_STYLES[song.status] || STATUS_STYLES.FAILED;
  statusEl.textContent = style.label;
  statusEl.className   = `text-xs px-2 py-0.5 rounded-full font-medium ${style.classes}`;

  // Sit above the player if it's visible
  const playerVisible = !document.getElementById('music-player').classList.contains('hidden');
  sidebar.style.bottom = playerVisible ? '4rem' : '0';
  sidebar.classList.remove('hidden');

  document.querySelectorAll('.song-card').forEach(c => c.classList.remove('border-brand'));
  document.querySelectorAll('.song-card').forEach(c => {
    if (c.querySelector('.song-title')?.textContent === song.title)
      c.classList.add('border-brand');
  });
}

function closeSidebar() {
  document.getElementById('detail-sidebar').classList.add('hidden');
  document.querySelectorAll('.song-card').forEach(c => c.classList.remove('border-brand'));
  activeSidebarSong = null;
}
