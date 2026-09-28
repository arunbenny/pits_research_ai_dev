from pathlib import Path
import os

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel

from app.agent.analyzer import analyze_requirement
from app.agent.planner import create_research_plan
from app.agent.executor import execute_research_plan
from app.agent.synthesizer import synthesize_research

from app.memory.session import (
    get_history,
    add_message,
    save_research_state,
    get_research_state,
)

from app.reports.docx_report import (
    generate_research_docx,
)


app = FastAPI()

BASE_DIR = Path(__file__).resolve().parent


class ResearchRequest(BaseModel):
    session_id: str
    query: str


@app.get("/")
def home():
    return FileResponse(
        BASE_DIR / "static" / "index.html"
    )


@app.post("/research")
def research(request: ResearchRequest):

    # ----------------------------------
    # Load session context
    # ----------------------------------

    history = get_history(
        request.session_id
    )

    previous_research = get_research_state(
        request.session_id
    )


    # ----------------------------------
    # Analyze requirement
    # ----------------------------------

    analysis = analyze_requirement(
        request.query,
        history,
    )


    # Store user message
    add_message(
        request.session_id,
        "user",
        request.query,
    )


    # ----------------------------------
    # Requirement is unclear
    # ----------------------------------

    if not analysis.is_clear:

        question = (
            analysis.clarification_question
            or "Could you clarify your research request?"
        )

        add_message(
            request.session_id,
            "assistant",
            question,
        )

        return {
            "status": "clarification_required",
            "message": question,
        }


    # ----------------------------------
    # Requirement is clear
    # ----------------------------------

    resolved_query = analysis.resolved_query

    print(
        "\nResolved Query:",
        resolved_query,
    )


    # ----------------------------------
    # Create research plan
    # ----------------------------------

    plan = create_research_plan(
        resolved_query
    )


    # ----------------------------------
    # Execute research
    # ----------------------------------

    results = execute_research_plan(
        plan,
        previous_research=previous_research,
    )


    # ----------------------------------
    # Generate final answer
    # ----------------------------------

    final_answer = synthesize_research(
        resolved_query,
        results,
    )


    # ----------------------------------
    # Generate DOCX report
    # ----------------------------------

    report_path = generate_research_docx(
        session_id=request.session_id,
        query=resolved_query,
        plan=plan,
        results=results,
        final_answer=final_answer,
    )

    print(
        "\nGenerated report:",
        report_path,
    )


    # ----------------------------------
    # Save research state
    # ----------------------------------

    save_research_state(
        session_id=request.session_id,
        query=resolved_query,
        plan=plan,
        results=results,
        final_answer=final_answer,
        report_path=report_path,
    )

    print(
        "\nSaved research state for session:",
        request.session_id,
    )


    # ----------------------------------
    # Save assistant response
    # ----------------------------------

    add_message(
        request.session_id,
        "assistant",
        final_answer,
    )


    # ----------------------------------
    # Build simple activity information
    # ----------------------------------

    successful_tasks = sum(
        1
        for result in results
        if result.get("status") == "success"
    )

    failed_tasks = sum(
        1
        for result in results
        if result.get("status") == "failed"
    )

    activities = [
        {
            "name": "Requirement analysis",
            "status": "completed",
        },
        {
            "name": "Research planning",
            "status": "completed",
        },
        {
            "name": "Research execution",
            "status": "completed",
            "details": (
                f"{successful_tasks} successful, "
                f"{failed_tasks} failed"
            ),
        },
        {
            "name": "Final synthesis",
            "status": "completed",
        },
        {
            "name": "DOCX report generation",
            "status": "completed",
        },
    ]


    # ----------------------------------
    # API response
    # ----------------------------------

    return {
        "status": "completed",
        "topic": plan.topic,
        "goal": plan.goal,
        "results": results,
        "answer": final_answer,
        "activities": activities,
        "report_url": (
            f"/research/report/"
            f"{request.session_id}"
        ),
    }


@app.get(
    "/research/report/{session_id}"
)
def download_research_report(
    session_id: str,
):

    state = get_research_state(
        session_id
    )

    if not state:
        raise HTTPException(
            status_code=404,
            detail="Research session not found.",
        )


    report_path = state.get(
        "report_path"
    )


    if (
        not report_path
        or not os.path.exists(report_path)
    ):
        raise HTTPException(
            status_code=404,
            detail="Research report not found.",
        )


    return FileResponse(
        path=report_path,
        filename=os.path.basename(
            report_path
        ),
        media_type=(
            "application/vnd.openxmlformats-"
            "officedocument.wordprocessingml.document"
        ),
    )