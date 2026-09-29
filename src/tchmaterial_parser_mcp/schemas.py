"""Stable data structures exposed by the MCP layer."""

from __future__ import annotations

from typing import TypedDict


class MaterialSummary(TypedDict):
    resource_id: str
    title: str
    path: list[str]
    stage: str | None
    subject: str | None
    edition: str | None
    grade: str | None
    volume: str | None
    resource_type: str
    source_url: str


class ResolvedResource(TypedDict):
    title: str
    file_format: str
    edition: str | None
    relative_dir: list[str]
    download_url: str
    chapters: list[dict]


class DownloadedResource(TypedDict):
    title: str
    file_format: str
    status: str
    path: str
    bytes: int
    error: str | None

