# Cithara - AI Song Generation Platform

A Django-based application for AI-powered song generation using prompts.

## Project Overview

Cithara is a song generation platform that allows users to create songs based on detailed prompts including genre, mood, occasion, and lyrics. The system manages the entire lifecycle of song generation from prompt creation to final output.

## Domain Model

The application implements the following core entities:

- **Prompt**: Represents a song generation request with title, description, occasion, genre, mood, voice type, and lyrics
- **Song**: Generated songs with metadata, audio files, and generation status
- **Genre**: Enumeration (Pop, Rock, Jazz, Classical, R&B)
- **Mood**: Enumeration (Happy, Sad, Energetic, Relaxed)
- **SongStatus**: Enumeration (Generating, Ready, Failed)

## Technology Stack

- **Backend**: Django 6.0.3
- **API**: Django REST Framework 3.17.0
- **Database**: SQLite (development)
- **Python**: 3.13+

## Exercise Scope Notes

- Authentication is intentionally not required for this exercise.
- AI integration and UI design are out of scope.
- Focus is on domain modeling, persistence, and CRUD on real data.

## Setup Instructions

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- Git

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/LylatierN/Cithara.git
   cd Cithara
   ```

2. **Create and activate virtual environment**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```
   On Windows:
   ```bash
   python3 -m venv .venv
   .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**

   Copy `.env.example` to `.env` and fill in your values:
   ```bash
   cp .env.example .env
   ```

   Edit `.env`:
   ```
   SECRET_KEY=your-django-secret-key
   GENERATOR_STRATEGY=mock
   SUNO_API_KEY=your-suno-api-key-here
   GOOGLE_CLIENT_ID=your-google-client-id
   GOOGLE_CLIENT_SECRET=your-google-client-secret
   EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
   ```

   | Variable | Description |
   |----------|-------------|
   | `SECRET_KEY` | Django secret key |
   | `GENERATOR_STRATEGY` | `mock` (offline) or `suno` (real AI) |
   | `SUNO_API_KEY` | API key from [sunoapi.org](https://sunoapi.org/api-key) — only needed when using `suno` |
   | `GOOGLE_CLIENT_ID` | Google OAuth client ID — required for `/api/auth/google/` |
   | `GOOGLE_CLIENT_SECRET` | Google OAuth client secret |
   | `EMAIL_BACKEND` | Email backend — default prints to terminal |

   > ⚠️ Never commit `.env` to GitHub. It is listed in `.gitignore`.

5. **Run database migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Create a superuser (for admin access)**
   ```bash
   python manage.py createsuperuser
   ```

7. **Run the development server**
   ```bash
   python manage.py runserver
   ```

8. **Access the application**
   - Admin Panel: http://127.0.0.1:8000/admin/
   - API Root: http://127.0.0.1:8000/api/
   - Browsable API Login: http://127.0.0.1:8000/api-auth/login/

---

## Exercise 4: Strategy Pattern for Song Generation

### Overview

This exercise implements the Strategy design pattern for song generation. The strategy is selected via an environment variable, making it easy to swap between mock and real generation without changing any code.

Two strategies are available:
- **Mock**: Offline, no API calls, instant result — for development/testing
- **Suno**: Calls the real SunoApi.org to generate AI music

### Strategy Pattern Structure

```
song/
  generation/
    __init__.py        # Empty init
    base.py            # Strategy interface + GenerationRequest/GenerationResult dataclasses
    mock_strategy.py   # Strategy A: Mock generator (offline, deterministic)
    suno_strategy.py   # Strategy B: Suno API generator (real AI music)
    factory.py         # Centralized strategy selector (reads GENERATOR_STRATEGY setting)
