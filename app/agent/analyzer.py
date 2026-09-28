from langchain_core.prompts import ChatPromptTemplate

from app.llm.models import get_llm
from app.models.schemas import RequirementAnalysis


llm = get_llm()

structured_llm = llm.with_structured_output(
    RequirementAnalysis
)


prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """
        You are the requirement analyzer for a research agent.

        Your job is to determine whether the user's COMPLETE
        research requirement is clear enough before research begins.

        Use BOTH:
        - previous conversation
        - current user message

        IMPORTANT RULES:

        1. Never assume the meaning of an ambiguous product or term.

        2. If the user says only "bike" and the conversation does
           not establish whether they mean a bicycle or motorcycle,
           you MUST return:

           is_clear = false

           clarification_question =
           "Are you looking for a bicycle or a motorcycle?"

        3. If previous conversation already resolves the ambiguity,
           do not ask the same question again.

        Example:

        Previous conversation:
        none

        Current message:
        "I need to buy a bike"

        Result:
        is_clear = false
        clarification_question =
        "Are you looking for a bicycle or a motorcycle?"


        Example:

        Previous conversation:
        user: I need to buy a bike
        assistant: Are you looking for a bicycle or a motorcycle?

        Current message:
        motorcycle

        Result:
        is_clear = true
        resolved_query = "I need to buy a motorcycle."


        Example:

        Previous conversation:
        user: I want to buy a Dominar 400 2026

        Current message:
        Compare it with similar bikes

        Result:
        is_clear = true
        resolved_query =
        "Compare the Dominar 400 2026 with similar motorcycles."


        Determine:
        - is_clear
        - intent
        - topic
        - requires_current_information
        - clarification_question
        - resolved_query

        The resolved_query must be a standalone request that can
        be understood without reading the previous conversation.

        Do not perform research.
        Do not create research tasks.
        """
    ),
    (
        "human",
        """
        Previous conversation:

        {conversation}

        Current user message:

        {user_query}
        """
    )
])


def analyze_requirement(
    user_query: str,
    history: list,
) -> RequirementAnalysis:

    conversation = ""

    for message in history:

        conversation += (
            f"{message['role']}: "
            f"{message['content']}\n"
        )

    messages = prompt.invoke({
        "conversation": conversation,
        "user_query": user_query,
    })

    analysis = structured_llm.invoke(messages)
    


    return analysis
