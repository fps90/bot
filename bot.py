import telebot
from telebot import types
import smtplib
import threading
import time

bot_token = '7776128183:AAF_6eLK5vlX_GLfA02BRYX19WB-CZZTBk4'
owner_id = 7925487648
bot = telebot.TeleBot(bot_token)

admins = {}
error_notifications = set()

def initialize_admin_data(admin_id):
    admins[admin_id] = {
        'subject': '',
        'template': '',
        'recipients': [],
        'emails': [],
        'attachment': None,
        'sending': False,
        'sleep_time': 5
    }

def is_admin(user_id):
    return user_id in admins or user_id == owner_id

def send_emails(admin_id):
    admin_data = admins[admin_id]
    while admin_data['sending']:
        for email_detail in admin_data['emails']:
            email_detail = email_detail.strip()
            if not email_detail or ':' not in email_detail:
                bot.send_message(admin_id, f"تنسيق غير صحيح للبريد الإلكتروني وكلمة المرور: {email_detail}")
                continue

            parts = email_detail.split(':')
            if len(parts) != 2:
                bot.send_message(admin_id, f"تنسيق غير صحيح للبريد الإلكتروني وكلمة المرور: {email_detail}")
                continue

            email, password = parts
            try:
                with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
                    server.login(email, password)
                    for recipient in admin_data['recipients']:
                        message = f"Subject: {admin_data['subject']}\n\n{admin_data['template']}"
                        if admin_data['attachment']:
                            with open(admin_data['attachment'], 'rb') as attachment:
                                server.sendmail(email, recipient, message, attachment.read())
                        else:
                            server.sendmail(email, recipient, message)
                        time.sleep(admin_data['sleep_time'])  # Delay between sending emails
            except smtplib.SMTPAuthenticationError:
                if email not in error_notifications:
                    bot.send_message(admin_id, f"فشل تسجيل الدخول للبريد الإلكتروني: {email}")
                    error_notifications.add(email)
                admin_data['emails'].remove(email_detail)
            except Exception as e:
                error_message = f"خطأ أثناء محاولة إرسال البريد من {email} إلى {recipient}: {e}"
                if error_message not in error_notifications:
                    bot.send_message(admin_id, error_message)
                    error_notifications.add(error_message)
        time.sleep(admin_data['sleep_time'])  # Delay between iterations of the sending loop
        

@bot.message_handler(commands=['start'])
def start(message):
    if not is_admin(message.from_user.id):
        bot.send_message(message.chat.id, " - فقط vip @RR8R9 .")
        return

    admin_id = message.from_user.id
    if admin_id not in admins:
        initialize_admin_data(admin_id)

    markup = types.ReplyKeyboardMarkup(row_width=2)
    btn1 = types.KeyboardButton('اضف موضوع')
    btn2 = types.KeyboardButton('اضف كليشة')
    btn3 = types.KeyboardButton('اضف مستلم')
    btn4 = types.KeyboardButton('اضف ايميل')
    btn5 = types.KeyboardButton('بدء الارسال')
    btn6 = types.KeyboardButton('إيقاف الارسال')
    btn7 = types.KeyboardButton('تعيين سليب')
    btn8 = types.KeyboardButton('اضف صورة رفع')
    btn9 = types.KeyboardButton('مسح صورة الرفع')
    btn10 = types.KeyboardButton('عرض المعلومات')
    btn11 = types.KeyboardButton('مسح المعلومات')  # زر جديد لمسح المعلومات
    markup.add(btn1, btn2, btn3, btn4, btn5, btn6, btn7, btn8, btn9, btn10, btn11)

    if message.from_user.id == owner_id:
        btn12 = types.KeyboardButton('إضافة مشرف')
        btn13 = types.KeyboardButton('عرض المشرفين')
        btn14 = types.KeyboardButton('إزالة مشرف')
        markup.add(btn12, btn13, btn14)

    bot.send_message(message.chat.id, "ok :", reply_markup=markup)

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    admin_id = message.from_user.id

    if not is_admin(admin_id):
        bot.send_message(message.chat.id, "لا تملك صلاحيات للوصول إلى هذا الأمر.")
        return

    if admin_id not in admins:
        initialize_admin_data(admin_id)

    admin_data = admins[admin_id]

    if message.text == 'اضف موضوع':
        msg = bot.reply_to(message, "أدخل الموضوع:")
        bot.register_next_step_handler(msg, add_subject)
    elif message.text == 'اضف كليشة':
        msg = bot.reply_to(message, "أدخل الكليشة:")
        bot.register_next_step_handler(msg, add_template)
    elif message.text == 'اضف مستلم':
        msg = bot.reply_to(message, "أدخل عنوان البريد الإلكتروني للمستلم:")
        bot.register_next_step_handler(msg, add_recipient)
    elif message.text == 'اضف ايميل':
        msg = bot.reply_to(message, "أدخل الإيميل وكلمة المرور بصيغة ايميل:باسورد")
        bot.register_next_step_handler(msg, add_email)
    elif message.text == 'بدء الارسال':
        if not admin_data['subject'] or not admin_data['template'] or not admin_data['recipients'] or not admin_data['emails']:
            bot.send_message(message.chat.id, "الرجاء التأكد من إدخال جميع البيانات.")
        else:
            admin_data['sending'] = True
            threading.Thread(target=send_emails, args=(admin_id,)).start()
            bot.send_message(message.chat.id, "تم بدء إرسال الرسائل.")
    elif message.text == 'إيقاف الارسال':
        admin_data['sending'] = False
        bot.send_message(message.chat.id, "تم إيقاف إرسال الرسائل.")
    elif message.text == 'تعيين سليب':
        msg = bot.reply_to(message, "أدخل وقت السليب بالثواني:")
        bot.register_next_step_handler(msg, set_sleep_time)
    elif message.text == 'اضف صورة رفع':
        msg = bot.reply_to(message, "قم بإرسال الصورة:")
        bot.register_next_step_handler(msg, add_attachment)
    elif message.text == 'مسح صورة الرفع':
        admin_data['attachment'] = None
        bot.send_message(message.chat.id, "تم مسح صورة الرفع.")
    elif message.text == 'عرض المعلومات':
        admin_data = admins[admin_id]  # تأكد من أن البيانات محدثة
        info = (
            f"الموضوع: {admin_data['subject']}\n"
            f"الكليشة: {admin_data['template']}\n"
            f"المستلمون: {', '.join(admin_data['recipients'])}\n"
            f"الإيميلات: {', '.join(admin_data['emails'])}\n"
            f"صورة الرفع: {'موجودة' if admin_data['attachment'] else 'غير موجودة'}\n"
            f"وقت السليب: {admin_data['sleep_time']} ثواني"
        )
        bot.send_message(message.chat.id, info)
    elif message.text == 'مسح المعلومات':  # وظيفة لمسح المعلومات
        admins[admin_id] = {
            'subject': '',
            'template': '',
            'recipients': [],
            'emails': [],
            'attachment': None,
            'sending': False,
            'sleep_time': 5
        }
        bot.send_message(message.chat.id, "تم مسح جميع المعلومات.")
    elif message.text == 'إضافة مشرف':
        if message.from_user.id == owner_id:
            msg = bot.reply_to(message, "أدخل معرف المشرف الجديد:")
            bot.register_next_step_handler(msg, add_admin)
    elif message.text == 'عرض المشرفين':
        if message.from_user.id == owner_id:
            show_admins(message)
    elif message.text == 'إزالة مشرف':
        if message.from_user.id == owner_id:
            msg = bot.reply_to(message, "أدخل معرف المشرف الذي تريد إزالته:")
            bot.register_next_step_handler(msg, remove_admin)