```

The `factory.py` is the single place in the codebase that decides which strategy to use — there are no scattered if/else checks anywhere else.

### Where to Put the Suno API Key

Add it to your `.env` file:
```
SUNO_API_KEY=your-actual-key-here
```

Get your API key from: https://sunoapi.org/api-key

> ⚠️ Never commit this key to GitHub. The `.env` file is in `.gitignore`.

### New API Endpoints (Exercise 4)

- `POST /api/songs/{id}/generate/` — Trigger song generation using the active strategy
- `GET /api/songs/{id}/check_status/` — Poll Suno for the latest generation status

### How to Run Mock Mode

1. Set `GENERATOR_STRATEGY=mock` in your `.env` file
2. Start the server:
   ```bash
   python manage.py runserver
   ```
3. Create a prompt:
   ```bash
   curl -X POST http://127.0.0.1:8000/api/prompts/ \
     -H "Content-Type: application/json" \
     -d '{
       "title": "My Song",
       "description": "A fun song",
       "occasion": "Birthday",
       "genre": "POP",
       "mood": "HAPPY",
       "voice_type": "Female",
       "lyrics": ""
     }'
   ```
4. Create a song linked to that prompt (use the prompt `id` from step 3):
   ```bash
   curl -X POST http://127.0.0.1:8000/api/songs/ \
     -H "Content-Type: application/json" \
     -d '{
       "title": "My Song",
       "description": "A fun song",
       "prompt": 1,
       "status": "GENERATING",
       "url": "",
       "meta_data": {}
     }'
   ```
5. Trigger mock generation (use the song `id` from step 4):
   ```bash
   curl -X POST http://127.0.0.1:8000/api/songs/1/generate/ \
     -H "Accept: application/json"
   ```
6. Response returns immediately with `"status": "READY"` and a placeholder audio URL:
   ```json
   {
     "status": "READY",
     "url": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3",
     "meta_data": {
       "mock": true,
       "task_id": "mock-task-12345"
     }
   }
   ```

### How to Run Suno Mode

1. Set `GENERATOR_STRATEGY=suno` in your `.env` file
2. Make sure `SUNO_API_KEY` is set in your `.env` file
3. Start the server:
   ```bash
   python manage.py runserver
   ```
4. Create a prompt and song (same as Mock Mode steps 3–4)
5. Trigger Suno generation:
   ```bash
   curl -X POST http://127.0.0.1:8000/api/songs/1/generate/ \
     -H "Accept: application/json"
   ```
6. Response returns a `taskId` from Suno:
   ```json
   {
     "status": "GENERATING",
     "meta_data": {
       "task_id": "8bed802b4d9da98a18754ce97825a7ed"
     }
   }
   ```
7. Wait 30–40 seconds, then poll for status:
   ```bash
   curl http://127.0.0.1:8000/api/songs/1/check_status/ \
     -H "Accept: application/json"
   ```
8. Keep polling until you see `"suno_status": "SUCCESS"`:
   ```json
   {
     "task_id": "8bed802b4d9da98a18754ce97825a7ed",
     "suno_status": "SUCCESS",
     "audio_url": "https://..../song.mp3",
     "song_status": "READY"
   }
   ```
9. Copy the `audio_url` and open it in your browser to listen to the generated song.

---

## API Endpoints

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/auth/login/` | Obtain JWT access + refresh tokens |
| `POST` | `/api/auth/logout/` | Invalidate the current session |
| `POST` | `/api/auth/refresh/` | Refresh a JWT access token |
| `GET` | `/api/auth/google/` | Redirect to Google OAuth consent screen |
| `GET` | `/api/auth/google/callback/` | Handle Google OAuth callback |
| `POST` | `/api/auth/forgot-password/` | Send a password reset email |
| `POST` | `/api/auth/reset-password/` | Reset password using a token |

