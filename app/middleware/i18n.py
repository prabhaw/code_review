from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response

from app.config import settings
from app.i18n import set_locale


class I18nMiddleware(BaseHTTPMiddleware):
    """
    Reads the `x-lang` header from each request and sets the
    locale for the current request context. Defaults to 'en'.
    """

    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        lang = request.headers.get("x-lang", settings.DEFAULT_LOCALE).lower().strip()
        set_locale(lang)

        response = await call_next(request)
        response.headers["x-lang"] = lang
        return response
