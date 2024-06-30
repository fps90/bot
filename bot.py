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
emails = ["abuse@telegram.org", "Support@telegram.org", "Security@telegram.org", "Dmca@telegram.org", "StopCA@telegram.org"]
sent_count = 0
sent_emails = []
email_sent_count = {}
failed_emails = []
email_send_times = {}
last_send_time = None

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
    markup.add(types.InlineKeyboardButton("حالة الإرسال", callback_data="show_status"))
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
        if message.chat.id in admin_data:
            admin_data[message.chat.id]['image_data'] = image_data
        else:
            admin_data[message.chat.id] = {'image_data': image_data}
        bot.send_message(message.chat.id, "تم حفظ الصورة بنجاح.")
    else:
        bot.send_message(message.chat.id, "يرجى إرسال صورة.")

def display_info(message):
    if message.chat.id not in admins:
        bot.send_message(message.chat.id, "- البوت خاص بالمشتركين - قم بمراسلة المطور ليتم اعطائك الوضع الـ vip @RR8R9 .")
        return

    if message.chat.id in admin_data:
        info = admin_data[message.chat.id]
        email_list = info.get('email_list', 'لم يتم تحديد الإيميلات')
        subject = info.get('subject', 'لم يتم تحديد الموضوع')
        body = info.get('body', 'لم يتم تحديد كليشة الرسالة')
        sleep_time = info.get('sleep_time', 'لم يتم تحديد فترة السليب')
        image_status = 'نعم' if 'image_data' in info else 'لا'
        bot.send_message(message.chat.id, f"الإيميلات: {email_list}\nالموضوع: {subject}\nكليشة الرسالة: {body}\nفترة السليب: {sleep_time} ثواني\nالصورة مرفوعة: {image_status}")
    else:
        bot.send_message(message.chat.id, "لا توجد معلومات لعرضها.")

def start_sending_emails(message):
    global sending_active, sending_thread, sent_count, sent_emails, email_sent_count, last_send_time
    if message.chat.id not in admins:
        bot.send_message(message.chat.id, "- البوت خاص بالمشتركين - قم بمراسلة المطور ليتم اعطائك الوضع الـ vip @RR8R9 .")
        return

    if sending_active:
        bot.send_message(message.chat.id, "الإرسال جاري بالفعل.")
        return

    if message.chat.id not in admin_data or 'email_list' not in admin_data[message.chat.id] or 'subject' not in admin_data[message.chat.id]:
        bot.send_message(message.chat.id, "يرجى تعيين الإيميلات والموضوع أولاً.")
        return

    sending_active = True
    sent_count = 0
    sent_emails = []
    email_sent_count = {email: 0 for email in admin_data[message.chat.id]['email_list']}
    failed_emails = []
    last_send_time = datetime.datetime.now()
    bot.send_message(message.chat.id, "بدء الإرسال...")

    # تعيين فترة السليب الافتراضية إلى 4 ثوانٍ إذا لم يتم تعيينها
    sleep_time = admin_data[message.chat.id].get('sleep_time', 4)

    def send_emails():
        global sent_count, email_sent_count, last_send_time
        while sending_active:
            try:
                for recipient_email in emails:
                    for email, password in zip(admin_data[message.chat.id]['email_list'], admin_data[message.chat.id]['password_list']):
                        try:
                            send_email(email, password, recipient_email, admin_data[message.chat.id].get('subject', ''), admin_data[message.chat.id].get('body', ''), admin_data[message.chat.id].get('image_data', None))
                            sent_count += 1
                            email_sent_count[email] += 1
                        except Exception as e:
                            failed_emails.append(f"حدث خطأ أثناء إرسال الرسالة من {email} إلى {recipient_email}: {e}")
                    time.sleep(sleep_time)
                last_send_time = datetime.datetime.now()
            except Exception as e:
                failed_emails.append(f"حدث خطأ أثناء الإرسال: {e}")

    sending_thread = threading.Thread(target=send_emails)
    sending_thread.start()

def stop_sending_emails(message):
    global sending_active
    if message.chat.id not in admins:
        bot.send_message(message.chat.id, "- البوت خاص بالمشتركين - قم بمراسلة المطور ليتم اعطائك الوضع الـ vip @RR8R9 .")
        return

    sending_active = False
    if sending_thread:
        sending_thread.join()
    bot.send_message(message.chat.id, "تم إيقاف الإرسال.")

def show_sending_status(message):
    global sent_count, email_sent_count, sending_active
    if message.chat.id not in admins:
        bot.send_message(message.chat.id, "- البوت خاص بالمشتركين - قم بمراسلة المطور ليتم اعطائك الوضع الـ vip @RR8R9 .")
        return

    if not sending_active:
        bot.send_message(message.chat.id, "لا توجد عمليات إرسال نشطة في الوقت الحالي.")
        return

    status_message = f"عدد الرسائل المرسلة: {sent_count}\n"
    if email_sent_count:
        status_message += "توزيع الرسائل على الإيميلات:\n"
        for email, count in email_sent_count.items():
            status_message += f"{email}: {count} رسالة(بالثواني)\n"
    else:
        status_message += "توزيع الرسائل على الإيميلات: لا توجد بيانات\n"

    # إضافة حالة الحسابات
    if email_sent_count:
        status_message += "\nحالة الحسابات:\n"
        for email, count in email_sent_count.items():
            status_message += f"{email}: {'شغال' if count > 0 else 'لا يتم الإرسال خطأ'}\n"
    else:
        status_message += "\nحالة الحسابات: لا توجد بيانات"

    bot.send_message(message.chat.id, status_message)
    
def add_admin(message):
    try:
        new_admin_id = int(message.text)
        if new_admin_id not in admins:
            admins.append(new_admin_id)
            bot.send_message(message.chat.id, f"تمت إضافة المستخدم {new_admin_id} كأدمن.")
        else:
            bot.send_message(message.chat.id, "هذا المستخدم موجود بالفعل في قائمة الأدمنز.")
    except ValueError:
        bot.send_message(message.chat.id, "يرجى إدخال معرف صحيح.")

def remove_admin(message):
    try:
        admin_id = int(message.text)
        if admin_id in admins:
            admins.remove(admin_id)
            bot.send_message(message.chat.id, f"تمت إزالة المستخدم {admin_id} من قائمة الأدمنز.")
        else:
            bot.send_message(message.chat.id, "لم يتم العثور على هذا المستخدم في قائمة الأدمنز.")
    except ValueError:
        bot.send_message(message.chat.id, "يرجى إدخال معرف صحيح.")

def show_admin_ids(message):
    admin_ids = "\n".join(str(admin) for admin in admins)
    bot.send_message(message.chat.id, f"قائمة الأدمنز الحالية:\n{admin_ids}")

def send_email(email, password, to_email, subject, body, image_data):
    try:
        msg = MIMEMultipart()
        msg['From'] = email
        msg['To'] = to_email
        msg['Subject'] = subject

        msg.attach(MIMEText(body, 'plain'))

        if image_data:
            image = MIMEImage(image_data.read())
            image.add_header('Content-ID', '<image1>')
            msg.attach(image)
            image_data.seek(0)

        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(email, password)
            text = msg.as_string()
            server.sendmail(email, to_email, text)
    except Exception as e:
        # Log errors but don't notify via bot
        pass

bot.polling(none_stop=True)
