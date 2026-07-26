from copy import deepcopy

from langgraph.prebuilt import ToolNode


class ThreadAwareToolNode(ToolNode):
    """
    Automatically injects thread_id into rag_tool calls.
    """

    def invoke(self, state, config=None):

        state = deepcopy(state)

        thread_id = state.get("thread_id")

        messages = state.get("messages", [])

        if not messages:
            return super().invoke(state, config)

        last_message = messages[-1]

        if hasattr(last_message, "tool_calls"):

            for tool_call in last_message.tool_calls:

                if tool_call["name"] == "rag_tool":

                    tool_call.setdefault("args", {})

                    tool_call["args"]["thread_id"] = thread_id

        return super().invoke(state, config)