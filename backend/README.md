Django + DRF backend scaffold for Thinktank LMS

Quick start (with Docker):

1. Copy `.env.example` to `.env` and fill values.
2. docker-compose up --build
3. Apply migrations: docker-compose exec web python manage.py migrate
4. Create superuser: docker-compose exec web python manage.py createsuperuser

This scaffold includes `users` and `courses` apps, JWT auth, and is S3-ready.
