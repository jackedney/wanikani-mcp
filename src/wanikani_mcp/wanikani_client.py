import httpx
from datetime import datetime
from typing import Optional, Dict, Any, List
from .config import settings


class WaniKaniClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = settings.wanikani_api_base_url
        self.client = httpx.AsyncClient(
            headers={
                "Authorization": f"Bearer {api_key}",
                "Wanikani-Revision": "20170710",
            },
            timeout=30.0,
        )

    async def close(self):
        await self.client.aclose()

    async def _get(
        self, endpoint: str, params: Optional[Dict] = None
    ) -> Dict[str, Any]:
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        response = await self.client.get(url, params=params)
        response.raise_for_status()
        return response.json()

    async def get_user(self) -> Dict[str, Any]:
        return await self._get("user")

    async def get_subjects(
        self, updated_after: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        params = {}
        if updated_after:
            params["updated_after"] = updated_after.isoformat()

        all_subjects = []
        url = "subjects"

        while url:
            data = await self._get(url, params)
            all_subjects.extend(data["data"])
            url = data["pages"]["next_url"]
            if url:
                url = url.replace(self.base_url + "/", "")
                params = None  # URL already has params

        return all_subjects

    async def get_assignments(
        self, updated_after: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        params = {}
        if updated_after:
            params["updated_after"] = updated_after.isoformat()

        all_assignments = []
        url = "assignments"

        while url:
            data = await self._get(url, params)
            all_assignments.extend(data["data"])
            url = data["pages"]["next_url"]
            if url:
                url = url.replace(self.base_url + "/", "")
                params = None

        return all_assignments

    async def get_reviews(
        self, updated_after: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        params = {}
        if updated_after:
            params["updated_after"] = updated_after.isoformat()

        all_reviews = []
        url = "reviews"

        while url:
            data = await self._get(url, params)
            all_reviews.extend(data["data"])
            url = data["pages"]["next_url"]
            if url:
                url = url.replace(self.base_url + "/", "")
                params = None

        return all_reviews

    async def get_review_statistics(
        self, updated_after: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        params = {}
        if updated_after:
            params["updated_after"] = updated_after.isoformat()

        all_stats = []
        url = "review_statistics"

        while url:
            data = await self._get(url, params)
            all_stats.extend(data["data"])
            url = data["pages"]["next_url"]
            if url:
                url = url.replace(self.base_url + "/", "")
                params = None

        return all_stats
