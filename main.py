#!/usr/bin/python
from __future__ import print_function

import telebot
import db
import user_repository
import lab_repository
import question_repository
import answer_option_repository
import progress_repository
import answer_repository
import api
import util
from telebot import types

# Token бота
TOKEN = "1530147988:AAFrwGIZfNEC7sRWqs6Y"
# Пароль, используемый для смены прав пользователей
PASSWORD = "1530"

bot = telebot.TeleBot(TOKEN)
spreadsheetApi = api.init_google_spreadsheet_api()
driveApi = api.init_google_drive_api()
db = db.init_database_connection()


def pass_lab(message):
    if lab_repository.is_user_has_unfinished_labs(message.from_user.id):
        bot.send_message(message.chat.id, 'Чтобу начать новую лаборотную работу сначало завершите текущию')
    else:
        markup = types.ReplyKeyboardRemove(selective=False)
        bot.send_message(message.chat.id, "ID лабороторной работы", reply_markup=markup)
        bot.register_next_step_handler(message, process_pass_lab_step)


def process_pass_lab_step(message):
    if not lab_repository.is_lab_exist(message.text):
        bot.send_message(message.chat.id, "Лабороторная работа не существует")
        bot.register_next_step_handler(message, pass_lab)
        return
    if lab_repository.is_user_finished_lab(message.from_user.id, message.text):
        bot.send_message(message.chat.id, "Вы уже проходили эту работу")
        bot.register_next_step_handler(message, pass_lab)
    else:
        lab_repository.create_new_lab_for_user(message.from_user.id, message.text)
        current_question_id = progress_repository.get_current_question(message.from_user.id)[0]
        question = question_repository.get_question(current_question_id)
        if question[0][1] == 1:
            markup = types.ReplyKeyboardMarkup()
            for i in range(0, len(question[1])):
                markup.add(types.KeyboardButton(question[1][i][0]))
            bot.send_message(message.from_user.id, question[0][0] + ' Выберите ответ', reply_markup=markup)
        else:
            bot.send_message(message.from_user.id, question[0][0])


def answer(message):
    if lab_repository.is_user_has_unfinished_labs(message.from_user.id):
        current_question = progress_repository.get_current_question(message.from_user.id)
        answer_repository.create_answer(message.from_user.id, current_question[1], message.text)

        if progress_repository.set_next_question(message.from_user.id, current_question[1], current_question[0]):
            markup = types.ReplyKeyboardMarkup()

            spreadsheet_link = lab_repository.get_answer_spreadsheet_link(current_question[1])
            answers = answer_repository.get_answers(message.from_user.id, current_question[1])
            full_name = user_repository.get_user_full_name(message.from_user.id)

            answer_str = str(answers[0][0])
            for i in range(1, len(answers)):
                answer_str += ", " + str(answers[i][0])
            markup.add(types.KeyboardButton("Создать лабораторную работу"))
            markup.add(types.KeyboardButton("Пройти лабораторную работу"))
            bot.send_message(message.chat.id, 'Лабораторная работа завершена. Ваши ответы: ' + answer_str,
                             reply_markup=create_markup(message.from_user.id))

            sheet_info = spreadsheetApi.spreadsheets().get(spreadsheetId=spreadsheet_link).execute()["sheets"][0][
                "properties"]
            values = [
                [
                ],
            ]
            values[0].append(full_name)
            for i in range(0, len(answers)):
                values[0].append(answers[i][0])
            body = {
                'values': values
            }
            try:
                spreadsheetApi.spreadsheets().values().append(
                    spreadsheetId=spreadsheet_link, range=sheet_info["title"],
                    valueInputOption="RAW", body=body).execute()
            except Exception as e:
                print(e)
        else:
            current_question_id = progress_repository.get_current_question(message.from_user.id)[0]
            question = question_repository.get_question(current_question_id)
            if question[0][1] == 1:
                markup = types.ReplyKeyboardMarkup()
                for i in range(0, len(question[1])):
                    markup.add(types.KeyboardButton(question[1][i][0]))
                bot.send_message(message.chat.id, question[0][0] + ' Выберите ответ', reply_markup=markup)
            else:
                markup = types.ReplyKeyboardRemove(selective=False)
                bot.send_message(message.chat.id, question[0][0], reply_markup=markup)


def create_lab(message):
    markup = types.ReplyKeyboardRemove(selective=False)
    bot.send_message(message.chat.id,
                     'Ссылка на Google таблица с вопросами. Таблица должна быть доступна для всех у кого есть ссылка. '
                     'Ссылка вида: '
                     'https://docs.google.com/spreadsheets/d/1QmmRlZcEP_9ul_0iEXkivNYeGDjeZDXbPTC5G_Kjcf8/edit?usp'
                     '=sharing',
                     reply_markup=markup)
    bot.register_next_step_handler(message, process_question_spreadsheet_link_step)


