from datetime import datetime
from typing import Dict, Any, Optional
import uuid

class JobManager:
    """
    Gerencia o estado de tarefas em segundo plano (in-memory).
    """
    _instance = None
    _jobs: Dict[str, Dict[str, Any]] = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(JobManager, cls).__new__(cls)
        return cls._instance

    def create_job(self) -> str:
        job_id = str(uuid.uuid4())
        self._jobs[job_id] = {
            "status": "pending",
            "progress": 0,
            "message": "Iniciando...",
            "started_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat()
        }
        return job_id

    def update_job(self, job_id: str, status: Optional[str] = None, progress: Optional[int] = None, message: Optional[str] = None):
        if job_id in self._jobs:
            if status: self._jobs[job_id]["status"] = status
            if progress is not None: self._jobs[job_id]["progress"] = progress
            if message: self._jobs[job_id]["message"] = message
            self._jobs[job_id]["updated_at"] = datetime.now().isoformat()

    def get_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        return self._jobs.get(job_id)

job_manager = JobManager()
