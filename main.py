import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from datetime import datetime, timedelta
import json
import os
from pathlib import Path

# Global o'zgaruvchilar
TOKEN = "7598783058:AAEDN0RnwQc7biR3QbQdJxDeqrzG-vMDEzg"
bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)



 

admin_ids = {5921153725, 6446277435}
blocked_user_ids = set()
user_data = {}
start_message = "Xush kelibsiz!"
DATA_FILE = "user_data.json"

BASE_PATH = Path(__file__).parent / "rasmlaar"  # main.py bilan bir darajadagi "rasmlaar" papkasi

def load_data():
    global user_data, blocked_user_ids
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)
            user_data = {int(k): v for k, v in data.get("users", {}).items()}
            blocked_user_ids = set(data.get("blocked", []))
    return user_data.keys()

def save_data():
    with open(DATA_FILE, "w", encoding="utf-8") as file:
        json.dump({
            "users": {str(k): v for k, v in user_data.items()},
            "blocked": list(blocked_user_ids)
        }, file, ensure_ascii=False, indent=4)

main_menu = ReplyKeyboardMarkup(resize_keyboard=True)
main_menu.row(KeyboardButton("MyGov'dan ro‘yxatdan o‘tish 📲")) 
main_menu.row(KeyboardButton("Subsidiya👍"), KeyboardButton("Oila va bolalar👨‍👩‍👧"))
main_menu.row(KeyboardButton("Ijtimoiy himoya 🛡️"), KeyboardButton("Ma'lumotnomalar 📋"))
main_menu.row(KeyboardButton("Pensiya 👴👵"), KeyboardButton("Ta'lim 📚"))
main_menu.row(KeyboardButton("Yoshlar 👩‍💼👨‍💼"), KeyboardButton("Soliq 💸"))

def get_options(section):
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("Bo‘lim haqida", callback_data=f"{section}_info"))
    keyboard.add(InlineKeyboardButton("Xizmat narxi va vaqti", callback_data=f"{section}_cost_time"))
    keyboard.add(InlineKeyboardButton("Kerakli hujjatlar", callback_data=f"{section}_docs"))
    keyboard.add(InlineKeyboardButton("Bosh menyuga qaytish", callback_data="back_to_main"))
    return keyboard

def get_back_button(section):
    keyboard = InlineKeyboardMarkup()
    keyboard.row(
        InlineKeyboardButton("Orqaga qaytish", callback_data=f"back_to_{section}"),
        InlineKeyboardButton("Bosh menyuga qaytish", callback_data="back_to_main")
    )
    return keyboard

