from langchain_core.messages import (
    HumanMessage,
    SystemMessage,
    ToolMessage,
)

from app.llm.models import get_llm
from app.tools.web_search import search_web
from app.agent.source_evaluator import evaluate_sources
from app.agent.verifier import verify_evidence
from app.agent.primary_source import create_primary_source_query
from app.agent.evidence_relevance import (
    evaluate_evidence_relevance,
)


llm = get_llm()

tools = [search_web]

llm_with_tools = llm.bind_tools(tools)


def research_task(
    task: str,
    previous_findings: list | None = None,
    previous_research: dict | None = None,
) -> dict:

    previous_findings = previous_findings or []


    previous_research_context = ""

    if previous_research:
        previous_research_context = f"""
    Previous research query:
    {previous_research.get("query", "")}

    Previous final answer:
    {previous_research.get("final_answer", "")}

    Previous research findings:
    """

        for result in previous_research.get(
            "results",
            []
        ):
            if result.get("status") == "success":
                previous_research_context += f"""
    Task:
    {result.get("task", "")}

    Finding:
    {result.get("result", "")}
    """

    research_context = ""

    for finding in previous_findings:

        research_context += (
            f"\nTask: {finding['task']}\n"
            f"Finding: {finding['result']}\n"
        )

    messages = [

        SystemMessage(
            content="""
            You are a research agent.

            Complete the assigned research task carefully.

            You may receive findings from previously completed
            research tasks.

            Use those findings when relevant.

            Use web search when current or externally
            verifiable information is required.

            Do not invent facts.

            If sources disagree, mention the disagreement.

            If information cannot be verified, clearly state it.

            Only make factual claims supported by the supplied
            research evidence or previous findings.

            Previous research may be supplied from earlier user requests.

            Reuse previous findings when they already answer part of
            the current task.

            Do not unnecessarily search again for information that is
            already adequately supported by previous research.

            Use web search when new, missing, current, or externally
            verifiable information is required.
            """
        ),

        HumanMessage(
            content=f"""
        Current research task:

        {task}


        Findings from tasks completed during this research:

        {research_context if research_context else "None"}


        Research from previous user requests:

        {
            previous_research_context
            if previous_research_context
            else "None"
        }
        """
        ),
    ]

    response = llm_with_tools.invoke(messages)

    messages.append(response)

    # No web search requested
    if not response.tool_calls:

        return {
            "answer": response.content,
            "evidence": [],
            "search_performed": False,
            "search_success": False,
        }

    all_evidence = []

    # Execute tool calls
    for tool_call in response.tool_calls:

        if tool_call["name"] == "search_web":

            search_results = search_web.invoke(
                tool_call["args"]
            )

            if search_results:

                all_evidence.extend(
                    search_results
                )

            messages.append(
                ToolMessage(
                    content=str(search_results),
                    tool_call_id=tool_call["id"],
                )
            )

    # Search was requested but nothing was found
    if not all_evidence:
        return {
            "answer": (
                "The required information could not "
                "be verified because the web search "
                "did not return reliable evidence."
            ),
            "evidence": [],
            "search_performed": True,
            "search_success": False,
            "verification": None,
        }


    # Try to discover additional primary-source evidence
    primary_source = create_primary_source_query(task)

    if primary_source.search_query:

        print(
            f"Primary source search: "
            f"{primary_source.search_query}"
        )

        primary_results = search_web.invoke({
            "query": primary_source.search_query
        })

        if primary_results:
            all_evidence.extend(primary_results)


    # Remove duplicate URLs
    unique_evidence = []
    seen_urls = set()

    for evidence in all_evidence:

        url = evidence.get("link", "")

        if url and url not in seen_urls:
            seen_urls.add(url)
            unique_evidence.append(evidence)


    all_evidence = unique_evidence


    # Evaluate source quality
    evaluated_evidence = evaluate_sources(
        all_evidence,
        official_domain=primary_source.official_domain,
    )

    # Evaluate relevance of each source
    relevance_evaluated_evidence = []

    for evidence in evaluated_evidence:

        relevance = evaluate_evidence_relevance(
            task,
            evidence,
        )

        evidence["relevant"] = relevance.relevant
        evidence["relevance"] = relevance.relevance
        evidence["relevance_reason"] = relevance.reason

        relevance_evaluated_evidence.append(
            evidence
        )


    # Verify evidence
    verification = verify_evidence(
        task,
        relevance_evaluated_evidence,
    )


    # Give evaluated evidence to the LLM
    messages.append(
        HumanMessage(
            content=f"""
    Source evaluation and verification:

    {verification.model_dump()}

    When producing the final answer:

    - Use only the supplied evidence.
    - Mention important unresolved conflicts.
    - Do not present conflicting information as verified fact.
    - Minor rounding differences such as 349.13cc versus
    350cc should not automatically be treated as a conflict.
    """
        )
    )


    final_response = llm.invoke(messages)


    return {
        "answer": final_response.content,
        "evidence": relevance_evaluated_evidence,
        "search_performed": True,
        "search_success": True,
        "verification": verification.model_dump(),
    }