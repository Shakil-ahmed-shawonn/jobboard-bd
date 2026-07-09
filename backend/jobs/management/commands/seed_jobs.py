"""
jobs/management/commands/seed_jobs.py

Seeds 4 fictional employer accounts (with company profiles) and 8 realistic
job posts across backend, ML, frontend, DevOps, and QA roles — matching the
kind of listings a Bangladeshi tech job board would realistically show.

Usage:
    python manage.py seed_jobs

Safe to re-run: skips creating an employer/job if a user with that username
already exists, so running it twice won't create duplicates.
"""

from django.core.management.base import BaseCommand

from accounts.models import CompanyProfile, User
from jobs.models import JobPost

EMPLOYERS = [
    {
        "username": "hr_nexustech",
        "email": "hr@nexustech.example",
        "company_name": "NexusTech Solutions",
        "website": "https://nexustech.example",
        "description": "Mid-size software house in Dhaka building B2B SaaS products for logistics and retail clients across South Asia.",
    },
    {
        "username": "hr_databird",
        "email": "careers@databird.example",
        "company_name": "DataBird Analytics",
        "website": "https://databird.example",
        "description": "Data and ML consultancy helping e-commerce companies in Bangladesh build recommendation and forecasting systems.",
    },
    {
        "username": "hr_pixelforge",
        "email": "jobs@pixelforge.example",
        "company_name": "PixelForge Studio",
        "website": "https://pixelforge.example",
        "description": "Product design and frontend engineering studio, remote-first, working with startups across Southeast Asia.",
    },
    {
        "username": "hr_cloudnine",
        "email": "hr@cloudnine.example",
        "company_name": "CloudNine Systems",
        "website": "https://cloudnine.example",
        "description": "Cloud infrastructure and DevOps consultancy serving fintech and telecom clients in Bangladesh.",
    },
]

