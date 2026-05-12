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
    STUDY_DETAILS,
    EXPERIENCE,
    EXPERIENCE_PLACE,
    LANGUAGES,
    DEPARTMENTS,
    HAS_BIKE,
    MEDIA_SKILLS,
    AVAILABLE,
    MEDIA_APPEAR,
    SALARY,
    PROVINCE,
    ADDRESS,
    PHONE,
    PHOTO,
) = range(18)

LANGUAGE_OPTIONS = ["عربي", "إنكليزي", "فارسي", "كردي", "تركي"]
DEPARTMENT_OPTIONS = [
    "قسم الأجهزة",
    "قسم الاكسسوارات",
    "قسم الحسابات",
    "قسم الإعلام",
    "قسم الصيانة",
    "قسم التوصيل",
    "قسم الموارد البشرية",
]
MEDIA_SKILL_OPTIONS = ["تصميم", "تصوير", "مونتاج", "تقديم"]


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
        study_details TEXT,
        experience TEXT,
        experience_place TEXT,
        languages TEXT,
        departments TEXT,
        has_bike TEXT,
        media_skills TEXT,
        available TEXT,
        media_appear TEXT,
        salary TEXT,
        province TEXT,
        address TEXT,
        phone TEXT,
        photo TEXT,
        rating TEXT DEFAULT 'بدون تقييم'
    )
    """)

    existing_columns = [row[1] for row in cur.execute("PRAGMA table_info(applications)").fetchall()]

    new_columns = {
        "study_details": "TEXT",
        "experience_place": "TEXT",
        "departments": "TEXT",
        "has_bike": "TEXT",
        "media_skills": "TEXT",
        "media_appear": "TEXT",
        "province": "TEXT",
        "address": "TEXT",
    }

    for column, col_type in new_columns.items():
        if column not in existing_columns:
            cur.execute(f"ALTER TABLE applications ADD COLUMN {column} {col_type}")

    conn.commit()
    conn.close()


def is_admin(user_id):
    return user_id in ADMIN_IDS


def is_super_admin(user_id):
    return user_id in SUPER_ADMIN_IDS


def admin_keyboard():
    return ReplyKeyboardMarkup(
        [
            ["📋 كل المتقدمين"],
            ["👨 الذكور", "👩 الإناث"],
            ["⭐ التقييمات"],
            ["⏰ المتفرغين"],
            ["🎥 الظهور الإعلامي"],
            ["🗑 حذف البيانات"],
        ],
        resize_keyboard=True,
    )


def multi_keyboard(options):
    rows = []
    for i in range(0, len(options), 2):
        rows.append(options[i:i + 2])
    rows.append(["✅ تم الاختيار"])
    return ReplyKeyboardMarkup(rows, resize_keyboard=True)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if is_admin(user_id):
        await update.message.reply_text(
            "مرحبا أدمن\nهذه لوحة التحكم الخاصة بالتقديمات",
            reply_markup=admin_keyboard(),
        )
        return ConversationHandler.END

    context.user_data.clear()

    await update.message.reply_text(
        "مرحبا بك في التقديم على وظائف شركة الوان كربلاء\n\nيرجى كتابة الاسم الكامل",
        reply_markup=ReplyKeyboardRemove(),
    )

    return FULL_NAME


async def apply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()

    await update.message.reply_text(
        "تم بدء طلب تقديم جديد\n\nيرجى كتابة الاسم الكامل",
        reply_markup=ReplyKeyboardRemove(),
    )

    return FULL_NAME


async def full_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["full_name"] = update.message.text.strip()
    await update.message.reply_text("اكتب تاريخ الميلاد\nمثال:\n2001/5/10")
    return BIRTH


async def birth(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["birth"] = update.message.text.strip()

    await update.message.reply_text(
        "اختر الجنس",
        reply_markup=ReplyKeyboardMarkup([["ذكر", "أنثى"]], resize_keyboard=True, one_time_keyboard=True),
    )
    return GENDER


async def gender(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["gender"] = update.message.text.strip()

    await update.message.reply_text(
        "الحالة الدراسية",
        reply_markup=ReplyKeyboardMarkup([["خريج", "طالب", "تارك"]], resize_keyboard=True, one_time_keyboard=True),
    )
    return STUDY


async def study(update: Update, context: ContextTypes.DEFAULT_TYPE):
    value = update.message.text.strip()
    context.user_data["study"] = value

    if value == "خريج":
        await update.message.reply_text("اكتب القسم الذي تخرجت منه", reply_markup=ReplyKeyboardRemove())
    elif value == "طالب":
        await update.message.reply_text("اكتب المرحلة الحالية والقسم", reply_markup=ReplyKeyboardRemove())
    else:
        await update.message.reply_text("اكتب آخر مرحلة دراسية وصلت لها", reply_markup=ReplyKeyboardRemove())

    return STUDY_DETAILS


async def study_details(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["study_details"] = update.message.text.strip()

    await update.message.reply_text(
        "هل لديك خبرة عمل؟",
        reply_markup=ReplyKeyboardMarkup([["نعم", "لا"]], resize_keyboard=True, one_time_keyboard=True),
    )
    return EXPERIENCE


async def experience(update: Update, context: ContextTypes.DEFAULT_TYPE):
    value = update.message.text.strip()
    context.user_data["experience"] = value

    if value == "نعم":
        await update.message.reply_text(
            "اكتب مكان الخبرة السابقة",
            reply_markup=ReplyKeyboardRemove(),
        )
        return EXPERIENCE_PLACE

    context.user_data["experience_place"] = "لا يوجد"
    context.user_data["selected_languages"] = []

    await update.message.reply_text(
        "اختر اللغات التي تتحدث بها\nيمكنك اختيار أكثر من لغة ثم اضغط ✅ تم الاختيار",
        reply_markup=multi_keyboard(LANGUAGE_OPTIONS),
    )
    return LANGUAGES


async def experience_place(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["experience_place"] = update.message.text.strip()
    context.user_data["selected_languages"] = []

    await update.message.reply_text(
        "اختر اللغات التي تتحدث بها\nيمكنك اختيار أكثر من لغة ثم اضغط ✅ تم الاختيار",
        reply_markup=multi_keyboard(LANGUAGE_OPTIONS),
    )
    return LANGUAGES


async def languages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()

    if text == "✅ تم الاختيار":
        selected = context.user_data.get("selected_languages", [])

        if not selected:
            await update.message.reply_text("اختر لغة واحدة على الأقل")
            return LANGUAGES

        context.user_data["languages"] = "، ".join(selected)
        context.user_data["selected_departments"] = []

        await update.message.reply_text(
            "اختر الأقسام المفضلة\nيمكنك اختيار أكثر من قسم ثم اضغط ✅ تم الاختيار",
            reply_markup=multi_keyboard(DEPARTMENT_OPTIONS),
        )
        return DEPARTMENTS

    if text in LANGUAGE_OPTIONS:
        selected = context.user_data.setdefault("selected_languages", [])

        if text in selected:
            selected.remove(text)
            await update.message.reply_text(f"تم حذف {text} من الاختيارات")
        else:
            selected.append(text)
            await update.message.reply_text(f"تم اختيار {text}")

        return LANGUAGES

    await update.message.reply_text("يرجى الاختيار من الأزرار")
    return LANGUAGES
async def departments(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()

    if text == "✅ تم الاختيار":
        selected = context.user_data.get("selected_departments", [])

        if not selected:
            await update.message.reply_text("اختر قسم واحد على الأقل")
            return DEPARTMENTS

        context.user_data["departments"] = "، ".join(selected)

        if "قسم التوصيل" in selected:
            await update.message.reply_text(
                "هل تمتلك دراجة؟",
                reply_markup=ReplyKeyboardMarkup([["نعم", "لا"]], resize_keyboard=True, one_time_keyboard=True),
            )
            return HAS_BIKE

        context.user_data["has_bike"] = "غير مطلوب"

        if "قسم الإعلام" in selected:
            context.user_data["selected_media_skills"] = []
            await update.message.reply_text(
                "ما هو مجال خبرتك في الإعلام؟\nيمكنك اختيار أكثر من مجال ثم اضغط ✅ تم الاختيار",
                reply_markup=multi_keyboard(MEDIA_SKILL_OPTIONS),
            )
            return MEDIA_SKILLS

        context.user_data["media_skills"] = "غير مطلوب"

        await update.message.reply_text(
            "هل أنت متفرغ للعمل؟",
            reply_markup=ReplyKeyboardMarkup([["نعم", "لا"]], resize_keyboard=True, one_time_keyboard=True),
        )
        return AVAILABLE

    if text in DEPARTMENT_OPTIONS:
        selected = context.user_data.setdefault("selected_departments", [])

        if text in selected:
            selected.remove(text)
            await update.message.reply_text(f"تم حذف {text} من الاختيارات")
        else:
            selected.append(text)
            await update.message.reply_text(f"تم اختيار {text}")

        return DEPARTMENTS

    await update.message.reply_text("يرجى الاختيار من الأزرار")
    return DEPARTMENTS


async def has_bike(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["has_bike"] = update.message.text.strip()

    selected = context.user_data.get("selected_departments", [])

    if "قسم الإعلام" in selected:
        context.user_data["selected_media_skills"] = []

        await update.message.reply_text(
            "ما هو مجال خبرتك في الإعلام؟\nيمكنك اختيار أكثر من مجال ثم اضغط ✅ تم الاختيار",
            reply_markup=multi_keyboard(MEDIA_SKILL_OPTIONS),
        )
        return MEDIA_SKILLS

    context.user_data["media_skills"] = "غير مطلوب"

    await update.message.reply_text(
        "هل أنت متفرغ للعمل؟",
        reply_markup=ReplyKeyboardMarkup([["نعم", "لا"]], resize_keyboard=True, one_time_keyboard=True),
    )
    return AVAILABLE


async def media_skills(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()

    if text == "✅ تم الاختيار":
        selected = context.user_data.get("selected_media_skills", [])

        if not selected:
            await update.message.reply_text("اختر مجال واحد على الأقل")
            return MEDIA_SKILLS

        context.user_data["media_skills"] = "، ".join(selected)

        await update.message.reply_text(
            "هل أنت متفرغ للعمل؟",
            reply_markup=ReplyKeyboardMarkup([["نعم", "لا"]], resize_keyboard=True, one_time_keyboard=True),
        )
        return AVAILABLE

    if text in MEDIA_SKILL_OPTIONS:
        selected = context.user_data.setdefault("selected_media_skills", [])

        if text in selected:
            selected.remove(text)
            await update.message.reply_text(f"تم حذف {text} من الاختيارات")
        else:
            selected.append(text)
            await update.message.reply_text(f"تم اختيار {text}")

        return MEDIA_SKILLS

    await update.message.reply_text("يرجى الاختيار من الأزرار")
    return MEDIA_SKILLS


async def available(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["available"] = update.message.text.strip()

    await update.message.reply_text(
        "هل تستطيع الظهور إعلاميا في صفحات الشركة؟",
        reply_markup=ReplyKeyboardMarkup([["نعم", "لا"]], resize_keyboard=True, one_time_keyboard=True),
    )
    return MEDIA_APPEAR


async def media_appear(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["media_appear"] = update.message.text.strip()

    await update.message.reply_text(
        "ما الراتب المتوقع؟",
        reply_markup=ReplyKeyboardRemove(),
    )
    return SALARY


async def salary(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["salary"] = update.message.text.strip()

    await update.message.reply_text(
        "اكتب المحافظة",
        reply_markup=ReplyKeyboardRemove(),
    )
    return PROVINCE


async def province(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["province"] = update.message.text.strip()

    await update.message.reply_text("اكتب عنوان السكن بالتفصيل")
    return ADDRESS


async def address(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["address"] = update.message.text.strip()

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
        full_name, birth, gender, study, study_details,
        experience, experience_place, languages, departments,
        has_bike, media_skills, available, media_appear,
        salary, province, address, phone, photo
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data.get("full_name", ""),
        data.get("birth", ""),
        data.get("gender", ""),
        data.get("study", ""),
        data.get("study_details", ""),
        data.get("experience", ""),
        data.get("experience_place", ""),
        data.get("languages", ""),
        data.get("departments", ""),
        data.get("has_bike", ""),
        data.get("media_skills", ""),
        data.get("available", ""),
        data.get("media_appear", ""),
        data.get("salary", ""),
        data.get("province", ""),
        data.get("address", ""),
        data.get("phone", ""),
        photo_file,
    ))

    application_id = cur.lastrowid
    conn.commit()
    conn.close()

    text = f"""
