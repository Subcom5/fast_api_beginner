from fastapi import FastAPI
from app.routers import (
    categories, products, users, review, cart, orders
)
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware
from fastapi.middleware.gzip import GZipMiddleware


# Создаем приложение FastAPI
app = FastAPI(
    title="FastAPI Интернет-магазин",
    version="0.1.0"
)

# список источников которым разрешен доступ к API
origins = [
    "http://localhost:5000",
    "https://example.com",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    # чтобы браузер мог распознавать совпадения адресов
    # домена и отправлять файл cookie авторизации для разрешения запроса
    allow_credentials=True,
    # разрешены все HTTP-методы
    allow_methods=["*"],
    # разрешены все заголовки запроса
    # (включая Content-Type, Authorization и кастомные)
    allow_headers=["*"],
)
# Сжатие ответов через gzip, если тело ответа больше minimum_size байт.
# Экономит трафик для текстовых ответов (JSON, HTML, CSS).
# Для маленьких ответов сжатие не применяется — overhead больше выгоды.
# app.add_middleware(GZipMiddleware, minimum_size=1000)

# Автоматический редирект всех HTTP-запросов на HTTPS.
# Все ответы будут с кодом 307/308 на https://-версию того же URL.
# Полезно в проде; за обратным прокси (nginx, traefik) часто не нужно,
# т.к. редирект делает сам прокси.
# app.add_middleware(HTTPSRedirectMiddleware)

# Доверенные хосты: какие значения заголовка Host принимать.
# Защита от атак типа Host Header Injection.
# "*" — разрешить любой хост (удобно для разработки, небезопасно для продакшена).
# В проде лучше явно перечислить домены, например:
#   allowed_hosts=["example.com", "*.example.com"]
# app.add_middleware(
#     TrustedHostMiddleware,
#     allowed_hosts=["*"],
# )

app.mount("/media", StaticFiles(directory="media"), name="media")

# Подключаем маршруты категорий
app.include_router(categories.router)
app.include_router(products.router)
app.include_router(users.router)
app.include_router(review.router)
app.include_router(cart.router)
app.include_router(orders.router)
