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

## Project Structure

```
Cithara/
├── Cithara/                # Project configuration
│   ├── settings.py        # Django settings
│   ├── urls.py           # Main URL configuration
│   └── wsgi.py           # WSGI configuration
├── song/                  # Song app
│   ├── models.py         # Domain models
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

1. Modify models in `song/models.py`
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
