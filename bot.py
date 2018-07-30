import time
import threading
import telebot
import config
import dbworker
import parser_api
from telebot import types

bot = telebot.TeleBot(config.token)


def dispatch(interval):
    while True:
        list_of_users = dbworker.get_status_for_dispatch()
        for user in list_of_users:
            result = dbworker.get_users_crypto(user[0])
            if not result:
                print('User', user[0], 'have empty list')
                continue
            bot.send_message(user[0], 'Криптовалюты которые вы отслеживаете:\n' +
                             show_crypto(result) + 'Вы получили это сообщения, так как подписаны на ежедневное '
                                                   'уведомление. Для отключения рассылки введите команду /off')
            dbworker.set_state(user[0], config.States.S_CLEAR_STATE.value)
        time.sleep(interval)


def show_crypto(message):
    result_message = ''
    for i in message:
        if i[4] is None:
            change24h = '-'
        else:
            change24h = str(i[4])
        result_message += 'Валюта: ' + i[2] + ' (' + i[1] + ')\nСтоимость: ' + str(i[3]) + \
                          '$\nИзменение за 24ч: ' + change24h + '%\n\n'
    return result_message


@bot.message_handler(commands=['start'])
def start_message(message):
    dbworker.set_status(message.chat.id, 1)
    result = dbworker.get_users_crypto(message.chat.id)
    if result is False:
        dbworker.set_state(message.chat.id, config.States.S_ADD_CRYPTO.value)
        bot.send_message(message.chat.id, 'Я бот для отслеживания цен на криптовалюту. '
                                          'Для начала работы введите название '
                                          'криптовалюты которую хотите отслеживать. Например "Bitcoin"')
    else:
        dbworker.set_state(message.chat.id, config.States.S_CLEAR_STATE.value)
        keyboard = types.InlineKeyboardMarkup()
        callback1 = types.InlineKeyboardButton(text='Добавить', callback_data='Add')
        callback2 = types.InlineKeyboardButton(text='Удалить', callback_data='Delete')
        callback3 = types.InlineKeyboardButton(text='Обновить', callback_data='Update')
        keyboard.add(callback3)
        keyboard.add(callback1, callback2)
        bot.send_message(message.chat.id, 'Криптовалюты которые вы отслеживаете:\n' +
                         show_crypto(result), reply_markup=keyboard)


@bot.message_handler(commands=['off'])  # Turn off notification for user
def off_notification(message):
    dbworker.set_status(message.chat.id, 0)
    dbworker.set_state(message.chat.id, config.States.S_CLEAR_STATE.value)
    bot.send_message(message.chat.id, 'Уведомления о изменении отключены. Для включения введите команду /on')


@bot.message_handler(commands=['on'])  # Turn on notification for user
def on_notification(message):
    dbworker.set_status(message.chat.id, 1)
    dbworker.set_state(message.chat.id, config.States.S_CLEAR_STATE.value)
    bot.send_message(message.chat.id, 'Уведомления о изменении включены. Для отключения введите команду /off')


@bot.message_handler(commands=['menu'])  # Show menu for user
def show_menu(message):
    dbworker.set_state(message.chat.id, config.States.S_CLEAR_STATE.value)
    keyboard = types.InlineKeyboardMarkup()
    callback1 = types.InlineKeyboardButton(text='Вывести портфель', callback_data='Show crypto')
    callback2 = types.InlineKeyboardButton(text='Добавить', callback_data='Add')
    callback3 = types.InlineKeyboardButton(text='Удалить', callback_data='Delete')
    keyboard.add(callback1)
    keyboard.add(callback2, callback3)
    if dbworker.get_status(message.chat.id) is True:
        status = ['включены', 'отключения', '/off']
    else:
        status = ['выключены', 'включения', '/on']
    bot.send_message(message.chat.id, 'Уведомления о изменении ' + status[0] + ', для ' +
                     status[1] + ' используйте команду ' + status[2], reply_markup=keyboard)


@bot.message_handler(func=lambda message: (message.text and
                                           dbworker.get_state(message.chat.id) == config.States.S_ADD_CRYPTO.value))
def add_crypto(message):
    #  Поиск криптовалюты в базе данных. Если найдено, то добавляем пользователю криптовалюту в портфель и выводим:
    db_result = dbworker.add_crypto(message.chat.id, message.text)
    if db_result is False:
        bot.send_message(message.chat.id, 'К сожалению такая криптовалюта не найдена. Возможно вы допустили ошибку, '
                                          'попробуйте еще раз.')
    else:
        keyboard = types.InlineKeyboardMarkup()
        callback1 = types.InlineKeyboardButton(text='Вывести портфель', callback_data='Show crypto')
        callback2 = types.InlineKeyboardButton(text='Добавить', callback_data='Add')
        callback3 = types.InlineKeyboardButton(text='Удалить', callback_data='Delete')
        keyboard.add(callback1)
        keyboard.add(callback2, callback3)
        bot.send_message(message.chat.id, db_result, reply_markup=keyboard)
        dbworker.set_state(message.chat.id, config.States.S_CLEAR_STATE.value)


