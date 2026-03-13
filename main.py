import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

import database
import keyboards
from config import TOKEN, ADMINS

bot = Bot(TOKEN)
dp = Dispatcher()

class Form(StatesGroup):
    folder_name = State()
    file = State()
    file_name = State()
    rename_target = State()  # новое состояние для переименования

# -------------------
# Вспомогательная функция отображения папки
async def open_folder(message: types.Message, folder_id, user_id):
    folders = database.get_folders(folder_id)
    files = database.get_files(folder_id)
    await message.edit_text(
        "📂 Содержимое",
        reply_markup=keyboards.folder_kb(folders, files, folder_id, user_id in ADMINS)
    )

# -------------------
# Старт
@dp.message(Command("start"))
async def start(message: types.Message):
    folders = database.get_folders(None)
    files = []
    await message.answer(
        "📂 Главное меню",
        reply_markup=keyboards.folder_kb(folders, files, None, message.from_user.id in ADMINS)
    )

# -------------------
# Открытие папки
@dp.callback_query(F.data.startswith("open_"))
async def open_f(callback: types.CallbackQuery):
    folder_id = int(callback.data.split("_")[1])
    await open_folder(callback.message, folder_id, callback.from_user.id)
    await callback.answer()

# -------------------
# Создание новой папки
@dp.callback_query(F.data.startswith("newfolder_"))
async def new_folder(callback: types.CallbackQuery, state: FSMContext):
    parent = callback.data.split("_")[1]
    parent = None if parent == "None" else int(parent)
    await state.update_data(parent=parent)
    await callback.message.answer("✏️ Введи название папки")
    await state.set_state(Form.folder_name)
    await callback.answer()

@dp.message(Form.folder_name)
async def save_folder(message: types.Message, state: FSMContext):
    data = await state.get_data()
    database.add_folder(message.text, data["parent"])
    await state.clear()
    await message.answer("✅ Папка создана")

# -------------------
# Загрузка файла
@dp.callback_query(F.data.startswith("upload_"))
async def upload_start(callback: types.CallbackQuery, state: FSMContext):
    folder = callback.data.split("_")[1]
    folder = None if folder == "None" else int(folder)
    await state.update_data(folder=folder)
    await callback.message.answer("📥 Отправь файл")
    await state.set_state(Form.file)
    await callback.answer()

@dp.message(Form.file)
async def get_file(message: types.Message, state: FSMContext):
    file_id = None
    if message.document:
        file_id = message.document.file_id
    elif message.photo:
        file_id = message.photo[-1].file_id

    if not file_id:
        await message.answer("❌ Это не файл, попробуй ещё раз")
        return

    await state.update_data(file=file_id)
    await message.answer("✏️ Введи название файла")
    await state.set_state(Form.file_name)

@dp.message(Form.file_name)
async def save_file(message: types.Message, state: FSMContext):
    data = await state.get_data()
    database.add_file(data["folder"], data["file"], message.text)
    await state.clear()
    await message.answer("✅ Файл сохранён")

# -------------------
# Скачивание файла
@dp.callback_query(F.data.startswith("file_"))
async def send_file(callback: types.CallbackQuery):
    file_id = int(callback.data.split("_")[1])
    f = database.get_file(file_id)
    await callback.message.answer_document(f)
    await callback.answer()

# -------------------
# Кнопка Назад
@dp.callback_query(F.data.startswith("back_"))
async def go_back(callback: types.CallbackQuery):
    folder = callback.data.split("_")[1]
    folder = None if folder == "None" else int(folder)
    parent = None if folder is None else database.get_parent(folder)
    folders = database.get_folders(parent)
    files = database.get_files(parent)
    await callback.message.edit_text(
        "📂 Содержимое",
        reply_markup=keyboards.folder_kb(folders, files, parent, callback.from_user.id in ADMINS)
    )
    await callback.answer()

# -------------------
# Кнопка Главное меню
@dp.callback_query(F.data == "menu")
async def menu(callback: types.CallbackQuery):
    folders = database.get_folders(None)
    files = []
    await callback.message.edit_text(
        "📂 Главное меню",
        reply_markup=keyboards.folder_kb(folders, files, None, callback.from_user.id in ADMINS)
    )
    await callback.answer()

# -------------------
# Переименование папки
@dp.callback_query(F.data.startswith("renamefolder_"))
async def rename_folder_start(callback: types.CallbackQuery, state: FSMContext):
    folder_id = int(callback.data.split("_")[1])
    await state.update_data(rename_id=folder_id, rename_type="folder")
    await callback.message.answer("✏️ Введи новое название папки:")
    await state.set_state(Form.rename_target)
    await callback.answer()

# -------------------
# Переименование файла
@dp.callback_query(F.data.startswith("renamefile_"))
async def rename_file_start(callback: types.CallbackQuery, state: FSMContext):
    file_id = int(callback.data.split("_")[1])
    await state.update_data(rename_id=file_id, rename_type="file")
    await callback.message.answer("✏️ Введи новое название файла:")
    await state.set_state(Form.rename_target)
    await callback.answer()

# -------------------
# Сохранение нового имени
@dp.message(Form.rename_target)
async def rename_target_finish(message: types.Message, state: FSMContext):
    data = await state.get_data()
    new_name = message.text
    conn = database.connect()
    cur = conn.cursor()
    if data["rename_type"] == "folder":
        cur.execute("UPDATE folders SET name=? WHERE id=?", (new_name, data["rename_id"]))
        await message.answer(f"✅ Папка переименована в '{new_name}'")
    elif data["rename_type"] == "file":
        cur.execute("UPDATE files SET name=? WHERE id=?", (new_name, data["rename_id"]))
        await message.answer(f"✅ Файл переименован в '{new_name}'")
    conn.commit()
    conn.close()
    await state.clear()

# -------------------
# Запуск бота
async def main():
    database.init_db()
    print("Бот запущен...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())