### Users

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/users/` | List all users |
| `POST` | `/api/users/` | Create a new user |
| `GET` | `/api/users/{id}/` | Retrieve a specific user |
| `PUT` | `/api/users/{id}/` | Full update a user |
| `PATCH` | `/api/users/{id}/` | Partial update a user |
| `DELETE` | `/api/users/{id}/` | Delete a user |
| `GET` | `/api/users/{id}/library/` | Get the user's song library |
| `POST` | `/api/users/{id}/add_song/` | Add a song to the library |
| `POST` | `/api/users/{id}/remove_song/` | Remove a song from the library |

### Prompts

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/prompts/` | List all prompts |
| `POST` | `/api/prompts/` | Create a new prompt |
| `GET` | `/api/prompts/{id}/` | Retrieve a specific prompt |
| `PUT` | `/api/prompts/{id}/` | Full update a prompt |
| `PATCH` | `/api/prompts/{id}/` | Partial update a prompt |
| `DELETE` | `/api/prompts/{id}/` | Delete a prompt |
| `GET` | `/api/prompts/{id}/songs/` | List all songs generated from a prompt |

### Songs

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/songs/` | List all songs |
| `POST` | `/api/songs/` | Create a new song |
| `GET` | `/api/songs/{id}/` | Retrieve a specific song |
| `PUT` | `/api/songs/{id}/` | Full update a song |
| `PATCH` | `/api/songs/{id}/` | Partial update a song |
| `DELETE` | `/api/songs/{id}/` | Delete a song |
| `POST` | `/api/songs/{id}/mark_ready/` | Mark a song as ready |
| `POST` | `/api/songs/{id}/mark_failed/` | Mark a song as failed |
| `POST` | `/api/songs/{id}/generate/` | Trigger song generation (active strategy) |
| `GET` | `/api/songs/{id}/check_status/` | Poll the generation status from Suno |
| `GET` | `/api/songs/{id}/share/` | Get a shareable audio URL for the song (FR-13) |
| `GET` | `/api/songs/{id}/download/` | Redirect (302) to the audio file for download (FR-12) |

### Filtering & Search

- Filter prompts by genre and mood: `/api/prompts/?genre=POP&mood=HAPPY`
- Search prompts by title/description/occasion/lyrics: `/api/prompts/?search=birthday`
- Filter songs by status or prompt: `/api/songs/?status=READY`
- Search songs by title/description: `/api/songs/?search=love`
- Search users by username/email/name: `/api/users/?search=alice`

## CRUD Operations

### Using Django Admin (Recommended for Testing)

1. Navigate to http://127.0.0.1:8000/admin/
2. Log in with superuser credentials
3. Manage Prompts and Songs through the admin interface

### Using API (Programmatic Access)

**Create a Prompt:**
```bash
curl -X POST http://127.0.0.1:8000/api/prompts/ \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Birthday Song",
    "description": "Upbeat birthday celebration",
    "occasion": "Birthday Party",
    "genre": "POP",
    "mood": "HAPPY",
    "voice_type": "Female",
    "lyrics": "Happy birthday to you..."
  }'
```

**Create a Song:**
```bash
curl -X POST http://127.0.0.1:8000/api/songs/ \
  -H "Content-Type: application/json" \
  -d '{
    "title": "My Birthday Song",
    "description": "Generated birthday song",
    "prompt": 1,
    "status": "GENERATING"
  }'
```

**Retrieve All Songs:**
```bash
curl http://127.0.0.1:8000/api/songs/
```

**Update Song Status:**
```bash
curl -X PATCH http://127.0.0.1:8000/api/songs/1/ \
  -H "Content-Type: application/json" \
  -d '{"status": "READY"}'
```

**Delete a Song:**
```bash
curl -X DELETE http://127.0.0.1:8000/api/songs/1/
```

**Create a User:**
```bash
curl -X POST http://127.0.0.1:8000/api/users/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "alice",
    "password": "securepass123",
    "email": "alice@example.com"
  }'
```

**Add a Song to User Library:**
```bash
curl -X POST http://127.0.0.1:8000/api/users/1/add_song/ \
  -H "Content-Type: application/json" \
  -d '{"song_id": 1}'
