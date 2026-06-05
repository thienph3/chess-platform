from fastapi import Request
from fastapi.responses import JSONResponse


class AnalysisException(Exception):
    def __init__(self, message: str, status_code: int = 400):
        self.message = message
        self.status_code = status_code


class EngineNotAvailableException(AnalysisException):
    def __init__(self, engine: str):
        super().__init__(f"Engine '{engine}' không khả dụng", status_code=503)


async def analysis_exception_handler(request: Request, exc: AnalysisException) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={"data": None, "message": exc.message, "errors": None},
    )
