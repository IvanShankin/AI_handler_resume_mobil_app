from typing import List, Optional

from src.api_client.base import BaseAPIClient
from src.api_client.exceptions import APIClientError, NotFoundData
from src.api_client.models import RequirementsOut, IsDeleteOut


class RequirementClient:
    def __init__(self, api: BaseAPIClient):
        self.api = api

    async def get_requirement(
        self,
        requirements_id: Optional[int] = None
    ) -> List[RequirementsOut]:

        try:
            params = {}
            if requirements_id is not None:
                params["requirements_id"] = requirements_id

            response = await self.api.request(
                "GET",
                "/storage/get_requirements",
                params=params
            )

            data = response.json()

            return [RequirementsOut.model_validate(item) for item in data]

        except NotFoundData:
            return []

    async def create_requirement(self, requirement: str) -> bool:
        await self.api.request(
            "POST",
            "upload/create_requirements/text",
            json={"requirements": requirement}

        )
        return True

    async def delete_requirements(self, requirements_ids: List[int]) -> bool:
        response = await self.api.request(
            "DELETE",
            "upload/delete_requirements",
            json={"requirements_ids": requirements_ids}

        )
        data = response.json()

        return IsDeleteOut.model_validate(data).is_deleted