```

**Retrieve User Library:**
```bash
curl http://127.0.0.1:8000/api/users/1/library/
```

**Delete a User:**
```bash
curl -X DELETE http://127.0.0.1:8000/api/users/1/
```

## CRUD Verification Evidence

The following commands were prepared as repeatable verification steps for persistent CRUD behavior:

1. Create prompt (`POST /api/prompts/`)
2. Read prompts (`GET /api/prompts/`)
3. Update prompt (`PATCH /api/prompts/{id}/`)
4. Delete prompt (`DELETE /api/prompts/{id}/`)
5. Create song linked to prompt (`POST /api/songs/`)
6. Read songs (`GET /api/songs/`)
7. Update song status (`PATCH /api/songs/{id}/` or `POST /api/songs/{id}/mark_ready/`)
8. Delete song (`DELETE /api/songs/{id}/`)
9. Create user with hashed password (`POST /api/users/`)
10. Read users (`GET /api/users/`)
11. Add song to user library (`POST /api/users/{id}/add_song/`)
12. Update user (`PATCH /api/users/{id}/`)
13. Delete user (`DELETE /api/users/{id}/`)

The same operations can also be demonstrated through Django Admin at `/admin/`.

## Project Structure

```
Cithara/
├── Cithara/                    # Project configuration
│   ├── settings.py             # Django settings
│   ├── urls.py                 # Main URL configuration
│   ├── asgi.py                 # ASGI configuration
│   └── wsgi.py                 # WSGI configuration
├── song/                       # Song app
│   ├── generation/             # Strategy pattern for song generation (Exercise 4)
│   │   ├── __init__.py
│   │   ├── base.py             # Strategy interface + dataclasses
│   │   ├── content_filter.py   # Prompt content filter
│   │   ├── mock_strategy.py    # Mock strategy (offline/testing)
│   │   ├── suno_strategy.py    # Suno API strategy (real AI music)
│   │   └── factory.py         # Centralized strategy selector
│   ├── models/                 # One class per file domain models
│   │   ├── __init__.py
│   │   ├── genre.py
│   │   ├── mood.py
│   │   ├── prompt.py
│   │   ├── song.py
│   │   └── song_status.py
│   ├── migrations/             # Database migrations
│   ├── serializers.py          # DRF serializers
│   ├── views.py                # API views
│   ├── urls.py                 # App URL configuration
│   ├── admin.py                # Admin configuration
│   └── tests.py                # Unit tests
├── user/                       # User app
│   ├── models/                 # One class per file domain models
│   │   ├── __init__.py
│   │   ├── user.py
│   │   └── password_reset.py   # Password reset token model
│   ├── views/                  # Split view modules
│   │   ├── __init__.py
│   │   ├── auth_views.py       # Login / logout
│   │   ├── google_views.py     # Google OAuth
│   │   ├── password_views.py   # Forgot / reset password
│   │   └── user_views.py       # User CRUD + library
│   ├── migrations/             # Database migrations
│   ├── serializers.py          # DRF serializers
│   ├── urls.py                 # App URL configuration
│   ├── admin.py                # Admin configuration
│   └── tests.py                # Unit tests
├── db.sqlite3                  # SQLite database (development)
├── .env.example                # Example environment variables (safe to commit)
├── .gitignore                  # Excludes .env and other sensitive files
├── manage.py                   # Django management script
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

## Development

### Running Tests

Activate the virtual environment first, then run:

On macOS/Linux:
```bash
source .venv/bin/activate
```
On Windows:
```bash
.venv\Scripts\activate
```
then run this:
```bash
python3 manage.py test
```

