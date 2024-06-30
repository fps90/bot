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
sending_threads = {}
sending_active = {}
sent_counts = {}
sent_emails = {}
email_sent_counts = {}
failed_emails = {}
email_send_times = {}
last_send_times = {}
spam_emails = {}

@bot.message_handler(commands=['start'])
def send_welcome(message):
    if message.chat.id not in admins:
        bot.send_message(message.chat.id, "- البوت خاص بالمشتركين - قم بمراسلة المطور ليتم اعطائك الوضع الـ vip @RR8R9 .")
        return

    markup = types.InlineKeyboardMarkup()

    markup.add(types.InlineKeyboardButton("أضف مطورين", callback_data="add_spam"))
    markup.add(types.InlineKeyboardButton("أضف ايميلات", callback_data="add_emails"))
    markup.add(types.InlineKeyboardButton("أضف موضوع", callback_data="add_subject"), types.InlineKeyboardButton("أضف كليشة الارسال", callback_data="add_body"))
    markup.add(types.InlineKeyboardButton("أضف صورة", callback_data="add_image"))
    markup.add(types.InlineKeyboardButton("تعيين سليب", callback_data="set_sleep"), types.InlineKeyboardButton("عرض المعلومات", callback_data="save_info"))
    markup.add(types.InlineKeyboardButton("مسح المعلومات", callback_data="clear_info"))
    markup.add(types.InlineKeyboardButton("بدء الارسال", callback_data="start_sending"), types.InlineKeyboardButton("إيقاف الإرسال", callback_data="stop_sending"))
    markup.add(types.InlineKeyboardButton("حالة الإرسال", callback_data="show_status"))

    bot.send_message(message.chat.id, "ok :", reply_markup=markup)

    if message.chat.id in [DEVELOPER_ID1, DEVELOPER_ID2]:
        admin_markup = types.InlineKeyboardMarkup()
        admin_markup.add(types.InlineKeyboardButton("أضف ادمن", callback_data="add_admin"))
        admin_markup.add(types.InlineKeyboardButton("إزالة ادمن", callback_data="remove_admin"), types.InlineKeyboardButton("عرض الادمنز", callback_data="show_admins"))
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

    if message.content_type == 'photo':
        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)
        image = BytesIO(downloaded_file)

        if message.chat.id in admin_data:
            admin_data[message.chat.id]['image'] = image
        else:
            admin_data[message.chat.id] = {'image': image}

        bot.send_message(message.chat.id, "تم حفظ الصورة بنجاح.")
    else:
        bot.send_message(message.chat.id, "يرجى إرسال صورة فقط.")

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
        bot.send_message(message.chat.id, "يرجى إدخال عدد صحيح.")

def display_info(message):
    if message.chat.id not in admins:
        bot.send_message(message.chat.id, "- البوت خاص بالمشتركين - قم بمراسلة المطور ليتم اعطائك الوضع الـ vip @RR8R9 .")
        return

    info = admin_data.get(message.chat.id, {})
    info_text = "\n".join(f"{key}: {value}" for key, value in info.items())
    bot.send_message(message.chat.id, f"المعلومات الحالية:\n{info_text}")

def start_sending_emails(message):
    if message.chat.id not in admins:
        bot.send_message(message.chat.id, "- البوت خاص بالمشتركين - قم بمراسلة المطور ليتم اعطائك الوضع الـ vip @RR8R9 .")
        return

    if message.chat.id in sending_active and sending_active[message.chat.id]:
        bot.send_message(message.chat.id, "عملية الإرسال جارية بالفعل.")
        return

    sending_active[message.chat.id] = True
    sending_threads[message.chat.id] = threading.Thread(target=send_emails, args=(message.chat.id,))
    sending_threads[message.chat.id].start()
    bot.send_message(message.chat.id, "تم بدء عملية الإرسال.")

def stop_sending_emails(message):
    if message.chat.id not in admins:
        bot.send_message(message.chat.id, "- البوت خاص بالمشتركين - قم بمراسلة المطور ليتم اعطائك الوضع الـ vip @RR8R9 .")
        return

    sending_active[message.chat.id] = False
    if message.chat.id in sending_threads and sending_threads[message.chat.id].is_alive():
        sending_threads[message.chat.id].join()
    bot.send_message(message.chat.id, "تم إيقاف عملية الإرسال.")