def process_question_spreadsheet_link_step(message):
    try:
        if not util.is_url(message.text):
            bot.send_message(message.chat.id, 'Некорректная ссылка')
            bot.register_next_step_handler(new_message, create_lab(message))
        else:
            lab_id = lab_repository.create_lab()
            spreadsheet_id = util.extract_google_spreadsheet_id(message.text)
            sheet_info = spreadsheetApi.spreadsheets().get(spreadsheetId=spreadsheet_id).execute()["sheets"][0][
                "properties"]
            sheet = spreadsheetApi.spreadsheets().values().get(spreadsheetId=spreadsheet_id,
                                                               range=sheet_info["title"]).execute()["values"]
            for i in range(len(sheet)):
                question_id = question_repository.create_question(lab_id, sheet[i][0], len(sheet[i]) != 1)
                for j in range(1, len(sheet[i])):
                    answer_option_repository.create_answer(question_id, sheet[i][j])

            spreadsheet = {
                'properties': {
                    'title': "Ответы " + str(lab_id)
                }
            }
            new_spreadsheet_id = \
                spreadsheetApi.spreadsheets().create(body=spreadsheet, fields='spreadsheetId').execute()[
                    "spreadsheetId"]

            lab_repository.set_answer_spreadsheet_link(lab_id, new_spreadsheet_id)

            permission = {
                'type': 'anyone',
                'role': 'writer',
            }
            driveApi.permissions().create(fileId=new_spreadsheet_id, body=permission, fields='id').execute()

            bot.send_message(message.chat.id, "Лабораторная работа создана, ID: " + str(lab_id) +
                             "\nСсылка: https://docs.google.com/spreadsheets/d/" + str(new_spreadsheet_id),
                             reply_markup=create_markup(message.from_user.id))
    except Exception as e:
        print(e)
        bot.register_next_step_handler(message, create_lab(message))


@bot.message_handler(commands=['start'])
def start_message(message):
    if not user_repository.is_user_exist(message.from_user.id):
        bot.send_message(message.chat.id, "ФИО")
        bot.register_next_step_handler(message, process_register_link_step)
    else:
        bot.send_message(message.chat.id, 'Выберите действие', reply_markup=create_markup(message.from_user.id))


@bot.message_handler(commands=['grant'])
def grant_role_message(message):
    params = message.text.split(" ")
    print(params[0])
    print(params)
    if params[1] == PASSWORD:
        if user_repository.is_user_exist(params[2]):
            user_repository.grant_role(params[2])
            bot.send_message(message.chat.id, 'Пользователь повышен')
        else:
            bot.send_message(message.chat.id, 'Пользователь не найден')
    else:
        bot.send_message(message.chat.id, 'Неверный пароль')


@bot.message_handler(commands=['revoke'])
def revoke_role_message(message):
    params = message.text.split(" ")
    if params[1] == PASSWORD:
        if user_repository.is_user_exist(params[2]):
            user_repository.revoke_role(params[2])
            bot.send_message(message.chat.id, 'Пользователь понижен')
        else:
            bot.send_message(message.chat.id, 'Пользователь не найден')
    else:
        bot.send_message(message.chat.id, 'Неверный пароль')


def process_register_link_step(message):
    try:
        if not user_repository.is_user_exist(message.from_user.id):
            user_repository.create_user(message.from_user.id, message.text)
            bot.send_message(message.chat.id, "Ваш ID: " + str(message.from_user.id))
        bot.send_message(message.chat.id, 'Выберите действие', reply_markup=create_markup(message.from_user.id))
    except Exception as error:
        bot.register_next_step_handler(message, start_message)


@bot.message_handler(func=lambda m: True)
def new_message(message):
    if not user_repository.is_user_exist(message.from_user.id):
        bot.send_message(message.chat.id, "ФИО")
        bot.register_next_step_handler(message, process_register_link_step)
    else:
        role = user_repository.get_user_role(message.from_user.id)
        if message.text == 'Создать лабораторную работу' and role == 1:
            create_lab(message)
        elif message.text == 'Пройти лабораторную работу':
            pass_lab(message)
        else:
            answer(message)


def create_markup(user_id):
    role = user_repository.get_user_role(user_id)
    markup = types.ReplyKeyboardMarkup()
    if role == 0:
        markup.add(types.KeyboardButton("Пройти лабораторную работу"))
    else:
        markup.add(types.KeyboardButton("Создать лабораторную работу"))
        markup.add(types.KeyboardButton("Пройти лабораторную работу"))
    return markup


bot.enable_save_next_step_handlers(delay=2)
bot.load_next_step_handlers()
bot.polling(none_stop=True)
