import sqlite3


class SQLite:
    def __init__(self, database_file):
        """Подключение к БД и создание курсора соединения"""
        self.connection = sqlite3.connect(database_file, check_same_thread=False)
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
        """Извлечь все из нужной таблицы"""
        with self.connection:
            result = self.cursor.execute(f'SELECT `password` '
                                         f'FROM users '
                                         f'WHERE `login` = "{user_name}"').fetchone()
            if not result:
                return None
            else:
                return "".join(result)