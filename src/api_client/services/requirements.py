from typing import List, Optional

from src.api_client.base import BaseAPIClient
from src.api_client.exceptions import NotFoundData
from src.api_client.schemas import RequirementsOut, DeleteRequirementsResponse


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

            return [RequirementsOut.parse_obj(item) for item in data]

        except NotFoundData:
            return []

    async def create_requirement(self, requirement: str) -> RequirementsOut | None:
        response = await self.api.request(
            "POST",
            "upload/create_requirement/text",
            json={"requirement": requirement}

        )
        data = response.json()
        if isinstance(data, list) and data:
            data = data[0]
        if isinstance(data, dict):
            try:
                return RequirementsOut.parse_obj(data)
            except Exception:
                return None
        return None

    async def delete_requirements(self, requirements_ids: List[int]) -> bool:
        response = await self.api.request(
            "DELETE",
            "upload/delete_requirements",
            json={"requirement_ids": requirements_ids}

        )
        data = response.json()

        return bool(DeleteRequirementsResponse.parse_obj(data))
