from langchain_core.prompts import ChatPromptTemplate

from app.llm.models import get_llm
from app.models.schemas import ResearchPlan

# Get the language model
llm = get_llm()

# used to generate structured output from the LLM "with_structured_output"
structured_llm = llm.with_structured_output(ResearchPlan)


prompt = ChatPromptTemplate.from_messages([
    (
        "system",
        """
        You are the planning component of a research agent.

        Understand the user's research requirement and
        create a clear research plan.

        Do not perform the actual research.

        Create only the tasks necessary to satisfy the
        user's requirement.

        For simple requests create 2-4 tasks.
        For medium requests create 3-6 tasks.
        For complex requests create at most 8 tasks.
        """
    ),
    (
        "human",
        "{user_query}"
    ),
])

# Function to create a research plan based on user query
def create_research_plan(user_query: str) -> ResearchPlan:

    messages = prompt.invoke({
        "user_query": user_query
    })

    plan = structured_llm.invoke(messages)

    return plan