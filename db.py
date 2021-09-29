import sqlite3


class SQLite:
    def __init__(self, database_file):
        """Подключение к БД и создание курсора соединения"""
        self.connection = sqlite3.connect(database_file,
                                          check_same_thread=False)
        self.cursor = self.connection.cursor()

    def create_tables(self, name_tab):
        """Создание таблиц"""
        with self.connection:
            self.cursor.execute(f"CREATE TABLE IF NOT EXISTS {name_tab} ("
                                "id INTEGER PRIMARY KEY AUTOINCREMENT,"
                                "`login` varchar UNIQUE ,"
                                "`password` TEXT );")

    def add_user(self, user_name, user_pasw):
        """Добавляю юзера и пароль"""
        with self.connection:
            self.cursor.execute("INSERT INTO users (`login`, `password`)"
                                " VALUES(?, ?);", (user_name, user_pasw))

    def get_user_data(self, user_name):
        """ Получаем имя пользователя """
        result = {}
        with self.connection:
            data = self.cursor.execute(
                "SELECT login, password "
                "FROM users "
                "WHERE login = ?", (user_name,)).fetchall()
            if not data:
                return None
            else:
                for i in data:
                    result["user"] = i[0]
                    result["password"] = i[1]
                return result

    def get_all_categories(self, user):
        """ Алиасы все категорий """
        result = {}
        with self.connection:
            data = self.cursor.execute(
                "SELECT codename, included "
                "FROM categories "
                "WHERE creator = ?", (user,)).fetchall()
            if not data:
                return None
            else:
                for i in data:
                    result[i[0]] = i[1]
                return result

    def select_sha(self, user_name):
        """ Извлечь все из нужной таблицы """
        with self.connection:
            result = self.cursor.execute(f'SELECT `password` '
                                         f'FROM users '
                                         f'WHERE `login` = "{user_name}"').fetchone()
            if not result:
                return None
            else:
                return "".join(result)

    def insert_cost(self, column_values: dict):
        """ Запись расхода """
        placeholders = ",".join("?" * len(column_values.keys()))
        columns = ', '.join(column_values.keys())
        values = tuple(column_values.values())
        with self.connection:
            self.cursor.execute(f"INSERT INTO costs "
                                f"({columns}) "
                                f"VALUES({placeholders});", values)

    def update_category(self, alias, user, category):
        """ добавить алиас в нужную категорию по определенному юзеру """
        with self.connection:
            self.cursor.execute(f'UPDATE categories '
                                f'SET included = included || " " || "{alias}" '
                                f'WHERE codename = "{category}" '
                                f'AND creator = "{user}"')

    def _select_aliases(self, category, user):
        """ Алиасы категории определенного юзера
        если нужно будет избежать повторов алиасов
        """
        with self.connection:
            result = self.cursor.execute(f"SELECT included "
                                         f"FROM categories "
                                         f"WHERE codename = '{category}' "
                                         f"AND creator = '{user}';").fetchone()
        return ''.join(result)


if __name__ == '__main__':
    pass
