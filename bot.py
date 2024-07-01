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
image_data = {}
sending_threads = {}
sending_active = {}
sent_counts = {}
sent_emails = {}
email_sent_counts = {}
failed_emails = {}
email_send_times = {}
last_send_times = {}
spam_emails = {}
error_counts = {}
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
            types.InlineKeyboardButton("عرض الأدمنية", callback_data="show_admins")
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
        spam_emails_list = message.text.splitlines()

        if message.chat.id in admin_data:
            admin_data[message.chat.id]['spam_emails'] = spam_emails_list
        else:
            admin_data[message.chat.id] = {'spam_emails': spam_emails_list}

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

def process_image_step(message):
    if message.chat.id not in admins:
        bot.send_message(message.chat.id, "- البوت خاص بالمشتركين - قم بمراسلة المطور ليتم اعطائك الوضع الـ vip @RR8R9 .")
        return

    if message.photo:
        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        image = BytesIO(downloaded_file)

        if message.chat.id in admin_data:
            admin_data[message.chat.id]['image'] = image
        else:
            admin_data[message.chat.id] = {'image': image}

        bot.send_message(message.chat.id, "تم حفظ الصورة بنجاح.")
    else:
        bot.send_message(message.chat.id, "لم يتم إرسال أي صورة. حاول مرة أخرى.")

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
        
        bot.send_message(message.chat.id, "تم تعيين فترة السليب بنجاح.")
    except ValueError:
        bot.send_message(message.chat.id, "صيغة غير صحيحة. يرجى إرسال رقم صحيح.")

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
        image_status = 'نعم' if 'image' in info else 'لا'
        spam_emails = info.get('spam_emails', 'لم يتم تحديد إيميلات السبام')
        bot.send_message(message.chat.id, f"الإيميلات: {email_list}\nالموضوع: {subject}\nكليشة الرسالة: {body}\nفترة السليب: {sleep_time} ثواني\nالصورة مرفوعة: {image_status}\nإيميلات السبام: {spam_emails}")
    else:
        bot.send_message(message.chat.id, "لا توجد معلومات لعرضها.")

def start_sending_emails(message):
    if message.chat.id not in admins:
        bot.send_message(message.chat.id, "- البوت خاص بالمشتركين - قم بمراسلة المطور ليتم اعطائك الوضع الـ vip @RR8R9 .")
        return
    
    if sending_active.get(message.chat.id, False):
        bot.send_message(message.chat.id, "الإرسال قيد التنفيذ بالفعل.")
        return

    if message.chat.id not in admin_data or not admin_data[message.chat.id]:
        bot.send_message(message.chat.id, "لا توجد معلومات كافية للبدء في الإرسال.")
        return

    sending_active[message.chat.id] = True
    sent_counts[message.chat.id] = 0
    sent_emails[message.chat.id] = []
    email_sent_counts[message.chat.id] = {}
    failed_emails[message.chat.id] = []
    email_send_times[message.chat.id] = {}
    last_send_times[message.chat.id] = None

    thread = threading.Thread(target=send_emails, args=(message.chat.id,))
    sending_threads[message.chat.id] = thread
    thread.start()
    bot.send_message(message.chat.id, "تم بدء عملية الإرسال.")

def stop_sending_emails(message):
    if message.chat.id not in admins:
        bot.send_message(message.chat.id, "- البوت خاص بالمشتركين - قم بمراسلة المطور ليتم اعطائك الوضع الـ vip @RR8R9 .")
        return
    
    if not sending_active.get(message.chat.id, False):
        bot.send_message(message.chat.id, "لا توجد عملية إرسال قيد التنفيذ.")
        return

    sending_active[message.chat.id] = False
    bot.send_message(message.chat.id, "تم إيقاف عملية الإرسال.")

