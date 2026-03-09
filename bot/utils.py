from pathlib import Path
from typing import NamedTuple

from aiogram.types import FSInputFile, MessageEntity

GIF_PATH = Path(__file__).parent.parent / "bubs.gif"
_gif_file_id: str | None = None


async def get_gif() -> FSInputFile | str:
    global _gif_file_id
    if _gif_file_id:
        return _gif_file_id
    return FSInputFile(GIF_PATH)


def cache_gif_id(file_id: str) -> None:
    global _gif_file_id
    _gif_file_id = file_id


class CaptionResult(NamedTuple):
    text: str
    entities: list[MessageEntity]


def _utf16_len(s: str) -> int:
    return len(s.encode("utf-16-le")) // 2


def bold(text: str) -> dict:
    return {"type": "bold", "text": text}


def custom_emoji(emoji_id: str, placeholder: str = "\u2753") -> dict:
    return {"type": "custom_emoji", "emoji_id": emoji_id, "text": placeholder}


def plain(text: str) -> dict:
    return {"type": "plain", "text": text}


def build_caption(*segments: dict | str) -> CaptionResult:
    text_parts: list[str] = []
    entities: list[MessageEntity] = []
    offset = 0

    for seg in segments:
        if isinstance(seg, str):
            seg = plain(seg)

        seg_text = seg["text"]
        seg_len = _utf16_len(seg_text)
        seg_type = seg["type"]

        if seg_type == "bold":
            entities.append(MessageEntity(type="bold", offset=offset, length=seg_len))
        elif seg_type == "custom_emoji":
            entities.append(
                MessageEntity(
                    type="custom_emoji",
                    offset=offset,
                    length=seg_len,
                    custom_emoji_id=seg["emoji_id"],
                )
            )

        text_parts.append(seg_text)
        offset += seg_len

    return CaptionResult("".join(text_parts), entities)
