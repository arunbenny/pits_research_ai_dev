from langchain_core.messages import (
    HumanMessage,
    SystemMessage,
)

from app.llm.models import get_llm


llm = get_llm()


def synthesize_research(
    query: str,
    results: list,
) -> str:

    findings = ""

    for result in results:

        if result["status"] == "success":

            findings += (
                f"\n\nResearch Task:\n"
                f"{result['task']}\n\n"
                f"Finding:\n"
                f"{result['result']}\n"
            )

        else:

            findings += (
                f"\n\nResearch Task:\n"
                f"{result['task']}\n\n"
                f"Status: Research failed\n"
            )

    messages = [

        SystemMessage(
            content="""
            You are the final response generator for a
            research agent.

            Produce a clear and useful answer to the user's
            original request using the research findings.

            Rules:

            - Use only information supported by the findings.
            - Do not invent missing facts.
            - Do not claim failed research was successful.
            - Mention important limitations when information
              could not be verified.
            - Organize the response clearly.
            - Avoid repeating the same information.
            - Prefer concise but useful answers.
            """
        ),

        HumanMessage(
            content=f"""
            User request:

            {query}


            Research findings:

            {findings}


            Produce the final research response.
            """
        ),
    ]

    response = llm.invoke(messages)

    return response.content