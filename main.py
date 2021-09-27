import re

cost = 't60 кола кола кола кола кола кола кола кола'
cost2 = '1200 учеба курс stepik'
cost1 = cost.split()


def get_category_name(find_item: str, data: dict) -> str:
    """ Определяем категорию по алиасу """
    for category, aliases in data.items():
        if find_item in aliases:
            return category


def pars_user_input(user_in: str):
    """ Проверка на длину и что первый аргумент число """
    if not len(user_in) > 55 and all(map(str.isdigit, user_in.split()[0])):
        num = re.sub(r'\D', '', user_in.split()[0])
        alias = user_in.split()[1]
        description = ' '.join(user_in.split()[1:])
        return num, alias, description


if __name__ == '__main__':
    pass

    # print(pars_user_input(cost2))
    sum_of_cost1, alias1, description1 = pars_user_input(cost2)
    print(sum_of_cost1)
    print(alias1)
    print(description1)

