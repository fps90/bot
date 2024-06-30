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
        bot.send_message(message.chat.id, "تم حفظ إيميلات الرفع بنجاح.")
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

def process_sleep_step(message):
    if message.chat.id not in admins:
        bot.send_message(message.chat.id, "- البوت خاص بالمشتركين - قم بمراسلة المطور ليتم اعطائك الوضع الـ vip @RR8R9 .")
        return
        
    try:
        sleep_time = int(message.text)
        admin_data[message.chat.id]['sleep_time'] = sleep_time
        bot.send_message(message.chat.id, "تم تعيين فترة السليب بنجاح.")
    except ValueError:
        bot.send_message(message.chat.id, "صيغة غير صحيحة. يرجى إرسال رقم صحيح لفترة السليب.")

def process_image_step(message):
    if message.chat.id not in admins:
        bot.send_message(message.chat.id, "- البوت خاص بالمشتركين - قم بمراسلة المطور ليتم اعطائك الوضع الـ vip @RR8R9 .")
        return

    try:
        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        image = BytesIO(downloaded_file)
        admin_data[message.chat.id]['image'] = image
        bot.send_message(message.chat.id, "تم حفظ الصورة بنجاح.")
    except Exception as e:
        bot.send_message(message.chat.id, f"حدث خطأ أثناء معالجة الصورة: {e}")

def display_info(message):
    if message.chat.id not in admins:
        bot.send_message(message.chat.id, "- البوت خاص بالمشتركين - قم بمراسلة المطور ليتم اعطائك الوضع الـ vip @RR8R9 .")
        return

    if message.chat.id in admin_data:
        data = admin_data[message.chat.id]
        info = "المعلومات الحالية:\n"
        info += f"إيميلات: {data.get('email_list', 'غير محددة')}\n"
        info += f"موضوع: {data.get('subject', 'غير محدد')}\n"
        info += f"كليشة: {data.get('body', 'غير محددة')}\n"
        info += f"فترة السليب: {data.get('sleep_time', 'غير محددة')} ثانية\n"
        info += f"صورة: {'محددة' if 'image' in data else 'غير محددة'}\n"
        bot.send_message(message.chat.id, info)
    else:
        bot.send_message(message.chat.id, "لا توجد معلومات محفوظة.")

def send_email(email, password, recipient, subject, body, image):
    try:
        msg = MIMEMultipart()
        msg['From'] = email
        msg['To'] = recipient
        msg['Subject'] = subject

        msg.attach(MIMEText(body, 'plain'))

        if image:
            image.seek(0)
            img = MIMEImage(image.read())
            msg.attach(img)

        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(email, password)
            server.send_message(msg)

        return True
    except Exception as e:
        return False

def email_sender(chat_id):
    global sending_active, sent_count, last_send_time
    data = admin_data[chat_id]
    email_list = data['email_list']
    password_list = data['password_list']
    recipients = data.get('spam_emails', [])
    subject = data['subject']
    body = data['body']
    image = data.get('image', None)
    sleep_time = data['sleep_time']

    while sending_active:
        for email, password in zip(email_list, password_list):
            for recipient in recipients:
                if not sending_active:
                    break

                success = send_email(email, password, recipient, subject, body, image)
                if success:
                    sent_count += 1
                    sent_emails.append(recipient)
                    email_sent_count[recipient] = email_sent_count.get(recipient, 0) + 1
                    email_send_times[recipient] = datetime.datetime.now()
                else:
                    failed_emails.append(recipient)

                time.sleep(sleep_time)
            if not sending_active:
                break
        last_send_time = datetime.datetime.now()
        time.sleep(sleep_time)

def start_sending_emails(message):
    global sending_active, sending_thread
    if message.chat.id not in admins:
        bot.send_message(message.chat.id, "- البوت خاص بالمشتركين - قم بمراسلة المطور ليتم اعطائك الوضع الـ vip @RR8R9 .")
        return

    if message.chat.id not in admin_data:
        bot.send_message(message.chat.id, "يرجى إدخال جميع المعلومات أولاً.")
        return

    if sending_active:
        bot.send_message(message.chat.id, "الإرسال جاري بالفعل.")
        return

    sending_active = True
    sending_thread = threading.Thread(target=email_sender, args=(message.chat.id,))
    sending_thread.start()
    bot.send_message(message.chat.id, "تم بدء الإرسال.")

def stop_sending_emails(message):
    global sending_active
    if message.chat.id not in admins:
        bot.send_message(message.chat.id, "- البوت خاص بالمشتركين - قم بمراسلة المطور ليتم اعطائك الوضع الـ vip @RR8R9 .")
        return

    sending_active = False
    bot.send_message(message.chat.id, "تم إيقاف الإرسال.")

def show_sending_status(message):
    if message.chat.id not in admins:
        bot.send_message(message.chat.id, "- البوت خاص بالمشتركين - قم بمراسلة المطور ليتم اعطائك الوضع الـ vip @RR8R9 .")
        return

    status = "الحالة الحالية للإرسال:\n"
    status += f"الإرسال {'شغال' if sending_active else 'متوقف'}\n"
    status += f"عدد الرسائل المرسلة: {sent_count}\n"
    status += f"آخر مرة تم فيها الإرسال: {last_send_time}\n"
    bot.send_message(message.chat.id, status)

def add_admin(message):
    try:
        new_admin_id = int(message.text)
        if new_admin_id not in admins:
            admins.append(new_admin_id)
            bot.send_message(message.chat.id, f"تم إضافة المستخدم {new_admin_id} كأدمن.")
        else:
            bot.send_message(message.chat.id, "المستخدم موجود بالفعل كأدمن.")
    except ValueError:
        bot.send_message(message.chat.id, "معرف المستخدم غير صالح.")

def remove_admin(message):
    try:
        remove_admin_id = int(message.text)
        if remove_admin_id in admins:
            admins.remove(remove_admin_id)
            bot.send_message(message.chat.id, f"تم إزالة المستخدم {remove_admin_id} من الأدمن.")
        else:
            bot.send_message(message.chat.id, "المستخدم غير موجود كأدمن.")
    except ValueError:
        bot.send_message(message.chat.id, "معرف المستخدم غير صالح.")

def show_admin_ids(message):
    admin_list = "قائمة الإدمنز:\n" + "\n".join(map(str, admins))
    bot.send_message(message.chat.id, admin_list)

bot.polling(none_stop=True)
