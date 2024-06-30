import telebot
from telebot import types
import smtplib
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from io import BytesIO
import threading

bot = telebot.TeleBot("YOUR_BOT_API_KEY")

DEVELOPER_ID1 = 1854384004
DEVELOPER_ID2 = 6388638438
admins = [DEVELOPER_ID1, DEVELOPER_ID2]

admin_data = {}
image_data = None
sending_thread = None
sending_active = False
emails = ["abuse@telegram.org", "Support@telegram.org", "Security@telegram.org", "Dmca@telegram.org", "StopCA@telegram.org"]
send_success_count = 0
email_status = {}

@bot.message_handler(commands=['start'])
def send_welcome(message):
    if message.chat.id not in admins:
        bot.send_message(message.chat.id, "- البوت خاص بالمشتركين - قم بمراسلة المطور ليتم اعطائك الوضع الـ vip @RR8R9 .")
        return
    
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("أضف ايميلات", callback_data="add_emails"))
    markup.add(types.InlineKeyboardButton("أضف موضوع", callback_data="add_subject"))
    markup.add(types.InlineKeyboardButton("أضف كليشة الارسال", callback_data="add_body"))
    markup.add(types.InlineKeyboardButton("أضف صورة", callback_data="add_image"))
    markup.add(types.InlineKeyboardButton("تعيين سليب", callback_data="set_sleep"))
    markup.add(types.InlineKeyboardButton("عرض المعلومات", callback_data="save_info"))
    markup.add(types.InlineKeyboardButton("مسح المعلومات", callback_data="clear_info"))
    markup.add(types.InlineKeyboardButton("بدء الارسال", callback_data="start_sending"))
    markup.add(types.InlineKeyboardButton("إيقاف الإرسال", callback_data="stop_sending"))
    markup.add(types.InlineKeyboardButton("عدد الإرسال", callback_data="set_send_count"))
    markup.add(types.InlineKeyboardButton("الحالة", callback_data="status"))
    bot.send_message(message.chat.id, "ok :", reply_markup=markup)
    
    if message.chat.id in [DEVELOPER_ID1, DEVELOPER_ID2]:
        admin_markup = types.InlineKeyboardMarkup()
        admin_markup.add(types.InlineKeyboardButton("أضف ادمنز", callback_data="add_admin"))
        admin_markup.add(types.InlineKeyboardButton("إزالة ادمنز", callback_data="remove_admin"))
        admin_markup.add(types.InlineKeyboardButton("عرض الادمنز", callback_data="show_admins"))
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
    elif call.data == "set_send_count":
        msg = bot.send_message(call.message.chat.id, "أرسل لي عدد الرسائل التي تريد إرسالها قبل التوقف")
        bot.register_next_step_handler(msg, process_send_count_step)
    elif call.data == "add_admin" and call.message.chat.id in [DEVELOPER_ID1, DEVELOPER_ID2]:
        msg = bot.send_message(call.message.chat.id, "أرسل معرف التليجرام للمستخدم الذي تريد إضافته كأدمن.")
        bot.register_next_step_handler(msg, add_admin)
    elif call.data == "remove_admin" and call.message.chat.id in [DEVELOPER_ID1, DEVELOPER_ID2]:
        msg = bot.send_message(call.message.chat.id, "أرسل معرف التليجرام للمستخدم الذي تريد إزالته من الأدمن.")
        bot.register_next_step_handler(msg, remove_admin)
    elif call.data == "show_admins" and call.message.chat.id in [DEVELOPER_ID1, DEVELOPER_ID2]:
        show_admin_ids(call.message)
    elif call.data == "status":
        show_status(call.message)

def process_send_count_step(message):
    if message.chat.id not in admins:
        bot.send_message(message.chat.id, "- البوت خاص بالمشتركين - قم بمراسلة المطور ليتم اعطائك الوضع الـ vip @RR8R9 .")
        return

    try:
        send_count = int(message.text)
        if message.chat.id not in admin_data:
            admin_data[message.chat.id] = {}
        admin_data[message.chat.id]['send_count'] = send_count
        bot.send_message(message.chat.id, f"تم تعيين عدد الرسائل إلى {send_count}.")
    except ValueError:
        bot.send_message(message.chat.id, "يرجى إدخال عدد صحيح للرسائل.")

def clear_info(message):
    if message.chat.id not in admins:
        bot.send_message(message.chat.id, "- البوت خاص بالمشتركين - قم بمراسلة المطور ليتم اعطائك الوضع الـ vip @RR8R9 .")
        return

    if message.chat.id in admin_data:
        admin_data[message.chat.id].clear()
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
            email_status[email] = "جاهز"

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
        if message.chat.id in admin_data:
            admin_data[message.chat.id]['sleep_time'] = sleep_time
        else:
            admin_data[message.chat.id] = {'sleep_time': sleep_time}
        bot.send_message(message.chat.id, f"تم تعيين فترة السليب إلى {sleep_time} ثانية.")
    except ValueError:
        bot.send_message(message.chat.id, "يرجى إدخال عدد صحيح للفترة.")

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
        bot.send_message(message.chat.id, "لم يتم العثور على صورة. يرجى المحاولة مرة أخرى.")

