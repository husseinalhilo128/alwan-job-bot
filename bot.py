import os
import sqlite3
from telegram import (
    Update,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
)
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ConversationHandler,
    ContextTypes,
    filters,
)

BOT_TOKEN = os.getenv("BOT_TOKEN")

ADMIN_IDS = [int(x.strip()) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip()]
SUPER_ADMIN_IDS = [int(x.strip()) for x in os.getenv("SUPER_ADMIN_IDS", "").split(",") if x.strip()]

DB_NAME = "jobs.db"

(
    FULL_NAME,
    BIRTH,
    GENDER,
    STUDY,
    EXPERIENCE,
    LANGUAGES,
    AVAILABLE,
    MEDIA,
    SALARY,
    PHONE,
    PHOTO,
) = range(11)


def init_db():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS applications (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        full_name TEXT,
        birth TEXT,
        gender TEXT,
        study TEXT,
        experience TEXT,
        languages TEXT,
        available TEXT,
        media TEXT,
        salary TEXT,
        phone TEXT,
        photo TEXT,
        rating TEXT DEFAULT 'بدون تقييم'
    )
    """)

    conn.commit()
    conn.close()


def is_admin(user_id):
    return user_id in ADMIN_IDS


def is_super_admin(user_id):
    return user_id in SUPER_ADMIN_IDS


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text(
        "مرحبا بك في التقديم على وظائف شركة الوان كربلاء\n\nيرجى كتابة الاسم الكامل",
        reply_markup=ReplyKeyboardRemove(),
    )
    return FULL_NAME


async def full_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["full_name"] = update.message.text.strip()
    await update.message.reply_text("اكتب تاريخ الميلاد\nمثال:\n2001/5/10")
    return BIRTH


async def birth(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["birth"] = update.message.text.strip()

    keyboard = [["ذكر", "أنثى"]]
    await update.message.reply_text(
        "اختر الجنس",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True),
    )
    return GENDER


async def gender(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["gender"] = update.message.text.strip()

    keyboard = [["خريج", "طالب", "تارك"]]
    await update.message.reply_text(
        "الحالة الدراسية",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True),
    )
    return STUDY


async def study(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["study"] = update.message.text.strip()

    keyboard = [["نعم", "لا"]]
    await update.message.reply_text(
        "هل لديك خبرة عمل؟",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True),
    )
    return EXPERIENCE


async def experience(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["experience"] = update.message.text.strip()

    await update.message.reply_text(
        "اذكر اللغات التي تتحدث بها",
        reply_markup=ReplyKeyboardRemove(),
    )
    return LANGUAGES


async def languages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["languages"] = update.message.text.strip()

    keyboard = [["نعم", "لا"]]
    await update.message.reply_text(
        "هل أنت متفرغ للعمل؟",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True),
    )
    return AVAILABLE


async def available(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["available"] = update.message.text.strip()

    keyboard = [["نعم", "لا"]]
    await update.message.reply_text(
        "هل تستطيع الظهور إعلاميا في صفحات الشركة؟",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True, one_time_keyboard=True),
    )
    return MEDIA


async def media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["media"] = update.message.text.strip()

    await update.message.reply_text(
        "ما الراتب المتوقع؟",
        reply_markup=ReplyKeyboardRemove(),
    )
    return SALARY


async def salary(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["salary"] = update.message.text.strip()

    button = KeyboardButton("إرسال رقم الهاتف", request_contact=True)
    await update.message.reply_text(
        "أرسل رقم الهاتف",
        reply_markup=ReplyKeyboardMarkup([[button]], resize_keyboard=True, one_time_keyboard=True),
    )
    return PHONE


async def phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.contact:
        context.user_data["phone"] = update.message.contact.phone_number
    else:
        context.user_data["phone"] = update.message.text.strip()

    await update.message.reply_text(
        "أرسل صورة شخصية",
        reply_markup=ReplyKeyboardRemove(),
    )
    return PHOTO


async def photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo_file = update.message.photo[-1].file_id
    data = context.user_data

    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute("""
    INSERT INTO applications (
        full_name, birth, gender, study, experience,
        languages, available, media, salary, phone, photo
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data["full_name"],
        data["birth"],
        data["gender"],
        data["study"],
        data["experience"],
        data["languages"],
        data["available"],
        data["media"],
        data["salary"],
        data["phone"],
        photo_file,
    ))

    application_id = cur.lastrowid
    conn.commit()
    conn.close()

    text = f"""
طلب تقديم جديد

الرقم: {application_id}

الاسم: {data['full_name']}
الجنس: {data['gender']}
المواليد: {data['birth']}
الدراسة: {data['study']}
الخبرة: {data['experience']}
اللغات: {data['languages']}
متفرغ: {data['available']}
ظهور إعلامي: {data['media']}
الراتب: {data['salary']}
الهاتف: {data['phone']}
"""

    keyboard = [[
        InlineKeyboardButton("⭐", callback_data=f"rate_1_{application_id}"),
        InlineKeyboardButton("⭐⭐", callback_data=f"rate_2_{application_id}"),
        InlineKeyboardButton("⭐⭐⭐", callback_data=f"rate_3_{application_id}"),
    ]]

    for admin_id in ADMIN_IDS:
        await context.bot.send_photo(
            chat_id=admin_id,
            photo=photo_file,
            caption=text,
            reply_markup=InlineKeyboardMarkup(keyboard),
        )

    await update.message.reply_text("تم إرسال طلبك بنجاح")
    context.user_data.clear()

    return ConversationHandler.END


