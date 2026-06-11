import traceback

def attach_exception_logger(app):
    from fastapi import Request
    from starlette.responses import Response
    from starlette.middleware.base import BaseHTTPMiddleware

    class ExceptionLoggingMiddleware(BaseHTTPMiddleware):
        async def dispatch(self, request: Request, call_next):
            try:
                response = await call_next(request)
                return response
            except Exception as e:
                with open("error_500_traceback.txt", "a") as f:
                    f.write(f"\n--- ERROR 500 TRACEBACK for {request.url.path} ---\n")
                    f.write(traceback.format_exc())
                raise e

    app.add_middleware(ExceptionLoggingMiddleware)
