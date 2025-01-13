import asyncio
import os

from dotenv import load_dotenv
from llama_index.core.memory import ChatMemoryBuffer
from llama_index.core.tools import BaseTool
from llama_index.core.workflow import Context
from llama_index.llms.openai import OpenAI
from llama_index.utils.workflow import draw_all_possible_flows

from workflow import (
    AgentConfig,
    SystemAgent,
    ProgressEvent,
    ToolRequestEvent,
    ToolApprovedEvent,
)
from utils import FunctionToolWithContext


def get_initial_state() -> dict:
    return {}


def get_health_coach_tools() -> list[BaseTool]:
    async def get_user_information(ctx: Context) -> str:
        """Get the user information from API and Database."""
        mocked_user_persona = {"age": 25, "weight": 70, "height": 180}
        mocked_user_tasks = ["walk 1000 steps", "eat two apples"]
        ctx.write_event_to_stream(ProgressEvent(msg="Retrieving user information"))
        user_state = await ctx.get("user_state")
        user_state["user_persona"] = mocked_user_persona
        user_state["user_tasks"] = mocked_user_tasks
        await ctx.set("user_state", user_state)
        return f"The user information is {user_state["user_persona"]} and the user tasks are {user_state["user_tasks"]}."

    async def get_reference_from_rag(ctx: Context) -> str:
        """Get more reference from RAG."""
        mocked_rag_return = ["Walking regularly helps you grow taller and helps you sleep", "Eating fruits can ensure normal intake of vitamins and contribute to health"]
        ctx.write_event_to_stream(ProgressEvent(msg="Retrieving reference from RAG"))
        user_state = await ctx.get("user_state")
        user_state["user_reference"] = mocked_rag_return
        await ctx.set("user_state", user_state)
        return f"The reference information from RAG is {user_state["user_reference"]}."

    return [
        FunctionToolWithContext.from_defaults(async_fn=get_user_information),
        FunctionToolWithContext.from_defaults(async_fn=get_reference_from_rag)
    ]


def get_information_tools() -> list[BaseTool]:
    return []


def get_agent_configs() -> list[AgentConfig]:
    return [
        AgentConfig(
            name="Health Coach Agent",
            description="Coach the user to have a better health",
            system_prompt="""
You are a helpful assistant that is coaching a user to have better health.
You must follow those steps:
1. call "get_user_information" to get the user_persona and user tasks.
2. call "get_reference_from_rag" to get the reference information from RAG.
3. Ask user the goal of health coaching.
4. Use the information from step 1 and 2 and the user's goal to generate 3 related tasks, MUST give the suggestion directly, DO NOT ask user question.
Note: the function call might be rejected by use, if so, MUST highlight function call status in the beginning of your response.
            """,
            tools=get_health_coach_tools(),
            tools_requiring_human_confirmation=["get_user_information"]
        ),
        AgentConfig(
            name="Information Agent",
            description="Answer user's question related to health",
            system_prompt="""
You are a helpful assistant that is answering the question from a user.
Your task is to answer the question related to health, if the question is not related to health, you still need to answer it but with a gental reminder in the end of response.
            """,
            tools=get_information_tools(),
        )
    ]


async def main():
    """Main function to run the workflow."""

    from colorama import Fore, Style
    load_dotenv()

    llm = OpenAI(model="gpt-4o", temperature=0, api_base=os.getenv('API_BASE'), api_key=os.getenv('API_KEY'))
    memory = ChatMemoryBuffer.from_defaults(llm=llm)
    initial_state = get_initial_state()
    agent_configs = get_agent_configs()
    workflow = SystemAgent(timeout=None)
    draw_all_possible_flows(workflow, filename="workflow.html")

    # draw a diagram of the workflow
    # draw_all_possible_flows(workflow, filename="workflow.html")

    handler = workflow.run(
        user_msg="Hello!",
        agent_configs=agent_configs,
        llm=llm,
        chat_history=[],
        initial_state=initial_state,
    )

    while True:
        async for event in handler.stream_events():
            if isinstance(event, ToolRequestEvent):
                print(
                    Fore.GREEN
                    + "SYSTEM >> I need approval for the following tool call:"
                    + Style.RESET_ALL
                )
                print(event.tool_name)
                print(event.tool_kwargs)
                print()

                approved = input("Do you approve? (y/n): ")
                if "y" in approved.lower():
                    handler.ctx.send_event(
                        ToolApprovedEvent(
                            tool_id=event.tool_id,
                            tool_name=event.tool_name,
                            tool_kwargs=event.tool_kwargs,
                            approved=True,
                        )
                    )
                else:
                    reason = input("Why not? (reason): ")
                    handler.ctx.send_event(
                        ToolApprovedEvent(
                            tool_name=event.tool_name,
                            tool_id=event.tool_id,
                            tool_kwargs=event.tool_kwargs,
                            approved=False,
                            response=reason,
                        )
                    )
            elif isinstance(event, ProgressEvent):
                print(Fore.GREEN + f"SYSTEM >> {event.msg}" + Style.RESET_ALL)

        result = await handler
        print(Fore.BLUE + f"AGENT >> {result['response']}" + Style.RESET_ALL)

        # update the memory with only the new chat history
        for i, msg in enumerate(result["chat_history"]):
            if i >= len(memory.get()):
                memory.put(msg)

        user_msg = input("USER >> ")
        if user_msg.strip().lower() in ["exit", "quit", "bye"]:
            break

        # pass in the existing context and continue the conversation
        handler = workflow.run(
            ctx=handler.ctx,
            user_msg=user_msg,
            agent_configs=agent_configs,
            llm=llm,
            chat_history=memory.get(),
            initial_state=initial_state,
        )


if __name__ == "__main__":
    asyncio.run(main())