def show_sending_status(message):
    if message.chat.id not in admins:
        bot.send_message(message.chat.id, "- البوت خاص بالمشتركين - قم بمراسلة المطور ليتم اعطائك الوضع الـ vip @RR8R9 .")
        return

    if not sending_active.get(message.chat.id, False):
        bot.send_message(message.chat.id, "لا توجد عمليات إرسال نشطة في الوقت الحالي.")
        return

    if message.chat.id not in admin_data or 'email_list' not in admin_data[message.chat.id]:
        bot.send_message(message.chat.id, "لا توجد بيانات للإرسال حاليًا.")
        return

    status_message = f"عدد الرسائل المرسلة: {sent_counts.get(message.chat.id, 0)}\n"

    if email_sent_counts.get(message.chat.id):
        status_message += "توزيع الرسائل على الإيميلات:\n"
        for email, count in email_sent_counts.get(message.chat.id, {}).items():
            status_message += f"{email}: {count} رسالة\n"
    else:
        status_message += "توزيع الرسائل على الإيميلات: لا توجد بيانات\n"

    status_message += "\nحالة الحسابات:\n"
    for email in admin_data[message.chat.id].get('email_list', []):
        if error_counts.get(message.chat.id, {}).get(email, 0) < 5:
            status_message += f"{email}: شغال\n"
        else:
            status_message += f"{email}: لا يتم الإرسال خطأ\n"

    bot.send_message(message.chat.id, status_message)

def send_emails(admin_id):
    global sent_counts, failed_emails, last_send_times, error_counts

    email_list = admin_data[admin_id].get('email_list', [])
    password_list = admin_data[admin_id].get('password_list', [])
    subject = admin_data[admin_id].get('subject', "")
    body = admin_data[admin_id].get('body', "")
    image = admin_data[admin_id].get('image', None)
    sleep_time = admin_data[admin_id].get('sleep_time', 5)
    spam_email_list = admin_data[admin_id].get('spam_emails', [])

    if not email_list or not password_list:
        bot.send_message(admin_id, "لا توجد بيانات كافية لإرسال الرسائل.")
        return

    error_counts[admin_id] = {email: 0 for email in email_list}

    while sending_active.get(admin_id, False):
        for i, (email, password) in enumerate(zip(email_list, password_list)):
            if not sending_active.get(admin_id, False):
                break

            try:
                msg = MIMEMultipart()
                msg['From'] = email
                msg['To'] = ', '.join(spam_email_list)
                msg['Subject'] = subject
                msg.attach(MIMEText(body, 'plain'))

                if image:
                    img = MIMEImage(image.getvalue())
                    img.add_header('Content-ID', '<image1>')
                    msg.attach(img)

                with smtplib.SMTP('smtp.gmail.com', 587, timeout=60) as server:
                    server.starttls()
                    server.login(email, password)
                    server.sendmail(email, spam_email_list, msg.as_string())

                sent_counts[admin_id] += 1
                sent_emails[admin_id].append(email)
                email_sent_counts[admin_id][email] = email_sent_counts[admin_id].get(email, 0) + 1
                email_send_times[admin_id][email] = datetime.datetime.now()
                last_send_times[admin_id] = datetime.datetime.now()
                error_counts[admin_id][email] = 0  # Reset error count on successful send

            except Exception as e:
                failed_emails[admin_id].append((email, str(e)))
                error_counts[admin_id][email] += 1

            time.sleep(sleep_time)
def add_admin(message):
    try:
        new_admin_id = int(message.text)
        if new_admin_id not in admins:
            admins.append(new_admin_id)
            bot.send_message(message.chat.id, "تمت إضافة الأدمن بنجاح.")
        else:
            bot.send_message(message.chat.id, "الأدمن موجود بالفعل.")
    except ValueError:
        bot.send_message(message.chat.id, "معرف تليجرام غير صحيح.")
        
def remove_admin(message):
    try:
        admin_id = int(message.text)
        if admin_id in [DEVELOPER_ID1, DEVELOPER_ID2]:
            bot.send_message(message.chat.id, "- لا يمكنك إزالة نفسك عزيزي المطور .")
            return
        if admin_id in admins:
            admins.remove(admin_id)
            bot.send_message(message.chat.id, f"تمت إزالة المستخدم {admin_id} من قائمة الأدمنز.")
        else:
            bot.send_message(message.chat.id, "لم يتم العثور على هذا المستخدم في قائمة الأدمنز.")
    except ValueError:
        bot.send_message(message.chat.id, "يرجى إدخال معرف صحيح.")


def show_admin_ids(message):
    developer_ids = [DEVELOPER_ID1, DEVELOPER_ID2]
    admins_list = [admin for admin in admins if admin not in developer_ids]
    developer_list = "\n".join(str(dev) for dev in developer_ids)
    admin_list = "\n".join(str(admin) for admin in admins_list)
    response_message = (
        "مطورين البوت :\n" + developer_list + "\n\n" +
        "الأدمنية :\n" + admin_list
    )
    bot.send_message(message.chat.id, response_message)

bot.polling(none_stop=True)
        
