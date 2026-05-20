import os
import certifi
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional, Dict, List


class DBService:
    def __init__(self):
        self.client = None
        self.db = None
        # Collections
        self.collection = None         # courses (legacy name kept)
        self.users_col = None
        self.jobs_col = None
        self.exams_col = None
        self.certs_col = None
        self._initialize()

    def _initialize(self):
        try:
            mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")
            db_name = os.getenv("DB_NAME", "learntube_db")
            collection_name = os.getenv("COLLECTION_NAME", "courses")

            self.client = AsyncIOMotorClient(mongo_uri)
            self.db = self.client[db_name]

            self.collection = self.db[collection_name]
            self.users_col = self.db["users"]
            self.jobs_col = self.db["jobs"]
            self.exams_col = self.db["exams"]
            self.certs_col = self.db["certificates"]

        except Exception as e:
            print(f"[DB INIT ERROR] Failed to connect to MongoDB: {e}")

    async def init_db_async(self):
        """Called safely from FastAPI Lifespan."""
        print("[DB] Initializing database indexes and cleaning stale jobs...")
        await self._create_indexes()
        await self._reset_orphaned_jobs()

    async def _reset_orphaned_jobs(self):
        try:
            result = await self.jobs_col.update_many(
                {"status": "processing"}, 
                {"$set": {"status": "failed", "error": "Server restarted before job completed."}}
            )
            if result.modified_count > 0:
                print(f"[DB INIT] Cleaned up {result.modified_count} orphaned jobs.")
        except Exception as e:
            print(f"[DB INIT ERROR] Failed to clean orphaned jobs: {e}")

    async def _create_indexes(self):
        try:
            await self.collection.create_index("video_id", unique=True)
            await self.users_col.create_index("email", unique=True)
            await self.jobs_col.create_index("job_id", unique=True)
            await self.exams_col.create_index([("user_id", 1), ("video_id", 1)])
            await self.certs_col.create_index("certificate_id", unique=True)
        except Exception as e:
            print(f"[DB INDEX ERROR] {e}")

    # ------------------------------------------------------------------ #
    #  COURSES (original — unchanged for backward compat)
    # ------------------------------------------------------------------ #

    async def get_cached_course(self, video_id: str) -> Optional[Dict]:
        if self.collection is None:
            return None
        try:
            document = await self.collection.find_one({"video_id": video_id})
            if document:
                document.pop("_id", None)
                print(f"✅ Cache hit for video_id: {video_id}")
                return document
            return None
        except Exception as e:
            print(f"[DB READ ERROR]: {e}")
            return None

    async def cache_course(
        self,
        video_id: str,
        youtube_url: str,
        title: str,
        transcript_length: int,
        course_data: Dict,
        user_id: Optional[str] = None,
    ) -> bool:
        """Saves generated course data to cache. Overwrites existing."""
        if self.collection is None:
            return False
        try:
            document = {
                "video_id": video_id,
                "url": youtube_url,
                "title": title,
                "transcript_length": transcript_length,
                "course_data": course_data,
                "cached_at": datetime.now(timezone.utc).isoformat(),
            }
            if user_id:
                document["user_id"] = user_id
            await self.collection.update_one(
                {"video_id": video_id},
                {"$set": document},
                upsert=True,
            )
            print(f"📦 Cached course for: {video_id}")
            return True
        except Exception as e:
            print(f"[DB WRITE ERROR]: {e}")
            return False

    async def get_user_courses(self, user_id: str) -> List[Dict]:
        if self.collection is None:
            return []
        try:
            cursor = self.collection.find(
                {"user_id": user_id},
                {"_id": 0, "video_id": 1, "title": 1, "cached_at": 1, "transcript_length": 1},
            )
            return await cursor.to_list(length=100)
        except Exception as e:
            print(f"[DB LIST ERROR]: {e}")
            return []

    # ------------------------------------------------------------------ #
    #  USERS
    # ------------------------------------------------------------------ #

    async def create_user(self, user_doc: Dict) -> Optional[str]:
        try:
            result = await self.users_col.insert_one(user_doc)
            return str(result.inserted_id)
        except Exception as e:
            print(f"[DB USER CREATE ERROR]: {e}")
            return None

    async def get_user_by_email(self, email: str) -> Optional[Dict]:
        try:
            doc = await self.users_col.find_one({"email": email})
            if doc:
                doc["_id"] = str(doc["_id"])
            return doc
        except Exception as e:
            print(f"[DB USER READ ERROR]: {e}")
            return None

    async def get_user_by_id(self, user_id: str) -> Optional[Dict]:
        try:
            from bson import ObjectId
            doc = await self.users_col.find_one({"_id": ObjectId(user_id)})
            if doc:
                doc["_id"] = str(doc["_id"])
            return doc
        except Exception as e:
            print(f"[DB USER READ ERROR]: {e}")
            return None

    async def update_user(self, user_id: str, updates: Dict) -> bool:
        try:
            from bson import ObjectId
            await self.users_col.update_one(
                {"_id": ObjectId(user_id)},
                {"$set": updates},
            )
            return True
        except Exception as e:
            print(f"[DB USER UPDATE ERROR]: {e}")
            return False

    # ------------------------------------------------------------------ #
    #  JOBS (async background processing)
    # ------------------------------------------------------------------ #

    async def get_or_create_job(self, job_id: str, video_url: str, user_id: Optional[str] = None) -> Optional[Dict]:
        """
        Atomically gets an active processing job or creates a new one.
        Also sweeps any job that has timed out (stale heartbeat).
        """
        from pymongo import ReturnDocument
        from datetime import timedelta
        
        timeout_threshold = datetime.now(timezone.utc) - timedelta(minutes=30)
        
        # 1. Sweep stale jobs for this URL
        try:
            await self.jobs_col.update_many(
                {
                    "video_url": video_url, 
                    "status": "processing", 
                    "updated_at": {"$lt": timeout_threshold.isoformat()}
                },
                {"$set": {"status": "failed", "error": "Job timed out (stale processing lock)"}}
            )
        except Exception as e:
            print(f"[DB STALE SWEEP ERROR]: {e}")

        # 2. Atomic Upsert
        try:
            now_iso = datetime.now(timezone.utc).isoformat()
            doc = await self.jobs_col.find_one_and_update(
                {"video_url": video_url, "status": "processing"},
                {
                    "$setOnInsert": {
                        "job_id": job_id,
                        "status": "processing",
                        "video_url": video_url,
                        "user_id": user_id,
                        "created_at": now_iso,
                        "updated_at": now_iso,
                        "completed_at": None,
                        "result": None,
                        "error": None,
                    }
                },
                upsert=True,
                return_document=ReturnDocument.AFTER
            )
            if doc:
                doc.pop("_id", None)
            return doc
        except Exception as e:
            print(f"[DB ATOMIC UPSERT ERROR]: {e}")
            return None

    async def get_job(self, job_id: str) -> Optional[Dict]:
        try:
            doc = await self.jobs_col.find_one({"job_id": job_id})
            if doc:
                doc.pop("_id", None)
            return doc
        except Exception as e:
            print(f"[DB JOB READ ERROR]: {e}")
            # Prevent 404s by returning a dummy processing object
            return {"status": "processing", "job_id": job_id, "note": "Temporary database connection issue"}

    async def update_job_completed(self, job_id: str, result: Dict) -> bool:
        import asyncio
        for attempt in range(3):
            try:
                await self.jobs_col.update_one(
                    {"job_id": job_id},
                    {"$set": {
                        "status": "completed",
                        "result": result,
                        "completed_at": datetime.now(timezone.utc).isoformat(),
                    }},
                )
                return True
            except Exception as e:
                print(f"[DB JOB UPDATE ERROR] Attempt {attempt+1}/3 failed: {e}")
                if attempt < 2:
                    await asyncio.sleep(5)
        return False

    async def update_job_failed(self, job_id: str, error: str) -> bool:
        import asyncio
        for attempt in range(3):
            try:
                await self.jobs_col.update_one(
                    {"job_id": job_id},
                    {"$set": {
                        "status": "failed",
                        "error": error,
                        "completed_at": datetime.now(timezone.utc).isoformat(),
                    }},
                )
                return True
            except Exception as e:
                print(f"[DB JOB UPDATE ERROR] Attempt {attempt+1}/3 failed: {e}")
                if attempt < 2:
                    await asyncio.sleep(5)
        return False

    # ------------------------------------------------------------------ #
    #  EXAMS
    # ------------------------------------------------------------------ #

    async def save_exam_result(self, exam_doc: Dict) -> Optional[str]:
        try:
            result = await self.exams_col.insert_one(exam_doc)
            return str(result.inserted_id)
        except Exception as e:
            print(f"[DB EXAM SAVE ERROR]: {e}")
            return None

    async def get_exam_result(self, user_id: str, video_id: str) -> Optional[Dict]:
        try:
            doc = await self.exams_col.find_one(
                {"user_id": user_id, "video_id": video_id},
                sort=[("submitted_at", -1)],
            )
            if doc:
                doc.pop("_id", None)
            return doc
        except Exception as e:
            print(f"[DB EXAM READ ERROR]: {e}")
            return None

    # ------------------------------------------------------------------ #
    #  CERTIFICATES
    # ------------------------------------------------------------------ #

    async def save_certificate(self, cert_doc: Dict) -> bool:
        try:
            await self.certs_col.insert_one(cert_doc)
            return True
        except Exception as e:
            print(f"[DB CERT SAVE ERROR]: {e}")
            return False

    async def get_certificate(self, certificate_id: str) -> Optional[Dict]:
        try:
            doc = await self.certs_col.find_one({"certificate_id": certificate_id})
            if doc:
                doc.pop("_id", None)
            return doc
        except Exception as e:
            print(f"[DB CERT READ ERROR]: {e}")
            return None

    async def get_user_certificates(self, user_id: str) -> List[Dict]:
        try:
            cursor = self.certs_col.find({"user_id": user_id}, {"_id": 0})
            return await cursor.to_list(length=100)
        except Exception as e:
            print(f"[DB CERT LIST ERROR]: {e}")
            return []


# Singleton
db_service = DBService()
