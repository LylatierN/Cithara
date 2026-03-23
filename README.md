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
   git clone <repository-url>
   cd Cithara
   ```

2. **Create and activate virtual environment**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # On macOS/Linux
   # or
   .venv\Scripts\activate  # On Windows
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run database migrations**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

5. **Create a superuser (for admin access)**
   ```bash
   python manage.py createsuperuser
   ```

6. **Run the development server**
   ```bash
   python manage.py runserver
   ```

7. **Access the application**
   - Admin Panel: http://127.0.0.1:8000/admin/
   - API Root: http://127.0.0.1:8000/api/
   - Browsable API: http://127.0.0.1:8000/api-auth/

## API Endpoints

### Prompts

- `GET /api/prompts/` - List all prompts
- `POST /api/prompts/` - Create a new prompt
- `GET /api/prompts/{id}/` - Retrieve a specific prompt
- `PUT /api/prompts/{id}/` - Update a prompt
- `PATCH /api/prompts/{id}/` - Partial update a prompt
- `DELETE /api/prompts/{id}/` - Delete a prompt
- `GET /api/prompts/{id}/songs/` - Get all songs from a prompt

### Songs

- `GET /api/songs/` - List all songs
- `POST /api/songs/` - Create a new song
- `GET /api/songs/{id}/` - Retrieve a specific song
- `PUT /api/songs/{id}/` - Update a song
- `PATCH /api/songs/{id}/` - Partial update a song
- `DELETE /api/songs/{id}/` - Delete a song
- `POST /api/songs/{id}/mark_ready/` - Mark song as ready
- `POST /api/songs/{id}/mark_failed/` - Mark song as failed

### Users

- `GET /api/users/` - List all users
- `POST /api/users/` - Create a user profile
- `GET /api/users/{id}/` - Retrieve a specific user
- `PUT /api/users/{id}/` - Update a user
- `PATCH /api/users/{id}/` - Partial update a user
- `DELETE /api/users/{id}/` - Delete a user
- `GET /api/users/{id}/library/` - Get song library
- `POST /api/users/{id}/add_song/` - Add song to library
- `POST /api/users/{id}/remove_song/` - Remove song from library

### Filtering & Search

- Filter prompts by genre and mood: `/api/prompts/?genre=POP&mood=HAPPY`
- Search prompts: `/api/prompts/?search=birthday`
- Filter songs by status: `/api/songs/?status=READY`
- Search songs: `/api/songs/?search=love`

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
├── Cithara/                # Project configuration
│   ├── settings.py        # Django settings
│   ├── urls.py           # Main URL configuration
│   └── wsgi.py           # WSGI configuration
├── song/                  # Song app
│   ├── models/           # One class per file domain models
│   │   ├── __init__.py
│   │   ├── genre.py
│   │   ├── mood.py
│   │   ├── prompt.py
│   │   ├── song.py
│   │   └── song_status.py
│   ├── serializers.py    # DRF serializers
│   ├── views.py          # API views
│   ├── urls.py           # App URL configuration
│   ├── admin.py          # Admin configuration
│   └── migrations/       # Database migrations
├── user/                  # User app
│   ├── models/           # One class per file domain models
│   │   ├── __init__.py
│   │   └── user.py
│   ├── serializers.py    # DRF serializers
│   ├── views.py          # API views
│   ├── urls.py           # App URL configuration
│   ├── admin.py          # Admin configuration
│   └── migrations/       # Database migrations
├── manage.py             # Django management script
├── requirements.txt      # Python dependencies
└── README.md            # This file
```

## Development

### Running Tests
```bash
python manage.py test
```

### Making Model Changes

1. Modify models in `song/models/` or `user/models/`
2. Create migrations: `python manage.py makemigrations`
3. Apply migrations: `python manage.py migrate`

## Academic Project Requirements

This project fulfills the following requirements:

- ✅ **Task 1**: Django project setup with GitHub repository
- ✅ **Task 2**: Domain layer implementation with proper models
- ✅ **Task 3**: ORM and database migrations
- ✅ **Task 4**: Complete CRUD operations via Django Admin and REST API

## License

This is an academic project for educational purposes.

## Contributors

- Nattanan Pimjaipong
