import os
import re
from datetime import datetime

from docx import Document
from docx.shared import Pt


REPORT_DIRECTORY = "generated_reports"


def clean_markdown(text: str) -> str:
    """
    Remove basic Markdown formatting before writing
    text into the Word document.
    """

    if not text:
        return ""

    text = re.sub(r"\\([#*\-_])", r"\1", text)
    text = re.sub(r"\*\*(.*?)\*\*", r"\1", text)
    text = re.sub(r"###\s*", "", text)
    text = re.sub(r"##\s*", "", text)
    text = re.sub(r"#\s*", "", text)

    return text.strip()


def generate_research_docx(
    session_id: str,
    query: str,
    plan,
    results: list,
    final_answer: str,
) -> str:
    """
    Generate a DOCX report containing the completed
    research and return the generated file path.
    """

    os.makedirs(
        REPORT_DIRECTORY,
        exist_ok=True,
    )

    document = Document()

    # Default font
    styles = document.styles

    styles["Normal"].font.name = "Arial"
    styles["Normal"].font.size = Pt(11)

    # Title
    document.add_heading(
        "Research Report",
        level=0,
    )

    # Basic information
    document.add_paragraph(
        f"Research Query: {query}"
    )

    document.add_paragraph(
        "Generated: "
        + datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )
    )

    # Research topic
    if getattr(plan, "topic", None):
        document.add_heading(
            "Research Topic",
            level=1,
        )

        document.add_paragraph(
            plan.topic
        )

    # Research goal
    if getattr(plan, "goal", None):
        document.add_heading(
            "Research Goal",
            level=1,
        )

        document.add_paragraph(
            plan.goal
        )

    # Final answer
    document.add_heading(
        "Research Summary",
        level=1,
    )

    document.add_paragraph(
        clean_markdown(final_answer)
    )

    # Individual research tasks
    document.add_heading(
        "Research Findings",
        level=1,
    )

    for result in results:

        task = result.get(
            "task",
            "Research Task",
        )

        document.add_heading(
            task,
            level=2,
        )

        status = result.get(
            "status",
            "unknown",
        )

        document.add_paragraph(
            f"Status: {status}"
        )

        finding = result.get("result")

        if finding:
            document.add_paragraph(
                clean_markdown(finding)
            )

        evidence = result.get(
            "evidence",
            [],
        )

        if evidence:

            document.add_heading(
                "Sources",
                level=3,
            )

            for source in evidence:

                title = source.get(
                    "title",
                    "Source",
                )

                url = source.get(
                    "url",
                    "",
                )

                source_type = source.get(
                    "source_type",
                    "unknown",
                )

                relevance = source.get(
                    "relevance",
                    "unknown",
                )

                paragraph = (
                    f"{title}\n"
                    f"{url}\n"
                    f"Source type: {source_type}\n"
                    f"Relevance: {relevance}"
                )

                document.add_paragraph(
                    paragraph,
                    style="List Bullet",
                )

    # File name
    timestamp = datetime.now().strftime(
        "%Y%m%d_%H%M%S"
    )

    safe_session_id = re.sub(
        r"[^a-zA-Z0-9_-]",
        "",
        session_id,
    )

    filename = (
        f"research_report_"
        f"{safe_session_id}_"
        f"{timestamp}.docx"
    )

    file_path = os.path.join(
        REPORT_DIRECTORY,
        filename,
    )

    document.save(file_path)

    return file_path