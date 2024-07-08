from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, WebAppInfo

START = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Написать в поддержку🆘"),
            KeyboardButton(text="Пополнить баланс Vozarys💰"),
        ],
        [
            KeyboardButton(text="Личный кабинет👤"),
            KeyboardButton(text="Оставить отзыв")
        ]
    ],
    resize_keyboard=True,
    input_field_placeholder="Выберите один каталог"
)

profile_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[[
        InlineKeyboardButton(
            text="Перейти в профиль👤",
            web_app=WebAppInfo(url="https://x.com/home")
        ),
        InlineKeyboardButton(text="вернуться в главное меню🔙", callback_data="back")
    ]]
)

pay_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="Oплатить",
                web_app=WebAppInfo(url="https://x.com/home")
            ),
            InlineKeyboardButton(
                text="вернуться в главное меню🔙",
                callback_data="back"
            )
        ]
    ]
)
