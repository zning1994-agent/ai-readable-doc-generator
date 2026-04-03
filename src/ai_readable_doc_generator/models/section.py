"""Section model representing semantic sections within documents."""

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


class SectionType(str, Enum):
    """Types of semantic sections in a document."""

    HEADING_1 = "heading_1"
    HEADING_2 = "heading_2"
    HEADING_3 = "heading_3"
    HEADING_4 = "heading_4"
    HEADING_5 = "heading_5"
    HEADING_6 = "heading_6"
    PARAGRAPH = "paragraph"
    CODE_BLOCK = "code_block"
    INLINE_CODE = "inline_code"
    BLOCKQUOTE = "blockquote"
    LIST_ITEM = "list_item"
    ORDERED_LIST = "ordered_list"
    UNORDERED_LIST = "unordered_list"
    TABLE = "table"
    HORIZONTAL_RULE = "horizontal_rule"
    LINK = "link"
    IMAGE = "image"
    HTML_BLOCK = "html_block"
    MATH_BLOCK = "math_block"
    MATH_INLINE = "math_inline"
    FOOTNOTE_REFERENCE = "footnote_reference"
    DEFINITION_LIST = "definition_list"
    STRIKETHROUGH = "strikethrough"
    TASK_LIST = "task_list"
    FRONT_MATTER = "front_matter"
    COMMENT = "comment"
    CUSTOM = "custom"


class Section(BaseModel):
    """Represents a semantic section within a document."""

    section_type: SectionType = Field(default=SectionType.PARAGRAPH)
    content: str = ""
    raw_content: str | None = None
    heading_level: int | None = None
    children: list["Section"] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)
    language: str | None = None
    url: str | None = None
    alt_text: str | None = None
    checked: bool | None = None
    list_start: int | None = None
    importance: str = "normal"

    def model_post_init(self, __context: Any) -> None:
        """Post-initialization processing."""
        if self.heading_level is None and self.section_type.name.startswith("HEADING_"):
            try:
                self.heading_level = int(self.section_type.name.split("_")[1])
            except (IndexError, ValueError):
                pass