@bot.message_handler(func=lambda message: (message.text and
                                           dbworker.get_state(message.chat.id) == config.States.S_DELETE_CRYPTO.value))
def delete_crypto(message):
    #  Поиск криптовалюты в базе данных. Если найдено, то удаляем у пользователя из портфеля валюту и выводим:
    db_result = dbworker.delete_crypto(message.chat.id, message.text)
    if db_result is False:
        bot.send_message(message.chat.id, 'К сожалению такая криптовалюта не найдена. Или вы её не отслеживаете, '
                                          'попробуйте еще раз.')
    else:
        keyboard = types.InlineKeyboardMarkup()
        callback1 = types.InlineKeyboardButton(text='Вывести портфель', callback_data='Show crypto')
        callback2 = types.InlineKeyboardButton(text='Добавить', callback_data='Add')
        callback3 = types.InlineKeyboardButton(text='Удалить', callback_data='Delete')
        keyboard.add(callback1)
        keyboard.add(callback2, callback3)
        bot.send_message(message.chat.id, db_result, reply_markup=keyboard)
        dbworker.set_state(message.chat.id, config.States.S_CLEAR_STATE.value)


@bot.callback_query_handler(func=lambda call: (True and call.data == 'Show crypto'))
def callback_inline(call):
    #  Запрашиваем у БД какие криптовалюты есть у пользователя, потом по этим id делаем join, поулчаем данные
    result = dbworker.get_users_crypto(call.message.chat.id)
    keyboard = types.InlineKeyboardMarkup()
    callback1 = types.InlineKeyboardButton(text='Добавить', callback_data='Add')
    callback2 = types.InlineKeyboardButton(text='Удалить', callback_data='Delete')
    callback3 = types.InlineKeyboardButton(text='Обновить', callback_data='Update')
    if result is False:
        keyboard.add(callback1)
        bot.send_message(call.message.chat.id, 'Вы не отслеживаете ни одной криптовалюты', reply_markup=keyboard)
    else:
        keyboard.add(callback3)
        keyboard.add(callback1, callback2)
        bot.send_message(call.message.chat.id, 'Криптовалюты которые вы отслеживаете:\n' +
                         show_crypto(result), reply_markup=keyboard)
    dbworker.set_state(call.message.chat.id, config.States.S_CLEAR_STATE.value)


@bot.callback_query_handler(func=lambda call: (True and call.data == 'Update'))
def callback_inline(call):
    #  Запрашиваем у БД какие криптовалюты есть у пользователя, потом по этим id делаем join, поулчаем данные
    result = dbworker.get_users_crypto(call.message.chat.id)
    keyboard = types.InlineKeyboardMarkup()
    callback1 = types.InlineKeyboardButton(text='Добавить', callback_data='Add')
    callback2 = types.InlineKeyboardButton(text='Удалить', callback_data='Delete')
    callback3 = types.InlineKeyboardButton(text='Обновить', callback_data='Update')
    if result is False:
        keyboard.add(callback1)
        bot.send_message(call.message.chat.id, 'Вы не отслеживаете ни одной криптовалюты', reply_markup=keyboard)
    else:
        keyboard.add(callback3)
        keyboard.add(callback1, callback2)
        bot.send_message(call.message.chat.id, 'Криптовалюты которые вы отслеживаете:\n' +
                         show_crypto(result), reply_markup=keyboard)
    dbworker.set_state(call.message.chat.id, config.States.S_CLEAR_STATE.value)


@bot.callback_query_handler(func=lambda call: (True and call.data == 'Add'))
def callback_inline(call):
    dbworker.set_state(call.message.chat.id, config.States.S_ADD_CRYPTO.value)
    bot.send_message(call.message.chat.id, 'Введите название криптовалюты')


@bot.callback_query_handler(func=lambda call: (True and call.data == 'Delete'))
def callback_inline(call):
    dbworker.set_state(call.message.chat.id, config.States.S_DELETE_CRYPTO.value)
    bot.send_message(call.message.chat.id, 'Введите название криптовалюты которую хотите удалить')


if __name__ == '__main__':
    t = threading.Thread(target=parser_api.update)
    t2 = threading.Thread(target=dispatch, args=(86400,))
    t.daemon = True
    t2.daemon = True
    t.start()
    t2.start()
    while True:
        try:
            bot.polling()
        except Exception as e:
            print(e)
            time.sleep(5)
            continue
