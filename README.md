# Cithara - AI Song Generation Platform

A Django-based application for AI-powered song generation using prompts.

## Project Overview

Cithara is a song generation platform that allows users to create songs based on detailed prompts including genre, mood, occasion, and lyrics. The system manages the entire lifecycle of song generation from prompt creation to final output.

## Domain Model

- **Prompt**: Song generation request with title, description, occasion, genre, mood, voice type, and lyrics
- **Song**: Generated songs with metadata, audio files, and generation status
- **SongShareLink**: Opaque UUID token that lets unauthenticated users access a specific song via a public player URL
- **Genre**: Enumeration (Pop, Rock, Jazz, Classical, R&B)
- **Mood**: Enumeration (Happy, Sad, Energetic, Relaxed)
- **SongStatus**: Enumeration (Generating, Ready, Failed)

## Technology Stack

- **Backend**: Django 6.0.3
- **API**: Django REST Framework 3.17.0
- **Auth**: JWT via djangorestframework-simplejwt + Google OAuth 2.0
- **Database**: SQLite (development)
- **Python**: 3.13+

---

## Setup Instructions

### Prerequisites

- Python 3.8 or higher
- pip
- Git
- A Google Cloud project (for Google OAuth — optional)
- A Suno API key (for real AI generation — optional)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/LylatierN/Cithara.git
   cd Cithara
   ```

2. **Create and activate virtual environment**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # Windows: .venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**

   Copy `.env.example` to `.env`:
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
   | `SUNO_API_KEY` | API key from [sunoapi.org](https://sunoapi.org/api-key) — only needed when `GENERATOR_STRATEGY=suno` |
   | `GOOGLE_CLIENT_ID` | Google OAuth client ID — only needed for `/api/auth/google/` |
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

## Google OAuth Setup

To enable "Login with Google", you need a Google Cloud OAuth 2.0 client:

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (or select an existing one)
3. Navigate to **APIs & Services → Credentials**
4. Click **Create Credentials → OAuth 2.0 Client ID**
5. Set application type to **Web application**
6. Under **Authorised redirect URIs**, add:
   ```
   http://localhost:8000/api/auth/google/callback/
   ```
7. Click **Create** — copy the **Client ID** and **Client Secret**
8. Paste them into your `.env` file:
   ```
   GOOGLE_CLIENT_ID=your-client-id-here
   GOOGLE_CLIENT_SECRET=your-client-secret-here
   ```

The OAuth flow works as follows:
- `GET /api/auth/google/` — redirects user to Google's consent screen
- `GET /api/auth/google/callback/` — Google redirects back here with an auth code; the system exchanges it for tokens, creates or retrieves the user, and returns a JWT pair

> ⚠️ Google OAuth only works on `localhost` in development. For production, add your production domain to the redirect URIs in Google Cloud Console.

---

## Exercise 4: Strategy Pattern for Song Generation

### Overview

This exercise implements the Strategy design pattern for song generation. The strategy is selected via an environment variable, making it easy to swap between mock and real generation without changing any code.

Two strategies are available:
- **Mock**: Offline, no API calls, instant result — for development and testing
- **Suno**: Calls the real SunoApi.org to generate AI music

### Strategy Pattern Structure

```
song/
  generation/
    __init__.py
    base.py            # Abstract base class — SongGeneratorStrategy interface
    mock_strategy.py   # Concrete strategy A: offline, deterministic
    suno_strategy.py   # Concrete strategy B: real Suno API
    factory.py         # Reads GENERATOR_STRATEGY env var, returns correct strategy
    content_filter.py  # Profanity filter applied before generation
```

### Abstract Base Class

`base.py` defines the strategy interface using Python's `ABC` and `@abstractmethod`:

```python
class SongGeneratorStrategy(ABC):
    @abstractmethod
    def generate(self, request: GenerationRequest) -> GenerationResult:
        ...

    @abstractmethod
    def get_status(self, task_id: str) -> GenerationResult:
        ...
