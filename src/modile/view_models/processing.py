from typing import Optional, List

from src.api_client.exceptions import NotFoundData
from src.api_client.models import ProcessingDetailOut
from src.api_client.services.processing import ProcessingClient


class ProcessingModel:
    def __init__(self, proc_client: ProcessingClient):
        self.proc_client = proc_client

    async def get_processing(self, resume_id: Optional[int]) -> ProcessingDetailOut:
        processing = await self.proc_client.get_processing(resume_id)
        return processing

    async def create_new_processing(self, requirements_id: int, resume_id: int) -> bool:
        try:
            return await self.proc_client.start_processing(requirements_id, resume_id)
        except NotFoundData:
            return False

    async def delete_processing(self, processing_ids: List[int]) -> bool:
        try:
            return await self.proc_client.delete_processing(processing_ids)
        except NotFoundData:
            return False