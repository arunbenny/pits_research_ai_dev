from typing import Dict, List, Any


# Conversation messages
sessions: Dict[str, List[dict]] = {}


# Structured research state for each session
research_states: Dict[str, Dict[str, Any]] = {}


def get_history(session_id: str) -> List[dict]:
    """
    Return conversation history for a session.
    """

    return sessions.get(session_id, [])


def add_message(
    session_id: str,
    role: str,
    content: str,
):
    """
    Add a user or assistant message to session history.
    """

    if session_id not in sessions:
        sessions[session_id] = []

    sessions[session_id].append({
        "role": role,
        "content": content,
    })


def save_research_state(
    session_id: str,
    query: str,
    plan: Any,
    results: list,
    final_answer: str,
    report_path: str | None = None,
):
    """
    Store the latest completed research for follow-up queries.
    """

    research_states[session_id] = {
        "query": query,
        "plan": plan,
        "results": results,
        "final_answer": final_answer,
        "report_path": report_path,
    }


def get_research_state(
    session_id: str,
) -> Dict[str, Any] | None:
    """
    Return previous research state for a session.
    """

    return research_states.get(session_id)


def clear_session(
    session_id: str,
):
    """
    Remove conversation and research state.
    """

    sessions.pop(session_id, None)
    research_states.pop(session_id, None)