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
image_data = None
sending_thread = None
sending_active = False
sent_count = 0
sent_emails = []
email_sent_count = {}
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

    if message.chat.id in [DEVELOPER_ID1, DEVELOPER_ID2]:
        admin_markup = types.InlineKeyboardMarkup()
        admin_markup.add(types.InlineKeyboardButton("أضف ادمن", callback_data="add_admin"))
        admin_markup.add(
            types.InlineKeyboardButton("إزالة ادمن", callback_data="remove_admin"),
            types.InlineKeyboardButton("عرض الادمنز", callback_data="show_admins")
        )
        bot.send_message(message.chat.id, "التحكم :", reply_markup=admin_markup)

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
    elif call.data == "save_info":
        display_info(call.message)
    elif call.data == "clear_info":
        clear_info(call.message)
    elif call.data == "start_sending":
        start_sending_emails(call.message)
    elif call.data == "stop_sending":
        stop_sending_emails(call.message)
    elif call.data == "show_status":
        show_sending_status(call.message)
    elif call.data == "add_spam":  
        msg = bot.send_message(call.message.chat.id, "أرسل لي الإيميلات التي تريد إضافتها (مفصولة بفواصل).")
        bot.register_next_step_handler(msg, process_spam_emails_step)
    elif call.data == "add_admin" and call.message.chat.id in [DEVELOPER_ID1, DEVELOPER_ID2]:
        msg = bot.send_message(call.message.chat.id, "أرسل معرف التليجرام للمستخدم الذي تريد إضافته كأدمن.")
        bot.register_next_step_handler(msg, add_admin)
    elif call.data == "remove_admin" and call.message.chat.id in [DEVELOPER_ID1, DEVELOPER_ID2]:
        msg = bot.send_message(call.message.chat.id, "أرسل معرف التليجرام للمستخدم الذي تريد إزالته من الأدمن.")
        bot.register_next_step_handler(msg, remove_admin)
    elif call.data == "show_admins" and call.message.chat.id in [DEVELOPER_ID1, DEVELOPER_ID2]:
        show_admin_ids(call.message)

def process_spam_emails_step(message):
    if message.chat.id not in admins:
        bot.send_message(message.chat.id, "- البوت خاص بالمشتركين - قم بمراسلة المطور ليتم اعطائك الوضع الـ vip @RR8R9 .")
        return

    try:
        spam_emails = message.text.splitlines()
        if message.chat.id in admin_data:
            admin_data[message.chat.id]['spam_emails'] = spam_emails
        else:
            admin_data[message.chat.id] = {'spam_emails': spam_emails}
        bot.send_message(message.chat.id, "تم حفظ إيميلات السبام بنجاح.")
    except Exception as e:
        bot.send_message(message.chat.id, f"حدث خطأ: {e}")

def clear_info(message):
    if message.chat.id not in admins:
        bot.send_message(message.chat.id, "- البوت خاص بالمشتركين - قم بمراسلة المطور ليتم اعطائك الوضع الـ vip @RR8R9 .")
        return

    if message.chat.id in admin_data:
        admin_data[message.chat.id] = {}  
        bot.send_message(message.chat.id, "تم مسح جميع المعلومات بنجاح.")
    else:
        bot.send_message(message.chat.id, "لا توجد معلومات لحذفها.")

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

        if message.chat.id in admin_data:
            admin_data[message.chat.id].update({'email_list': email_list, 'password_list': password_list})
        else:
            admin_data[message.chat.id] = {'email_list': email_list, 'password_list': password_list}

        bot.send_message(message.chat.id, "تم حفظ الإيميلات وكلمات المرور بنجاح.")
    except ValueError:
        bot.send_message(message.chat.id, "صيغة غير صحيحة. يرجى الإرسال بالصورة الصحيحة: email1,password1;email2,password2;...")

def process_subject_step(message):
    if message.chat.id not in admins:
        bot.send_message(message.chat.id, "- البوت خاص بالمشتركين - قم بمراسلة المطور ليتم اعطائك الوضع الـ vip @RR8R9 .")
        return

    subject = message.text
    if message.chat.id in admin_data:
        admin_data[message.chat.id]['subject'] = subject
    else:
        admin_data[message.chat.id] = {'subject': subject}
    bot.send_message(message.chat.id, "تم حفظ موضوع الرسالة بنجاح.")

def process_body_step(message):
    if message.chat.id not in admins:
        bot.send_message(message.chat.id, "- البوت خاص بالمشتركين - قم بمراسلة المطور ليتم اعطائك الوضع الـ vip @RR8R9 .")
        return

    body = message.text
    if message.chat.id in admin_data:
        admin_data[message.chat.id]['body'] = body
    else:
        admin_data[message.chat.id] = {'body': body}
    bot.send_message(message.chat.id, "تم حفظ كليشة الرسالة بنجاح.")

def process_image_step(message):
    if message.chat.id not in admins:
        bot.send_message(message.chat.id, "- البوت خاص بالمشتركين - قم بمراسلة المطور ليتم اعطائك الوضع الـ vip @RR8R9 .")
        return

    global image_data
    if message.photo:
        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        image_data = BytesIO(downloaded_file)
        bot.send_message(message.chat.id, "تم حفظ الصورة بنجاح.")
    else:
        bot.send_message(message.chat.id, "يرجى إرسال صورة.")

