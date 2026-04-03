"""Document model representing a complete AI-readable document."""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class DocumentMetadata(BaseModel):
    """Metadata for a document."""

    title: str | None = None
    source_path: str | None = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    language: str = "en"
    version: str = "1.0"
    generator: str = "ai-readable-doc-generator"
    custom: dict[str, Any] = Field(default_factory=dict)


class Document(BaseModel):
    """Represents a complete AI-readable document with semantic structure."""

    metadata: DocumentMetadata = Field(default_factory=DocumentMetadata)
    title: str | None = None
    sections: list["Section"] = Field(default_factory=list)
    raw_content: str | None = None

    def model_post_init(self, __context: Any) -> None:
        """Post-initialization processing."""
        if self.title is None and self.metadata.title:
            self.title = self.metadata.title