def add_subject(message):
    admin_id = message.from_user.id
    admins[admin_id]['subject'] = message.text
    bot.send_message(message.chat.id, "تم إضافة الموضوع.")

def add_template(message):
    admin_id = message.from_user.id
    admins[admin_id]['template'] = message.text
    bot.send_message(message.chat.id, "تم إضافة الكليشة.")

def add_recipient(message):
    admin_id = message.from_user.id
    admins[admin_id]['recipients'].append(message.text)
    bot.send_message(message.chat.id, "تم إضافة المستلم.")

def add_email(message):
    admin_id = message.from_user.id
    email_detail = message.text.strip()
    if ':' in email_detail:
        admins[admin_id]['emails'].append(email_detail)
        bot.send_message(message.chat.id, "تم إضافة الإيميل وكلمة المرور.")
    else:
        bot.send_message(message.chat.id, "الرجاء إدخال الإيميل وكلمة المرور بصيغة صحيحة.")

def set_sleep_time(message):
    admin_id = message.from_user.id
    try:
        admins[admin_id]['sleep_time'] = int(message.text)
        bot.send_message(message.chat.id, f"تم تعيين وقت السليب إلى {admins[admin_id]['sleep_time']} ثواني.")
    except ValueError:
        bot.send_message(message.chat.id, "الرجاء إدخال عدد صحيح.")

def add_attachment(message):
    admin_id = message.from_user.id
    if message.content_type == 'photo':
        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        attachment_path = f"attachment{admin_id}.jpg"
        with open(attachment_path, 'wb') as new_file:
            new_file.write(downloaded_file)
        admins[admin_id]['attachment'] = attachment_path
        bot.send_message(message.chat.id, "تم إضافة صورة الرفع.")
    else:
        bot.send_message(message.chat.id, "يرجى إرسال صورة.")

def add_admin(message):
    if message.from_user.id == owner_id:
        new_admin_id = int(message.text)
        if new_admin_id not in admins:
            initialize_admin_data(new_admin_id)
            bot.send_message(message.chat.id, f"تم إضافة المشرف الجديد بالمعرف {new_admin_id}.")
        else:
            bot.send_message(message.chat.id, "المشرف موجود بالفعل.")

def show_admins(message):
    if message.from_user.id == owner_id:
        admin_list = "\n".join(str(admin) for admin in admins.keys())
        bot.send_message(message.chat.id, f"المشرفين الحاليين:\n{admin_list}")

def remove_admin(message):
    if message.from_user.id == owner_id:
        admin_id = int(message.text)
        if admin_id in admins:
            del admins[admin_id]
            bot.send_message(message.chat.id, f"تم إزالة المشرف بالمعرف {admin_id}.")
        else:
            bot.send_message(message.chat.id, "المشرف غير موجود.")

bot.polling(none_stop=True)