@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    user_id = message.from_user.id
    if user_id not in user_data:
        user_data[user_id] = {"join_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
        save_data()
    await message.reply(start_message, reply_markup=main_menu)

@dp.message_handler(lambda message: message.text in ["Subsidiya👍", "Oila va bolalar👨‍👩‍👧", "Ijtimoiy himoya 🛡️", "Ma'lumotnomalar 📋", 
                                                    "Pensiya 👴👵", "Ta'lim 📚", "Yoshlar 👩‍💼👨‍💼", "Soliq 💸", "MyGov'dan ro‘yxatdan o‘tish 📲"])
async def section_menu(message: types.Message):
    section_map = {
        "Subsidiya👍": ("subsidy", "1.jpg"),
        "Oila va bolalar👨‍👩‍👧": ("family", "2.jpg"),
        "Ijtimoiy himoya 🛡️": ("social", "3.jpg"),
        "Ma'lumotnomalar 📋": ("certificates", "4.jpg"),
        "Pensiya 👴👵": ("pension", "5.jpg"),
        "Ta'lim 📚": ("education", "6.jpg"),
        "Yoshlar 👩‍💼👨‍💼": ("youth", "7.jpg"),
        "Soliq 💸": ("tax", "8.jpg"),
        "MyGov'dan ro‘yxatdan o‘tish 📲": ("mygov", "9.jpg")
    }
    section_key, photo_name = section_map[message.text]
    photo_path = BASE_PATH / photo_name
    caption = f"{message.text} haqida ma'lumot olish uchun quyidagi tugmalardan birini tanlang:"
    
    try:
        with open(photo_path, 'rb') as photo:
            await bot.send_photo(
                chat_id=message.chat.id,
                photo=photo,
                caption=caption,
                reply_markup=get_options(section_key)
            )
    except FileNotFoundError:
        await message.reply(f"Kechirasiz, rasm topilmadi! Yo‘l: {photo_path}")

@dp.callback_query_handler(lambda c: c.data.startswith(("subsidy_", "family_", "social_", "certificates_", "pension_", "education_", "youth_", "tax_", "mygov_", "back_to_")) or c.data == "back_to_main")
async def process_section_callback(callback_query: types.CallbackQuery):
    data = callback_query.data
    chat_id = callback_query.message.chat.id
    message_id = callback_query.message.message_id

    if data == "back_to_main":
        await bot.delete_message(chat_id=chat_id, message_id=message_id)
        await bot.send_message(chat_id=chat_id, text=start_message, reply_markup=main_menu)
        await callback_query.answer()
        return

    section = data.split("_")[0] if "back_to_" not in data else data.split("_")[2]
    photo_map = {
        "subsidy": "1.jpg",
        "family": "2.jpg",
        "social": "3.jpg",
        "certificates": "4.jpg",
        "pension": "5.jpg",
        "education": "6.jpg",
        "youth": "7.jpg",
        "tax": "8.jpg",
        "mygov": "9.jpg"
    }
    photo_path = BASE_PATH / photo_map[section]

    # Matnlar uchun lug‘atlar
    info_captions = {
        "subsidy": "*Subsidiya haqida umumiy ma'lumot*\nSubsidiya — davlat yordami, uy-joy, tadbirkorlik yoki ijtimoiy ehtiyojlar uchun beriladi.\nQayerdan olish mumkin? MyGov portali orqali ariza berasiz.",
        "family": "*Oila va bolalar subsidiyasi*\nKam ta’minlangan oilalarga bolalar uchun nafaqa va moddiy yordam beriladi.\nKimlar oladi? Oylik daromadi past oilalar, Ijtimoiy himoya yagona reestridagilar, 18 yoshgacha farzandi bor oilalar.",
        "social": "*Ijtimoiy himoya bo‘limi*\nEhtiyojmandlarga davlat yordami: nafaqa yoki bir martalik yordam.\nKimlar uchun? Kam ta’minlanganlar, nogironligi borlar, pensionerlar.",
        "certificates": "*Ma'lumotnomalar bo‘limi*\nRasmiy hujjatlar: daromad, yashash joyi yoki oilaviy holat haqida.\nNima uchun kerak? Subsidiya olish, ishga kirish.",
        "pension": "*Pensiya bo‘limi*\nYoshlilar, nogironlar uchun nafaqa.\nKimlar oladi? 60 yosh (erkaklar), 55 yosh (ayollar), nogironlik guruhiga ega shaxslar.",
        "education": "*Ta'lim bo‘limi*\nTa'lim xizmatlari: stipendiya, attestat olish.\nKimlar uchun? Talabalar, o‘quvchilar.",
        "youth": "*Yoshlar bo‘limi*\nYoshlarga yordam: grantlar, tadbirkorlik.\nKimlar uchun? Talabalar, ishsiz yoshlar.",
        "tax": "*Soliq bo‘limi*\nSoliq xizmatlari: qarz tekshirish, STIR olish.\nKimlar uchun? Jismoniy shaxslar, tadbirkorlar.",
        "mygov": "*MyGov'dan ro‘yxatdan o‘tish haqida*\nMyGov — davlat xizmatlarini onlayn olish uchun yagona portal. Ro‘yxatdan o‘tish orqali subsidiya, hujjatlar va boshqa xizmatlarga ariza berish mumkin.\nKimlar uchun? O‘zbekiston fuqarolari.\nRo'yxatdan o'tish uchun: my.gov.uz"
    }
    cost_time_captions = {
        "subsidy": "*Xizmat narxi va vaqti*\nNarxi: Ko‘pincha bepul, subsidiya turiga qarab bank xarajatlari bo‘lishi mumkin.\nVaqti: Ariza tekshiruvi 7-15 ish kuni, tez bo‘lsa 3-10 kun.",
        "family": "*Xizmat narxi va vaqti*\nNarxi: Bepul — ariza uchun to‘lov yo‘q.\nVaqti: Ariza tekshiruvi 10-15 ish kuni, tez bo‘lsa 7 kun.",
        "social": "*Xizmat narxi va vaqti*\nNarxi: Bepul.\nVaqti: Ariza tekshiruvi 10-15 kun, tez tasdiqlash 5-7 kun.",
        "certificates": "*Xizmat narxi va vaqti*\nNarxi: Ko‘pincha bepul, pullik bo‘lsa 30-150 ming so‘m.\nVaqti: Onlayn 1-3 kun, standart 5-7 kun.",
        "pension": "*Xizmat narxi va vaqti*\nNarxi: Bepul.\nVaqti: Ariza tekshiruvi 10-15 kun, tez tasdiqlash 5-7 kun.",
        "education": "*Xizmat narxi va vaqti*\nNarxi: Ko‘pincha bepul, pullik bo‘lsa 30-150 ming so‘m.\nVaqti: Ariza tekshiruvi 3-10 kun, tez xizmat 1-3 kun.",
        "youth": "*Xizmat narxi va vaqti*\nNarxi: Bepul.\nVaqti: Ariza tekshiruvi 5-15 kun, tez tasdiqlash 3-7 kun.",
        "tax": "*Xizmat narxi va vaqti*\nNarxi: Bepul, pullik bo‘lsa 30-150 ming so‘m.\nVaqti: Tez xizmat 1-3 kun, standart 5-10 kun.",
        "mygov": "*Xizmat narxi va vaqti*\nNarxi: Ro‘yxatdan o‘tish bepul, internet va qurilma xarajatlari bundan mustasno.\nVaqti: Onlayn ro‘yxatdan o‘tish 5-10 daqiqa, tasdiqlash 1-2 daqiqa."
    }
    docs_captions = {
        "subsidy": "*Kerakli hujjatlar*\n- Pasport/ID\n- Ariza (onlayn to‘ldiriladi)\n- Daromad ma’lumoti (ba’zan avtomatik tekshiriladi)\n- Subsidiya turiga qarab: uy-joy uchun ipoteka shartnomasi, ijtimoiy holat uchun mahalla ma’lumotnomasi.",
        "family": "*Kerakli hujjatlar*\n- Pasport/ID\n- Ariza (onlayn)\n- Tug‘ilganlik guvohnomasi\n- Daromad ma’lumoti\n- Mahalla ma’lumotnomasi.",
        "social": "*Kerakli hujjatlar*\n- Pasport/ID\n- Ariza (onlayn)\n- Daromad ma’lumoti\n- Nogironlik guvohnomasi (agar kerak bo‘lsa).",
        "certificates": "*Kerakli hujjatlar*\n- Pasport/ID\n- Ariza (onlayn)\n- Daromad ma’lumotnomasi (agar kerak bo‘lsa).",
        "pension": "*Kerakli hujjatlar*\n- Pasport/ID\n- Ariza (onlayn)\n- Mehnat daftarchasi\n- Nogironlik hujjati (agar kerak bo‘lsa).",
        "education": "*Kerakli hujjatlar*\n- Pasport/ID\n- Ariza (onlayn)\n- O‘quv muassasasi ma’lumotnomasi.",
        "youth": "*Kerakli hujjatlar*\n- Pasport/ID\n- Ariza (onlayn)\n- Biznes-reja (tadbirkorlik uchun).",
        "tax": "*Kerakli hujjatlar*\n- Pasport/ID\n- Ariza (onlayn)\n- Tadbirkorlik hujjatlari (agar kerak bo‘lsa).",
        "mygov": "*Kerakli hujjatlar*\n- Pasport/ID raqami\n- Telefon raqami (SMS tasdiqlash uchun)\n- Elektron pochta (ixtiyoriy, lekin tavsiya etiladi)\nRo'yxatdan o'tish uchun: my.gov.uz"
    }

    # Callback ma’lumotlariga qarab caption tanlash
    if data.endswith("_info"):
        caption = info_captions[section]
    elif data.endswith("_cost_time"):
        caption = cost_time_captions[section]
    elif data.endswith("_docs"):
        caption = docs_captions[section]
    elif data.startswith("back_to_"):
        caption = f"{section.title()} haqida ma'lumot olish uchun quyidagi tugmalardan birini tanlang:"
    else:
        await callback_query.answer("Noma'lum buyruq!")
        return

    try:
        with open(photo_path, 'rb') as photo:
            media = types.InputMediaPhoto(media=photo, caption=caption, parse_mode="Markdown")
            if data.startswith("back_to_"):
                await bot.edit_message_media(
                    media=media,
                    chat_id=chat_id,
                    message_id=message_id,
                    reply_markup=get_options(section)
                )
            else:
                await bot.edit_message_media(
                    media=media,
                    chat_id=chat_id,
                    message_id=message_id,
                    reply_markup=get_back_button(section)
                )
        await callback_query.answer()
    except FileNotFoundError:
        await bot.send_message(chat_id, f"Kechirasiz, rasm topilmadi! Yo‘l: {photo_path}")
    except Exception as e:
        await bot.send_message(chat_id, f"Xatolik yuz berdi: {str(e)}")












# Ma'lumotlarni fayldan yuklash
def load_data():
    global user_data, blocked_user_ids
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)
            user_data = {int(k): v for k, v in data.get("users", {}).items()}
            blocked_user_ids = set(data.get("blocked", []))
    return user_data.keys()

