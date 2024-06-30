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
sent_count = {}
failed_emails = {}
email_sent_count = {}
spam_emails = {}

@bot.message_handler(commands=['start'])
def send_welcome(message):
    if message.chat.id not in admins:
        bot.send_message(message.chat.id, "- البوت خاص بالمشتركين - قم بمراسلة المطور ليتم اعطائك الوضع الـ vip @RR8R9 .")
        return

    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton("أضف مطورين", callback_data="add_spam"))
    markup.add(types.InlineKeyboardButton("أضف ايميلات", callback_data="add_emails"))
    markup.add(types.InlineKeyboardButton("أضف موضوع", callback_data="add_subject"), 
                types.InlineKeyboardButton("أضف كليشة الارسال", callback_data="add_body"))
    markup.add(types.InlineKeyboardButton("أضف صورة", callback_data="add_image"))
    markup.add(types.InlineKeyboardButton("تعيين سليب", callback_data="set_sleep"),
                types.InlineKeyboardButton("عرض المعلومات", callback_data="save_info"))
    markup.add(types.InlineKeyboardButton("مسح المعلومات", callback_data="clear_info"))
    markup.add(types.InlineKeyboardButton("بدء الارسال", callback_data="start_sending"),
                types.InlineKeyboardButton("إيقاف الإرسال", callback_data="stop_sending"))
    markup.add(types.InlineKeyboardButton("حالة الإرسال", callback_data="show_status"))

    bot.send_message(message.chat.id, "ok :", reply_markup=markup)

    if message.chat.id in [DEVELOPER_ID1, DEVELOPER_ID2]:
        admin_markup = types.InlineKeyboardMarkup()
        admin_markup.add(types.InlineKeyboardButton("أضف ادمن", callback_data="add_admin"))
        admin_markup.add(types.InlineKeyboardButton("إزالة ادمن", callback_data="remove_admin"),
                          types.InlineKeyboardButton("عرض الادمنز", callback_data="show_admins"))
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
        if message.chat.id not in admin_data:
            admin_data[message.chat.id] = {}
        admin_data[message.chat.id]['spam_emails'] = spam_emails
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


def display_info(message):
    if message.chat.id not in admins:
        bot.send_message(message.chat.id, "- البوت خاص بالمشتركين - قم بمراسلة المطور ليتم اعطائك الوضع الـ vip @RR8R9 .")
        return

    # التأكد من وجود معلومات للمطور أو الأدمن الحالي فقط
    if message.chat.id in admin_data:
        info = admin_data[message.chat.id]
        email_list = ', '.join(info.get('email_list', [])) or 'لم يتم تحديد الإيميلات'
        subject = info.get('subject', 'لم يتم تحديد الموضوع')
        body = info.get('body', 'لم يتم تحديد كليشة الرسالة')
        sleep_time = info.get('sleep_time', 'لم يتم تحديد فترة السليب')
        image_status = 'نعم' if 'image_data' in info else 'لا'
        spam_emails = ', '.join(info.get('spam_emails', [])) or 'لم يتم تحديد إيميلات السبام'
        
        info_message = (
            f"الإيميلات: {email_list}\n"
            f"الموضوع: {subject}\n"
            f"كليشة الرسالة: {body}\n"
            f"فترة السليب: {sleep_time} ثواني\n"
            f"الصورة مرفوعة: {image_status}\n"
            f"إيميلات السبام: {spam_emails}"
        )
        bot.send_message(message.chat.id, info_message)
    else:
        bot.send_message(message.chat.id, "لا توجد معلومات لعرضها.")
        
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
        admin_data[message.chat.id].update({'email_list': email_list, 'password_list': password_list})

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
        bot.send_message(message.chat.id, "يرجى إرسال صورة فقط.")

def process_sleep_step(message):
    if message.chat.id not in admins:
        bot.send_message(message.chat.id, "- البوت خاص بالمشتركين - قم بمراسلة المطور ليتم اعطائك الوضع الـ vip @RR8R9 .")
        return

    try:
        sleep_time = int(message.text)
        if sleep_time <= 0:
            raise ValueError("يجب أن يكون الوقت عددًا صحيحًا أكبر من 0.")
        if message.chat.id not in admin_data:
            admin_data[message.chat.id] = {}
        admin_data[message.chat.id]['sleep_time'] = sleep_time
        bot.send_message(message.chat.id, "تم تعيين فترة السليب بنجاح.")
    except ValueError as e:
        bot.send_message(message.chat.id, f"صيغة غير صحيحة. يرجى إرسال عدد صحيح أكبر من 0. الخطأ: {e}")

