from typing import List, Optional

from src.api_client.base import BaseAPIClient
from src.api_client.exceptions import NotFoundData, APIClientError, NotEnoughArguments, ToManyArguments
from src.api_client.models import ResumeOut


class ResumeClient:
    def __init__(self, api: BaseAPIClient):
        self.api = api

    async def get_resume(
        self,
        requirement_id: Optional[int] = None,
        resume_id: Optional[int] = None
    ) -> List[ResumeOut]:
        if requirement_id is None and resume_id is None:
            raise NotEnoughArguments("Недостаточно аргументов")

        if not requirement_id is None and not resume_id is None:
            raise ToManyArguments("Слишком много аргументов, передайте только один из них" )

        try:
            url = ""
            in_json_list = False

            params = {}
            if requirement_id is not None:
                params["requirement_id"] = requirement_id
                url = "/storage/get_resume_by_requirement"
                in_json_list = True

            if resume_id is not None:
                params["resume_id"] = resume_id
                url = "/storage/get_resume"

            response = await self.api.request("GET", url, params=params)
            data = response.json()
            return [ResumeOut.model_validate(item) for item in data] if in_json_list else [ResumeOut.model_validate(data)]

        except NotFoundData:
            return []

        except APIClientError as e:
            raise e

    async def create_resume(self, requirements_id: int, resume: str) -> bool:
        """
        :raise NotFoundData: Если `requirements_id` не найден
        """
        await self.api.request(
            "POST",
            "upload/create_resume/text",
            json={"resume": resume, "requirement_id": requirements_id}

        )
        return True

    async def delete_resume(self, resume_ids: List[int]):
        await self.api.request(
            "DELETE",
            "upload/delete_resume",
            json={"resume_ids": resume_ids}
        )
        return True