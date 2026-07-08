# JobBoard BD — Backend (Step 1 + Step 2)

## Step 1 — Models + Auth
- `accounts` app: custom `User` (role: employer/seeker), `CompanyProfile`, JWT registration
- JWT login/refresh: `/api/auth/token/`, `/api/auth/token/refresh/`
- Registration: `/api/accounts/register/`

## Step 2 — Jobs CRUD + Applications + AI Fit Scoring
- `jobs` app: full CRUD at `/api/jobs/`
  - `GET /api/jobs/?search=&location=` — public browse/search (active posts only)
  - `GET /api/jobs/?mine=true` — employer's own posts (active + inactive)
  - `POST/PUT/PATCH/DELETE` — restricted to the owning employer
- `applications` app: `/api/applications/`
  - `POST` (seeker only) — apply with resume upload (`.pdf`/`.docx`, max 5MB); resume
    is parsed and scored against the job's `requirements` via Claude **synchronously**
    on submit (see note in `applications/views.py` about moving this to a background
    task at scale)
  - `GET` — seeker sees own applications; employer sees applicants to their own posts,
    ordered by `ai_fit_score` (model default ordering)
  - `PATCH` (employer only) — update `status` only (`pending/reviewed/shortlisted/rejected`)

## Not yet built (next steps)
- Frontend (React)
- Background task queue for AI scoring (Celery/RQ) — optional hardening

## Local setup
```bash
python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env               # fill in real values incl. ANTHROPIC_API_KEY
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## Test the flow (curl)
```bash
# 1. Register employer
curl -X POST http://localhost:8000/api/accounts/register/ \
  -H "Content-Type: application/json" \
  -d '{"username":"acme_hr","email":"hr@acme.com","password":"StrongPass123!","role":"employer","company_name":"Acme Ltd"}'

# 2. Login (get access token)
curl -X POST http://localhost:8000/api/auth/token/ \
  -H "Content-Type: application/json" \
  -d '{"username":"acme_hr","password":"StrongPass123!"}'

# 3. Post a job (replace TOKEN)
curl -X POST http://localhost:8000/api/jobs/ \
  -H "Authorization: Bearer TOKEN" -H "Content-Type: application/json" \
  -d '{"title":"Backend Engineer","description":"...","requirements":"Python, FastAPI, PostgreSQL, 2+ yrs","location":"Dhaka"}'

# 4. Register + login a seeker, then apply (multipart)
curl -X POST http://localhost:8000/api/applications/ \
  -H "Authorization: Bearer SEEKER_TOKEN" \
  -F "job=1" -F "resume_file=@/path/to/resume.pdf" -F "cover_note=Excited to apply"
```

## Troubleshooting
| Error | Fix |
|---|---|
| `django.db.utils.OperationalError: could not connect to server` | PostgreSQL not running locally, or `.env` DB credentials wrong |
| `ImproperlyConfigured: AUTH_USER_MODEL refers to model 'accounts.User' that has not been installed` | Run `makemigrations accounts` **before** any other app's migrations |
| `company_name: Required for employer accounts` on seeker signup | Expected — only send `company_name` when `role=employer` |
| CORS error from frontend | Confirm frontend origin is listed in `CORS_ALLOWED_ORIGINS` in `.env` |
| `ResumeParsingError: No extractable text found` | Scanned/image-only PDF — application still saves, just without an AI score (check `ai_fit_score is null`) |
| `RuntimeError: AI fit scoring failed` | Check `ANTHROPIC_API_KEY` is set; check Anthropic API status |
| 403 on `POST /api/jobs/` | Account has `role=seeker` — only employers can create jobs |
| 403 on `POST /api/applications/` | Account has `role=employer` — only seekers can apply |
| `unique_together` violation on apply | Seeker already applied to this job — one application per job per seeker by design |

