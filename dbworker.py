import sqlite3
import config


def set_state(user_id, state):
    conn = sqlite3.connect(config.database)
    cursor = conn.cursor()
    cursor.execute('UPDATE users_state SET state="%s" WHERE user_id="%s"' % (state, str(user_id)))
    if conn.total_changes == 0:
        cursor.execute('INSERT INTO users_state (user_id, state) VALUES ("%s", "%s")' % (str(user_id), str(state)))
    conn.commit()
    cursor.close()
    conn.close()


def get_state(user_id):
    conn = sqlite3.connect(config.database)
    cursor = conn.cursor()
    cursor.execute('SELECT state FROM users_state WHERE user_id="%s"' % (str(user_id)))
    result = cursor.fetchone()
    cursor.close()
    conn.close()
    return False if result is None else result[0]


def set_status(user_id, status):
    conn = sqlite3.connect(config.database)
    cursor = conn.cursor()
    cursor.execute('SELECT status FROM users_status WHERE user_id="%s"' % str(user_id))
    check = cursor.fetchone()
    if check is None:  # if record in db is empty, make a new record
        cursor.execute('INSERT INTO users_status (user_id, status) VALUES ("%s", "%s")' % (str(user_id), str(status)))
        conn.commit()
        cursor.close()
        conn.close()
        return True
    else:  # Just change status
        cursor.execute('UPDATE users_status SET status="%s" WHERE user_id="%s"' % (str(status), str(user_id)))
        conn.commit()
        cursor.close()
        conn.close()
        return True


def get_status_for_dispatch():
    conn = sqlite3.connect(config.database)
    cursor = conn.cursor()
    cursor.execute('SELECT user_id FROM users_status WHERE status="1"')
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    return result


def get_status(user_id):
    conn = sqlite3.connect(config.database)
    cursor = conn.cursor()
    cursor.execute('SELECT status FROM users_status WHERE user_id="%s"' % str(user_id))
    check = cursor.fetchone()
    cursor.close()
    conn.close()
    return True if check[0] == 1 else False


def get_users_crypto(user_id):
    conn = sqlite3.connect(config.database)
    cursor = conn.cursor()
    cursor.execute('SELECT users_crypto.user_id, crypto_json.symbol, crypto_json.name, '
                   'crypto_json.price, crypto_json.percent_change_24h'
                   ' FROM users_crypto INNER JOIN crypto_json ON users_crypto.crypto_id=crypto_json.id '
                   'WHERE users_crypto.user_id="%s" ORDER BY crypto_json.id' % str(user_id))
    result = cursor.fetchall()
    cursor.close()
    conn.close()
    print(result)
    return False if not result else result


def add_crypto(user_id, text):
    conn = sqlite3.connect(config.database)
    cursor = conn.cursor()
    cursor.execute('SELECT id, name FROM crypto_json WHERE upper(name)="%s" OR upper(symbol) = "%s"'
                   % (text.upper(), text.upper()))
    result = cursor.fetchone()
    if result is None:
        cursor.close()
        conn.close()
        return False
    else:
        cursor.execute('SELECT user_id FROM users_crypto WHERE crypto_id="%s" AND user_id="%s"'
                               % (str(result[0]), str(user_id)))
        check = cursor.fetchone()
        if check is not None:
            cursor.close()
            conn.close()
            return 'Такая валюта уже у вас в протфеле'
        else:
            cursor.execute('INSERT INTO users_crypto (user_id, crypto_id) VALUES ("%s", "%s")'
                           % (str(user_id), result[0]))
            conn.commit()
            cursor.close()
            conn.close()
            return 'Криптовалюта ' + result[1] + ' добавлена в ваш портфель'


def delete_crypto(user_id, text):
    conn = sqlite3.connect(config.database)
    cursor = conn.cursor()
    cursor.execute('SELECT users_crypto.user_id, crypto_json.id, crypto_json.symbol, crypto_json.name '
                   'FROM users_crypto '
                   'INNER JOIN crypto_json ON users_crypto.crypto_id=crypto_json.id WHERE users_crypto.user_id="%s" '
                   'AND (upper(crypto_json.symbol)="%s" OR upper(crypto_json.name)="%s")'
                   % (str(user_id), text.upper(), text.upper()))
    result = cursor.fetchone()
    if result is None:
        cursor.close()
        conn.close()
        return False
    else:
        cursor.execute('DELETE FROM users_crypto WHERE user_id="%s" AND crypto_id="%s"' % (str(user_id), result[1]))
        conn.commit()
        cursor.close()
        conn.close()
        print(result)
        return 'Криптовалюта ' + result[3] + ' удалена из отслеживаемых'
