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
spam_emails = []
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

    # الصف العلوي: زر واحد
    markup.add(types.InlineKeyboardButton("أضف سبام", callback_data="add_spam"))

    # الصف الثاني: زران يمين ويسار
    markup.add(
        types.InlineKeyboardButton("أضف ايميلات", callback_data="add_emails"),
        types.InlineKeyboardButton("أضف موضوع", callback_data="add_subject")
    )

    # الصف الثالث: زر واحد
    markup.add(types.InlineKeyboardButton("أضف كليشة الارسال", callback_data="add_body"))

    # الصف الرابع: زران يمين ويسار
    markup.add(
        types.InlineKeyboardButton("أضف صورة", callback_data="add_image"),
        types.InlineKeyboardButton("تعيين سليب", callback_data="set_sleep")
    )

    # الصف الخامس: زر واحد
    markup.add(types.InlineKeyboardButton("عرض المعلومات", callback_data="save_info"))

    # الصف السادس: زران يمين ويسار
    markup.add(
        types.InlineKeyboardButton("مسح المعلومات", callback_data="clear_info"),
        types.InlineKeyboardButton("حالة الإرسال", callback_data="show_status")
    )

    # الصف السابع: زر واحد
    markup.add(types.InlineKeyboardButton("بدء الارسال", callback_data="start_sending"))

    # الصف الثامن: زر واحد
    markup.add(types.InlineKeyboardButton("إيقاف الإرسال", callback_data="stop_sending"))

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

    if call.data == "add_spam":
        msg = bot.send_message(call.message.chat.id, "أرسل لي الإيميلات (كل إيميل في سطر جديد).")
        bot.register_next_step_handler(msg, process_spam_emails_step)
    elif call.data == "add_emails":
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

def process_spam_emails_step(message):
    if message.chat.id not in admins:
        bot.send_message(message.chat.id, "- البوت خاص بالمشتركين - قم بمراسلة المطور ليتم اعطائك الوضع الـ vip @RR8R9 .")
        return

    spam_emails_list = message.text.split('\n')
    if message.chat.id in admin_data:
        if 'spam_emails' in admin_data[message.chat.id]:
            admin_data[message.chat.id]['spam_emails'].extend(spam_emails_list)
        else:
            admin_data[message.chat.id]['spam_emails'] = spam_emails_list
    else:
        admin_data[message.chat.id] = {'spam_emails': spam_emails_list}
    bot.send_message(message.chat.id, "تم حفظ إيميلات السبام بنجاح.")

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
            admin_data[message.chat.id]['email_list'] = email_list
            admin_data[message.chat.id]['password_list'] = password_list
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
        if message.chat.id in admin_data:
            admin_data[message.chat.id]['sleep_time'] = sleep_time
        else:
            admin_data[message.chat.id] = {'sleep_time': sleep_time}
        bot.send_message(message.chat.id, "تم تعيين فترة السليب بنجاح.")
    except ValueError:
        bot.send_message(message.chat.id, "يرجى إرسال رقم صحيح لفترة السليب بالثواني.")

def display_info(message):
    if message.chat.id not in admins:
        bot.send_message(message.chat.id, "- البوت خاص بالمشتركين - قم بمراسلة المطور ليتم اعطائك الوضع الـ vip @RR8R9 .")
        return

    if message.chat.id in admin_data:
        info = admin_data[message.chat.id]
        info_text = "المعلومات المحفوظة:\n"
        if 'spam_emails' in info:
            info_text += f"إيميلات السبام: {', '.join(info['spam_emails'])}\n"
        if 'email_list' in info:
            info_text += f"الإيميلات: {', '.join(info['email_list'])}\n"
        if 'subject' in info:
            info_text += f"موضوع الرسالة: {info['subject']}\n"
        if 'body' in info:
            info_text += f"كليشة الرسالة: {info['body']}\n"
        if 'sleep_time' in info:
            info_text += f"فترة السليب: {info['sleep_time']} ثانية\n"
        if 'image' in info:
            info_text += "الصورة: نعم\n"
        else:
            info_text += "الصورة: لا\n"
        bot.send_message(message.chat.id, info_text)
    else:
        bot.send_message(message.chat.id, "لا توجد معلومات محفوظة.")

