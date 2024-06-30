

import telebot
from telebot import types
import smtplib
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from io import BytesIO
import threading
import datetime

bot = telebot.TeleBot("5793326527:AAHkcE3j6xEmi-mN9mN6uSq84ev2G1bPERw")

DEVELOPER_ID1 = 1854384004
DEVELOPER_ID2 = 6388638438
admins = [DEVELOPER_ID1, DEVELOPER_ID2]

admin_data = {}
sending_thread = None
sending_active = False
sent_count = 0
sent_emails = []
failed_emails = []
email_send_times = {}
last_send_time = None
spam_emails = []

@bot.message_handler(commands=['start'])
def send_welcome(message):
    if message.chat.id not in admins:
        bot.send_message(message.chat.id, "- البوت خاص بالمشتركين - قم بمراسلة المطور ليتم اعطائك الوضع الـ vip @RR8R9 .")
        return

    markup = types.InlineKeyboardMarkup()

    markup.add(types.InlineKeyboardButton("أضف مطورين", callback_data="add_spam"))

    markup.add(types.InlineKeyboardButton("أضف ايميلات", callback_data="add_emails"))

    markup.add(
        types.InlineKeyboardButton("أضف موضوع", callback_data="add_subject"),
        types.InlineKeyboardButton("أضف كليشة الارسال", callback_data="add_body")
    )

    markup.add(types.InlineKeyboardButton("أضف صورة", callback_data="add_image"))

    markup.add(
        types.InlineKeyboardButton("تعيين سليب", callback_data="set_sleep"),
        types.InlineKeyboardButton("عرض المعلومات", callback_data="save_info")
    )

    markup.add(types.InlineKeyboardButton("مسح المعلومات", callback_data="clear_info"))

    markup.add(
        types.InlineKeyboardButton("بدء الارسال", callback_data="start_sending"),
        types.InlineKeyboardButton("إيقاف الإرسال", callback_data="stop_sending")
    )

    markup.add(types.InlineKeyboardButton("حالة الإرسال", callback_data="show_status"))

    bot.send_message(message.chat.id, "ok :", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    if call.message.chat.id not in admins:
        bot.answer_callback_query(call.id, "- البوت خاص بالمشتركين - قم بمراسلة المطور ليتم اعطائك الوضع الـ vip @RR8R9 .")
        return

    if call.data == "add_emails":
        msg = bot.send_message(call.message.chat.id, "أرسل لي الإيميلات وكلمات المرور في الصيغة: email1,password1;email2,password2;...")
        bot.register_next_step_handler(msg, process_emails_step)
    elif call.data == "add_subject":
        msg = bot.send_message(call.message.chat.id, "أرسل لي موضوع الرسالة")
        bot.register_next_step_handler(msg, process_subject_step)
    elif call.data == "add_body":
        msg = bot.send_message(call.message.chat.id, "أرسل لي كليشة الرسالة")
        bot.register_next_step_handler(msg, process_body_step)
    elif call.data == "add_image":
        msg = bot.send_message(call.message.chat.id, "أرسل لي الصورة التي تريد إضافتها")
        bot.register_next_step_handler(msg, process_image_step)
    elif call.data == "set_sleep":
        msg = bot.send_message(call.message.chat.id, "أرسل عدد الثواني لتعيين فترة السليب")
        bot.register_next_step_handler(msg, process_sleep_step)
    elif call.data == "clear_info":
        clear_info(call.message)
    elif call.data == "start_sending":
        start_sending_emails(call.message)
    elif call.data == "stop_sending":
        stop_sending_emails(call.message)
    elif call.data == "show_status":
        show_sending_status(call.message)
    
    # Administrative controls
    elif call.data == "add_admin" and call.message.chat.id in [DEVELOPER_ID1, DEVELOPER_ID2]:
        msg = bot.send_message(call.message.chat.id, "أرسل معرف التليجرام للمستخدم الذي تريد إضافته كأدمن.")
        bot.register_next_step_handler(msg, add_admin)
    elif call.data == "remove_admin" and call.message.chat.id in [DEVELOPER_ID1, DEVELOPER_ID2]:
        msg = bot.send_message(call.message.chat.id, "أرسل معرف التليجرام للمستخدم الذي تريد إزالته من الأدمن.")
        bot.register_next_step_handler(msg, remove_admin)
    elif call.data == "show_admins" and call.message.chat.id in [DEVELOPER_ID1, DEVELOPER_ID2]:
        show_admin_ids(call.message)

def process_emails_step(message):
    if message.chat.id not in admins:
        bot.send_message(message.chat.id, "- البوت خاص بالمشتركين - قم بمراسلة المطور ليتم اعطائك الوضع الـ vip @RR8R9 .")
        return

    try:
        email_entries = message.text.split(';')
        email_list = []
        password_list = []
        for entry in email_entries:
            email, password = entry.split(',')
            email_list.append(email)
            password_list.append(password)

        if message.chat.id not in admin_data:
            admin_data[message.chat.id] = {}

        admin_data[message.chat.id]['email_list'] = email_list
        admin_data[message.chat.id]['password_list'] = password_list

        bot.send_message(message.chat.id, "تم حفظ الإيميلات وكلمات المرور بنجاح.")
    except ValueError:
        bot.send_message(message.chat.id, "صيغة غير صحيحة. يرجى الإرسال بالصورة الصحيحة: email1,password1;email2,password2;...")

def process_subject_step(message):
    if message.chat.id not in admins:
        bot.send_message(message.chat.id, "- البوت خاص بالمشتركين - قم بمراسلة المطور ليتم اعطائك الوضع الـ vip @RR8R9 .")
        return

    subject = message.text
    if message.chat.id not in admin_data:
        admin_data[message.chat.id] = {}

    admin_data[message.chat.id]['subject'] = subject
    bot.send_message(message.chat.id, "تم حفظ موضوع الرسالة بنجاح.")

def process_body_step(message):
    if message.chat.id not in admins:
        bot.send_message(message.chat.id, "- البوت خاص بالمشتركين - قم بمراسلة المطور ليتم اعطائك الوضع الـ vip @RR8R9 .")
        return

    body = message.text
    if message.chat.id not in admin_data:
        admin_data[message.chat.id] = {}

    admin_data[message.chat.id]['body'] = body
    bot.send_message(message.chat.id, "تم حفظ كليشة الرسالة بنجاح.")

def process_sleep_step(message):
    if message.chat.id not in admins:
        bot.send_message(message.chat.id, "- البوت خاص بالمشتركين - قم بمراسلة المطور ليتم اعطائك الوضع الـ vip @RR8R9 .")
        return

    try:
        sleep_time = int(message.text)
        if message.chat.id not in admin_data:
            admin_data[message.chat.id] = {}

        admin_data[message.chat.id]['sleep_time'] = sleep_time
        bot.send_message(message.chat.id, f"تم تعيين فترة السليب إلى {sleep_time} ثواني.")
    except ValueError:
        bot.send_message(message.chat.id, "يرجى إدخال عدد صحيح للثواني.")

def process_image_step(message):
    global image_data
    if message.chat.id not in admins:
        bot.send_message(message.chat.id, "- البوت خاص بالمشتركين - قم بمراسلة المطور ليتم اعطائك الوضع الـ vip @RR8R9 .")
        return

    if message.photo:
        file_info = bot.get_file(message.photo[-1].file_id)
        file = bot.download_file(file_info.file_path)
        image_data = BytesIO(file)
        if message.chat.id not in admin_data:
            admin_data[message.chat.id] = {}

        admin_data[message.chat.id]['image_data'] = image_data
        bot.send_message(message.chat.id, "تم حفظ الصورة بنجاح.")
    else:
        bot.send_message(message.chat.id, "يرجى إرسال صورة للتأكيد.")

def start_sending_emails(message):
    global sending_thread, sending_active
    if message.chat.id not in admins:
        bot.send_message(message.chat.id, "- البوت خاص بالمشتركين - قم بمراسلة المطور ليتم اعطائك الوضع الـ vip @RR8R9 .")
        return

    if sending_active:
        bot.send_message(message.chat.id, "الإرسال قيد التشغيل بالفعل.")
        return

    if message.chat.id not in admin_data:
        bot.send_message(message.chat.id, "لا توجد معلومات للإرسال. يرجى إضافة الإيميلات، الموضوع، والكليشة أولاً.")
        return

    sending_active = True
    sending_thread = threading.Thread(target=send_emails, args=(message.chat.id,))
    sending_thread.start()
    bot.send_message(message.chat.id, "تم بدء الإرسال.")

def stop_sending_emails(message):
    global sending_active
    if message.chat.id not in admins:
        bot.send_message(message.chat.id, "- البوت خاص بالمشتركين - قم بمراسلة المطور ليتم اعطائك الوضع الـ vip @RR8R9 .")
        return

    if not sending_active:
        bot.send_message(message.chat.id, "الإرسال ليس قيد التشغيل.")
        return

    sending_active = False
    bot.send_message(message.chat.id, "تم إيقاف الإرسال.")

def show_sending_status(message):
    if message.chat.id not in admins:
        bot.send_message(message.chat.id, "- البوت خاص بالمشتركين - قم بمراسلة المطور ليتم اعطائك الوضع الـ vip @RR8R9 .")
        return

    status_message = "حالة الإرسال:\n"
    status_message += f"الإرسال قيد التشغيل: {'نعم' if sending_active else 'لا'}\n"
    status_message += f"عدد الرسائل المرسلة: {sent_count}\n"
    status_message += f"الإيميلات المرسلة: {', '.join(sent_emails)}\n"
    status_message += f"الإيميلات التي فشلت: {', '.join(failed_emails)}\n"
    status_message += f"الإيميلات المرسلة إلى قائمة التكرار: {', '.join(spam_emails)}\n"
    bot.send_message(message.chat.id, status_message)

def send_emails(chat_id):
    global sent_count, sent_emails, failed_emails, spam_emails, last_send_time

    if chat_id not in admin_data:
        bot.send_message(chat_id, "لا توجد معلومات للإرسال. يرجى إضافة الإيميلات، الموضوع، والكليشة أولاً.")
        sending_active = False
        return

    email_list = admin_data[chat_id].get('email_list', [])
    password_list = admin_data[chat_id].get('password_list', [])
    subject = admin_data[chat_id].get('subject', '')
    body = admin_data[chat_id].get('body', '')
    image_data = admin_data[chat_id].get('image_data', None)
    sleep_time = admin_data[chat_id].get('sleep_time', 0)

    if not email_list or not password_list or not subject or not body:
        bot.send_message(chat_id, "المعلومات غير مكتملة. يرجى التأكد من إضافة الإيميلات، الموضوع، والكليشة.")
        sending_active = False
        return

    for email, password in zip(email_list, password_list):
        if not sending_active:
            break

        if last_send_time:
            elapsed_time = time.time() - last_send_time
            if elapsed_time < sleep_time:
                time.sleep(sleep_time - elapsed_time)

        try:
            msg = MIMEMultipart()
            msg['From'] = email
            msg['To'] = email
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'plain'))

            if image_data:
                image = MIMEImage(image_data.getvalue())
                image.add_header('Content-ID', '<image1>')
                msg.attach(image)

            server = smtplib.SMTP('smtp.example.com', 587)  # Replace with your SMTP server details
            server.starttls()
            server.login(email, password)
            server.sendmail(email, email, msg.as_string())
            server.quit()

            sent_count += 1
            sent_emails.append(email)
            last_send_time = time.time()
        except Exception as e:
            failed_emails.append(email)
            bot.send_message(chat_id, f"فشل إرسال الرسالة إلى {email}. الخطأ: {str(e)}")

    sending_active = False
    bot.send_message(chat_id, "تم الانتهاء من الإرسال.")

