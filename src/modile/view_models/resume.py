from typing import Optional, List

from src.api_client.exceptions import NotFoundData
from src.api_client.models import ResumeOut
from src.api_client.services.resume import ResumeClient


class ResumeModel:
    def __init__(self, resum_client: ResumeClient):
        self.resum_client = resum_client

    async def get_resume(
        self,
        requirement_id: Optional[int] = None,
        resume_id: Optional[int] = None
    ) -> List[ResumeOut]:
        requirements = await self.resum_client.get_resume(requirement_id=requirement_id, resume_id=resume_id)
        return requirements

    async def create_resume(self, requirements_id: int, resume: str) -> bool:
        try:
            return await self.resum_client.create_resume(requirements_id, resume)
        except NotFoundData:
            return False

    async def delete_resume(self, resume_ids: List[int]) -> bool:
        try:
            return await self.resum_client.delete_resume(resume_ids)
        except NotFoundData:
            return False