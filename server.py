import hashlib
import hmac
import base64
import json
from typing import Optional
from pprint import pprint

from fastapi import FastAPI, Form, Cookie, Body, Request, status
from fastapi.staticfiles import StaticFiles
from fastapi.param_functions import Body
from fastapi.responses import Response, HTMLResponse, RedirectResponse, \
    JSONResponse
from fastapi.templating import Jinja2Templates
from loguru import logger

from db import SQLite
from main import pars_user_input, get_category_name
from make_data import make_date, ru_date_unix, convert_in_datetime
from config import (
    PASSWORD_SALT,
    SECRET_KEY
)

db = SQLite('log_info.db')
# db.create_tables('users')

app = FastAPI()

tem = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")


def encode_cookies(sting: str) -> str:
    return base64.b64encode(sting.encode()).decode()


def decode_cookies(sting: str) -> str:
    return base64.b64decode(sting).decode()


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
    try:
        username_base64, sign = username_signed.split('.')
        # logger.info(f'username_base64: {username_base64}')

        username = base64.b64decode(username_base64.encode()).decode()
        # logger.info(f'username: {username}')
        valid_sign = sign_data(username)
        if hmac.compare_digest(valid_sign, sign):
            return username
    except Exception:
        return


@app.get("/page/{page_name}", response_class=HTMLResponse)
async def page(request: Request, page_name: int = 3):
    context = {
        "request": request,
        "page": page_name
    }

    return tem.TemplateResponse("info.html", context)


@app.get('/', response_class=HTMLResponse)
def index_page(request: Request,
               username: Optional[str] = Cookie(default=None)):
    context = {
        "request": request,
    }
    if not username:
        return tem.TemplateResponse('login.html', context)
    valid_username = get_username_from_signed_string(username)
    if not valid_username:
        response = tem.TemplateResponse('login.html', context)
        response.delete_cookie(key="username")
        return response

    # 'count=3 - кол-во записей'
    data_notes = db.select_last_costs(valid_username, count=3)
    context = {
        "request": request,
        "name_user": valid_username,
        "last_notes": data_notes,
    }
    response = tem.TemplateResponse('main.html', context)
    return response


@app.post('/login', response_class=HTMLResponse)
def process_login_page(
        request: Request,
        username: str = Form(...),
        password: str = Form(...)):
    context = {
        "request": request,
        "notice": f'Я вас не знаю! {username}'
    }
    data_user = db.get_user_data(username)
    if not data_user or not verify_password(username, password):
        return tem.TemplateResponse('login.html', context)
    response = RedirectResponse(url='/', status_code=status.HTTP_302_FOUND)
    username_signed = base64.b64encode(
        username.encode()).decode() + "." + sign_data(username)
    response.set_cookie(key="username", value=username_signed)
    return response


@app.post('/add', response_class=HTMLResponse)
def add_new_alias(request: Request,
                  choice: str = Form(...),
                  username: Optional[str] = Cookie(default=None),
                  main_input: Optional[str] = Cookie(default=None)):
    valid_username = get_username_from_signed_string(username)
    sum_of_cost, alias, description = pars_user_input(
        decode_cookies(main_input))

    context = {
        "request": request,
        "added_alias": True,
        "not_alias": False,
        'choice': f'Из чек-бокса: {choice}',
        'name_user': valid_username,
        'main_input': f'То что ввели: {sum_of_cost} {alias} {description}',
        'add_info': f'Добавил Алиас: {alias} в категорию {choice}',
    }

    response = tem.TemplateResponse('add.html', context)
    return response


@app.get('/info', response_class=HTMLResponse)
def user_data(request: Request,
              username: Optional[str] = Cookie(default=None)):
    valid_username = get_username_from_signed_string(username)
    all_costs = db.select_last_costs(valid_username)
    context = {
        "request": request,
        "user": all_costs
    }
    response = tem.TemplateResponse('info.html', context)
    return response


