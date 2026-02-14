from typing import Optional, List

from pip._internal.resolution.resolvelib.base import Requirement

from src.api_client.models import RequirementsOut
from src.api_client.services.requirements import RequirementClient
from src.modile.config import get_config


class RequirementsModel:
    def __init__(self, req_client: RequirementClient):
        self.req_client = req_client

    def is_authenticated(self) -> bool:
        return bool(get_config().token_storage.get_access_token())

    async def get_requirements(self, requirement_id: Optional[int]) -> List[RequirementsOut]:
        try:
            requirements = await self.req_client.get_requirement(requirement_id)
            return requirements
        except Exception as e:
            raise e

    async def create_new_requirement(self, requirement: str) -> RequirementsOut:
        try:
            requirements = await self.req_client.create_requirement(requirement)
            return requirements
        except Exception as e:
            raise e