# Ma'lumotlarni faylga saqlash
def save_data():
    with open(DATA_FILE, "w", encoding="utf-8") as file:
        json.dump({
            "users": {str(k): v for k, v in user_data.items()},
            "blocked": list(blocked_user_ids)
        }, file, ensure_ascii=False, indent=4)

# Admin tekshiruvi uchun funksiya
def is_admin(user_id):
    return user_id in admin_ids

# Admin paneli uchun tugmalar
def get_admin_panel_keyboard():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row(KeyboardButton("🔄 Start xabari"), KeyboardButton("👨‍💻 Adminlar"))
    keyboard.row(KeyboardButton("🧑‍💼 Admin qoʻshish"), KeyboardButton("🚀 Habar yuborish"))
    keyboard.row(KeyboardButton("📊 Statistika"))
    return keyboard

# Holatlar klassi
class AdminStates(StatesGroup):
    add_admin = State()
    update_start_message = State()
    broadcast_message = State()

# Avvalgi state faol bo'lsa tugatish
async def reset_state_if_active(state: FSMContext):
    current_state = await state.get_state()
    if current_state is not None:
        await state.finish()

# Adminlarni ko'rsatish
@dp.message_handler(lambda message: message.text == "👨‍💻 Adminlar")
async def show_admins(message: types.Message):
    if not is_admin(message.from_user.id):
        await message.reply("Kechirasiz, bu buyruq faqat adminlarga!")
        return
    keyboard = InlineKeyboardMarkup()
    for admin_id in admin_ids:
        try:
            chat = await bot.get_chat(admin_id)
            username = f"@{chat.username}" if chat.username else f"Admin {admin_id}"
        except Exception:
            username = f"Admin {admin_id}"
        keyboard.add(
            InlineKeyboardButton(username, callback_data=f"admin_{admin_id}"),
            InlineKeyboardButton("🗑️", callback_data=f"delete_{admin_id}")
        )
    await message.reply("Mavjud adminlar:", reply_markup=keyboard)

