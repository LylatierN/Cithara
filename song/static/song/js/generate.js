// ─── Helpers ──────────────────────────────────────────────────────────────────

function getAccessToken() {
  return sessionStorage.getItem('access');
}

function getUserId() {
  return sessionStorage.getItem('user_id');
}

function showError(message) {
  const banner = document.getElementById('error-banner');
  if (!banner) return;
  banner.textContent = message;
  banner.classList.remove('hidden');
}

function clearError() {
  document.getElementById('error-banner')?.classList.add('hidden');
}

function showFieldError(fieldId, message) {
  const errorEl = document.getElementById(`${fieldId}-error`);
  const inputEl = document.getElementById(fieldId);
  if (errorEl) { errorEl.textContent = message; errorEl.classList.remove('hidden'); }
  if (inputEl) {
    inputEl.classList.add('border-red-500');
    inputEl.classList.remove('border-surface-border');
  }
}

function clearFieldErrors() {
  ['title', 'occasion', 'genre', 'mood', 'voice_type'].forEach(fieldId => {
    document.getElementById(`${fieldId}-error`)?.classList.add('hidden');
    const input = document.getElementById(fieldId);
    if (input) {
      input.classList.remove('border-red-500');
      input.classList.add('border-surface-border');
    }
  });
}

function setLoading(isLoading) {
  const btn      = document.getElementById('generate-btn');
  const spinner  = document.getElementById('generate-spinner');
  const text     = document.getElementById('generate-btn-text');
  const form     = document.getElementById('generate-form');
  const genState = document.getElementById('generating-state');

  if (isLoading) {
    btn.disabled = true;
    btn.classList.add('opacity-50', 'cursor-not-allowed');
    spinner.classList.remove('hidden');
    text.textContent = 'Starting...';
    form.classList.add('opacity-40', 'pointer-events-none');
    genState.classList.remove('hidden');
  } else {
    btn.disabled = false;
    btn.classList.remove('opacity-50', 'cursor-not-allowed');
    spinner.classList.add('hidden');
    text.textContent = 'Generate Song';
    form.classList.remove('opacity-40', 'pointer-events-none');
    genState.classList.add('hidden');
  }
}


// ─── Validation ───────────────────────────────────────────────────────────────

function validateForm(fields) {
  let valid = true;
  ['title', 'occasion', 'genre', 'mood', 'voice_type'].forEach(key => {
    if (!fields[key] || !fields[key].trim()) {
      showFieldError(key, 'This field is required.');
      valid = false;
    }
  });
  return valid;
}


// ─── API ──────────────────────────────────────────────────────────────────────

async function apiPost(url, body) {
  const token = getAccessToken();
  if (!token) { window.location.href = '/login/'; return null; }

  return fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`,
    },
    body: JSON.stringify(body),
  });
}

async function runGeneration(fields) {
  // Step 1: Create prompt
  const promptRes = await apiPost('/api/prompts/', {
    title:      fields.title,
    description: fields.description,
    occasion:   fields.occasion,
    genre:      fields.genre,
    mood:       fields.mood,
    voice_type: fields.voice_type,
    lyrics:     fields.lyrics,
  });
  if (!promptRes) return;
  if (!promptRes.ok) {
    const data = await promptRes.json();
    showError(data.detail || data.error || 'Failed to create prompt. Please try again.');
    setLoading(false); return;
  }
  const { id: promptId } = await promptRes.json();

  // Step 2: Create song
  const songRes = await apiPost('/api/songs/', {
    title:       fields.title,
    description: fields.description,
    prompt:      promptId,
    status:      'GENERATING',
    meta_data:   {},
  });
  if (!songRes) return;
  if (!songRes.ok) {
    const data = await songRes.json();
    showError(data.detail || data.error || 'Failed to create song. Please try again.');
    setLoading(false); return;
  }
  const { id: songId } = await songRes.json();

  // Step 3: Trigger generation
  const genRes = await apiPost(`/api/songs/${songId}/generate/`, {});
  if (!genRes) return;
  const genData = await genRes.json();

  if (genRes.status === 429) {
    showError('Too many songs generating at once. Please wait and try again shortly.');
    setLoading(false); return;
  }
  if (genRes.status === 400 && genData.error?.toLowerCase().includes('library')) {
    showError('Your library is full (max 20 songs). Please delete a song before generating.');
    setLoading(false); return;
  }
  if (genRes.status === 502) {
    showError('The AI generation service failed. Please try again.');
    setLoading(false); return;
  }

  // Step 4: Add song to user's library
  const userId = getUserId();
  await apiPost(`/api/users/${userId}/add_song/`, { song_id: songId });

  window.location.href = '/dashboard/';
}


// ─── Init ─────────────────────────────────────────────────────────────────────

function initGenerate() {
  if (!getAccessToken()) { window.location.href = '/login/'; return; }

  document.getElementById('generate-form')?.addEventListener('submit', async function (e) {
    e.preventDefault();
    clearError();
    clearFieldErrors();

    const fields = {
      title:       document.getElementById('title').value.trim(),
      occasion:    document.getElementById('occasion').value.trim(),
      genre:       document.getElementById('genre').value,
      mood:        document.getElementById('mood').value,
      voice_type:  document.getElementById('voice_type').value,
      lyrics:      document.getElementById('lyrics').value.trim(),
      description: document.getElementById('description').value,
    };

    if (!validateForm(fields)) return;

    setLoading(true);
    try {
      await runGeneration(fields);
    } catch {
      showError('Something went wrong. Please check your connection and try again.');
      setLoading(false);
    }
  });
}