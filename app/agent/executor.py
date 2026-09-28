from app.models.schemas import ResearchPlan
from app.agent.researcher import research_task


def execute_research_plan(
    plan: ResearchPlan,
    previous_research: dict | None = None,
):

    results = []

    for task in plan.tasks:

        print(f"\nExecuting Task {task.id}")
        print(task.description)

        try:

            previous_findings = [
                result
                for result in results
                if result["status"] == "success"
            ]

            research_result = research_task(
                task.description,
                previous_findings,
                previous_research,
            )

            # Determine actual research status
            if (
                research_result["search_performed"]
                and not research_result["search_success"]
            ):

                status = "failed"

            else:

                status = "success"

            results.append({
                "task_id": task.id,
                "task": task.description,
                "status": status,
                "result": research_result["answer"],
                "evidence": research_result["evidence"],
            })

            print(
                f"Task {task.id} finished "
                f"with status: {status}"
            )

        except Exception as error:

            print(
                f"Task {task.id} failed: {error}"
            )

            results.append({
                "task_id": task.id,
                "task": task.description,
                "status": "failed",
                "result": None,
                "evidence": [],
                "error": str(error),
            })

    return results