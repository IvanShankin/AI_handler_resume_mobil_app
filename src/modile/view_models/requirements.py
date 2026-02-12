from typing import Optional, List

from src.api_client.models import RequirementsOut
from src.api_client.services.requirements import RequirementClient


class RequirementsModel:
    def __init__(self, req_client: RequirementClient):
        self.req_client = req_client

    async def get_requirements(self, requirement_id: Optional[int]) -> List[RequirementsOut]:
        try:
            requirements = await self.req_client.get_requirement(requirement_id)
            return requirements
        except Exception as e:
            raise e
