import os
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
SECRET_KEY=os.environ.get("DJANGO_SECRET_KEY","local-only-not-a-deployment-key")
DEBUG=os.environ.get("NEXTSEASON_DEBUG","0")=="1"
ALLOWED_HOSTS=os.environ.get("DJANGO_ALLOWED_HOSTS","localhost,127.0.0.1,[::1],testserver").split(",")
ROOT_URLCONF="config.urls"
WSGI_APPLICATION="config.wsgi.application"
INSTALLED_APPS=["rest_framework"]
MIDDLEWARE=["django.middleware.security.SecurityMiddleware","django.middleware.common.CommonMiddleware","django.middleware.csrf.CsrfViewMiddleware","django.middleware.clickjacking.XFrameOptionsMiddleware"]
USE_TZ=True
TIME_ZONE="UTC"
DATA_UPLOAD_MAX_MEMORY_SIZE=32768
ALLOW_DEVELOPMENT_FIXTURES=DEBUG and os.environ.get("NEXTSEASON_ALLOW_FIXTURES","0")=="1"
POWER_CACHE_DIR=Path(os.environ.get("NEXTSEASON_CACHE_DIR",str(ROOT/".runtime/power")))
ENVIRONMENT_CACHE_DIR=Path(os.environ.get("NEXTSEASON_ENV_CACHE_DIR",str(ROOT/".runtime/environment")))
REST_FRAMEWORK={"DEFAULT_AUTHENTICATION_CLASSES":[],"UNAUTHENTICATED_USER":None,"DEFAULT_RENDERER_CLASSES":["rest_framework.renderers.JSONRenderer"],"DEFAULT_THROTTLE_CLASSES":["rest_framework.throttling.AnonRateThrottle"],"DEFAULT_THROTTLE_RATES":{"anon":"20/min"}}
SECURE_CONTENT_TYPE_NOSNIFF=True
SECURE_SSL_REDIRECT=os.environ.get("NEXTSEASON_SECURE_SSL_REDIRECT","0")=="1"
SECURE_HSTS_SECONDS=int(os.environ.get("NEXTSEASON_HSTS_SECONDS","0"))
CSRF_COOKIE_SECURE=SECURE_SSL_REDIRECT
if os.environ.get("NEXTSEASON_TRUST_PROXY_HEADERS","0")=="1":
    # Enable only when a trusted reverse proxy overwrites this header and Django is private.
    SECURE_PROXY_SSL_HEADER=("HTTP_X_FORWARDED_PROTO","https")