**Actual output (all passing):**
```
Found 8 test(s).
Creating test database for alias 'default' ('file:memorydb_default?mode=memory&cache=shared')...
Operations to perform:
  Synchronize unmigrated apps: django_filters, messages, rest_framework, staticfiles
  Apply all migrations: admin, auth, contenttypes, sessions, song, user
Running migrations:
  Applying contenttypes.0001_initial... OK
  Applying auth.0001_initial... OK
  ...
  Applying song.0001_initial... OK
  Applying song.0002_alter_prompt_lyrics... OK
  Applying user.0001_initial... OK
  Applying user.0002_merge_to_user... OK
  Applying user.0003_passwordresettoken... OK
System check identified no issues (0 silenced).
test_prompt_crud (song.tests.PromptSongCRUDTests.test_prompt_crud) ... ok
test_song_crud (song.tests.PromptSongCRUDTests.test_song_crud) ... ok
test_download_redirects_when_audio_exists (song.tests.SongShareDownloadTests.test_download_redirects_when_audio_exists) ... ok
test_download_returns_404_when_no_audio (song.tests.SongShareDownloadTests.test_download_returns_404_when_no_audio) ... ok
test_share_returns_404_when_no_audio (song.tests.SongShareDownloadTests.test_share_returns_404_when_no_audio) ... ok
test_share_returns_url_when_audio_exists (song.tests.SongShareDownloadTests.test_share_returns_url_when_audio_exists) ... ok
test_user_crud (user.tests.UserDomainCRUDTests.test_user_crud) ... ok
test_user_library_actions (user.tests.UserDomainCRUDTests.test_user_library_actions) ... ok

----------------------------------------------------------------------
Ran 8 tests in 0.269s

OK
Destroying test database for alias 'default' ('file:memorydb_default?mode=memory&cache=shared')...
```

Each `ok` is one passing test. Tests use an **in-memory SQLite database** — the production `db.sqlite3` is never touched during tests.

| Test Module | Test Class | Tests |
|-------------|------------|-------|
| `song.tests` | `PromptSongCRUDTests` | `test_prompt_crud`, `test_song_crud` |
| `song.tests` | `SongShareDownloadTests` | `test_share_returns_url_when_audio_exists`, `test_share_returns_404_when_no_audio`, `test_download_redirects_when_audio_exists`, `test_download_returns_404_when_no_audio` |
| `user.tests` | `UserDomainCRUDTests` | `test_user_crud`, `test_user_library_actions` |

---

## Test Groups and Expected Results

### Group 1: `song.tests.PromptSongCRUDTests`

#### `test_prompt_crud`
Tests full CRUD lifecycle for the `Prompt` entity.

**Create** — `POST /api/prompts/`
```json
// Request body
{
  "title": "Birthday Prompt",
  "description": "Generate an upbeat birthday song",
  "occasion": "Birthday Party",
  "genre": "POP",
  "mood": "HAPPY",
  "voice_type": "Female",
  "lyrics": "Happy birthday to you"
}
// Response — 201 Created
{
  "id": 1,
  "title": "Birthday Prompt",
  "description": "Generate an upbeat birthday song",
  "occasion": "Birthday Party",
  "genre": "POP",
  "mood": "HAPPY",
  "voice_type": "Female",
  "lyrics": "Happy birthday to you",
  "created_at": "2026-03-23T16:27:47.026484Z",
  "updated_at": "2026-03-23T16:27:47.026497Z",
  "songs_count": 0
}
```
*Database effect: 1 row inserted into `song_prompt`.*

**Read** — `GET /api/prompts/` → `200 OK`
```json
{
  "count": 1,
  "next": null,
  "previous": null,
  "results": [{ "id": 1, "title": "Birthday Prompt", ... }]
}
```

**Update** — `PATCH /api/prompts/1/` with `{"title": "Updated Birthday Prompt"}` → `200 OK`
```json
{
  "id": 1,
  "title": "Updated Birthday Prompt",
  ...
  "updated_at": "2026-03-23T16:27:47.030265Z"
}
```
*Database effect: `title` and `updated_at` updated in `song_prompt`.*

**Delete** — `DELETE /api/prompts/1/` → `204 No Content` (empty body)
*Database effect: row removed from `song_prompt`. All linked songs are also deleted (`CASCADE`).*

---

#### `test_song_crud`
Tests full CRUD lifecycle for the `Song` entity (requires a linked `Prompt`).

