# Incident-AI

Incident-AI is an intelligent technical incident management and investigation platform. It leverages AI to automatically analyze system outages, evidence files, and logs to help engineering teams resolve problems faster. 

## Tech Stack

### Frontend (Web)
- **Framework:** Next.js (App Router)
- **Authentication:** Clerk (Email & Google OAuth)
- **Deployment:** Vercel

### Backend (API)
- **Framework:** FastAPI (Python)
- **Database:** PostgreSQL (Neon)
- **ORM:** SQLAlchemy & Alembic
- **Storage:** Cloudinary (for evidence files)
- **AI Integration:** LangGraph, Ollama / Gemini (Multi-agent workflow)
- **Deployment:** Render

## Project Structure

This is a monorepo setup containing both the frontend and backend applications.

- `/apps/web` - The Next.js frontend application.
- `/apps/api` - The FastAPI Python backend.

## Local Development Setup

### 1. Backend Setup (`/apps/api`)
Ensure you have Python and `uv` installed.
1. Navigate to the api directory: `cd apps/api`
2. Install dependencies: `uv sync`
3. Create a `.env` file and fill in your required keys (`DATABASE_URL`, `CLERK_SECRET_KEY`, `CLOUDINARY_URL`, etc.).
4. Run database migrations: `uv run alembic upgrade head`
5. Start the server: `uv run uvicorn app.main:app --reload`

### 2. Frontend Setup (`/apps/web`)
Ensure you have Node.js installed.
1. Navigate to the web directory: `cd apps/web`
2. Install dependencies: `npm install`
3. Create a `.env.local` file with your Clerk keys (`NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY`, `CLERK_SECRET_KEY`).
4. Start the development server: `npm run dev`

The frontend will run at `http://localhost:3000` and automatically proxy API requests (`/api/*`) to the backend running at `http://127.0.0.1:8000`.

## Features
- **Incident Tracking:** Create and manage technical incidents.
- **Evidence Uploads:** Attach logs, screenshots, and context to incidents (backed by Cloudinary).
- **AI Investigation:** Trigger automated AI investigations using a multi-agent workflow that proposes hypotheses and validates them against the provided evidence.
- **Secure Authentication:** User management and Google OAuth powered by Clerk.

## Deployment Notes
- **Frontend (Vercel):** Ensure you set `NEXT_PUBLIC_CLERK_PUBLISHABLE_KEY`, `CLERK_SECRET_KEY`, and `API_URL` (pointing to the Render backend) in your Vercel environment variables. Also ensure your Google OAuth keys are added to your Clerk Production instance.
- **Backend (Render):** Set your `DATABASE_URL`, `CLERK_SECRET_KEY`, and Cloudinary variables in the Render environment settings.
