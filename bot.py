import telebot
from telebot import types
import smtplib
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from io import BytesIO
import threading

bot = telebot.TeleBot("YOUR_BOT_TOKEN")

DEVELOPER_ID1 = 1854384004
DEVELOPER_ID2 = 6388638438
admins = [DEVELOPER_ID1, DEVELOPER_ID2]

admin_data = {}
emails = ["abuse@telegram.org", "Support@telegram.org", "Security@telegram.org", "Dmca@telegram.org", "StopCA@telegram.org"]
sleep_time = 4
image_data = None
sending_thread = None
sending_active = False

@bot.message_handler(commands=['start'])
def send_welcome(message):
    if message.chat.id not in admins:
        bot.send_message(message.chat.id, "- البوت خاص بالمشتركين - قم بمراسلة المطور ليتم اعطائك الوضع الـ vip @RR8R9 .")
        return
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("أضف ايميل", callback_data="add_email"))
    markup.add(types.InlineKeyboardButton("أضف موضوع", callback_data="add_subject"))
    markup.add(types.InlineKeyboardButton("أضف كليشة الارسال", callback_data="add_body"))
    markup.add(types.InlineKeyboardButton("أضف صورة", callback_data="add_image"))
    markup.add(types.InlineKeyboardButton("تعيين سليب", callback_data="set_sleep"))
    markup.add(types.InlineKeyboardButton("عرض المعلومات", callback_data="save_info"))
    markup.add(types.InlineKeyboardButton("مسح المعلومات", callback_data="clear_info"))
    markup.add(types.InlineKeyboardButton("بدء الارسال", callback_data="start_sending"))
    markup.add(types.InlineKeyboardButton("إيقاف الإرسال", callback_data="stop_sending"))
    bot.send_message(message.chat.id, "ok :", reply_markup=markup)
    
    if message.chat.id in [DEVELOPER_ID1, DEVELOPER_ID2]:
        admin_markup = types.InlineKeyboardMarkup()
        admin_markup.add(types.InlineKeyboardButton("أضف ادمن", callback_data="add_admin"))
        admin_markup.add(types.InlineKeyboardButton("إزالة ادمن", callback_data="remove_admin"))
        admin_markup.add(types.InlineKeyboardButton("عرض الادمنز", callback_data="show_admins"))
        bot.send_message(message.chat.id, "التحكم :", reply_markup=admin_markup)

@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    if call.message.chat.id not in admins:
        bot.answer_callback_query(call.id, "- البوت خاص بالمشتركين - قم بمراسلة المطور ليتم اعطائك الوضع الـ vip @RR8R9 .")
        return

    if call.data == "add_email":
        msg = bot.send_message(call.message.chat.id, "أرسل لي الإيميلات وكلمات المرور في الصيغة: email,password\nemail2,password2")
        bot.register_next_step_handler(msg, process_email_step)
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
    elif call.data == "add_admin" and call.message.chat.id in [DEVELOPER_ID1, DEVELOPER_ID2]:
        msg = bot.send_message(call.message.chat.id, "أرسل معرف التليجرام للمستخدم الذي تريد إضافته كأدمن.")
        bot.register_next_step_handler(msg, add_admin)
    elif call.data == "remove_admin" and call.message.chat.id in [DEVELOPER_ID1, DEVELOPER_ID2]:
        msg = bot.send_message(call.message.chat.id, "أرسل معرف التليجرام للمستخدم الذي تريد إزالته من الأدمن.")
        bot.register_next_step_handler(msg, remove_admin)
    elif call.data == "show_admins" and call.message.chat.id in [DEVELOPER_ID1, DEVELOPER_ID2]:
        show_admin_ids(call.message)

def clear_info(message):
    if message.chat.id not in admins:
        bot.send_message(message.chat.id, "- البوت خاص بالمشتركين - قم بمراسلة المطور ليتم اعطائك الوضع الـ vip @RR8R9 .")
        return

    if message.chat.id in admin_data:
        admin_data[message.chat.id].pop('email_list', None)
        admin_data[message.chat.id].pop('password_list', None)
        admin_data[message.chat.id].pop('subject', None)
        admin_data[message.chat.id].pop('body', None)
        admin_data[message.chat.id].pop('sleep_time', None)
        admin_data[message.chat.id].pop('image_data', None)
        bot.send_message(message.chat.id, "تم مسح جميع المعلومات بنجاح.")
    else:
        bot.send_message(message.chat.id, "لا توجد معلومات لحذفها.")

