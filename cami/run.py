# import uuid

# from google.adk.events import Event
# from google.adk.runners import Runner
# from google.adk.sessions import DatabaseSessionService
# from google.adk.tools import LongRunningFunctionTool
# from google.genai import types
# from pydantic import BaseModel

# from cami.agent import root
# from cami.agent.tools.tools import AskForApproval, GetClaimStatus
# from cami.config import APP_NAME, DATABASE_PASSWORD, DATABASE_URL
# from cami.typedef import (
#     ChatEntry,
#     ClaimHistory,
#     LongRunningTask,
#     LongRunningTasks,
# )


# class Response(BaseModel):
#     status: str


# session_service = DatabaseSessionService(
#     db_url=f"postgresql://postgres:{DATABASE_PASSWORD}@{DATABASE_URL}/postgres",
#     echo=False,
# )


# # fixme: should come from auth layer.
# USER_ID = "sanchitrk"


# async def on_message(ctx: restate.ObjectContext, message: ChatEntry) -> Response:
#     print(f"-> ctx.key(): {ctx.key()}")
#     print(f"-> role: {message.role} content: {message.content}")

#     session = await session_service.get_session(
#         app_name=APP_NAME,
#         user_id=USER_ID,
#         session_id=ctx.key(),
#     )
#     if not session:
#         await session_service.create_session(
#             app_name=APP_NAME,
#             user_id=USER_ID,
#             session_id=ctx.key(),
#         )

#     ask_for_approval = AskForApproval(ctx=ctx)
#     get_claim_status = GetClaimStatus(ctx=ctx)

#     long_running_tool = LongRunningFunctionTool(func=ask_for_approval)

#     agent.tools = [get_claim_status, long_running_tool]

#     runner = Runner(
#         agent=agent,
#         app_name=APP_NAME,
#         session_service=session_service,
#     )

#     def get_long_running_function_call(event: Event) -> types.FunctionCall | None:
#         if (
#             not event.long_running_tool_ids
#             or not event.content
#             or not event.content.parts
#         ):
#             return
#         for part in event.content.parts:
#             if (
#                 part
#                 and part.function_call
#                 and event.long_running_tool_ids
#                 and part.function_call.id in event.long_running_tool_ids
#             ):
#                 return part.function_call

#     def get_function_response(
#         event: Event, function_call_id: str
#     ) -> types.FunctionResponse | None:
#         # Get the function response for the fuction call with specified id.
#         if not event.content or not event.content.parts:
#             return
#         for part in event.content.parts:
#             if (
#                 part
#                 and part.function_response
#                 and part.function_response.id == function_call_id
#             ):
#                 return part.function_response

#     tasks = await ctx.get("tasks", type_hint=LongRunningTasks) or LongRunningTasks()

#     content = types.Content(role="user", parts=[types.Part(text=message.content)])
#     final_reponse_text = None
#     async for event in runner.run_async(
#         user_id=USER_ID,
#         new_message=content,
#         session_id=ctx.key(),
#     ):
#         print(
#             f"Start of Event --------- \n"
#             f"Author: {event.author} \n"
#             f"Type: {type(event).__name__} \n"
#             f"Final: {event.is_final_response()}, Content: {event.content} \n"
#             f"** Event: {event} ** \n"
#             f"End of Event --------- \n"
#         )
#         long_running_function_call = get_long_running_function_call(event)
#         if long_running_function_call:
#             print("**** long running fnc: ", long_running_function_call)
#             task = LongRunningTask(
#                 id=long_running_function_call.id or str(uuid.uuid4()),
#                 args=long_running_function_call.args,
#                 name=long_running_function_call.name,
#             )
#             tasks.entries.append(task)
#             ctx.set("tasks", tasks)

#         if event.is_final_response():
#             if event.content and event.content.parts:
#                 final_reponse_text = event.content.parts[0].text
#             elif event.actions and event.actions.escalate and event.error_message:
#                 final_reponse_text = f"Escalated with message: {event.error_message}"
#             elif event.actions and event.actions.escalate:
#                 final_reponse_text = "Escalated without message"
#             break

#     claims = await ctx.get("claims", type_hint=ClaimHistory) or ClaimHistory()
#     tasks = await ctx.get("tasks", type_hint=LongRunningTasks) or LongRunningTasks()
#     print("----- agent state ----- \n")
#     print("tasks: ", tasks)
#     print("claims: ", claims)
#     print("----- agent state ----- \n")

#     print(f"Agent: {final_reponse_text}")
#     return Response(status="ok")


"""
Next steps: My thoughts

create a handler for approval and reject
from functions that require approval or reject, lets send the key - interrupt: true
if function is long running and has interrupt as true, then add it to the
interrupts state

approval and reject shall mutate the interrupt state, similar to tasks that
is now created.


we can also modify the message to take the typing.Content state, in this way we
can create a new message that we can send handler-message e.g:
async for event in runner.run_async(
      session_id=session.id, user_id=USER_ID,
      new_message=types.Content(
      parts=[types.Part(function_response = updated_response)],
      role='user')
    ):

here instead of the run_async we call the ctx handler with the paylaod of new message
maintaining the loop
"""