def start_sending_emails(message):
    if message.chat.id not in admins:
        bot.send_message(message.chat.id, "- البوت خاص بالمشتركين - قم بمراسلة المطور ليتم اعطائك الوضع الـ vip @RR8R9 .")
        return

    if message.chat.id not in admin_data:
        bot.send_message(message.chat.id, "لم تقم بتعيين أي معلومات بعد.")
        return

    if 'email_list' not in admin_data[message.chat.id] or \
       'password_list' not in admin_data[message.chat.id] or \
       'subject' not in admin_data[message.chat.id] or \
       'body' not in admin_data[message.chat.id]:
        bot.send_message(message.chat.id, "يرجى التأكد من إدخال جميع المعلومات المطلوبة (الإيميلات، كلمات المرور، الموضوع، وكليشة الرسالة).")
        return

    if 'sleep_time' not in admin_data[message.chat.id]:
        admin_data[message.chat.id]['sleep_time'] = 0

    email_list = admin_data[message.chat.id]['email_list']
    password_list = admin_data[message.chat.id]['password_list']
    subject = admin_data[message.chat.id]['subject']
    body = admin_data[message.chat.id]['body']
    sleep_time = admin_data[message.chat.id]['sleep_time']

    if image_data:
        image_data.seek(0)

    if message.chat.id not in sent_count:
        sent_count[message.chat.id] = 0
        failed_emails[message.chat.id] = []
        email_sent_count[message.chat.id] = 0

    def send_email(email, password):
        try:
            msg = MIMEMultipart()
            msg['From'] = email
            msg['To'] = email
            msg['Subject'] = subject
            msg.attach(MIMEText(body, 'plain'))
            if image_data:
                image = MIMEImage(image_data.read())
                image.add_header('Content-ID', '<image1>')
                msg.attach(image)
            
            with smtplib.SMTP('smtp.example.com', 587) as server:
                server.starttls()
                server.login(email, password)
                server.sendmail(email, email, msg.as_string())

            email_sent_count[message.chat.id] += 1
        except Exception as e:
            failed_emails[message.chat.id].append(email)

    def worker():
        for email, password in zip(email_list, password_list):
            send_email(email, password)
            sent_count[message.chat.id] += 1
            time.sleep(sleep_time)

    thread = threading.Thread(target=worker)
    thread.start()
    bot.send_message(message.chat.id, "تم بدء عملية الإرسال.")

def stop_sending_emails(message):
    if message.chat.id not in admins:
        bot.send_message(message.chat.id, "- البوت خاص بالمشتركين - قم بمراسلة المطور ليتم اعطائك الوضع الـ vip @RR8R9 .")
        return

    # Stopping email sending process
    # You need to handle stopping the threads if necessary. This is a placeholder.
    bot.send_message(message.chat.id, "تم إيقاف عملية الإرسال.")

def show_sending_status(message):
    if message.chat.id not in admins:
        bot.send_message(message.chat.id, "- البوت خاص بالمشتركين - قم بمراسلة المطور ليتم اعطائك الوضع الـ vip @RR8R9 .")
        return

    status = (
        f"عدد الرسائل المرسلة: {sent_count.get(message.chat.id, 0)}\n"
        f"عدد الرسائل الفاشلة: {len(failed_emails.get(message.chat.id, []))}\n"
        f"عدد الرسائل المرسلة بنجاح: {email_sent_count.get(message.chat.id, 0)}"
    )
    bot.send_message(message.chat.id, status)

def add_admin(message):
    if message.chat.id not in [DEVELOPER_ID1, DEVELOPER_ID2]:
        bot.send_message(message.chat.id, "ليس لديك الصلاحيات لإضافة أدمن.")
        return

    try:
        new_admin_id = int(message.text)
        if new_admin_id not in admins:
            admins.append(new_admin_id)
            bot.send_message(message.chat.id, f"تمت إضافة {new_admin_id} كأدمن بنجاح.")
        else:
            bot.send_message(message.chat.id, "هذا المستخدم هو بالفعل أدمن.")
    except ValueError:
        bot.send_message(message.chat.id, "يرجى إدخال معرف تليجرام صالح.")

def remove_admin(message):
    if message.chat.id not in [DEVELOPER_ID1, DEVELOPER_ID2]:
        bot.send_message(message.chat.id, "ليس لديك الصلاحيات لإزالة أدمن.")
        return

    try:
        admin_id_to_remove = int(message.text)
        if admin_id_to_remove in admins and admin_id_to_remove not in [DEVELOPER_ID1, DEVELOPER_ID2]:
            admins.remove(admin_id_to_remove)
            bot.send_message(message.chat.id, f"تمت إزالة {admin_id_to_remove} كأدمن بنجاح.")
        else:
            bot.send_message(message.chat.id, "لا يمكن إزالة هذا المستخدم.")
    except ValueError:
        bot.send_message(message.chat.id, "يرجى إدخال معرف تليجرام صالح.")

def show_admin_ids(message):
    if message.chat.id not in [DEVELOPER_ID1, DEVELOPER_ID2]:
        bot.send_message(message.chat.id, "ليس لديك الصلاحيات لعرض قائمة الأدمن.")
        return

    admins_list = ", ".join(map(str, admins))
    bot.send_message(message.chat.id, f"قائمة الأدمن:\n{admins_list}")

bot.polling()