def process_email_step(message):
    if message.chat.id not in admins:
        bot.send_message(message.chat.id, "- البوت خاص بالمشتركين - قم بمراسلة المطور ليتم اعطائك الوضع الـ vip @RR8R9 .")
        return

    try:
        emails_passwords = message.text.split('\n')
        email_list = []
        password_list = []
        for entry in emails_passwords:
            email, password = entry.split(',')
            email_list.append(email.strip())
            password_list.append(password.strip())
        admin_data[message.chat.id] = {'email_list': email_list, 'password_list': password_list}
        bot.send_message(message.chat.id, "تم حفظ الإيميلات وكلمات المرور بنجاح.")
    except ValueError:
        bot.send_message(message.chat.id, "صيغة غير صحيحة. يرجى الإرسال بالصورة الصحيحة: email,password\nemail2,password2")

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

def process_sleep_step(message):
    if message.chat.id not in admins:
        bot.send_message(message.chat.id, "- البوت خاص بالمشتركين - قم بمراسلة المطور ليتم اعطائك الوضع الـ vip @RR8R9 .")
        return

    try:
        sleep_time = int(message.text)
        if message.chat.id in admin_data:
            admin_data[message.chat.id]['sleep_time'] = sleep_time
        else:
            admin_data[message.chat.id] = {'sleep_time': sleep_time}
        bot.send_message(message.chat.id, f"تم تعيين فترة السليب إلى {sleep_time} ثواني.")
    except ValueError:
        bot.send_message(message.chat.id, "يرجى إدخال قيمة عددية صحيحة.")

def process_image_step(message):
    if message.chat.id not in admins:
        bot.send_message(message.chat.id, "- البوت خاص بالمشتركين - قم بمراسلة المطور ليتم اعطائك الوضع الـ vip @RR8R9 .")
        return

    if message.photo:
        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        global image_data
        image_data = BytesIO(downloaded_file)
        bot.send_message(message.chat.id, "تم حفظ الصورة بنجاح.")
    else:
        bot.send_message(message.chat.id, "يرجى إرسال صورة.")

def start_sending_emails(message):
    global sending_active
    if sending_active:
        bot.send_message(message.chat.id, "الإرسال جاري بالفعل.")
        return

    if message.chat.id not in admin_data:
        bot.send_message(message.chat.id, "يرجى إعداد جميع المعلومات المطلوبة أولاً.")
        return

    sending_active = True
    email_list = admin_data[message.chat.id].get('email_list', [])
    password_list = admin_data[message.chat.id].get('password_list', [])
    subject = admin_data[message.chat.id].get('subject', '')
    body = admin_data[message.chat.id].get('body', '')
    global sleep_time
    sleep_time = admin_data[message.chat.id].get('sleep_time', 4)

    def send_email_thread(email, password):
        try:
            server = smtplib.SMTP('smtp.example.com', 587)
            server.starttls()
            server.login(email, password)

            msg = MIMEMultipart()
            msg['From'] = email
            msg['To'] = ", ".join(emails)
            msg['Subject'] = subject

            msg.attach(MIMEText(body, 'plain'))

            if image_data:
                img = MIMEImage(image_data.read())
                img.add_header('Content-ID', '<image1>')
                msg.attach(img)

            server.sendmail(email, emails, msg.as_string())
            server.quit()

        except Exception as e:
            bot.send_message(message.chat.id, f"حدث خطأ أثناء إرسال الرسالة من {email}: {str(e)}")

    for email, password in zip(email_list, password_list):
        threading.Thread(target=send_email_thread, args=(email, password)).start()
        time.sleep(sleep_time)

    bot.send_message(message.chat.id, "بدأت عملية الإرسال.")

def stop_sending_emails(message):
    global sending_active
    sending_active = False
    bot.send_message(message.chat.id, "تم إيقاف الإرسال.")

def add_admin(message):
    if message.chat.id not in [DEVELOPER_ID1, DEVELOPER_ID2]:
        bot.send_message(message.chat.id, "- البوت خاص بالمشتركين - قم بمراسلة المطور ليتم اعطائك الوضع الـ vip @RR8R9 .")
        return

    try:
        new_admin_id = int(message.text)
        if new_admin_id not in admins:
            admins.append(new_admin_id)
            bot.send_message(message.chat.id, "تم إضافة أدمن جديد بنجاح.")
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
        if admin_id in admins:
            admins.remove(admin_id)
            bot.send_message(message.chat.id, "تم إزالة الأدمن بنجاح.")
        else:
            bot.send_message(message.chat.id, "المستخدم ليس أدمن.")
    except ValueError:
        bot.send_message(message.chat.id, "يرجى إدخال معرف تليجرام صحيح.")

def show_admin_ids(message):
    if message.chat.id not in [DEVELOPER_ID1, DEVELOPER_ID2]:
        bot.send_message(message.chat.id, "- البوت خاص بالمشتركين - قم بمراسلة المطور ليتم اعطائك الوضع الـ vip @RR8R9 .")
        return

    admin_list = ', '.join(str(admin) for admin in admins)
    bot.send_message(message.chat.id, f"معرفات الأدمنز: {admin_list}")

bot.polling(none_stop=True)
