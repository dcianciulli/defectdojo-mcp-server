"""HTTP client wrapper for DefectDojo API v2."""

from __future__ import annotations

import os
from typing import Any

import httpx


class DefectDojoClient:
    """Async HTTP client for DefectDojo REST API.

    Handles authentication, pagination, and error formatting.
    Requires DEFECTDOJO_URL and DEFECTDOJO_API_KEY environment variables.
    """

    def __init__(self) -> None:
        self.base_url = os.environ.get("DEFECTDOJO_URL", "").rstrip("/")
        self.api_key = os.environ.get("DEFECTDOJO_API_KEY", "")
        if not self.base_url:
            raise ValueError("DEFECTDOJO_URL environment variable is required")
        if not self.api_key:
            raise ValueError("DEFECTDOJO_API_KEY environment variable is required")
        self._client: httpx.AsyncClient | None = None

    @property
    def client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=f"{self.base_url}/api/v2",
                headers={
                    "Authorization": f"Token {self.api_key}",
                    "Accept": "application/json",
                },
                timeout=60.0,
            )
        return self._client

    async def close(self) -> None:
        if self._client and not self._client.is_closed:
            await self._client.aclose()

    async def get(
        self,
        path: str,
        params: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """GET request. Returns parsed JSON response."""
        resp = await self.client.get(path, params=_clean_params(params))
        resp.raise_for_status()
        return resp.json()

    async def get_list(
        self,
        path: str,
        params: dict[str, Any] | None = None,
        limit: int = 25,
        offset: int = 0,
    ) -> dict[str, Any]:
        """GET paginated list. Returns the full paginated response envelope."""
        p = dict(params or {})
        p["limit"] = limit
        p["offset"] = offset
        return await self.get(path, p)

    async def get_all(
        self,
        path: str,
        params: dict[str, Any] | None = None,
        max_results: int = 500,
    ) -> list[dict[str, Any]]:
        """Fetch all pages up to max_results."""
        results: list[dict[str, Any]] = []
        offset = 0
        limit = min(100, max_results)
        while len(results) < max_results:
            data = await self.get_list(path, params, limit=limit, offset=offset)
            results.extend(data.get("results", []))
            if not data.get("next"):
                break
            offset += limit
        return results[:max_results]

    async def post(
        self,
        path: str,
        json_data: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """POST request with JSON body."""
        resp = await self.client.post(path, json=json_data)
        resp.raise_for_status()
        if resp.status_code == 204:
            return {"status": "success"}
        return resp.json()

    async def post_multipart(
        self,
        path: str,
        data: dict[str, Any],
        files: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """POST multipart/form-data (used for scan imports)."""
        resp = await self.client.post(
            path,
            data={k: v for k, v in data.items() if v is not None},
            files=files,
        )
        resp.raise_for_status()
        return resp.json()

    async def put(
        self,
        path: str,
        json_data: dict[str, Any],
    ) -> dict[str, Any]:
        """PUT request (full update)."""
        resp = await self.client.put(path, json=json_data)
        resp.raise_for_status()
        return resp.json()

    async def patch(
        self,
        path: str,
        json_data: dict[str, Any],
    ) -> dict[str, Any]:
        """PATCH request (partial update). Tolerates empty response bodies."""
        resp = await self.client.patch(path, json=json_data)
        resp.raise_for_status()
        if resp.status_code == 204 or not resp.content.strip():
            return {"status": "success"}
        return resp.json()

    async def delete(self, path: str) -> dict[str, Any]:
        """DELETE request."""
        resp = await self.client.delete(path)
        resp.raise_for_status()
        return {"status": "deleted"}


def _clean_params(params: dict[str, Any] | None) -> dict[str, Any] | None:
    """Remove None values from params dict."""
    if params is None:
        return None
    return {k: v for k, v in params.items() if v is not None}
