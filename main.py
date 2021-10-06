import re

cost = 't60 кола кола кола кола кола кола кола кола'
cost2 = '1200 учеба курс stepik'
cost3 = '250 сыр'
cost4 = '250 кола жб'
cost5 = '250'


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

    # print(pars_user_input(cost2))
    for i in (cost, cost2, cost3, cost4, cost5):
        print(pars_user_input(i))
    # print(len(' '.join(cost3.split()[1:])))
    # print(cost3.split()[1:])
    # sum_of_cost1, alias1, description1 = pars_user_input(cost2)
    # print(sum_of_cost1)
    # print(alias1)
    # print(description1)


