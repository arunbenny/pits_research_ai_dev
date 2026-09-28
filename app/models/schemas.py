from typing import List

from pydantic import BaseModel, Field


class ResearchTask(BaseModel):
    id: int = Field(
        description="Sequential task number"
    )

    description: str = Field(
        description="Research task that should be performed"
    )

# Model for the overall research plan
class ResearchPlan(BaseModel):
    topic: str = Field(
        description="Main research topic"
    )

    goal: str = Field(
        description="Main goal of the research"
    )

    tasks: List[ResearchTask] = Field(
        description="Tasks required to complete the research"
    )


class RequirementAnalysis(BaseModel):
    is_clear: bool = Field(
        description="Whether the user's requirement is clear enough to research"
    )

    intent: str = Field(
        description="The user's main intent"
    )

    topic: str = Field(
        description="The main topic identified from the request"
    )

    requires_current_information: bool = Field(
        description="Whether current or up-to-date information is required"
    )

    clarification_question: str | None = Field(
        default=None,
        description="Question to ask the user if the requirement is unclear"
    )

    resolved_query: str = Field(
        description=(
            "A standalone research request combining the current "
            "message with relevant previous conversation context"
        )
    )

from typing import List
from pydantic import BaseModel, Field


class ResearchEvidence(BaseModel):
    title: str = Field(
        description="Title of the source"
    )

    url: str = Field(
        description="URL of the source"
    )

    snippet: str = Field(
        description="Relevant information retrieved from the source"
    )


class ResearchTaskResult(BaseModel):
    task_id: int

    task: str

    status: str

    answer: str

    evidence: List[ResearchEvidence] = []


class VerificationResult(BaseModel):
    has_conflicts: bool = Field(
        description="Whether important factual conflicts exist between sources"
    )

    verified: bool = Field(
        description="Whether the evidence reasonably supports the main factual claim"
    )

    notes: str = Field(
        description="Short explanation of the verification result"
    )

class EvidenceRelevance(BaseModel):
    relevant: bool = Field(
        description=(
            "Whether the evidence is relevant to the "
            "specific research task"
        )
    )

    relevance: str = Field(
        description="high, medium, or low"
    )

    reason: str = Field(
        description=(
            "Short explanation of why the evidence "
            "is or is not relevant"
        )
    )