# Adminni o'chirish
@dp.callback_query_handler(lambda c: c.data.startswith("delete_"))
async def delete_admin(callback_query: types.CallbackQuery):
    if not is_admin(callback_query.from_user.id):
        await callback_query.answer("Sizda bu huquq yo‘q!", show_alert=True)
        return
    admin_id = int(callback_query.data.split("_")[1])
    if admin_id in admin_ids and len(admin_ids) > 1:  # Kamida bitta admin qolishi uchun
        admin_ids.remove(admin_id)
        await callback_query.answer("Admin o'chirildi!")
        await bot.edit_message_text("Admin o'chirildi", callback_query.message.chat.id, callback_query.message.message_id)
    elif len(admin_ids) <= 1:
        await callback_query.answer("Oxirgi adminni o‘chirib bo‘lmaydi!", show_alert=True)
    else:
        await callback_query.answer("Bu admin mavjud emas.")

# Admin paneliga kirish
@dp.message_handler(commands=['panel'])
async def admin_panel(message: types.Message):
    if is_admin(message.from_user.id):
        await message.reply("Admin paneliga xush kelibsiz!", reply_markup=get_admin_panel_keyboard())
    else:
        await message.reply("Kechirasiz, bu buyruq faqat adminlarga!")

# Start xabarini yangilash
@dp.message_handler(lambda message: message.text == "🔄 Start xabari")
async def update_start_message(message: types.Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        await message.reply("Kechirasiz, bu buyruq faqat adminlarga!")
        return
    await reset_state_if_active(state)
    await message.reply("Yangi start xabarini kiriting.")
    await AdminStates.update_start_message.set()

@dp.message_handler(state=AdminStates.update_start_message)
async def save_start_message(message: types.Message, state: FSMContext):
    global start_message
    start_message = message.text
    await message.reply(f"Start xabari yangilandi:\n{start_message}")
    await state.finish()

# Admin qo'shish
@dp.message_handler(lambda message: message.text == "🧑‍💼 Admin qoʻshish")
async def add_admin(message: types.Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        await message.reply("Kechirasiz, bu buyruq faqat adminlarga!")
        return
    await reset_state_if_active(state)
    await message.reply("Yangi adminning ID raqamini kiriting.")
    await AdminStates.add_admin.set()

@dp.message_handler(state=AdminStates.add_admin)
async def save_admin(message: types.Message, state: FSMContext):
    try:
        new_admin_id = int(message.text)
        if new_admin_id not in admin_ids:
            admin_ids.add(new_admin_id)
            try:
                chat = await bot.get_chat(new_admin_id)
                username = f"@{chat.username}" if chat.username else f"Admin {new_admin_id}"
                await message.reply(f"Yangi admin qo‘shildi: {username}")
            except Exception:
                await message.reply(f"Yangi admin qo‘shildi: Admin {new_admin_id}")
        else:
            await message.reply("Bu foydalanuvchi allaqachon admin.")
    except ValueError:
        await message.reply("Noto‘g‘ri ID. Faqat son kiriting.")
    await state.finish()

# Xabar yuborish
@dp.message_handler(lambda message: message.text == "🚀 Habar yuborish")
async def broadcast_message(message: types.Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        await message.reply("Kechirasiz, bu buyruq faqat adminlarga!")
        return
    await reset_state_if_active(state)
    await message.reply("Barcha foydalanuvchilarga yuboriladigan xabarni kiriting.")
    await AdminStates.broadcast_message.set()

@dp.message_handler(state=AdminStates.broadcast_message)
async def send_broadcast(message: types.Message, state: FSMContext):
    broadcast_text = message.text
    user_ids = list(user_data.keys())
    successful_count = 0
    for user_id in user_ids:
        if user_id not in blocked_user_ids:
            try:
                await bot.send_message(user_id, broadcast_text)
                successful_count += 1
                await asyncio.sleep(0.05)  # Telegram cheklovlaridan qochish uchun kechikish
            except Exception as e:
                print(f"Xato: {e} foydalanuvchi ID {user_id}")
                blocked_user_ids.add(user_id)
    save_data()  # Bloklangan ID’larni saqlash
    await message.reply(f"Xabar {successful_count} foydalanuvchiga yetib bordi!")
    await state.finish()

# Statistika ko'rsatish
@dp.message_handler(lambda message: message.text == "📊 Statistika")
async def show_statistics(message: types.Message):
    if not is_admin(message.from_user.id):
        await message.reply("Kechirasiz, bu buyruq faqat adminlarga!")
        return
    total_users = len(user_data)
    blocked_users = len(blocked_user_ids)
    one_month_ago = datetime.now() - timedelta(days=30)
    recent_users = sum(1 for join_date in user_data.values() if datetime.strptime(join_date["join_date"], "%Y-%m-%d %H:%M:%S") >= one_month_ago)

    stats_text = (
        f"📊 *Statistika:*\n"
        f"Jami foydalanuvchilar: *{total_users}*\n"
        f"Botni bloklaganlar: *{blocked_users}*\n"
        f"Oxirgi 30 kunda qo‘shilganlar: *{recent_users}*"
    )
    await message.reply(stats_text, parse_mode=types.ParseMode.MARKDOWN)

# Start komandasi
@dp.message_handler(commands=['start'])
async def start_command(message: types.Message):
    user_id = message.from_user.id
    if user_id not in user_data:
        user_data[user_id] = {"join_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
        save_data()
    await message.reply(start_message, reply_markup=main_menu)


# Botni ishga tushirish
async def main():
    
    load_data()  # Bot ishga tushganda ma'lumotlarni yuklash
    await dp.start_polling()

if __name__ == "__main__":
    asyncio.run(main())
