from typing import Optional, List

from src.api_client.exceptions import NotFoundData
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

    async def create_new_requirement(self, requirement: str) -> bool:
        try:
            return await self.req_client.create_requirement(requirement)
        except Exception as e:
            raise e

    async def delete_requirements(self, requirements_ids: List[int]) -> bool:
        try:
            return await self.req_client.delete_requirements(requirements_ids)
        except NotFoundData as e:
            return False
        except Exception as e:
            raise e