async def rate_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if not is_admin(query.from_user.id):
        return

    parts = query.data.split("_")
    stars = parts[1]
    application_id = parts[2]

    rating = "⭐" * int(stars)

    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    cur.execute(
        "UPDATE applications SET rating = ? WHERE id = ?",
        (rating, application_id),
    )

    conn.commit()
    conn.close()

    await query.message.reply_text(f"تم تقييم المتقدم: {rating}")


async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return

    keyboard = [
        ["📋 كل المتقدمين"],
        ["👨 الذكور", "👩 الإناث"],
        ["⭐ التقييمات"],
        ["⏰ المتفرغين"],
        ["🎥 الظهور الإعلامي"],
        ["🗑 حذف البيانات"],
    ]

    await update.message.reply_text(
        "لوحة الأدمن",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True),
    )


async def filters_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return

    text = update.message.text.strip()

    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    if text == "📋 كل المتقدمين":
        cur.execute("SELECT id, full_name, gender, available, media, rating FROM applications")

    elif text == "👨 الذكور":
        cur.execute("SELECT id, full_name, gender, available, media, rating FROM applications WHERE gender='ذكر'")

    elif text == "👩 الإناث":
        cur.execute("SELECT id, full_name, gender, available, media, rating FROM applications WHERE gender='أنثى'")

    elif text == "⏰ المتفرغين":
        cur.execute("SELECT id, full_name, gender, available, media, rating FROM applications WHERE available='نعم'")

    elif text == "🎥 الظهور الإعلامي":
        cur.execute("SELECT id, full_name, gender, available, media, rating FROM applications WHERE media='نعم'")

    elif text == "⭐ التقييمات":
        cur.execute("SELECT id, full_name, gender, available, media, rating FROM applications WHERE rating!='بدون تقييم'")

    elif text == "🗑 حذف البيانات":
        if not is_super_admin(update.effective_user.id):
            await update.message.reply_text("هذا الأمر للسوبر أدمن فقط")
            conn.close()
            return

        keyboard = [[
            InlineKeyboardButton("✅ نعم، احذف الكل", callback_data="delete_all_confirm"),
            InlineKeyboardButton("❌ إلغاء", callback_data="delete_all_cancel"),
        ]]

        await update.message.reply_text(
            "هل أنت متأكد من حذف جميع بيانات المتقدمين؟",
            reply_markup=InlineKeyboardMarkup(keyboard),
        )
        conn.close()
        return

    else:
        conn.close()
        return

    rows = cur.fetchall()
    conn.close()

    if not rows:
        await update.message.reply_text("لا توجد نتائج")
        return

    result = ""
    for row in rows:
        result += (
            f"رقم: {row[0]}\n"
            f"الاسم: {row[1]}\n"
            f"الجنس: {row[2]}\n"
            f"متفرغ: {row[3]}\n"
            f"ظهور إعلامي: {row[4]}\n"
            f"التقييم: {row[5]}\n"
            f"--------------------\n"
        )

    await update.message.reply_text(result)


async def delete_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if not is_super_admin(query.from_user.id):
        return

    if query.data == "delete_all_cancel":
        await query.message.reply_text("تم إلغاء الحذف")
        return

    if query.data == "delete_all_confirm":
        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()
        cur.execute("DELETE FROM applications")
        conn.commit()
        conn.close()

        await query.message.reply_text("تم حذف جميع البيانات")


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()

    await update.message.reply_text(
        "تم الإلغاء",
        reply_markup=ReplyKeyboardRemove(),
    )

    return ConversationHandler.END


def main():
    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN غير موجود داخل Railway Variables")

    init_db()

    app = Application.builder().token(BOT_TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            FULL_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, full_name)],
            BIRTH: [MessageHandler(filters.TEXT & ~filters.COMMAND, birth)],
            GENDER: [MessageHandler(filters.TEXT & ~filters.COMMAND, gender)],
            STUDY: [MessageHandler(filters.TEXT & ~filters.COMMAND, study)],
            EXPERIENCE: [MessageHandler(filters.TEXT & ~filters.COMMAND, experience)],
            LANGUAGES: [MessageHandler(filters.TEXT & ~filters.COMMAND, languages)],
            AVAILABLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, available)],
            MEDIA: [MessageHandler(filters.TEXT & ~filters.COMMAND, media)],
            SALARY: [MessageHandler(filters.TEXT & ~filters.COMMAND, salary)],
            PHONE: [
                MessageHandler(filters.CONTACT, phone),
                MessageHandler(filters.TEXT & ~filters.COMMAND, phone),
            ],
            PHOTO: [MessageHandler(filters.PHOTO, photo)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv_handler)
    app.add_handler(CommandHandler("admin", admin))
    app.add_handler(CallbackQueryHandler(rate_callback, pattern="^rate_"))
    app.add_handler(CallbackQueryHandler(delete_callback, pattern="^delete_all_"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, filters_handler))

    print("Bot Running...")
    app.run_polling()


if __name__ == "__main__":
    main()