**Create** — `POST /api/songs/`
```json
// Request body
{
  "title": "Birthday Song",
  "description": "Generated song",
  "prompt": 1,
  "status": "GENERATING",
  "url": "https://example.com/song.mp3",
  "meta_data": { "source": "test" }
}
// Response — 201 Created
{
  "id": 1,
  "title": "Birthday Song",
  "description": "Generated song",
  "prompt": 1,
  "status": "GENERATING",
  "url": "https://example.com/song.mp3",
  "meta_data": { "source": "test" }
}
```
*Database effect: 1 row inserted into `song_song`.*

**Update** — `PATCH /api/songs/1/` with `{"status": "READY"}` → `200 OK`
```json
{ "status": "READY", ... }
```
*Database effect: `status` field updated to `READY` in `song_song`.*

**Delete** — `DELETE /api/songs/1/` → `204 No Content`
*Database effect: row removed from `song_song`.*

---

### Group 2: `song.tests.SongShareDownloadTests`

Tests the share (FR-13) and download (FR-12) endpoints. Uses two songs: one with an audio URL (happy path) and one without (error path).

#### `test_share_returns_url_when_audio_exists` (FR-13 happy path)
**GET** `/api/songs/{id}/share/` on a song with a URL → `200 OK`
```json
{ "share_url": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3" }
```

#### `test_share_returns_404_when_no_audio` (FR-13 error path)
**GET** `/api/songs/{id}/share/` on a song with no URL → `404 Not Found`
```json
{ "error": "No audio available for this song yet." }
```

#### `test_download_redirects_when_audio_exists` (FR-12 happy path)
**GET** `/api/songs/{id}/download/` on a song with a URL → `302 Found`
- `Location` header points to the audio file URL.
- The test uses `follow=False` to assert the redirect itself, not the destination.

#### `test_download_returns_404_when_no_audio` (FR-12 error path)
**GET** `/api/songs/{id}/download/` on a song with no URL → `404 Not Found`
```json
{ "error": "No audio available for this song yet." }
```

---

### Group 3: `user.tests.UserDomainCRUDTests`

#### `test_user_crud`
Tests full CRUD lifecycle for the `User` profile entity.

**Create** — `POST /api/users/`
```json
// Request body
{
  "username": "testuser1",
  "password": "securepass123",
  "email": "testuser1@example.com"
}
// Response — 201 Created
{
  "user": 1,
  "library": []
}
```
*Database effect: 1 row in `auth_user` (password stored as bcrypt/PBKDF2 hash, never plain text) + 1 row in `user_user`.*

**Read (list)** — `GET /api/users/` → `200 OK`, `count >= 1`

**Read (detail)** — `GET /api/users/1/` → `200 OK`

**Update** — `PATCH /api/users/1/` with `{"library": []}` → `200 OK`

**Delete** — `DELETE /api/users/1/` → `204 No Content`
*Database effect: row removed from `user_user` and `auth_user` (CASCADE).*

---

#### `test_user_library_actions`
Tests song library management on a `User` profile.

**Add song** — `POST /api/users/1/add_song/` with `{"song_id": 1}` → `200 OK`
```json
{ "message": "Song added to library" }
```
*Database effect: 1 row inserted into the `user_user_library` join table.*

**View library** — `GET /api/users/1/library/` → `200 OK`
```json
[
  {
    "id": 1,
    "title": "Library Song",
    "status": "GENERATING",
    "prompt_title": "Prompt for user tests",
    "created_at": "2026-03-23T16:27:47.044795Z",
    "url": ""
  }
]
```
*Database effect: 1 entry in `user_user_library` — confirms persistence.*

**Remove song** — `POST /api/users/1/remove_song/` with `{"song_id": 1}` → `200 OK`
```json
{ "message": "Song removed from library" }
```
*Database effect: row deleted from `user_user_library`.*

**Verify empty** — `GET /api/users/1/library/` → `200 OK`, returns `[]`

---

### Making Model Changes

1. Modify models in `song/models/` or `user/models/`
2. Create migrations: `python manage.py makemigrations`
3. Apply migrations: `python manage.py migrate`


## Contributors

- 6710545601 Nattanan Pimjaipong