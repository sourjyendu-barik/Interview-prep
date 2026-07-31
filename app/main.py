import logging
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from app.models import InterviewRequest
from app.prompts import build_interview_prompt
from app.callLlm import fetchLlm
from app.routers import auth
from app.dependencies import get_current_user

logger = logging.getLogger("uvicorn")

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",     # local dev frontend
        "https://interview-preparation-tan.vercel.app",  # production frontend
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Routers ──────────────────────────────────────────
app.include_router(auth.public_router)   # /auth/login  — no auth
app.include_router(auth.private_router)  # /auth/me, /auth/logout — protected

@app.get("/")
def greet():
    return {"message": "My first app."}

@app.post("/interview/start", dependencies=[Depends(get_current_user)])
async def start_interview(data: InterviewRequest):
    logger.info("Authenticated user")

    logger.info("Building prompt")
    prompt = build_interview_prompt(
        job_role=data.job_role,
        years_experience=data.years_experience,
        technical_keywords=data.technical_keywords,
        company_type=data.company_type,
        focus_area=data.focus_area,
    )

    logger.info("Prompt built")

    logger.info("Calling Gemini")
    response = await fetchLlm(prompt)

    logger.info("Gemini returned")

    return response