طلب تقديم جديد

الرقم: {application_id}

الاسم: {data.get('full_name', '')}
الجنس: {data.get('gender', '')}
المواليد: {data.get('birth', '')}
الحالة الدراسية: {data.get('study', '')}
تفاصيل الدراسة: {data.get('study_details', '')}
الخبرة: {data.get('experience', '')}
مكان الخبرة: {data.get('experience_place', '')}
اللغات: {data.get('languages', '')}
الأقسام المفضلة: {data.get('departments', '')}
يمتلك دراجة: {data.get('has_bike', '')}
مجالات الإعلام: {data.get('media_skills', '')}
متفرغ: {data.get('available', '')}
ظهور إعلامي: {data.get('media_appear', '')}
الراتب: {data.get('salary', '')}
المحافظة: {data.get('province', '')}
عنوان السكن: {data.get('address', '')}
الهاتف: {data.get('phone', '')}
"""

    keyboard = [[
        InlineKeyboardButton("⭐", callback_data=f"rate_1_{application_id}"),
        InlineKeyboardButton("⭐⭐", callback_data=f"rate_2_{application_id}"),
        InlineKeyboardButton("⭐⭐⭐", callback_data=f"rate_3_{application_id}"),
    ]]

    sent_count = 0

    for admin_id in ADMIN_IDS:
        try:
            await context.bot.send_photo(
                chat_id=admin_id,
                photo=photo_file,
                caption=text,
                reply_markup=InlineKeyboardMarkup(keyboard),
            )
            sent_count += 1
        except Exception as e:
            print(f"Failed to send application to admin {admin_id}: {e}")

    await update.message.reply_text("تم إرسال طلبك بنجاح")
    print(f"Application {application_id} saved. Sent to {sent_count} admins.")

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

    await update.message.reply_text(
        "لوحة الأدمن",
        reply_markup=admin_keyboard(),
    )


async def filters_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not is_admin(update.effective_user.id):
        return

    text = update.message.text.strip()

    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()

    if text == "📋 كل المتقدمين":
        cur.execute("""
            SELECT id, full_name, gender, departments, available, media_appear, rating
            FROM applications
        """)

    elif text == "👨 الذكور":
        cur.execute("""
            SELECT id, full_name, gender, departments, available, media_appear, rating
            FROM applications
            WHERE gender='ذكر'
        """)

    elif text == "👩 الإناث":
        cur.execute("""
            SELECT id, full_name, gender, departments, available, media_appear, rating
            FROM applications
            WHERE gender='أنثى'
        """)

    elif text == "⏰ المتفرغين":
        cur.execute("""
            SELECT id, full_name, gender, departments, available, media_appear, rating
            FROM applications
            WHERE available='نعم'
        """)

    elif text == "🎥 الظهور الإعلامي":
        cur.execute("""
            SELECT id, full_name, gender, departments, available, media_appear, rating
            FROM applications
            WHERE media_appear='نعم'
        """)

    elif text == "⭐ التقييمات":
        cur.execute("""
            SELECT id, full_name, gender, departments, available, media_appear, rating
            FROM applications
            WHERE rating!='بدون تقييم'
        """)

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
            f"الأقسام: {row[3]}\n"
            f"متفرغ: {row[4]}\n"
            f"ظهور إعلامي: {row[5]}\n"
            f"التقييم: {row[6]}\n"
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
        entry_points=[
            CommandHandler("start", start),
            CommandHandler("apply", apply),
        ],
        states={
            FULL_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, full_name)],
            BIRTH: [MessageHandler(filters.TEXT & ~filters.COMMAND, birth)],
            GENDER: [MessageHandler(filters.TEXT & ~filters.COMMAND, gender)],
            STUDY: [MessageHandler(filters.TEXT & ~filters.COMMAND, study)],
            STUDY_DETAILS: [MessageHandler(filters.TEXT & ~filters.COMMAND, study_details)],
            EXPERIENCE: [MessageHandler(filters.TEXT & ~filters.COMMAND, experience)],
            EXPERIENCE_PLACE: [MessageHandler(filters.TEXT & ~filters.COMMAND, experience_place)],
            LANGUAGES: [MessageHandler(filters.TEXT & ~filters.COMMAND, languages)],
            DEPARTMENTS: [MessageHandler(filters.TEXT & ~filters.COMMAND, departments)],
            HAS_BIKE: [MessageHandler(filters.TEXT & ~filters.COMMAND, has_bike)],
            MEDIA_SKILLS: [MessageHandler(filters.TEXT & ~filters.COMMAND, media_skills)],
            AVAILABLE: [MessageHandler(filters.TEXT & ~filters.COMMAND, available)],
            MEDIA_APPEAR: [MessageHandler(filters.TEXT & ~filters.COMMAND, media_appear)],
            SALARY: [MessageHandler(filters.TEXT & ~filters.COMMAND, salary)],
            PROVINCE: [MessageHandler(filters.TEXT & ~filters.COMMAND, province)],
            ADDRESS: [MessageHandler(filters.TEXT & ~filters.COMMAND, address)],
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
