import telebot
from currency_converter import CurrencyConverter
from telebot import types

bot = telebot.TeleBot('give code')

currency = CurrencyConverter()

user_amounts = {}


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, f"Hello, {message.from_user.username}! Please enter the amount for conversion:")
    bot.register_next_step_handler(message, summa)


def summa(message):
    try:
        amount = int(message.text.strip())
        if amount <= 0:
            bot.send_message(message.chat.id, 'Please enter an amount greater than 0.')
            bot.register_next_step_handler(message, summa)
            return
        user_amounts[message.chat.id] = amount

        markup = types.InlineKeyboardMarkup(row_width=2)
        btn1 = types.InlineKeyboardButton('USD/EUR', callback_data='usd/eur')
        btn2 = types.InlineKeyboardButton('EUR/USD', callback_data='eur/usd')
        btn3 = types.InlineKeyboardButton('USD/GBP', callback_data='usd/gbp')
        btn4 = types.InlineKeyboardButton('Other', callback_data='else')
        markup.add(btn1, btn2, btn3, btn4)
        bot.send_message(message.chat.id, "Choose a currency pair for conversion:", reply_markup=markup)

    except ValueError:
        bot.send_message(message.chat.id, 'Invalid format. Please enter a number.')
        bot.register_next_step_handler(message, summa)


@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    if call.data != 'else':
        values = call.data.upper().split('/')
        amount = user_amounts.get(call.message.chat.id, 0)
        result = currency.convert(amount, values[0], values[1])
        bot.send_message(call.message.chat.id, f"{amount} {values[0]} = {round(result, 2)} {values[1]}")
    else:
        bot.send_message(call.message.chat.id, 'Enter the currency pair (e.g., usd/eur):')
        bot.register_next_step_handler(call.message, enter)


def enter(message):
    try:
        values = message.text.upper().split('/')
        if len(values) != 2:
            raise ValueError('Invalid currency pair format')

        amount = user_amounts.get(message.chat.id, 0)
        result = currency.convert(amount, values[0], values[1])
        bot.send_message(message.chat.id, f"{amount} {values[0]} = {round(result, 2)} {values[1]}")

    except (ValueError, Exception) as e:
        bot.send_message(message.chat.id, f'Error: {str(e)}. Please enter the currency pair in the format "usd/eur".')
        bot.register_next_step_handler(message, enter)


bot.polling(none_stop=True)