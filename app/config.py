import os
from dotenv import load_dotenv
from typing import Final


load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
"""Секретный ключ"""
if SECRET_KEY is None:
    raise ValueError("SECRET_KEY must be set in .env")


_ALGORITHM_STR = os.getenv("ALGORITHM")
if _ALGORITHM_STR is None:
    raise ValueError("ALGORITHM must be set in .env")
ALGORITHM = str(_ALGORITHM_STR)
"""Алгоритм шифрования для JWT"""


_ACCESS_TOKEN_EXPIRE_MINUTES_STR = os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES")
if _ACCESS_TOKEN_EXPIRE_MINUTES_STR is None:
    raise ValueError("ACCESS_TOKEN_EXPIRE_MINUTES must be set in .env")
ACCESS_TOKEN_EXPIRE_MINUTES = int(_ACCESS_TOKEN_EXPIRE_MINUTES_STR)
"""Срок действия access токена в минутах."""


_REFRESH_TOKEN_EXPIRE_DAYS_STR = os.getenv("REFRESH_TOKEN_EXPIRE_DAYS")
if _REFRESH_TOKEN_EXPIRE_DAYS_STR is None:
    raise ValueError("REFRESH_TOKEN_EXPIRE_DAYS must be set in .env")
REFRESH_TOKEN_EXPIRE_DAYS = int(_REFRESH_TOKEN_EXPIRE_DAYS_STR)
"""Срок действия refresh токена в днях."""