JOBS = [
    {
        "employer": "hr_nexustech",
        "title": "Backend Developer (Python/Django)",
        "location": "Dhaka, Bangladesh",
        "salary_range": "৳45,000 - ৳70,000",
        "description": (
            "We're looking for a Backend Developer to join our core platform team, building and "
            "maintaining REST APIs that power our logistics dashboard used by 200+ retail clients. "
            "You'll work closely with frontend and DevOps engineers in a small, fast-moving team."
        ),
        "requirements": (
            "2+ years of professional experience with Python and Django or FastAPI. "
            "Solid understanding of REST API design and PostgreSQL. "
            "Experience with Django REST Framework, authentication (JWT/OAuth), and writing unit tests (pytest). "
            "Familiarity with Docker and basic Linux server administration is a plus. "
            "Comfortable working with Git and collaborating via GitHub pull requests."
        ),
    },
    {
        "employer": "hr_nexustech",
        "title": "Full Stack Developer (Django + React)",
        "location": "Dhaka, Bangladesh (Hybrid)",
        "salary_range": "৳55,000 - ৳85,000",
        "description": (
            "Join our product team to build customer-facing features end to end — from Django API "
            "endpoints to React components. You'll own features from design review through deployment."
        ),
        "requirements": (
            "3+ years building full-stack web applications with Django and React. "
            "Strong JavaScript/TypeScript fundamentals, comfortable with React hooks and state management. "
            "Experience with Django REST Framework and PostgreSQL. "
            "Understanding of CI/CD pipelines and basic cloud deployment (Render, Vercel, or AWS). "
            "Good communication skills — this role works directly with product managers."
        ),
    },
    {
        "employer": "hr_databird",
        "title": "Machine Learning Engineer",
        "location": "Dhaka, Bangladesh (Remote-friendly)",
        "salary_range": "৳70,000 - ৳110,000",
        "description": (
            "Build and deploy ML models for demand forecasting and product recommendation systems used "
            "by our e-commerce clients. You'll work across the full ML lifecycle — from data pipeline to "
            "production API."
        ),
        "requirements": (
            "2+ years of hands-on ML engineering experience with scikit-learn or PyTorch. "
            "Strong Python skills and experience serving models via FastAPI or Flask. "
            "Practical experience with pandas, feature engineering, and model evaluation metrics. "
            "Familiarity with Hugging Face Transformers for NLP tasks is a strong plus. "
            "Bachelor's degree in CS, Statistics, or a related field, or equivalent demonstrated experience "
            "(GitHub portfolio, Kaggle competitions, or published projects)."
        ),
    },
    {
        "employer": "hr_databird",
        "title": "NLP Engineer — Sentiment & Text Classification",
        "location": "Dhaka, Bangladesh (Remote)",
        "salary_range": "৳65,000 - ৳100,000",
        "description": (
            "Work on text classification and sentiment analysis pipelines processing customer reviews "
            "for retail clients. You'll evaluate and fine-tune transformer models and ship them as "
            "production APIs."
        ),
        "requirements": (
            "1-2+ years of experience with NLP, including sentiment analysis or text classification. "
            "Practical experience with Hugging Face Transformers and model evaluation (precision/recall/F1). "
            "Strong Python skills; experience building inference APIs with FastAPI. "
            "Experience comparing and selecting pretrained models (e.g. BERT variants) for a specific task. "
            "Comfortable working with imbalanced or noisy real-world text data."
        ),
    },
    {
        "employer": "hr_pixelforge",
        "title": "Frontend Developer (React)",
        "location": "Remote (Bangladesh-based preferred)",
        "salary_range": "৳50,000 - ৳75,000",
        "description": (
            "Build clean, accessible interfaces for our clients' web products. You'll work from Figma "
            "designs and collaborate closely with our design team to ship polished, responsive UIs."
        ),
        "requirements": (
            "2+ years of professional React development experience. "
            "Strong CSS fundamentals and experience with Tailwind CSS. "
            "Comfortable consuming REST APIs and managing client-side state (Context API or Redux). "
            "Experience with Vite or similar modern build tooling. "
            "An eye for design detail — spacing, typography, and responsive behavior matter here."
        ),
    },
    {
        "employer": "hr_pixelforge",
        "title": "Junior Frontend Developer",
        "location": "Dhaka, Bangladesh",
        "salary_range": "৳30,000 - ৳45,000",
        "description": (
            "Entry-level role for a recent graduate or self-taught developer ready to work on real "
            "client projects. You'll be mentored by senior engineers while contributing to production code."
        ),
        "requirements": (
            "Solid fundamentals in HTML, CSS, and JavaScript. "
            "Some hands-on experience with React, even from personal or academic projects. "
            "Familiarity with Git and basic command-line usage. "
            "Strong willingness to learn and take feedback — this is a growth-focused role. "
            "A portfolio or GitHub profile with 2-3 projects is preferred, even if small."
        ),
    },
    {
        "employer": "hr_cloudnine",
        "title": "DevOps Engineer",
        "location": "Dhaka, Bangladesh",
        "salary_range": "৳60,000 - ৳95,000",
        "description": (
            "Own CI/CD pipelines and cloud infrastructure for fintech clients with strict uptime and "
            "security requirements. You'll work with Docker, Kubernetes, and infrastructure-as-code tools."
        ),
        "requirements": (
            "2+ years of DevOps or SRE experience. "
            "Strong experience with Docker and container orchestration (Kubernetes preferred). "
            "Familiarity with CI/CD tools (GitHub Actions, GitLab CI, or Jenkins). "
            "Experience with at least one cloud provider (AWS, GCP, or Azure). "
            "Scripting proficiency in Bash or Python for automation tasks. "
            "Understanding of monitoring/logging tools (Prometheus, Grafana, or similar)."
        ),
    },
    {
        "employer": "hr_cloudnine",
        "title": "QA / Test Automation Engineer",
        "location": "Dhaka, Bangladesh (Hybrid)",
        "salary_range": "৳40,000 - ৳60,000",
        "description": (
            "Ensure product quality across our client delivery pipeline by building automated test "
            "suites and working closely with backend and frontend teams to catch issues before release."
        ),
        "requirements": (
            "1-2+ years of QA experience, including manual and automated testing. "
            "Experience writing automated tests with pytest or Selenium. "
            "Understanding of REST API testing (Postman or similar tools). "
            "Familiarity with CI pipelines and integrating automated tests into them. "
            "Detail-oriented with strong written communication for bug reports."
        ),
    },
]


class Command(BaseCommand):
    help = "Seeds demo employer accounts and realistic job posts for testing/screenshots."

    def handle(self, *args, **options):
        created_employers = 0
        for emp in EMPLOYERS:
            if User.objects.filter(username=emp["username"]).exists():
                self.stdout.write(f"Skipping existing employer: {emp['username']}")
                continue

            user = User.objects.create_user(
                username=emp["username"],
                email=emp["email"],
                password="DemoPass123!",
                role=User.Role.EMPLOYER,
            )
            CompanyProfile.objects.create(
                user=user,
                company_name=emp["company_name"],
                website=emp["website"],
                description=emp["description"],
            )
            created_employers += 1
            self.stdout.write(self.style.SUCCESS(f"Created employer: {emp['username']}"))

        created_jobs = 0
        for job in JOBS:
            employer = User.objects.get(username=job["employer"])
            if JobPost.objects.filter(employer=employer, title=job["title"]).exists():
                self.stdout.write(f"Skipping existing job: {job['title']}")
                continue

            JobPost.objects.create(
                employer=employer,
                title=job["title"],
                description=job["description"],
                requirements=job["requirements"],
                location=job["location"],
                salary_range=job["salary_range"],
            )
            created_jobs += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"\nDone. Created {created_employers} employer(s) and {created_jobs} job(s)."
            )
        )
        self.stdout.write(
            "All demo employer accounts use the password: DemoPass123!\n"
            "Log in as e.g. 'hr_nexustech' to view/manage a specific company's posts."
        )
