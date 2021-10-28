import hashlib
import hmac
import base64
import json
from typing import Optional, Union

from fastapi import FastAPI, Form, Cookie, Request, status
from fastapi.staticfiles import StaticFiles
from fastapi.param_functions import Body
from fastapi.responses import Response, HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from db import SQLite
from main import pars_user_input, get_category_name
from make_data import make_date, ru_date_unix
from config import (
    PASSWORD_SALT,
    SECRET_KEY,
    DB_NAME
)

db = SQLite(DB_NAME)

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
        username = base64.b64decode(username_base64.encode()).decode()
        valid_sign = sign_data(username)
        if hmac.compare_digest(valid_sign, sign):
            return username
    except Exception:
        return


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

    # 'count=3 - кол-во крайних записей'
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
    """ Добавление алиасов """
    valid_username = get_username_from_signed_string(username)
    sum_of_cost, alias, description = pars_user_input(
        decode_cookies(main_input))

    db.update_category(alias, valid_username, choice)
    data_from_category = db.get_all_categories(valid_username)
    ready_category = get_category_name(alias, data_from_category)
    db.insert_cost({'sum_of_money_co': sum_of_cost,
                    'descrip_co': description,
                    'category': ready_category,
                    'who_spend': valid_username,
                    'view_date': ru_date_unix()[1],
                    'created': make_date()})
    context = {
        "request": request,
        "added_alias": True,
        "not_alias": False,
        'name_user': valid_username,
        'main_input': f'То что ввели: {sum_of_cost} {alias} {description}',
        'add_info': {'sum_of_cost': sum_of_cost,
                     'description': description,
                     'alias': alias,
                     'category': choice},
    }

    response = tem.TemplateResponse('add.html', context)
    return response


@app.post('/input')
def update_table(data: dict = Body(...)):
    """ Изменение суммы расхода """
    try:
        int(data['cost'])
        db.update_cost(data)
        return Response(
            json.dumps({
                'success': True,
                'message': 'Запись изменена!!'
            }),
            media_type='application/json')
    except ValueError:
        return Response(
            json.dumps({
                'success': False,
                'message': 'Некорректное число!'
            }),
            media_type='application/json')


@app.get("/items/", response_class=HTMLResponse)
def read_item(request: Request,
              username: Optional[str] = Cookie(default=None),
              skip: Union[int, str] = 0,
              limit: Union[int, str] = 5):
    """ Редактирование / Удаление / отображение расходов """
    valid_username = get_username_from_signed_string(username)
    try:
        limit = skip + limit
        all_costs, count_costs = db.select_all_costs(valid_username, start=skip,
                                                     end=limit)
        context = {
            "request": request,
            "user": valid_username,
            "all_costs": all_costs,
            "count_costs": count_costs,
            "skip_more": skip + 5,
            "skip_less": skip - 5,
        }
        response = tem.TemplateResponse('edit.html', context)
        return response
    except Exception as e:
        return f'Wrong: {e}'


@app.post('/main', response_class=HTMLResponse)
def private_page(request: Request,
                 username: Optional[str] = Cookie(default=None),
                 main_input: str = Form(...)):
    """ Главная страница записи """
    valid_username = get_username_from_signed_string(username)
    data_from_category = db.get_all_categories(valid_username)
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

    else:  # если невалидное число
        context = {
            "request": request,
            "name_user": valid_username,
            "incorrect_input": True,
            "message": main_input}

        response = tem.TemplateResponse('main.html', context)
        return response


@app.post('/del', response_class=HTMLResponse)
def delete_last_cost(request: Request,
                     id_cost: str = Form(...),
                     username: Optional[str] = Cookie(default=None),
                     ):
    """ Удаление только что записанного расхода """
    cost_id, description = id_cost.split(', ')
    valid_username = get_username_from_signed_string(username)
    db.delete_last_cost(cost_id)
    context = {
        "request": request,
        "name_user": valid_username,
        "delete_cost": True,
        "report": description}

    response = tem.TemplateResponse('main.html', context)
    return response


@app.post('/del_cost', response_class=HTMLResponse)
def delete_selected_cost(cost_id: str = Form(...)):
    """ Удаление записи расхода из выборки """
    db.delete_last_cost(int(cost_id))
    response = RedirectResponse(url='/items/', status_code=status.HTTP_302_FOUND)
    return response


@app.get('/logout', response_class=HTMLResponse)
def logout_user():
    response = RedirectResponse(url='/', status_code=status.HTTP_302_FOUND)
    response.delete_cookie(key="username")
    response.delete_cookie(key="main_input")
    return response


@app.get('/resume', response_class=HTMLResponse)
def continue_record():
    """ Выход после добавления алиаса """
    response = RedirectResponse(url='/', status_code=status.HTTP_302_FOUND)
    response.delete_cookie(key="main_input")
    return response


if __name__ == '__main__':
    pass
