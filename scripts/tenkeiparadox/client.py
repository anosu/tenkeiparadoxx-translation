import json
from typing import Literal

import httpx

from .serialize import deserialize_api


class TenkeiparadoxClient:
    API_BASE_URL = "https://app-paripari-prod.tenkei-paradox.com/api"
    MASTER_BASE_URL = "https://cdne-paripari-prod.tenkei-paradox.com/master-data"

    token: str
    version: str | None
    master_version: str | None
    headers: dict[str, str]
    session: httpx.Client

    def __init__(self, token: str):
        if token.startswith("Bearer "):
            token = token[7:]
        self.token = token
        self.version = None
        self.master_version = None
        self.headers = {"x-rating": "r18", "x-platform": "dmm", "x-device": "pc"}
        self.session = httpx.Client(
            headers={
                "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36"
            }
        )

    def get_master(self) -> tuple[str, str]:
        resp = self.request("GET", "data/master")
        data, ver = resp.json()["result"]
        self.master_version = ver
        return data, ver

    def request(
        self,
        method: Literal["GET", "POST"],
        path: str,
        payload=None,
        msgpack: bool = True,
    ):
        separate = "" if path.startswith("/") else "/"
        url = f"{self.API_BASE_URL}{separate}{path}"
        headers = {
            **self.headers,
            "accept": "application/vnd.msgpack" if msgpack else "*/*",
            "authorization": f"Bearer {self.token}",
        }
        if self.version:
            headers["x-client-version"] = self.version
        if self.master_version:
            headers["x-masterdata-version"] = self.master_version
        resp = self.session.request(method, url, headers=headers, content=payload)
        if msgpack:
            setattr(
                resp,
                "_content",
                json.dumps(deserialize_api(resp.content), ensure_ascii=False).encode(),
            )
        if not self.version:
            self.version = resp.headers.get("x-client-version")
        return resp
