import asyncpg as aspg


class DBConnect:
    def __init__(self, database, user, password, host) -> None:
        self.db = database
        self.user = user
        self.password = password
        self.host = host

    async def connect(self):
        try:
            conn = await aspg.connect(database=self.db,
                                    user=self.user,
                                    password=self.password,
                                    host=self.host)
        except Exception as e:
            print(f"Ошибка при подключении к базе данных: {e}")
        return conn