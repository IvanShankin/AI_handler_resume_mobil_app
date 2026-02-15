from typing import Optional, List

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
        try:
            requirements = await self.resum_client.get_resume(requirement_id=requirement_id, resume_id=resume_id)
            return requirements
        except Exception as e:
            raise e