def add_admin(message):
    try:
        new_admin_id = int(message.text)
        if new_admin_id not in admins:
            admins.append(new_admin_id)
            bot.send_message(message.chat.id, f"تمت إضافة {new_admin_id} كأدمن.")
        else:
            bot.send_message(message.chat.id, "المستخدم هو بالفعل أدمن.")
    except ValueError:
        bot.send_message(message.chat.id, "معرف غير صحيح. يرجى إرسال معرف صحيح للمستخدم.")

def remove_admin(message):
    try:
        admin_id_to_remove = int(message.text)
        if admin_id_to_remove in admins and admin_id_to_remove not in [DEVELOPER_ID1, DEVELOPER_ID2]:
            admins.remove(admin_id_to_remove)
            bot.send_message(message.chat.id, f"تمت إزالة {admin_id_to_remove} من الأدمن.")
        else:
            bot.send_message(message.chat.id, "لا يمكن إزالة هذا المستخدم كأدمن.")
    except ValueError:
        bot.send_message(message.chat.id, "معرف غير صحيح. يرجى إرسال معرف صحيح للمستخدم.")

def show_admin_ids(message):
    admin_ids = ", ".join(map(str, admins))
    bot.send_message(message.chat.id, f"قائمة الأدمنز: {admin_ids}")

def clear_info(message):
    if message.chat.id in admin_data:
        admin_data[message.chat.id] = {}
        bot.send_message(message.chat.id, "تم مسح المعلومات.")

bot.polling(none_stop=True)
