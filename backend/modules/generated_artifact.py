"""Validation and deployment rules for untrusted generated file sets."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path, PurePosixPath
from tempfile import TemporaryDirectory
from typing import Mapping


MAX_FILE_COUNT = 100
MAX_FILE_BYTES = 2 * 1024 * 1024
MAX_TOTAL_BYTES = 5 * 1024 * 1024
MAX_PATH_LENGTH = 240

_WINDOWS_RESERVED_NAMES = {
    "CON",
    "PRN",
    "AUX",
    "NUL",
    *(f"COM{number}" for number in range(1, 10)),
    *(f"LPT{number}" for number in range(1, 10)),
}
_DEPLOYMENT_NAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_-]{0,127}$")
_WINDOWS_INVALID_CHARS = re.compile(r'[<>:"|?*]|[\x00-\x1f]')


class ArtifactValidationError(ValueError):
    """Generated files violate the deployable artifact contract."""


@dataclass(frozen=True)
class ArtifactFile:
    path: PurePosixPath
    content: str


@dataclass(frozen=True)
class GeneratedArtifact:
    """A validated, self-contained set of generated files."""

    files: tuple[ArtifactFile, ...]
    total_bytes: int

    @classmethod
    def from_mapping(cls, files: Mapping[str, str]) -> "GeneratedArtifact":
        if not isinstance(files, Mapping) or not files:
            raise ArtifactValidationError("生成文件不能为空")
        if len(files) > MAX_FILE_COUNT:
            raise ArtifactValidationError(f"生成文件数量不能超过 {MAX_FILE_COUNT}")

        normalized_files: list[ArtifactFile] = []
        seen_paths: set[str] = set()
        total_bytes = 0

        for raw_path, content in files.items():
            path = _normalize_path(raw_path)
            normalized = path.as_posix()
            if normalized in seen_paths:
                raise ArtifactValidationError(f"生成文件路径重复: {normalized}")
            if not isinstance(content, str):
                raise ArtifactValidationError(f"文件内容必须是文本: {normalized}")

            content_bytes = len(content.encode("utf-8"))
            if content_bytes > MAX_FILE_BYTES:
                raise ArtifactValidationError(
                    f"单个文件不能超过 {MAX_FILE_BYTES // (1024 * 1024)} MiB: {normalized}"
                )
            total_bytes += content_bytes
            if total_bytes > MAX_TOTAL_BYTES:
                raise ArtifactValidationError(
                    f"生成文件总大小不能超过 {MAX_TOTAL_BYTES // (1024 * 1024)} MiB"
                )

            seen_paths.add(normalized)
            normalized_files.append(ArtifactFile(path=path, content=content))

        if "index.html" not in seen_paths:
            raise ArtifactValidationError("生成产物必须包含根目录 index.html")

        return cls(files=tuple(normalized_files), total_bytes=total_bytes)

    def deploy(self, projects_dir: Path, deployment_name: str) -> Path:
        """Write atomically beneath projects_dir and return the final directory."""
        if not _DEPLOYMENT_NAME.fullmatch(deployment_name):
            raise ArtifactValidationError("部署目录名称不安全")

        projects_dir = projects_dir.resolve()
        projects_dir.mkdir(parents=True, exist_ok=True)
        final_dir = (projects_dir / deployment_name).resolve()
        _ensure_within(projects_dir, final_dir)
        if final_dir.exists():
            raise ArtifactValidationError("部署目录已存在")

        with TemporaryDirectory(prefix=".dreamcoder-", dir=projects_dir) as temp_name:
            temp_dir = Path(temp_name).resolve()
            _ensure_within(projects_dir, temp_dir)

            for artifact_file in self.files:
                target = (temp_dir / artifact_file.path.as_posix()).resolve()
                _ensure_within(temp_dir, target)
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_text(artifact_file.content, encoding="utf-8")

            temp_dir.replace(final_dir)

        return final_dir


def _normalize_path(raw_path: object) -> PurePosixPath:
    if not isinstance(raw_path, str):
        raise ArtifactValidationError("生成文件路径必须是字符串")
    if not raw_path or len(raw_path) > MAX_PATH_LENGTH or "\x00" in raw_path:
        raise ArtifactValidationError("生成文件路径为空或过长")

    portable_path = raw_path.replace("\\", "/")
    if re.match(r"^[A-Za-z]:", portable_path):
        raise ArtifactValidationError(f"不允许绝对路径: {raw_path}")

    path = PurePosixPath(portable_path)
    if path.is_absolute() or ".." in path.parts:
        raise ArtifactValidationError(f"不允许越过部署目录: {raw_path}")
    if not path.parts or path.as_posix() in {"", "."}:
        raise ArtifactValidationError("生成文件路径不能为空")

    for part in path.parts:
        if part.startswith("."):
            raise ArtifactValidationError(f"不允许隐藏文件或目录: {raw_path}")
        if _WINDOWS_INVALID_CHARS.search(part):
            raise ArtifactValidationError(f"文件路径包含系统不支持的字符: {raw_path}")
        if part.endswith((" ", ".")):
            raise ArtifactValidationError(f"文件路径不能以空格或句点结尾: {raw_path}")
        if PurePosixPath(part).stem.upper() in _WINDOWS_RESERVED_NAMES:
            raise ArtifactValidationError(f"不允许系统保留文件名: {raw_path}")

    return path


def _ensure_within(root: Path, candidate: Path) -> None:
    try:
        candidate.relative_to(root)
    except ValueError as exc:
        raise ArtifactValidationError("目标路径越过部署目录") from exc
