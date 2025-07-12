import httpx
import asyncio
from datetime import datetime
from typing import Optional, Dict, Any, List
from .config import settings


class RateLimiter:
    def __init__(self, max_requests: int, period: float = 60.0):
        self.max_requests = max_requests
        self.period = period
        self.requests: list[float] = []
        self._lock = asyncio.Lock()

    async def acquire(self):
        async with self._lock:
            now = asyncio.get_event_loop().time()
            # Remove old requests outside the period
            self.requests = [
                req_time for req_time in self.requests if now - req_time < self.period
            ]

            if len(self.requests) >= self.max_requests:
                # Calculate how long to wait
                oldest_request = min(self.requests)
                wait_time = self.period - (now - oldest_request)
                if wait_time > 0:
                    await asyncio.sleep(wait_time)
                # After waiting, clean up old requests again and proceed
                now = asyncio.get_event_loop().time()
                self.requests = [
                    req_time
                    for req_time in self.requests
                    if now - req_time < self.period
                ]

            self.requests.append(now)


class WaniKaniClient:
    # Class-level rate limiter shared across all instances
    _rate_limiter = RateLimiter(settings.wanikani_rate_limit, 60.0)

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
        # Apply rate limiting
        await self._rate_limiter.acquire()

        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        response = await self.client.get(url, params=params)
        response.raise_for_status()
        return response.json()

    async def get_user(self) -> Dict[str, Any]:
        return await self._get("user")

    async def get_subjects(
        self, updated_after: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        params: Optional[Dict[str, str]] = {}
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
                params = None

        return all_subjects

    async def get_assignments(
        self, updated_after: Optional[datetime] = None
    ) -> List[Dict[str, Any]]:
        params: Optional[Dict[str, str]] = {}
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
        params: Optional[Dict[str, str]] = {}
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
        params: Optional[Dict[str, str]] = {}
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

    async def get_summary(self) -> Dict[str, Any]:
        """Get summary with current lesson and review counts"""
        return await self._get("summary")