def process_sleep_step(message):
    if message.chat.id not in admins:
        bot.send_message(message.chat.id, "- البوت خاص بالمشتركين - قم بمراسلة المطور ليتم اعطائك الوضع الـ vip @RR8R9 .")
        return

    try:
        sleep_time = int(message.text)
        if sleep_time > 0:
            admin_data[message.chat.id]['sleep_time'] = sleep_time
            bot.send_message(message.chat.id, f"تم تعيين فترة السليب إلى {sleep_time} ثانية.")
        else:
            bot.send_message(message.chat.id, "يرجى إدخال عدد صحيح أكبر من الصفر.")
    except ValueError:
        bot.send_message(message.chat.id, "يرجى إدخال عدد صحيح.")

def display_info(message):
    if message.chat.id not in admins:
        bot.send_message(message.chat.id, "- البوت خاص بالمشتركين - قم بمراسلة المطور ليتم اعطائك الوضع الـ vip @RR8R9 .")
        return

    data = admin_data.get(message.chat.id, {})
    info = (
        f"الإيميلات: {data.get('email_list', [])}\n"
        f"كلمات المرور: {data.get('password_list', [])}\n"
        f"موضوع الرسالة: {data.get('subject', 'غير محدد')}\n"
        f"كليشة الرسالة: {data.get('body', 'غير محدد')}\n"
        f"فترة السليب: {data.get('sleep_time', 'غير محدد')} ثانية\n"
    )
    if image_data:
        info += "الصورة: موجودة\n"
    else:
        info += "الصورة: غير موجودة\n"
    
    bot.send_message(message.chat.id, info)

def start_sending_emails(message):
    global sending_active
    global sending_thread

    if sending_active:
        bot.send_message(message.chat.id, "عملية الإرسال قيد التنفيذ بالفعل.")
        return

    sending_active = True
    sending_thread = threading.Thread(target=send_emails)
    sending_thread.start()
    bot.send_message(message.chat.id, "بدأت عملية الإرسال.")

def stop_sending_emails(message):
    global sending_active

    if not sending_active:
        bot.send_message(message.chat.id, "لا توجد عملية إرسال قيد التشغيل.")
        return

    sending_active = False
    if sending_thread:
        sending_thread.join()
    bot.send_message(message.chat.id, "تم إيقاف عملية الإرسال.")

def show_sending_status(message):
    if sending_active:
        bot.send_message(message.chat.id, f"العملية قيد التشغيل. عدد الإيميلات المرسلة: {sent_count}.")
    else:
        bot.send_message(message.chat.id, "لا توجد عملية إرسال قيد التشغيل.")

def send_emails():
    global sent_count
    global email_sent_count
    global failed_emails
    global last_send_time
    global image_data
    global spam_emails

    if not admins:
        return

    admin_id = list(admins)[0]  # Assuming we use the first admin for sending

    data = admin_data.get(admin_id, {})
    email_list = data.get('email_list', [])
    password_list = data.get('password_list', [])
    subject = data.get('subject', '')
    body = data.get('body', '')
    sleep_time = data.get('sleep_time', 60)

    if not email_list or not password_list:
        return

    for email, password in zip(email_list, password_list):
        if not sending_active:
            break
        try:
            send_email(email, password, subject, body, image_data)
            sent_count += 1
            email_sent_count[email] = email_sent_count.get(email, 0) + 1
            time.sleep(sleep_time)
        except Exception as e:
            failed_emails.append((email, str(e)))

def send_email(email, password, subject, body, image_data):
    msg = MIMEMultipart()
    msg['From'] = email
    msg['To'] = email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    if image_data:
        image = MIMEImage(image_data.read())
        msg.attach(image)

    try:
        with smtplib.SMTP('smtp.example.com', 587) as server:
            server.starttls()
            server.login(email, password)
            server.sendmail(email, email, msg.as_string())
    except Exception as e:
        raise Exception(f"فشل إرسال البريد: {str(e)}")

def add_admin(message):
    if message.chat.id not in [DEVELOPER_ID1, DEVELOPER_ID2]:
        bot.send_message(message.chat.id, "- البوت خاص بالمشتركين - قم بمراسلة المطور ليتم اعطائك الوضع الـ vip @RR8R9 .")
        return

    try:
        new_admin_id = int(message.text)
        if new_admin_id not in admins:
            admins.append(new_admin_id)
            bot.send_message(message.chat.id, f"تم إضافة {new_admin_id} كأدمن بنجاح.")
        else:
            bot.send_message(message.chat.id, "المستخدم هو بالفعل أدمن.")
    except ValueError:
        bot.send_message(message.chat.id, "يرجى إدخال معرف تليجرام صحيح.")

def remove_admin(message):
    if message.chat.id not in [DEVELOPER_ID1, DEVELOPER_ID2]:
        bot.send_message(message.chat.id, "- البوت خاص بالمشتركين - قم بمراسلة المطور ليتم اعطائك الوضع الـ vip @RR8R9 .")
        return

    try:
        admin_id = int(message.text)
        if admin_id in admins and admin_id not in [DEVELOPER_ID1, DEVELOPER_ID2]:
            admins.remove(admin_id)
            bot.send_message(message.chat.id, f"تم إزالة {admin_id} من الأدمنز بنجاح.")
        else:
            bot.send_message(message.chat.id, "لا يمكن إزالة هذا المستخدم أو ليس من الأدمنز.")
    except ValueError:
        bot.send_message(message.chat.id, "يرجى إدخال معرف تليجرام صحيح.")

def show_admin_ids(message):
    if message.chat.id not in [DEVELOPER_ID1, DEVELOPER_ID2]:
        bot.send_message(message.chat.id, "- البوت خاص بالمشتركين - قم بمراسلة المطور ليتم اعطائك الوضع الـ vip @RR8R9 .")
        return

    admin_list = "\n".join(str(admin) for admin in admins)
    bot.send_message(message.chat.id, f"الأدمنز:\n{admin_list}")

bot.polling(none_stop=True)
