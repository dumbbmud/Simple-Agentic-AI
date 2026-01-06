# runtime/sessions.py
import asyncio
from google.adk.sessions import InMemorySessionService

async def init_session(session_service, app_name:str,user_id:str,session_id:str, state=None) -> InMemorySessionService:
    session = await session_service.create_session(
        app_name=app_name,
        user_id=user_id,
        session_id=session_id,
        state=None
    )
    print(f"Session created: App='{app_name}', User='{user_id}', Session='{session_id}'")
    return session
