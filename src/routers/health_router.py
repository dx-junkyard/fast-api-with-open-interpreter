from fastapi import APIRouter

from src.config.tool_version_config import tool_version

router = APIRouter()


@router.get("/")
def read_root():
    return {"version": tool_version}
