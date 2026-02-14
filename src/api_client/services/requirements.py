from typing import List, Optional

from src.api_client.base import BaseAPIClient
from src.api_client.exceptions import APIClientError, NotFoundData
from src.api_client.models import RequirementsOut


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

        except APIClientError as e:
            raise e

    async def create_requirement(self, requirement: str) -> RequirementsOut:
        response = await self.api.request(
            "POST",
            "upload/create_requirements/text",
            json={"requirements": requirement}

        )
        data = response.json()
        return RequirementsOut.model_validate(data)
