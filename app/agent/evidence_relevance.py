from langchain_core.messages import (
    HumanMessage,
    SystemMessage,
)

from app.llm.models import get_llm
from app.models.schemas import EvidenceRelevance


llm = get_llm()

structured_llm = llm.with_structured_output(
    EvidenceRelevance
)


def evaluate_evidence_relevance(
    task: str,
    evidence: dict,
) -> EvidenceRelevance:

    messages = [
        SystemMessage(
            content="""
You evaluate whether a piece of evidence is relevant
to a specific research task.

Consider:

- Does it refer to the correct product/topic?
- Does it refer to the requested model/version/year?
- Does it refer to the appropriate market or region?
- Does it actually contain information needed for the task?

Important:

An official source is not automatically relevant.

For example, an official page describing an older product
version should not be treated as strong evidence for a
newer model year.

Do not use outside knowledge.

Evaluate only the supplied task and evidence.
"""
        ),

        HumanMessage(
            content=f"""
Research task:

{task}


Evidence title:

{evidence.get("title", "")}


Evidence domain:

{evidence.get("domain", "")}


Evidence snippet:

{evidence.get("snippet", "")}
"""
        ),
    ]

    return structured_llm.invoke(messages)