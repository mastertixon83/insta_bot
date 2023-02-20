from psycopg2 import sql
class DBCommands():
    ###  Добавление нового пользователя с рефералом и без ###
    ADD_NEW_USER = "INSERT INTO users (username, nickname, url, follow) VALUES (%s, %s, %s, %s, %s) RETURNING id"
    ADD_NEW_USER_TUPLE = "INSERT INTO users (username, nickname, url) VALUES (%s, %s, %s) RETURNING id"
    GET_USERS = "SELECT * FROM users WHERE follow = %s ORDER BY id"
    UPDATE_FOLLOW_STATUS = "UPDATE users SET follow = true WHERE id = %s"
    UPDATE_UNFOLLOW_STATUS = "UPDATE users SET unfollow = true WHERE id = %s"

    ###  Добавление нового пользователя с рефералом и без ###

    def add_new_user(self, username, nickname, url, follow=False, followers_count=0):

        args = username, nickname, url, follow, followers_count
        command = self.ADD_NEW_USER

        return command, args

    def add_new_user_tuple(self, followers):
        data_tuple = [
            tuple(d.values()) + (float('nan'),) * (len(max(followers, key=len)) - len(d))
            for d in followers
        ]
        args = data_tuple
        command = (
            sql.SQL(
                'INSERT INTO users (username, nickname, url) VALUES {}')
            .format(sql.SQL(',').join(map(sql.Literal, data_tuple))
                    )
        )
        return command

    def get_users(self, follow):
        command = self.GET_USERS
        args = (follow,)

        return command, args

    def update_user_follow_status(self, id):
        command = self.UPDATE_FOLLOW_STATUS
        args = (id,)

        return command, args


    def update_user_unfollow_status(self, id):
        command = self.UPDATE_UNFOLLOW_STATUS
        args = (id,)

        return command, args
