from pydantic import BaseModel, Field
from langchain_core.messages import (
    SystemMessage,
    HumanMessage,
)

from app.llm.models import get_llm


class PrimarySourceQuery(BaseModel):

    organization: str | None = Field(
        description=(
            "Primary organization or authority "
            "for the topic"
        )
    )

    official_domain: str | None = Field(
        description=(
            "Official root domain of the organization, "
            "such as python.org or bajajauto.com. "
            "Return None if uncertain."
        )
    )

    search_query: str | None = Field(
        description=(
            "Search query targeting the primary source"
        )
    )


llm = get_llm()

structured_llm = llm.with_structured_output(
    PrimarySourceQuery
)


def create_primary_source_query(
    task: str,
) -> PrimarySourceQuery:

    messages = [

        SystemMessage(
            content="""
You identify primary sources for research tasks.

Identify the primary authority for the research task.

A primary authority may be:
- an official manufacturer
- an official company
- an official organization
- official documentation
- a government institution
- the original project or product website

Also identify its official root domain only when you are
confident about it.

Examples:

Bajaj Auto
official_domain: bajajauto.com

Python Software Foundation / Python documentation
official_domain: python.org

Do not invent a domain.

If uncertain, return:
official_domain=None

The search query should target the official source when an
official domain is known.

If there is no clear primary authority for the task,
return:
organization=None
official_domain=None
search_query=None
"""
        ),

        HumanMessage(
            content=f"""
Research task:

{task}
"""
        ),
    ]

    return structured_llm.invoke(messages)