```

Both `MockSongGeneratorStrategy` and `SunoSongGeneratorStrategy` inherit from this class and implement both methods. This guarantees that swapping strategies never requires changes anywhere else in the codebase.

### How to Switch Strategy

Set `GENERATOR_STRATEGY` in your `.env` file:

```
GENERATOR_STRATEGY=mock   # offline, no API key needed
GENERATOR_STRATEGY=suno   # real AI, requires SUNO_API_KEY
```

`factory.py` is the single place in the codebase that reads this value and decides which strategy to return. There are no scattered `if/else` checks anywhere else.

### How to Get a Suno API Key

1. Go to [sunoapi.org/api-key](https://sunoapi.org/api-key)
2. Sign up or log in
3. Copy your API key
4. Add it to your `.env` file:
   ```
   SUNO_API_KEY=your-actual-key-here
   ```

> ⚠️ Never commit this key to GitHub. The `.env` file is in `.gitignore`.

### Running Mock Mode

1. Set `GENERATOR_STRATEGY=mock` in `.env`
2. Start the server: `python manage.py runserver`
3. Obtain a JWT token:
   ```bash
   curl -X POST http://127.0.0.1:8000/api/auth/login/ \
     -H "Content-Type: application/json" \
     -d '{"username": "your-username", "password": "your-password"}'
   ```
4. Create a prompt:
   ```bash
   curl -X POST http://127.0.0.1:8000/api/prompts/ \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer <access_token>" \
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
5. Create a song linked to that prompt:
   ```bash
   curl -X POST http://127.0.0.1:8000/api/songs/ \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer <access_token>" \
     -d '{"title": "My Song", "description": "", "prompt": 1, "status": "GENERATING", "meta_data": {}}'
   ```
6. Trigger mock generation:
   ```bash
   curl -X POST http://127.0.0.1:8000/api/songs/1/generate/ \
     -H "Authorization: Bearer <access_token>"
   ```
7. Response returns immediately with `"status": "READY"` and a placeholder audio URL:
   ```json
   {
     "status": "READY",
     "url": "https://www.soundhelix.com/examples/mp3/SoundHelix-Song-1.mp3",
     "meta_data": { "mock": true, "task_id": "mock-task-12345" }
   }
   ```

### Running Suno Mode

1. Set `GENERATOR_STRATEGY=suno` and `SUNO_API_KEY=your-key` in `.env`
2. Start the server: `python manage.py runserver`
3. Follow steps 3–5 from Mock Mode above
4. Trigger Suno generation:
   ```bash
   curl -X POST http://127.0.0.1:8000/api/songs/1/generate/ \
     -H "Authorization: Bearer <access_token>"
   ```
5. Response returns a `taskId` from Suno:
   ```json
   { "status": "GENERATING", "meta_data": { "task_id": "8bed802b4d9da98a18754ce97825a7ed" } }
   ```
6. Poll for status after 30–40 seconds:
   ```bash
   curl http://127.0.0.1:8000/api/songs/1/check_status/ \
     -H "Authorization: Bearer <access_token>"
   ```
7. When ready:
   ```json
   {
     "task_id": "8bed802b4d9da98a18754ce97825a7ed",
     "suno_status": "SUCCESS",
     "audio_url": "https://..../song.mp3",
     "song_status": "READY"
   }
   ```

---

## Authentication

All endpoints require a valid JWT access token except:
- `POST /api/auth/login/` — obtain tokens
- `POST /api/users/` — register a new account
- `GET /api/songs/play/{token}/` — public song player via share link
- `GET /api/songs/download/{token}/` — public song download via share link

### JWT Tokens

| Setting | Value |
|---------|-------|
| Access token lifetime | 30 minutes |
| Refresh token lifetime | 7 days |

Include the token in every request header:
```
Authorization: Bearer <access_token>
```

---

## API Endpoints

### Authentication

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `POST` | `/api/auth/login/` | No | Obtain JWT access + refresh tokens |
| `POST` | `/api/auth/logout/` | Yes | Invalidate the current session |
| `POST` | `/api/auth/refresh/` | No | Refresh a JWT access token |
| `GET` | `/api/auth/google/` | No | Redirect to Google OAuth consent screen |
| `GET` | `/api/auth/google/callback/` | No | Handle Google OAuth callback |
| `POST` | `/api/auth/forgot-password/` | No | Send a password reset email |
| `POST` | `/api/auth/reset-password/` | No | Reset password using a token |

### Users

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `GET` | `/api/users/` | Yes | List all users |
| `POST` | `/api/users/` | No | Create a new user |
| `GET` | `/api/users/{id}/` | Yes | Retrieve a specific user |
| `PUT` | `/api/users/{id}/` | Yes | Full update a user |
| `PATCH` | `/api/users/{id}/` | Yes | Partial update a user |
| `DELETE` | `/api/users/{id}/` | Yes | Delete a user |
| `GET` | `/api/users/{id}/library/` | Yes | Get the user's song library |
| `POST` | `/api/users/{id}/add_song/` | Yes | Add a song to the library |
| `POST` | `/api/users/{id}/remove_song/` | Yes | Remove a song from the library |

