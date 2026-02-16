from typing import List, Optional

from src.api_client.base import BaseAPIClient
from src.api_client.models import IsDeleteOut, ProcessingDetailOut


class ProcessingClient:
    def __init__(self, api: BaseAPIClient):
        self.api = api

    async def get_processing(
        self,
        resume_id: Optional[int] = None
    ) -> ProcessingDetailOut:
        """
        :raise NotFoundData:
        """

        params = {}
        if resume_id is not None:
            params["resume_id"] = resume_id

        response = await self.api.request(
            "GET",
            "/storage/get_processing_detail_by_resume",
            params=params
        )

        data = response.json()

        return ProcessingDetailOut.model_validate(data)


    async def start_processing(self, requirement: str) -> bool:
        pass
        # await self.api.request(
        #     "POST",
        #     "upload/start_processing",
        #     json={"requirements": requirement}
        # )

    async def delete_processing(self, processing_ids: List[int]) -> bool:
        response = await self.api.request(
            "DELETE",
            "upload/delete_processing",
            json={"processings_ids": processing_ids}

        )
        data = response.json()

        return IsDeleteOut.model_validate(data).is_deleted