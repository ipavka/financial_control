import hashlib
import hmac
import base64
import json
from typing import Optional
from pprint import pprint

from fastapi import FastAPI, Form, Cookie, Body, Request, status
from fastapi.param_functions import Body
from fastapi.responses import Response, HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from loguru import logger

from db import SQLite
from config import (
    PASSWORD_SALT,
    SECRET_KEY
)


db = SQLite('log_info.db')
db.create_tables('users')

app = FastAPI()

tem = Jinja2Templates(directory="templates")


def verify_password(username: str, password: str) -> bool:
    """ Делаем Хеш и проверяем сходство """
    password_hash = hmac.new(
        password.encode(), (username + PASSWORD_SALT).encode(), hashlib.sha256
    ).hexdigest()
    hash_in_db = db.get_user_data(username).get('password')
    return password_hash == hash_in_db


def sign_data(data: str) -> str:
    """ Возвращает подписанные данные data """
    return hmac.new(
        SECRET_KEY.encode(),
        msg=data.encode(),
        digestmod=hashlib.sha256
    ).hexdigest()


def get_username_from_signed_string(username_signed: str) -> Optional[str]:
    username_base64, sign = username_signed.split('.')
    logger.info(f'username_base64: {username_base64}')
    try:
        username = base64.b64decode(username_base64.encode()).decode()
        logger.info(f'username: {username}')
        valid_sign = sign_data(username)
        if hmac.compare_digest(valid_sign, sign):
            return username
    except Exception:
        return


@app.get('/cabinet', response_class=HTMLResponse)
def index_page(request: Request, username: Optional[str] = Cookie(default=None)):
    logger.info(f'request {request}')
    logger.info(f'request {username}')
    context = {
        "request": request,
    }
    if not username:
        logger.info(f'Первый if')
        return tem.TemplateResponse('index.html', context)
    valid_username = get_username_from_signed_string(username)
    logger.info(f'request {valid_username}')
    if not valid_username:
        response = tem.TemplateResponse('index.html', context)
        response.delete_cookie(key="username")
        return response
    context = {
        "request": request,
        "answer": f'Привет!!! {valid_username}'
    }
    response = tem.TemplateResponse('index.html', context)
    return response


@app.post('/login', response_class=HTMLResponse)
def process_login_page(
        request: Request,
        username: str = Form(...),
        password: str = Form(...)):
    context = {
        "request": request,
        "answer": f'Я вас не знаю! {username}'
    }
    data_user = db.get_user_data(username)
    if not data_user or not verify_password(username, password):
        # return Response(f'Я вас не знаю! <h2>{username}</h2>', media_type='text/html')
        return tem.TemplateResponse('index.html', context)
    user = data_user.get('user')
    # response = Response(
    #     f'Привет, {user}',
    #     media_type='text/html'
    # )
    context['answer'] = f'Привет, {user}!'
    response = tem.TemplateResponse('index.html', context)
    # response = RedirectResponse('/main.html', status_code=status.HTTP_302_FOUND)
    username_signed = base64.b64encode(username.encode()).decode() + "." + sign_data(username)
    response.set_cookie(key="username", value=username_signed)
    return response


if __name__ == '__main__':
    pass

