import uvicorn
from starlette.middleware.httpsredirect import HTTPSRedirectMiddleware

from app import app
from app.config import settings

if __name__ == "__main__":
    if settings.SSL_CERT_ENABLED:
        app.add_middleware(HTTPSRedirectMiddleware)
        uvicorn.run(app, host=settings.WEB_HOST, port=443, ssl_keyfile=settings.SSL_KEY_PATH, ssl_certfile=settings.SSL_CERT_PATH)
    else:
        uvicorn.run(app, host=settings.WEB_HOST, port=settings.WEB_PORT)