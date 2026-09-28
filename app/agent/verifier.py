from langchain_core.messages import (
    HumanMessage,
    SystemMessage,
)

from app.llm.models import get_llm
from app.models.schemas import VerificationResult


llm = get_llm()

structured_llm = llm.with_structured_output(
    VerificationResult
)


def verify_evidence(
    task: str,
    evidence: list,
) -> VerificationResult:

    if not evidence:
        return VerificationResult(
            has_conflicts=False,
            verified=False,
            notes="No evidence was available for verification.",
        )

    evidence_text = ""

    for index, source in enumerate(
        evidence,
        start=1,
    ):

        evidence_text += f"""
Source {index}
Title: {source["title"]}
Domain: {source["domain"]}
Source Type: {source["source_type"]}
Confidence: {source["confidence"]}
Relevant: {source.get("relevant", True)}
Relevance: {source.get("relevance", "unknown")}
Relevance Reason: {source.get("relevance_reason", "")}
Snippet: {source["snippet"]}
"""

    messages = [
        SystemMessage(
            content="""
You are an evidence verification component.

Your job is to determine whether the supplied evidence
reasonably supports the research task and whether there
are important unresolved factual conflicts.

Use ONLY the supplied evidence.
Do not use outside knowledge.
Do not invent missing information.


SOURCE QUALITY AND RELEVANCE

Source quality and evidence relevance are different.

Source quality describes who published the information.

Evidence relevance describes whether that particular
evidence actually supports the current research task.

An official source with low relevance must NOT
automatically override a highly relevant source.

Give more weight to evidence that directly matches:

- the requested product or topic
- model or version
- year
- market or region
- information requested by the task

Evidence marked Relevant=False should not be treated as
strong support for the requested claim.


CONFLICT DETECTION

CONFLICT DETECTION

First, identify which evidence is relevant to the exact
research task.

Evidence marked Relevant=False must NOT create a conflict
with relevant evidence. It may be mentioned as background,
but exclude it when deciding whether the requested claim
is conflicting.

Compare factual claims only between evidence that is
relevant to the same product, version, model year,
market, and context.

Before declaring numerical values conflicting, check
whether the difference can reasonably be explained by:

- rounding
- unit conversion
- measurement precision

Examples:

349.13cc and 350cc:
Treat as equivalent unless the evidence indicates they
refer to different engines.

40.6 PS and approximately 40.54 PS:
Treat as equivalent for conflict detection.

40.04 bhp and approximately 40.54 PS:
Treat as equivalent after unit conversion.

349cc and 373cc:
Treat as a meaningful conflict ONLY when both sources are
relevant to the same model/version/year.

Do not set has_conflicts=True merely because some
specifications are missing.

Missing information affects verification completeness,
but missing information is not itself a factual conflict.


VERIFICATION

VERIFICATION

Evaluate verification using relevant evidence only.

has_conflicts=True means relevant evidence contains
meaningful incompatible factual claims.

has_conflicts=False does not necessarily mean
verified=True.

verified=True means the relevant evidence provides
reasonable support for the main information requested.

verified=False may be used when evidence is incomplete,
weak, insufficient, or does not clearly support the
requested claim.

Therefore:

conflict and verification are separate decisions.
"""
        ),

        HumanMessage(
            content=f"""
Research task:

{task}


Evidence:

{evidence_text}


Evaluate the evidence and return the verification result.
"""
        ),
    ]

    return structured_llm.invoke(messages)
    