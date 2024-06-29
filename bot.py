import telebot
from telebot import types
import smtplib
import time
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from io import BytesIO
import threading

bot = telebot.TeleBot("5793326527:AAHkcE3j6xEmi-mN9mN6uSq84ev2G1bPERw")

DEVELOPER_ID = 1854384004
admins = [DEVELOPER_ID]  


admin_data = {}  
email = ""
password = ""
subject = ""
body = ""
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
    bot.send_message(message.chat.id, "اختر أحد الخيارات:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    if call.message.chat.id not in admins:
        bot.answer_callback_query(call.id, "- البوت خاص بالمشتركين - قم بمراسلة المطور ليتم اعطائك الوضع الـ vip @RR8R9 .")
        return

    if call.data == "add_email":
        msg = bot.send_message(call.message.chat.id, "أرسل لي الإيميل وكلمة المرور في الصيغة: email,password")
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
    elif call.data == "add_admin":
        msg = bot.send_message(call.message.chat.id, "أرسل معرف التليجرام للمستخدم الذي تريد إضافته كأدمن.")
        bot.register_next_step_handler(msg, add_admin)
    elif call.data == "remove_admin":
        msg = bot.send_message(call.message.chat.id, "أرسل معرف التليجرام للمستخدم الذي تريد إزالته من الأدمن.")
        bot.register_next_step_handler(msg, remove_admin)
    elif call.data == "show_admins":
        show_admin_ids(call.message)

def clear_info(message):
    if message.chat.id not in admins:
        bot.send_message(message.chat.id, "- البوت خاص بالمشتركين - قم بمراسلة المطور ليتم اعطائك الوضع الـ vip @RR8R9 .")
        return

    if message.chat.id in admin_data:
        admin_data[message.chat.id].pop('email', None)
        admin_data[message.chat.id].pop('password', None)
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
        email, password = message.text.split(',')
        admin_data[message.chat.id] = {'email': email, 'password': password}
        bot.send_message(message.chat.id, "تم حفظ الإيميل وكلمة المرور بنجاح.")
    except ValueError:
        bot.send_message(message.chat.id, "صيغة غير صحيحة. يرجى الإرسال بالصورة الصحيحة: email,password")

def process_subject_step(message):
    if message.chat.id not in admins:
        bot.send_message(message.chat.id, "- - البوت خاص بالمشتركين - قم بمراسلة المطور ليتم اعطائك الوضع الـ vip @RR8R9 .")
        return

    subject = message.text
    if message.chat.id in admin_data:
        admin_data[message.chat.id]['subject'] = subject
    else:
        admin_data[message.chat.id] = {'subject': subject}
    bot.send_message(message.chat.id, "تم حفظ موضوع الرسالة بنجاح.")

def process_body_step(message):
    if message.chat.id not in admins:
        bot.send_message(message.chat.id, "-- البوت خاص بالمشتركين - قم بمراسلة المطور ليتم اعطائك الوضع الـ vip @RR8R9 .")
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
        bot.send_message(message.chat.id, "يرجى إدخال عدد صحيح للثواني.")

def process_image_step(message):
    global image_data
    if message.chat.id not in admins:
        bot.send_message(message.chat.id, "- البوت خاص بالمشتركين - قم بمراسلة المطور ليتم اعطائك الوضع الـ vip @RR8R9 .")
        return

    if message.photo:
        photo_id = message.photo[-1].file_id
        file_info = bot.get_file(photo_id)
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
        bot.send_message(message.chat.id, "لا يمكنك استخدام هذا البوت.")
        return

    if message.chat.id not in admin_data:
        bot.send_message(message.chat.id, "لم تقم بإضافة أي معلومات بعد.")
        return

    admin_info = admin_data.get(message.chat.id, {})
    info = (
        f"الإيميل: {admin_info.get('email', 'لم يتم إضافته')}\n"
        f"كلمة المرور: {admin_info.get('password', 'لم يتم إضافته')}\n"
        f"موضوع الرسالة: {admin_info.get('subject', 'لم يتم إضافته')}\n"
        f"كليشة الرسالة: {admin_info.get('body', 'لم يتم إضافته')}\n"
        f"فترة السليب: {admin_info.get('sleep_time', 'لم يتم تعيينها')} ثواني\n"
        f"صورة مرفقة: {'نعم' if 'image_data' in admin_info else 'لا'}\n"
    )
    bot.send_message(message.chat.id, f"المعلومات المدخلة:\n{info}")

def add_admin(message):
    global admins
    try:
        new_admin_id = int(message.text)
        if new_admin_id not in admins:
            admins.append(new_admin_id)
            admin_data[new_admin_id] = {}
            bot.send_message(message.chat.id, f"{new_admin_id} هو بالفعل أدمن.")
    except ValueError:
        bot.send_message(message.chat.id, "يرجى إدخال معرف صحيح.")

def remove_admin(message):
    global admins
    try:
        admin_id_to_remove = int(message.text)
        if admin_id_to_remove in admins:
            admins.remove(admin_id_to_remove)
            admin_data.pop(admin_id_to_remove, None)
            bot.send_message(message.chat.id, f"تمت إزالة {admin_id_to_remove} من الأدمنين بنجاح.")
        else:
            bot.send_message(message.chat.id, f"{admin_id_to_remove} ليس أدمن.")
    except ValueError:
        bot.send_message(message.chat.id, "يرجى إدخال معرف صحيح.")

def show_admin_ids(message):
    if message.chat.id != DEVELOPER_ID:
        bot.send_message(message.chat.id, "- البوت خاص بالمشتركين - قم بمراسلة المطور ليتم اعطائك الوضع الـ vip @RR8R9 .")
        return

    admin_ids = "\n".join(map(str, admins))
    bot.send_message(message.chat.id, f"معرفات الأدمنين:\n{admin_ids}")

def start_sending_emails(message):
    global sending_active, sending_thread
    if sending_active:
        bot.send_message(message.chat.id, "الإرسال جاري بالفعل.")
        return

    if message.chat.id not in admin_data:
        bot.send_message(message.chat.id, "يرجى إضافة جميع المعلومات قبل بدء الإرسال.")
        return

    bot.send_message(message.chat.id, "بدء الإرسال... ستصلك رسالة عند الانتهاء في حال حدوث خطأ.")
    sending_active = True
    sending_thread = threading.Thread(target=send_emails, args=(message.chat.id,))
    sending_thread.start()

def send_emails(chat_id):
    global sending_active, sleep_time, image_data
    admin_info = admin_data.get(chat_id, {})
    email = admin_info.get('email')
    password = admin_info.get('password')
    subject = admin_info.get('subject')
    body = admin_info.get('body')
    sleep_time = admin_info.get('sleep_time', 4)
    image_data = admin_info.get('image_data')

    if not email or not password or not subject or not body:
        bot.send_message(chat_id, "يرجى إضافة جميع المعلومات قبل بدء الإرسال.")
        sending_active = False
        return

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(email, password)

        while sending_active:
            for recipient in emails:
                if not sending_active:
                    break

                msg = MIMEMultipart()
                msg['From'] = email
                msg['To'] = recipient
                msg['Subject'] = subject

                msg.attach(MIMEText(body, 'plain'))

                if image_data:
                    image = MIMEImage(image_data.getvalue())
                    msg.attach(image)

                try:
                    server.sendmail(email, recipient, msg.as_string())
                except Exception as e:
                    bot.send_message(chat_id, f"تم الانتهاء من عملية الإرسال بسبب خطأ: {str(e)}")
                    sending_active = False
                    break

                time.sleep(sleep_time)

        server.quit()
    except Exception as e:
        bot.send_message(chat_id, f"تم الانتهاء من عملية الإرسال بسبب خطأ: {str(e)}")
    finally:
        sending_active = False

def stop_sending_emails(message):
    global sending_active
    if not sending_active:
        bot.send_message(message.chat.id, "لا يوجد عملية إرسال جارية.")
        return

    sending_active = False
    if sending_thread:
        sending_thread.join()
    bot.send_message(message.chat.id, "تم إيقاف الإرسال.")
    
bot.polling(none_stop=True)
