import re


def get_category_name(find_item: str, data: dict) -> str:
    """ Определяем категорию по алиасу """
    for category, aliases in data.items():
        if find_item in aliases.split():
            return category


def pars_user_input(user_in: str):
    """ Проверка на длину и что первый аргумент число,
        если просто число вернет категорию "other"
        и description "без описания"
    """
    if not len(user_in) > 55 and all(map(str.isdigit, user_in.split()[0])):
        num = re.sub(r'\D', '', user_in.split()[0])
        alias = user_in.split()[1] if len(user_in.split()) > 1 else 'без_описания'
        description = ' '.join(user_in.split()[1:])\
            if len(' '.join(user_in.split()[1:])) > 0 else 'что-то...'
        return num, alias, description


if __name__ == '__main__':
    pass
