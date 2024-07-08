from aiogram import Router, types, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext  
from aiogram.fsm.state import State, StatesGroup
from .keyboards import START, profile_keyboard, pay_keyboard
import sqlite3
import logging
import asyncio

router = Router()

class UserState(StatesGroup):
    username = State()
    amount = State()
    user_id = State()
    support_query = State()
    feedback = State()

def save_user_to_db(username, user_id, amount=0.0):
    try:
        conn = sqlite3.connect('db.sqlite3')
        cursor = conn.cursor()
        cursor.execute('''
        INSERT OR REPLACE INTO user_profile (username, user_id, amount)
        VALUES (?, ?, ?)
        ''', (username, user_id, amount))
        conn.commit()
    except sqlite3.Error as e:
        logging.error(f"Error saving user to database: {e}")
    finally:
        conn.close()

def get_user_from_db(user_id):
    try:
        conn = sqlite3.connect('db.sqlite3')
        cursor = conn.cursor()
        cursor.execute('SELECT username, amount FROM user_profile WHERE user_id = ?', (user_id,))
        result = cursor.fetchone()
        return result
    except sqlite3.Error as e:
        logging.error(f"Error retrieving user from database: {e}")
        return None
    finally:
        conn.close()

def save_feedback_to_db(user_id, message):
    try:
        conn = sqlite3.connect('db.sqlite3')
        cursor = conn.cursor()
        cursor.execute('''
        INSERT INTO feedback (user_id, message)
        VALUES (?, ?)
        ''', (user_id, message))
        conn.commit()
    except sqlite3.Error as e:
        logging.error(f"Error saving feedback to database: {e}")
    finally:
        conn.close()

@router.message(CommandStart())
async def start_command(event: types.Message | CallbackQuery, state: FSMContext):
    user_id = event.from_user.id
    first_name = event.from_user.first_name

    await state.set_state(UserState.username)
    await state.update_data(username=first_name, user_id=user_id, amount="0")

    if isinstance(event, types.Message):
        await event.answer(f"👋 Привет, {first_name}! Ваш ID: {user_id}", reply_markup=START)
    elif isinstance(event, types.CallbackQuery):
        await event.message.answer(f"👋 Привет, {first_name}! Ваш ID: {user_id}", reply_markup=START)
        await event.answer()

    save_user_to_db(first_name, user_id)

@router.message(F.text == "Личный кабинет👤")
async def user_profile(message: types.Message, state: FSMContext):
    state_data = await state.get_data()
    user_id = state_data.get('user_id', 'Не указано')
    user_data = get_user_from_db(user_id)
    username, amount = user_data if user_data else ('Не указано', 'Не указано')

    await message.answer(
        text=f"Пользователь: {username}\nБаланс: {amount}\nID: {user_id}\n\nЕсли у вас нет профиля, создайте его",
        reply_markup=profile_keyboard
    )

@router.message(Command('profile'))
async def setting(message: types.Message, state: FSMContext):
    state_data = await state.get_data()
    user_id = state_data.get('user_id', 'Не указано')
    user_data = get_user_from_db(user_id)
    username, amount = user_data if user_data else ('Не указано', 'Не указано')

    await message.answer(text=f"ваш баланс: {amount}\nВаш ID: {user_id}", reply_markup=profile_keyboard)

@router.callback_query(F.data == 'back')
async def back_to_main_menu(callback_query: types.CallbackQuery, state: FSMContext):
    bot = callback_query.bot  
    await callback_query.answer()
    await bot.delete_message(callback_query.message.chat.id, callback_query.message.message_id)
    await start_command(callback_query, state)

@router.message(F.text == "Написать в поддержку🆘")
async def ask_for_support_query(message: types.Message, state: FSMContext):
    await message.answer("Напишите ваш вопрос или проблему:")
    await state.set_state(UserState.support_query)

    await asyncio.sleep(10)
    state_data = await state.get_data()
    if 'support_query' not in state_data:
        await message.answer("Почему вы не отправляете проблему, я готов вас выслушать, отправьте мне вопрос или проблему.")

@router.message(UserState.support_query)
async def receive_support_query(message: types.Message, state: FSMContext):
    await state.update_data(support_query=message.text)
    await message.answer("Ваше сообщение сохранено.")
    await state.clear()

@router.message(F.text == "Оставить отзыв")
async def ask_for_feedback(message: types.Message, state: FSMContext):
    await message.answer("Пожалуйста, оставьте свой отзыв:")
    await state.set_state(UserState.feedback)

@router.message(UserState.feedback)
async def receive_feedback(message: types.Message, state: FSMContext):
    state_data = await state.get_data()
    user_id = state_data.get('user_id')
    save_feedback_to_db(user_id, message.text)
    await message.answer("Ваш отзыв сохранен. Спасибо!")
    await state.clear()

@router.message(F.text == "Пополнить баланс Vozarys💰")
async def pay(message: types.Message, state: FSMContext):
    state_data = await state.get_data()
    user_id = state_data.get('user_id')
    user_data = get_user_from_db(user_id)
    username, amount = user_data if user_data else ('Не указано', 'Не указано')
    await message.answer(
        text=f"Ваш баланс: {amount}\nДля пополнения счета нажмите кнопку ниже",
        reply_markup=pay_keyboard  
    )