def show_sending_status(message):
    if message.chat.id not in admins:
        bot.send_message(message.chat.id, "- البوت خاص بالمشتركين - قم بمراسلة المطور ليتم اعطائك الوضع الـ vip @RR8R9 .")
        return

    status = "جاري الإرسال" if sending_active.get(message.chat.id, False) else "الإرسال متوقف"
    bot.send_message(message.chat.id, f"حالة الإرسال الحالية: {status}")

def send_emails(chat_id):
    if chat_id not in admin_data:
        bot.send_message(chat_id, "لا توجد بيانات للإرسال.")
        return

    email_list = admin_data[chat_id].get('email_list', [])
    password_list = admin_data[chat_id].get('password_list', [])
    subject = admin_data[chat_id].get('subject', '')
    body = admin_data[chat_id].get('body', '')
    image = admin_data[chat_id].get('image', None)
    sleep_time = admin_data[chat_id].get('sleep_time', 1)
    spam_emails_list = admin_data[chat_id].get('spam_emails', [])

    sent_count = 0
    failed_count = 0

    for email, password in zip(email_list, password_list):
        if not sending_active.get(chat_id, False):
            break

        for spam_email in spam_emails_list:
            try:
                msg = MIMEMultipart()
                msg['From'] = email
                msg['To'] = spam_email
                msg['Subject'] = subject
                msg.attach(MIMEText(body, 'plain'))

                if image:
                    image.seek(0)
                    img = MIMEImage(image.read())
                    msg.attach(img)

                server = smtplib.SMTP('smtp.gmail.com', 587)
                server.starttls()
                server.login(email, password)
                server.sendmail(email, spam_email, msg.as_string())
                server.quit()

                sent_count += 1
                bot.send_message(chat_id, f"تم إرسال {sent_count} رسائل بنجاح.")
                time.sleep(sleep_time)
            except Exception as e:
                failed_count += 1
                bot.send_message(chat_id, f"فشل إرسال الرسالة إلى {spam_email}. السبب: {e}")

    bot.send_message(chat_id, f"تم إنهاء عملية الإرسال. تم إرسال {sent_count} رسائل بنجاح، وفشلت {failed_count} رسائل.")
    sending_active[chat_id] = False

def add_admin(message):
    if message.chat.id not in [DEVELOPER_ID1, DEVELOPER_ID2]:
        bot.send_message(message.chat.id, "- هذا الأمر خاص بالمطورين فقط.")
        return

    try:
        new_admin_id = int(message.text)
        admins.append(new_admin_id)
        bot.send_message(message.chat.id, f"تم إضافة المستخدم {new_admin_id} كأدمن.")
    except ValueError:
        bot.send_message(message.chat.id, "يرجى إدخال معرف صحيح.")

def remove_admin(message):
    if message.chat.id not in [DEVELOPER_ID1, DEVELOPER_ID2]:
        bot.send_message(message.chat.id, "- هذا الأمر خاص بالمطورين فقط.")
        return

    try:
        admin_id = int(message.text)
        if admin_id in admins:
            admins.remove(admin_id)
            bot.send_message(message.chat.id, f"تم إزالة المستخدم {admin_id} من الأدمن.")
        else:
            bot.send_message(message.chat.id, "المعرف غير موجود في قائمة الأدمن.")
    except ValueError:
        bot.send_message(message.chat.id, "يرجى إدخال معرف صحيح.")

def show_admin_ids(message):
    if message.chat.id not in [DEVELOPER_ID1, DEVELOPER_ID2]:
        bot.send_message(message.chat.id, "- هذا الأمر خاص بالمطورين فقط.")
        return

    admin_ids = "\n".join(map(str, admins))
    bot.send_message(message.chat.id, f"قائمة الأدمن الحالية:\n{admin_ids}")

if __name__ == "__main__":
    bot.polling(none_stop=True)
