from typing import List, Optional

from src.api_client.base import BaseAPIClient
from src.api_client.schemas import ProcessingOut, DeleteProcessingResponse


class ProcessingClient:
    def __init__(self, api: BaseAPIClient):
        self.api = api

    async def get_processing(
        self,
        resume_id: Optional[int] = None
    ) -> ProcessingOut:
        """
        :raise NotFoundData:
        """
        response = await self.api.request(
            "GET",
            f"/storage/get_processing_by_resume/{resume_id}",
        )

        data = response.json()

        return ProcessingOut.model_validate(data)


    async def start_processing(self, requirement_id: int, resume_id: int) -> bool:
        await self.api.request(
            "POST",
            "upload/start_processing",
            json={
                "requirements_id": requirement_id,
                "resume_id": resume_id,
            }
        )
        return True

    async def delete_processing(self, processing_ids: List[int]) -> bool:
        response = await self.api.request(
            "DELETE",
            "upload/delete_processing",
            json={"processing_ids": processing_ids}

        )
        data = response.json()

        return bool(DeleteProcessingResponse.model_validate(data))