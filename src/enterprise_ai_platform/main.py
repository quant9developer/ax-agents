from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse, Response

from enterprise_ai_platform.api.middleware.auth import AuthMiddleware
from enterprise_ai_platform.api.middleware.rate_limit import RateLimitMiddleware
from enterprise_ai_platform.api.middleware.request_logging import RequestLoggingMiddleware
from enterprise_ai_platform.api.router import router
from enterprise_ai_platform.config import get_settings
from enterprise_ai_platform.web_demo import demo_html_response



def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title=settings.app_name, version=settings.app_version, debug=settings.debug)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.add_middleware(RequestLoggingMiddleware)
    app.add_middleware(RateLimitMiddleware)
    app.add_middleware(AuthMiddleware)
    app.include_router(router)

    @app.get("/", include_in_schema=False)
    def root_redirect() -> RedirectResponse:
        return RedirectResponse(url="/demo")

    @app.get("/demo", include_in_schema=False)
    def demo_page():
        return demo_html_response()

    @app.get("/demo/", include_in_schema=False)
    def demo_page_slash():
        return demo_html_response()

    @app.get("/favicon.ico", include_in_schema=False)
    def favicon() -> Response:
        return Response(content=b"", media_type="image/x-icon")

    return app


app = create_app()
