import telebot
import re
import datetime
from telebot.types import Message, ReplyKeyboardMarkup
from telebot import apihelper
from creds import TOKEN, PROXY_SETTINGS, AUTH_USERS

apihelper.proxy = {'https': f"socks5h://{PROXY_SETTINGS['user']}:{PROXY_SETTINGS['pwd']}@{PROXY_SETTINGS['url']}:{PROXY_SETTINGS['port']}"}
bot = telebot.TeleBot(TOKEN)

user_dict = {}

ACCOUNTS = ('Личный', 'Общак')
CATEGORY = ('Продукты', 'Развлечения', 'Платежи', 'Подарки')


class Answer:
    def __init__(self, date):
        self.date = datetime.date.fromtimestamp(date).strftime('%d.%m.%Y')
        self.account = None
        self.category = None
        self.comment = ''
        self.amount = None

    def __repr__(self):
        return f'{self.date}, {self.account}, {self.category}, {self.comment}, {self.amount}'

    def fill_all(self, account, category, comment, amount):
        self.account = account
        self.category = category
        self.comment = comment
        self.amount = amount

def check_user(user_id):
    if user_id in AUTH_USERS:
        return True
    else:
        return False

# Обработка ввода данных через диалоги
@bot.message_handler(commands=["add_payment"])
def choose_account(message:Message):
    if check_user(message.from_user.id):
        chat_id = message.chat.id
        answ = Answer(message.date)
        user_dict[chat_id] = answ
        keyboard_Accounts = ReplyKeyboardMarkup(row_width=1, one_time_keyboard=True)
        for acc in ACCOUNTS:
            keyboard_Accounts.add(acc)
        msg = bot.reply_to(message, "Choose an Account", reply_markup=keyboard_Accounts)
        bot.register_next_step_handler(msg, choose_category)


def choose_category(message: Message):
    chat_id = message.chat.id
    answ = user_dict[chat_id]
    answ.account = message.text
    keyboard_Category = ReplyKeyboardMarkup(row_width=2, one_time_keyboard=True)
    for ctg in CATEGORY:
        keyboard_Category.add(ctg)
    msg = bot.reply_to(message, "Choose a Category", reply_markup=keyboard_Category)
    bot.register_next_step_handler(msg, enter_comment)


def enter_comment(message: Message):
    chat_id = message.chat.id
    answ = user_dict[chat_id]
    answ.category = message.text
    msg = bot.reply_to(message, "Enter a comment for payment")
    bot.register_next_step_handler(msg, enter_amount)


def enter_amount(message: Message):
    chat_id = message.chat.id
    answ = user_dict[chat_id]
    answ.comment = message.text
    msg = bot.reply_to(message, "Enter a amount of payment")
    bot.register_next_step_handler(msg, check_answer)


def check_answer(message: Message):
    amount = message.text
    amount_pattern = r'\d*[\,.]\d*'
    if not re.match(amount_pattern, amount):
        msg = bot.reply_to(message, "Amount should be a number. Enter an amount of payment")
        bot.register_next_step_handler(msg, check_answer)
        return
    chat_id = message.chat.id
    answ = user_dict[chat_id]
    answ.amount = float(amount.replace(',','.'))
    print(answ)

# Окончание обработки ввода данных платежа через диалог

# Ввод платежа одной строкой
@bot.message_handler(content_types=["text"])
def text_message_handler(message:Message):
    if check_user(message.from_user.id):
        message_to_utf = message.text.encode('utf').decode('utf')
        payment_pattern = r'(\w*);(\w*);(.*);([0-9]*[\.,][0-9]*)'
        result = re.findall(payment_pattern, message_to_utf)
        print(result)
        if result:
            answ = Answer(message.date)
            account_fm, category_fm,comment_fm, amount_fm = result[0]
            answ.fill_all(account_fm, category_fm,comment_fm, amount_fm)
            print(answ)
            bot.reply_to(message, answ)
        else:
            bot.reply_to(message, "Just text")


if __name__ == '__main__':
    bot.polling()