def process_image_step(message):
    if message.chat.id not in admins:
        bot.send_message(message.chat.id, "- البوت خاص بالمشتركين - قم بمراسلة المطور ليتم اعطائك الوضع الـ vip @RR8R9 .")
        return

    if message.content_type == 'photo':
        file_info = bot.get_file(message.photo[-1].file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        if message.chat.id in admin_data:
            admin_data[message.chat.id]['image'] = downloaded_file
        else:
            admin_data[message.chat.id] = {'image': downloaded_file}
        bot.send_message(message.chat.id, "تم حفظ الصورة بنجاح.")
    else:
        bot.send_message(message.chat.id, "يرجى إرسال صورة.")

def start_sending_emails(message):
    global sending_thread, sending_active
    if message.chat.id not in admins:
        bot.send_message(message.chat.id, "- البوت خاص بالمشتركين - قم بمراسلة المطور ليتم اعطائك الوضع الـ vip @RR8R9 .")
        return

    if not sending_active:
        sending_active = True
        sending_thread = threading.Thread(target=send_emails, args=(message.chat.id,))
        sending_thread.start()
        bot.send_message(message.chat.id, "تم بدء عملية الإرسال.")
    else:
        bot.send_message(message.chat.id, "عملية الإرسال جارية بالفعل.")

def stop_sending_emails(message):
    global sending_active
    if message.chat.id not in admins:
        bot.send_message(message.chat.id, "- البوت خاص بالمشتركين - قم بمراسلة المطور ليتم اعطائك الوضع الـ vip @RR8R9 .")
        return

    if sending_active:
        sending_active = False
        bot.send_message(message.chat.id, "تم إيقاف عملية الإرسال.")
    else:
        bot.send_message(message.chat.id, "لا توجد عملية إرسال جارية.")

def show_sending_status(message):
    global sending_active, sent_count
    if message.chat.id not in admins:
        bot.send_message(message.chat.id, "- البوت خاص بالمشتركين - قم بمراسلة المطور ليتم اعطائك الوضع الـ vip @RR8R9 .")
        return

    status = "نشط" if sending_active else "غير نشط"
    bot.send_message(message.chat.id, f"حالة الإرسال: {status}\nعدد الرسائل المرسلة: {sent_count}")

def add_admin(message):
    if message.chat.id not in admins:
        bot.send_message(message.chat.id, "- البوت خاص بالمشتركين - قم بمراسلة المطور ليتم اعطائك الوضع الـ vip @RR8R9 .")
        return

    try:
        new_admin_id = int(message.text)
        admins.append(new_admin_id)
        bot.send_message(message.chat.id, "تم إضافة الأدمن بنجاح.")
    except ValueError:
        bot.send_message(message.chat.id, "يرجى إرسال معرف تليجرام صحيح.")

def remove_admin(message):
    if message.chat.id not in admins:
        bot.send_message(message.chat.id, "- البوت خاص بالمشتركين - قم بمراسلة المطور ليتم اعطائك الوضع الـ vip @RR8R9 .")
        return

    try:
        admin_id_to_remove = int(message.text)
        if admin_id_to_remove in admins:
            admins.remove(admin_id_to_remove)
            bot.send_message(message.chat.id, "تم إزالة الأدمن بنجاح.")
        else:
            bot.send_message(message.chat.id, "الأدمن غير موجود.")
    except ValueError:
        bot.send_message(message.chat.id, "يرجى إرسال معرف تليجرام صحيح.")

def show_admin_ids(message):
    if message.chat.id not in admins:
        bot.send_message(message.chat.id, "- البوت خاص بالمشتركين - قم بمراسلة المطور ليتم اعطائك الوضع الـ vip @RR8R9 .")
        return

    admin_ids = "\n".join(map(str, admins))
    bot.send_message(message.chat.id, f"معرفات الأدمنز:\n{admin_ids}")

def send_emails(chat_id):
    global sending_active, sent_count, last_send_time
    if chat_id not in admin_data:
        bot.send_message(chat_id, "لم يتم تعيين البيانات اللازمة للإرسال.")
        return

    data = admin_data[chat_id]
    if 'email_list' not in data or 'password_list' not in data or 'spam_emails' not in data:
        bot.send_message(chat_id, "البيانات غير مكتملة. يرجى تعيين الإيميلات وكلمات المرور وإيميلات السبام.")
        return

    email_list = data['email_list']
    password_list = data['password_list']
    spam_emails = data['spam_emails']
    subject = data.get('subject', "لا يوجد موضوع")
    body = data.get('body', "لا توجد كليشة")
    image = data.get('image')
    sleep_time = data.get('sleep_time', 1)

    while sending_active:
        for email, password in zip(email_list, password_list):
            if not sending_active:
                break

            for spam_email in spam_emails:
                if not sending_active:
                    break

                try:
                    msg = MIMEMultipart()
                    msg['From'] = email
                    msg['To'] = spam_email
                    msg['Subject'] = subject
                    msg.attach(MIMEText(body, 'plain'))

                    if image:
                        image_data = MIMEImage(image, name='image.jpg')
                        msg.attach(image_data)

                    server = smtplib.SMTP('smtp.gmail.com', 587)
                    server.starttls()
                    server.login(email, password)
                    server.sendmail(email, spam_email, msg.as_string())
                    server.quit()

                    sent_count += 1
                    sent_emails.append(spam_email)
                    email_sent_count[spam_email] = email_sent_count.get(spam_email, 0) + 1
                    email_send_times[spam_email] = datetime.datetime.now()

                    last_send_time = datetime.datetime.now()

                    time.sleep(sleep_time)
                except Exception as e:
                    failed_emails.append(spam_email)

if __name__ == "__main__":
    bot.polling(none_stop=True)