@app.post('/main', response_class=HTMLResponse)
def private_page(request: Request,
                 username: Optional[str] = Cookie(default=None),
                 main_input: str = Form(...)):
    valid_username = get_username_from_signed_string(username)
    data_from_category = db.get_all_categories(valid_username)
    # data_notes = db.select_last_costs(valid_username, count=3)
    if pars_user_input(main_input):  # проверка на валидность цифры расхода
        sum_of_cost, alias, description = pars_user_input(main_input)
        ready_category = get_category_name(alias, data_from_category)
        if ready_category:  # есть ли такой алиас в категориях
            db.insert_cost({'sum_of_money_co': sum_of_cost,
                            'descrip_co': description,
                            'category': ready_category,
                            'who_spend': valid_username,
                            'view_date': ru_date_unix()[1],
                            'created': make_date()})

            data_notes = db.select_last_costs(valid_username, count=3)
            costs_id = sorted(data_notes.items())[-1][0]
            what = sorted(data_notes.items())[-1][1].split(',')[0]
            context = {
                "request": request,
                "name_user": valid_username,
                "write_down": True,
                "message": {"sum_of_cost": sum_of_cost,
                            "description": description,
                            "ready_category": ready_category,
                            "costs_id": f'{costs_id}, {what}'
                            },
                "last_notes": data_notes,
            }

            response = tem.TemplateResponse('main.html', context)
            return response

        else:  # если нет такого алиаса
            context = {
                "request": request,
                "name_user": valid_username,
                "main_message": alias,
                "not_alias": True,
                "added_alias": False,
                "data_table": data_from_category,
                "data_in": alias,
            }
            response = tem.TemplateResponse('add.html', context)
            response.set_cookie(key="main_input",
                                value=encode_cookies(main_input))
            return response

    else:  # если не валиндное число
        context = {
            "request": request,
            "name_user": valid_username,
            "incorrect_input": True,
            "message": main_input,
        }
        response = tem.TemplateResponse('main.html', context)
        return response


@app.post('/del', response_class=HTMLResponse)
def delete_last_cost(request: Request,
                     id_cost: str = Form(...),
                     username: Optional[str] = Cookie(default=None),
                     ):
    cost_id, description = id_cost.split(', ')
    valid_username = get_username_from_signed_string(username)
    db.delete_last_cost(cost_id)
    context = {
        "request": request,
        "name_user": valid_username,
        "delete_cost": True,
        "report": description,
    }
    response = tem.TemplateResponse('main.html', context)
    return response


@app.get('/logout', response_class=HTMLResponse)
def logout_user():
    response = RedirectResponse(url='/', status_code=status.HTTP_302_FOUND)
    response.delete_cookie(key="username")
    response.delete_cookie(key="main_input")
    return response


@app.get('/resume', response_class=HTMLResponse)
def logout_user():
    response = RedirectResponse(url='/', status_code=status.HTTP_302_FOUND)
    response.delete_cookie(key="main_input")
    return response


if __name__ == '__main__':
    pass
    # data_dict = db.select_last_costs('demo')
    # result = {}
    # for i in data_dict:
    #     result[i[0]] = f"{i[1]}, {convert_in_datetime(i[2])}"
    # data_dict = db._select_aliases('junkFood', 'demo')
    # print(get_category_name('мтс', data_dict))
    # print(result)
    # pprint(data_dict.get(max(data_dict.keys())))
    # pprint(sorted(data_dict.items())[-1])
    # pprint(data_dict)
    # result = db.get_all_categories('demo')
    # print(result)
    # for i in data_dict.values():
    #     print(i)
    # all_category = db.get_all_categories('demo')
    # ready_category = get_category_name('мтсt', all_category)
    # print(ready_category)
    # print(encode_cookies('60 кола'))
    # print(decode_cookies('NjAg0LrQvtC70LA='))
