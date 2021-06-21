import db

database = db.init_database_connection()


def get_user_role(user_id):
    sql = 'SELECT role FROM "user" WHERE id = (%s) LIMIT 1'
    value = [user_id]
    cursor = database.cursor()
    cursor.execute(sql, value)
    result = cursor.fetchall()
    database.commit()
    return result[0][0]


def is_user_exist(user_id):
    sql = 'SELECT full_name, role FROM "user" WHERE id = (%s) LIMIT 1'
    value = [user_id]
    cursor = database.cursor()
    cursor.execute(sql, value)
    result = cursor.fetchall()
    database.commit()
    return len(result) != 0


def grant_role(user_id):
    sql = 'UPDATE "user" SET role = 1 WHERE id = (%s)'
    value = [user_id]
    cursor = database.cursor()
    cursor.execute(sql, value)
    database.commit()


def revoke_role(user_id):
    sql = 'UPDATE "user" SET role = 0 WHERE id = (%s)'
    value = [user_id]
    cursor = database.cursor()
    cursor.execute(sql, value)
    database.commit()


def create_user(user_id, full_name):
    sql = 'INSERT INTO "user" (id, full_name) VALUES (%s, %s)'
    values = [user_id, full_name]
    cursor = database.cursor()
    cursor.execute(sql, values)
    database.commit()


def get_user_full_name(user_id):
    sql = 'SELECT full_name FROM "user" WHERE id = (%s) LIMIT 1'
    value = [user_id]
    cursor = database.cursor()
    cursor.execute(sql, value)
    result = cursor.fetchall()
    database.commit()
    return result[0][0]
