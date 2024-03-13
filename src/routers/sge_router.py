import json
from typing import Annotated

from fastapi import APIRouter, HTTPException, Form
from fastapi.responses import StreamingResponse

from src.repository.sge_interpreter_client import create_interpreter

router = APIRouter(prefix="/api")


@router.post("/sge")
def chat_endpoint(
        query: Annotated[str, Form()],
):
    try:
        return StreamingResponse(
            event_stream(query),
            media_type="text/event-stream")
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500)


def event_stream(message: str):
    ai = create_interpreter()

    for result in ai.chat(message, stream=True, display=False):
        result_json = json.dumps(result, ensure_ascii=False)
        yield f"data: {result_json}\n\n"