### Prompts

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `GET` | `/api/prompts/` | Yes | List all prompts |
| `POST` | `/api/prompts/` | Yes | Create a new prompt |
| `GET` | `/api/prompts/{id}/` | Yes | Retrieve a specific prompt |
| `PUT` | `/api/prompts/{id}/` | Yes | Full update a prompt |
| `PATCH` | `/api/prompts/{id}/` | Yes | Partial update a prompt |
| `DELETE` | `/api/prompts/{id}/` | Yes | Delete a prompt |
| `GET` | `/api/prompts/{id}/songs/` | Yes | List all songs generated from a prompt |

### Songs

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `GET` | `/api/songs/` | Yes | List all songs |
| `POST` | `/api/songs/` | Yes | Create a new song |
| `GET` | `/api/songs/{id}/` | Yes | Retrieve a specific song |
| `PUT` | `/api/songs/{id}/` | Yes | Full update a song |
| `PATCH` | `/api/songs/{id}/` | Yes | Partial update a song |
| `DELETE` | `/api/songs/{id}/` | Yes | Delete a song |
| `POST` | `/api/songs/{id}/generate/` | Yes | Trigger song generation |
| `GET` | `/api/songs/{id}/check_status/` | Yes | Poll generation status |
| `GET` | `/api/songs/{id}/share/` | Yes | Generate a public share link |
| `GET` | `/api/songs/play/{token}/` | No | Public player — returns title + audio URL |
| `GET` | `/api/songs/download/{token}/` | No | Public download — 302 redirect to audio |

---

## Running Tests

```bash
source .venv/bin/activate
python manage.py test
```

Expected output (all passing):

```
Found 24 test(s).
...
Ran 24 tests in x.xxxs
OK
```

| Test Class | What it covers |
|------------|----------------|
| `PromptSongCRUDTests` | Full CRUD for Prompt and Song |
| `SongShareDownloadTests` | Token-based share/play/download, auth requirements |
| `SongGenerationTimeoutTests` | NFR-06: 10-minute generation timeout |
| `SongLibraryLimitTests` | FR-14: 20-song library limit at generate time |
| `SongConcurrentGenerationLimitTests` | NFR-12: max 3 songs generating at once |
| `SongGenerationRetryTests` | NFR-20: retry once on failure, no double retry |
| `SongGenerationFailureTests` | FR-15: clear error message on generation failure |

---

## Project Structure

```
Cithara/
├── Cithara/
│   ├── settings.py
│   ├── urls.py
│   ├── asgi.py
│   └── wsgi.py
├── song/
│   ├── generation/
│   │   ├── base.py             # Abstract strategy interface + dataclasses
│   │   ├── content_filter.py   # Profanity filter
│   │   ├── mock_strategy.py    # Mock strategy (offline/testing)
│   │   ├── suno_strategy.py    # Suno API strategy (real AI music)
│   │   └── factory.py          # Reads GENERATOR_STRATEGY, returns correct strategy
│   ├── models/
│   │   ├── genre.py
│   │   ├── mood.py
│   │   ├── prompt.py
│   │   ├── song.py
│   │   ├── song_share_link.py  # UUID token for public share links
│   │   └── song_status.py
│   ├── migrations/
│   ├── serializers.py
│   ├── services.py             # Business logic (limits, generation, retry)
│   ├── views.py                # HTTP layer only
│   ├── urls.py
│   ├── admin.py
│   └── tests.py
├── user/
│   ├── models/
│   │   ├── user.py
│   │   └── password_reset.py
│   ├── views/
│   │   ├── auth_views.py       # Login / logout
│   │   ├── google_views.py     # Google OAuth
│   │   ├── password_views.py   # Forgot / reset password
│   │   └── user_views.py       # User CRUD + library
│   ├── migrations/
│   ├── serializers.py
│   ├── urls.py
│   ├── admin.py
│   └── tests.py
├── .env.example
├── .gitignore
├── manage.py
├── requirements.txt
└── README.md
```

## Contributors

- 6710545601 Nattanan Pimjaipong