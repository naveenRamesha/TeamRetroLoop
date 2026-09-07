# TeamRetroLoop
Weekly feedback team retro application developed by following AI-Native or Spec driven Development 

## Local setup

Install the project and development dependencies:

```powershell
uv sync
```

Run the test suite:

```powershell
uv run pytest
```

Start the local Django server:

```powershell
uv run python manage.py runserver
```

## Authentication API

The MVP currently uses Django session authentication. Obtain a CSRF token from
`GET /api/auth/csrf/`, then send it in the `X-CSRFToken` header for
state-changing browser requests.

- `POST /api/auth/login/` authenticates a username and password.
- `POST /api/auth/logout/` ends the current session.
- `GET /api/auth/me/` returns the authenticated user profile.
- `PATCH /api/auth/me/` updates `first_name`, `last_name`, or `email`.