def display_info(message):
    if message.chat.id not in admins:
        bot.send_message(message.chat.id, "- البوت خاص بالمشتركين - قم بمراسلة المطور ليتم اعطائك الوضع الـ vip @RR8R9 .")
        return

    if message.chat.id in admin_data:
        data = admin_data[message.chat.id]
        info = "المعلومات المحفوظة:\n"
        info += f"الإيميلات: {data.get('email_list', 'غير محدد')}\n"
        info += f"موضوع الرسالة: {data.get('subject', 'غير محدد')}\n"
        info += f"كليشة الرسالة: {data.get('body', 'غير محدد')}\n"
        info += f"فترة السليب: {data.get('sleep_time', 'غير محدد')}\n"
        info += f"عدد الإرسال: {data.get('send_count', 'غير محدد')}\n"
        bot.send_message(message.chat.id, info)
    else:
        bot.send_message(message.chat.id, "لا توجد معلومات محفوظة.")

def add_admin(message):
    try:
        new_admin = int(message.text)
        if new_admin not in admins:
            admins.append(new_admin)
            bot.send_message(message.chat.id, f"تم إضافة المستخدم {new_admin} كأدمن بنجاح.")
        else:
            bot.send_message(message.chat.id, "المستخدم موجود بالفعل كأدمن.")
    except ValueError:
        bot.send_message(message.chat.id, "يرجى إدخال معرف تليجرام صحيح.")

def remove_admin(message):
    try:
        admin_to_remove = int(message.text)
        if admin_to_remove in admins:
            admins.remove(admin_to_remove)
            bot.send_message(message.chat.id, f"تم إزالة المستخدم {admin_to_remove} من قائمة الأدمنز.")
        else:
            bot.send_message(message.chat.id, "المستخدم غير موجود في قائمة الأدمنز.")
    except ValueError:
        bot.send_message(message.chat.id, "يرجى إدخال معرف تليجرام صحيح.")

def show_admin_ids(message):
    if admins:
        admin_ids = "قائمة الأدمنز:\n" + "\n".join(map(str, admins))
        bot.send_message(message.chat.id, admin_ids)
    else:
        bot.send_message(message.chat.id, "لا توجد معرفات أدمنز مسجلة.")

def start_sending_emails(message):
    if message.chat.id not in admins:
        bot.send_message(message.chat.id, "- البوت خاص بالمشتركين - قم بمراسلة المطور ليتم اعطائك الوضع الـ vip @RR8R9 .")
        return

    global sending_active, sending_thread
    if sending_active:
        bot.send_message(message.chat.id, "الإرسال جارٍ بالفعل.")
        return

    if message.chat.id not in admin_data or not all(k in admin_data[message.chat.id] for k in ("email_list", "password_list", "subject", "body")):
        bot.send_message(message.chat.id, "يرجى التأكد من إدخال جميع المعلومات المطلوبة (الإيميلات، الموضوع، كليشة الرسالة).")
        return

    sending_active = True
    sending_thread = threading.Thread(target=send_emails, args=(message.chat.id,))
    sending_thread.start()
    bot.send_message(message.chat.id, "تم بدء الإرسال.")

def stop_sending_emails(message):
    global sending_active
    sending_active = False
    bot.send_message(message.chat.id, "تم إيقاف الإرسال.")

def show_status(message):
    if message.chat.id not in admins:
        bot.send_message(message.chat.id, "- البوت خاص بالمشتركين - قم بمراسلة المطور ليتم اعطائك الوضع الـ vip @RR8R9 .")
        return

    status_message = f"عدد الرسائل المرسلة بنجاح: {send_success_count}\n"
    for email, status in email_status.items():
        status_message += f"{email}: {status}\n"
    bot.send_message(message.chat.id, status_message)

def send_emails(chat_id):
    global send_success_count, sending_active
    data = admin_data[chat_id]
    email_list = data['email_list']
    password_list = data['password_list']
    subject = data['subject']
    body = data['body']
    sleep_time = data.get('sleep_time', 1)  # الافتراضي ثانية واحدة
    send_count = data.get('send_count', 0)  # الافتراضي إرسال غير محدود

    success_count = 0
    while sending_active:
        for i in range(len(email_list)):
            if not sending_active:
                break

            email = email_list[i]
            password = password_list[i]

            try:
                send_email(email, password, emails, subject, body)
                success_count += 1
                email_status[email] = "تم الإرسال بنجاح"
            except Exception as e:
                email_status[email] = f"خطأ: {str(e)}"

            time.sleep(sleep_time)

            if send_count > 0 and success_count >= send_count:
                sending_active = False
                break

    bot.send_message(chat_id, f"تم الانتهاء من عملية الإرسال. عدد الرسائل المرسلة بنجاح: {success_count}")

def send_email(sender_email, sender_password, receiver_emails, subject, body):
    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['Subject'] = subject
    msg.attach(MIMEText(body, 'plain'))

    if image_data:
        image_data.seek(0)
        img = MIMEImage(image_data.read())
        msg.attach(img)

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(sender_email, sender_password)

    for receiver_email in receiver_emails:
        msg['To'] = receiver_email
        server.sendmail(sender_email, receiver_email, msg.as_string())

    server.quit()

bot.polling(none_stop=True)
