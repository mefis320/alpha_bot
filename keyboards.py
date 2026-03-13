from aiogram.utils.keyboard import InlineKeyboardBuilder

def folder_kb(folders, files, folder_id, is_admin):
    kb = InlineKeyboardBuilder()

    # Папки
    for f in folders:
        kb.button(
            text=f"📂 {f[1]}",
            callback_data=f"open_{f[0]}"
        )
    # Файлы
    for file in files:
        kb.button(
            text=f"📄 {file[1]}",
            callback_data=f"file_{file[0]}"
        )

    # Админ кнопки: создать и переименовать
    if is_admin:
        kb.button(
            text="➕ Создать папку",
            callback_data=f"newfolder_{folder_id}"
        )
        kb.button(
            text="📥 Загрузить файл",
            callback_data=f"upload_{folder_id}"
        )
        # Переименовать папки
        for f in folders:
            kb.button(
                text=f"✏️ Переименовать {f[1]}",
                callback_data=f"renamefolder_{f[0]}"
            )
        # Переименовать файлы
        for file in files:
            kb.button(
                text=f"✏️ Переименовать {file[1]}",
                callback_data=f"renamefile_{file[0]}"
            )

    # Кнопка назад
    if folder_id is not None:
        kb.button(
            text="⬅ Назад",
            callback_data=f"back_{folder_id}"
        )

    # Главное меню
    kb.button(
        text="🏠 В меню",
        callback_data="menu"
    )

    kb.adjust(1)
    return kb.as_markup()