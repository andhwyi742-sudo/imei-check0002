import requests
import re
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    ContextTypes,
    filters,
    CommandHandler
)

# =====================================================
# 🔑 КОНФІГУРАЦІЯ
# =====================================================

TOKEN = "8588926481:AAE4tVcAryIfKuHhwR347IHf32rE3R9b4Tk"

# 👑 ГОЛОВНИЙ АДМІН
YOUR_ID = 2061131189

# 👮 СПИСОК АДМІНІВ
ADMINS = [YOUR_ID]

API_KEY = "8EkY2-6WohA-AzFpu-PcsIc-01bh1-6ozIE"

API_BASE_URL = "https://alpha.imeicheck.com/api/php-api"

SERVICE_ID = "4"

# =====================================================
# 📌 КНОПКИ
# =====================================================

keyboard = ReplyKeyboardMarkup(
    [
        ["💰 Баланс"],
        ["👮 Додати адміна"]
    ],
    resize_keyboard=True
)

# =====================================================
# 👮 ДОДАТИ АДМІНА
# =====================================================

async def add_admin(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_user.id

    # тільки головний адмін
    if user_id != YOUR_ID:

        await update.message.reply_text(
            "нет доступа"
        )

        return

    # перевірка аргументу
    if not context.args:

        await update.message.reply_text(
            "❗ Використання:\n/addadmin ID"
        )

        return

    try:

        new_admin = int(context.args[0])

    except:

        await update.message.reply_text(
            "❌ Невірний ID"
        )

        return

    # якщо вже адмін
    if new_admin in ADMINS:

        await update.message.reply_text(
            "⚠️ Цей користувач вже адмін"
        )

        return

    ADMINS.append(new_admin)

    await update.message.reply_text(
        f"✅ Адмін доданий:\n<code>{new_admin}</code>",
        parse_mode="HTML"
    )

# =====================================================
# 📱 КРАСИВИЙ ПАРСЕР
# =====================================================

def clean_result(raw: str):

    if not raw:
        return "❌ Немає даних"

    # HTML OFF
    raw = re.sub(r"<[^>]+>", "", str(raw))

    # нормалізація
    raw = raw.replace("\r", "\n").strip()

    raw_upper = raw.upper()

    # =====================================================
    # IMEI
    # =====================================================

    imei = "—"

    imei_match = re.search(
        r"(\d{15,16})",
        raw
    )

    if imei_match:
        imei = imei_match.group(1)

    # =====================================================
    # МОДЕЛЬ
    # =====================================================

    model = "Невідомо"

    model_patterns = [
        r"(iPhone[^\n]+)",
        r"Model:\s*(.+)",
        r"Device:\s*(.+)"
    ]

    for pattern in model_patterns:

        m = re.search(pattern, raw, re.IGNORECASE)

        if m:
            model = m.group(1).strip()

            model = re.sub(r"IMEI.*", "", model).strip()

            break

    # TAC визначення
    if model == "Невідомо" and imei != "—":

        tac = imei[:8]

        tac_models = {

            # iPhone 11
            "35391510": "iPhone 11",
            "35656510": "iPhone 11",
            "35291311": "iPhone 11",

            "35391810": "iPhone 11 Pro",
            "35282011": "iPhone 11 Pro",

            "35392010": "iPhone 11 Pro Max",
            "35392110": "iPhone 11 Pro Max",

            # iPhone 12
            "35305110": "iPhone 12",
            "35275510": "iPhone 12",

            "35668511": "iPhone 12 mini",
            "35301211": "iPhone 12 mini",

            "35668711": "iPhone 12 Pro",
            "35668611": "iPhone 12 Pro",

            "35671911": "iPhone 12 Pro Max",
            "35672011": "iPhone 12 Pro Max",

            # iPhone 13
            "35210527": "iPhone 13 mini",
            "35210627": "iPhone 13 mini",

            "35070450": "iPhone 13",
            "35070550": "iPhone 13",

            "35614449": "iPhone 13 Pro",
            "35614549": "iPhone 13 Pro",

            "35655150": "iPhone 13 Pro Max",
            "35655250": "iPhone 13 Pro Max",

            # iPhone 14
            "35391505": "iPhone 14",
            "35391605": "iPhone 14",

            "35762966": "iPhone 14 Plus",
            "35763066": "iPhone 14 Plus",

            "35536182": "iPhone 14 Pro",
            "35536282": "iPhone 14 Pro",

            "35342568": "iPhone 14 Pro Max",
            "35342668": "iPhone 14 Pro Max",

            # iPhone 15
            "35113493": "iPhone 15",
            "35113593": "iPhone 15",

            "35286263": "iPhone 15 Plus",
            "35286363": "iPhone 15 Plus",

            "35630374": "iPhone 15 Pro",
            "35630474": "iPhone 15 Pro",

            "35837595": "iPhone 15 Pro Max",
            "35837695": "iPhone 15 Pro Max",

            # iPhone 16
            "35574150": "iPhone 16",
            "35574250": "iPhone 16",

            "35789421": "iPhone 16 Plus",
            "35789521": "iPhone 16 Plus",

            "35920311": "iPhone 16 Pro",
            "35920411": "iPhone 16 Pro",

            "35209918": "iPhone 16 Pro Max",
            "35210018": "iPhone 16 Pro Max",

            # iPhone 17
            "35199827": "iPhone 17",
            "35199927": "iPhone 17",

            "35200027": "iPhone 17 Plus",
            "35200127": "iPhone 17 Plus",

            "35200227": "iPhone 17 Pro",
            "35200327": "iPhone 17 Pro",

            "35200427": "iPhone 17 Pro Max",
            "35200527": "iPhone 17 Pro Max",
        }

        model = tac_models.get(tac, "iPhone")

    # =====================================================
    # FIND MY
    # =====================================================

    find_my = "—"

    if any(x in raw_upper for x in [
        "FIND MY IPHONE: ON",
        "FMI: ON",
        "FIND MY: ON",
        "LOST MODE"
    ]):
        find_my = "ON"

    elif any(x in raw_upper for x in [
        "FIND MY IPHONE: OFF",
        "FMI: OFF",
        "FIND MY: OFF"
    ]):
        find_my = "OFF"

    # =====================================================
    # ICLOUD STATUS
    # =====================================================

    icloud = "UNKNOWN"

    if "LOST MODE" in raw_upper or "LOST" in raw_upper:
        icloud = "LOST"

    elif "CLEAN" in raw_upper:
        icloud = "CLEAN"

    # =====================================================
    # ІКОНКИ
    # =====================================================

    if find_my == "ON":
        fm_icon = "🔴"
    elif find_my == "OFF":
        fm_icon = "⚪"
    else:
        fm_icon = "🟡"

    if icloud == "LOST":
        ic_icon = "🔴"
    elif icloud == "CLEAN":
        ic_icon = "⚪"
    else:
        ic_icon = "🟡"

    # =====================================================
    # ФІНАЛЬНЕ ПОВІДОМЛЕННЯ
    # =====================================================

    result = (
        f"📱 <b>Результат перевірки</b>\n\n"
        f"🔹 <b>{model}</b>\n"
        f"🧾 IMEI: <code>{imei}</code>\n\n"
        f"{fm_icon} Find My: <b>{find_my}</b>\n"
        f"{ic_icon} iCloud Status: <b>{icloud}</b>"
    )

    return result

# =====================================================
# /start
# =====================================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_user.id not in ADMINS:

        await update.message.reply_text(
            "нет доступа"
        )

        return

    await update.message.reply_text(
        "👋 Надішли IMEI для перевірки:",
        reply_markup=keyboard
    )

# =====================================================
# ОБРОБКА ПОВІДОМЛЕНЬ
# =====================================================

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):

    if update.effective_user.id not in ADMINS:

        await update.message.reply_text(
            "нет доступа"
        )

        return

    text = update.message.text.strip()

    # =====================================================
    # 👮 КНОПКА ДОДАТИ АДМІНА
    # =====================================================

    if text == "👮 Додати адміна":

        if update.effective_user.id != YOUR_ID:

            await update.message.reply_text(
                "нет доступа"
            )

            return

        await update.message.reply_text(
            "📌 Напиши команду:\n/addadmin ID"
        )

        return

    # =====================================================
    # 💰 БАЛАНС
    # =====================================================

    if text == "💰 Баланс":

        try:

            r = requests.get(
                f"{API_BASE_URL}/balance",
                params={
                    "key": API_KEY
                }
            )

            bal = r.json().get("balance", "0")

            await update.message.reply_text(
                f"💰 Баланс: <b>{bal}</b> кр.",
                parse_mode="HTML"
            )

        except Exception as e:

            await update.message.reply_text(
                f"❌ Помилка API\n<code>{str(e)}</code>",
                parse_mode="HTML"
            )

        return

    # =====================================================
    # 📟 ПЕРЕВІРКА IMEI
    # =====================================================

    if not (text.isdigit() and len(text) in [15, 16]):

        await update.message.reply_text(
            "❗ Введи коректний IMEI"
        )

        return

    msg = await update.message.reply_text(
        "🔍 Перевіряю..."
    )

    # =====================================================
    # API ЗАПИТ
    # =====================================================

    try:

        r = requests.get(
            f"{API_BASE_URL}/create",
            params={
                "key": API_KEY,
                "service": SERVICE_ID,
                "imei": text
            }
        )

        res = r.json()

        print("========== API RESPONSE ==========")
        print(res)
        print("==================================")

        # =====================================================
        # УСПІХ
        # =====================================================

        if res.get("status") == "success":

            formatted = clean_result(
                res.get("result", "")
            )

            final_msg = (
                f"{formatted}\n\n"
                f"━━━━━━━━━━━━━━\n"
                f"💵 Вартість: <b>{res.get('price')}</b>\n"
                f"⏱ Час: <b>{res.get('duration')}</b>"
            )

            await msg.edit_text(
                final_msg,
                parse_mode="HTML"
            )

        # =====================================================
        # ПОМИЛКА API
        # =====================================================

        else:

            error_msg = (
                res.get("message")
                or res.get("result")
                or "Невідома помилка API"
            )

            await msg.edit_text(
                f"❌ <b>Помилка:</b>\n<code>{error_msg}</code>",
                parse_mode="HTML"
            )

    # =====================================================
    # СИСТЕМНА ПОМИЛКА
    # =====================================================

    except Exception as e:

        await msg.edit_text(
            f"❌ <b>Системна помилка:</b>\n<code>{str(e)}</code>",
            parse_mode="HTML"
        )

# =====================================================
# 🚀 ЗАПУСК БОТА
# =====================================================

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(
    CommandHandler("start", start)
)

app.add_handler(
    CommandHandler("addadmin", add_admin)
)

app.add_handler(
    MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        handle_message
    )
)

print("✅ Бот працює...")

app.run_polling()