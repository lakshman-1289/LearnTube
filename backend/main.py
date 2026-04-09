import os
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from routers.course_routes import router as course_router
from routers.auth_routes import router as auth_router
from routers.exam_routes import router as exam_router

# Load environment variables
env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=env_path)

# Ensure HF_TOKEN is set
if not os.getenv("HF_TOKEN"):
    os.environ["HF_TOKEN"] = "your_token_here"

app = FastAPI(
    title="LearnTube Modular Backend",
    version="3.0.0",
    description="LearnTube backend — courses, auth, exams, certificates.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(course_router)
app.include_router(auth_router)
app.include_router(exam_router)

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "LearnTube Backend"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
