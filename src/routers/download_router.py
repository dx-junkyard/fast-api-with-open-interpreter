from fastapi import APIRouter, HTTPException
from fastapi.responses import Response

from src.config.logger import logger
from src.repository.user_repository import get_user

router = APIRouter(prefix="/api")


@router.get("/download/{user_id}")
def download_file(
        user_id: str,
):
    try:
        file_data_bytes = get_user(user_id).file

        # ファイルを返す
        return Response(file_data_bytes, media_type="application/octet-stream")
    except Exception as e:
        # エラーが発生した場合500エラーを返す
        logger.error(e)
        raise HTTPException(status_code=500, detail="Undefined error")
