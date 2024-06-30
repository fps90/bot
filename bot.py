import telebot
import threading
import smtplib
import time
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage

API_TOKEN = '5793326527:AAHkcE3j6xEmi-mN9mN6uSq84ev2G1bPERw'
bot = telebot.TeleBot(API_TOKEN)

admins = [YOUR_ADMIN_ID]
admin_data = {}
sending_active = {}
sending_threads = {}
sent_counts = {}
failed_emails = {}

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "مرحبًا بك! استخدم الأوامر للتحكم في إعدادات البريد الإلكتروني.")

@bot.message_handler(commands=['set_email_list'])
def set_email_list(message):
    msg = bot.send_message(message.chat.id, "أرسل قائمة عناوين البريد الإلكتروني، مفصولة بفواصل.")
    bot.register_next_step_handler(msg, process_email_list_step)

def process_email_list_step(message):
    if message.chat.id not in admins:
        bot.send_message(message.chat.id, "البوت خاص بالمشتركين فقط.")
        return
    email_list = message.text.split(',')
    admin_data[message.chat.id] = admin_data.get(message.chat.id, {})
    admin_data[message.chat.id]['email_list'] = email_list
    bot.send_message(message.chat.id, "تم تعيين قائمة عناوين البريد الإلكتروني بنجاح.")

@bot.message_handler(commands=['set_password_list'])
def set_password_list(message):
    msg = bot.send_message(message.chat.id, "أرسل قائمة كلمات المرور، مفصولة بفواصل.")
    bot.register_next_step_handler(msg, process_password_list_step)

def process_password_list_step(message):
    if message.chat.id not in admins:
        bot.send_message(message.chat.id, "البوت خاص بالمشتركين فقط.")
        return
    password_list = message.text.split(',')
    admin_data[message.chat.id] = admin_data.get(message.chat.id, {})
    admin_data[message.chat.id]['password_list'] = password_list
    bot.send_message(message.chat.id, "تم تعيين قائمة كلمات المرور بنجاح.")

@bot.message_handler(commands=['set_subject'])
def set_subject(message):
    msg = bot.send_message(message.chat.id, "أرسل موضوع البريد الإلكتروني.")
    bot.register_next_step_handler(msg, process_subject_step)

def process_subject_step(message):
    if message.chat.id not in admins:
        bot.send_message(message.chat.id, "البوت خاص بالمشتركين فقط.")
        return
    admin_data[message.chat.id] = admin_data.get(message.chat.id, {})
    admin_data[message.chat.id]['subject'] = message.text
    bot.send_message(message.chat.id, "تم تعيين موضوع البريد الإلكتروني بنجاح.")

@bot.message_handler(commands=['set_body'])
def set_body(message):
    msg = bot.send_message(message.chat.id, "أرسل نص البريد الإلكتروني.")
    bot.register_next_step_handler(msg, process_body_step)

def process_body_step(message):
    if message.chat.id not in admins:
        bot.send_message(message.chat.id, "البوت خاص بالمشتركين فقط.")
        return
    admin_data[message.chat.id] = admin_data.get(message.chat.id, {})
    admin_data[message.chat.id]['body'] = message.text
    bot.send_message(message.chat.id, "تم تعيين نص البريد الإلكتروني بنجاح.")

@bot.message_handler(commands=['set_spam_emails'])
def set_spam_emails(message):
    msg = bot.send_message(message.chat.id, "أرسل قائمة العناوين البريدية المراد إرسال الرسائل لها، مفصولة بفواصل.")
    bot.register_next_step_handler(msg, process_spam_emails_step)

def process_spam_emails_step(message):
    if message.chat.id not in admins:
        bot.send_message(message.chat.id, "البوت خاص بالمشتركين فقط.")
        return
    spam_emails = message.text.split(',')
    admin_data[message.chat.id] = admin_data.get(message.chat.id, {})
    admin_data[message.chat.id]['spam_emails'] = spam_emails
    bot.send_message(message.chat.id, "تم تعيين قائمة العناوين البريدية بنجاح.")

@bot.message_handler(commands=['set_sleep'])
def set_sleep(message):
    msg = bot.send_message(message.chat.id, "أرسل مدة الانتظار بين كل رسالة (بالثواني).")
    bot.register_next_step_handler(msg, process_sleep_step)

@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    if message.chat.id not in admins:
        bot.send_message(message.chat.id, "البوت خاص بالمشتركين فقط.")
        return
    file_info = bot.get_file(message.photo[-1].file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    admin_data[message.chat.id] = admin_data.get(message.chat.id, {})
    admin_data[message.chat.id]['image'] = downloaded_file
    bot.send_message(message.chat.id, "تم حفظ الصورة بنجاح.")

def process_sleep_step(message):
    if message.chat.id not in admins:
        bot.send_message(message.chat.id, "البوت خاص بالمشتركين فقط.")
        return
    try:
        sleep_time = int(message.text)
        admin_data[message.chat.id] = admin_data.get(message.chat.id, {})
        admin_data[message.chat.id]['sleep'] = sleep_time
        bot.send_message(message.chat.id, "تم تعيين فترة السليب بنجاح.")
    except ValueError:
        bot.send_message(message.chat.id, "يرجى إرسال عدد صحيح من الثواني.")

@bot.message_handler(commands=['start_sending'])
def start_sending(message):
    if message.chat.id not in admins:
        bot.send_message(message.chat.id, "البوت خاص بالمشتركين فقط.")
        return
    start_sending_emails(message)

@bot.message_handler(commands=['stop_sending'])
def stop_sending(message):
    if message.chat.id not in admins:
        bot.send_message(message.chat.id, "البوت خاص بالمشتركين فقط.")
        return
    stop_sending_emails(message)

@bot.message_handler(commands=['status'])
def status(message):
    if message.chat.id not in admins:
        bot.send_message(message.chat.id, "البوت خاص بالمشتركين فقط.")
        return
    show_sending_status(message)

def display_info(message):
    if message.chat.id not in admins:
        bot.send_message(message.chat.id, "البوت خاص بالمشتركين فقط.")
        return
    info = admin_data.get(message.chat.id, "لا توجد معلومات متاحة.")
    bot.send_message(message.chat.id, f"معلومات الإرسال:\n{info}")

def start_sending_emails(message):
    if message.chat.id in sending_active and sending_active[message.chat.id]:
        bot.send_message(message.chat.id, "الإرسال قيد التنفيذ بالفعل.")
        return
    if message.chat.id in admin_data:
        sending_active[message.chat.id] = True
        sending_threads[message.chat.id] = threading.Thread(target=send_emails, args=(message.chat.id,))
        sending_threads[message.chat.id].start()
        bot.send_message(message.chat.id, "بدأ الإرسال.")
    else:
        bot.send_message(message.chat.id, "لا توجد بيانات للإرسال.")

def stop_sending_emails(message):
    if message.chat.id in sending_active:
        sending_active[message.chat.id] = False
        bot.send_message(message.chat.id, "تم إيقاف الإرسال.")
    else:
        bot.send_message(message.chat.id, "لا يوجد إرسال قيد التنفيذ لإيقافه.")

def show_sending_status(message):
    if message.chat.id in sending_active and sending_active[message.chat.id]:
        status = "الإرسال قيد التنفيذ."
    else:
        status = "لا يوجد إرسال قيد التنفيذ."
    bot.send_message(message.chat.id, status)

def send_emails(admin_id):
    data = admin_data[admin_id]
    email_list = data['email_list']
    password_list = data['password_list']
    subject = data['subject']
    body = data['body']
    sleep_time = data.get('sleep', 1)
    spam_emails = data.get('spam_emails', [])
    image = data.get('image', None)
    sent_counts[admin_id] = 0
    failed_emails[admin_id] = []
    while sending_active[admin_id]:
        for i, spam_email in enumerate(spam_emails):
            if not sending_active[admin_id]:
                break
            try:
                msg = MIMEMultipart()
                msg['From'] = email_list[i % len(email_list)]
                msg['To'] = spam_email
                msg['Subject'] = subject
                msg.attach(MIMEText(body, 'plain'))
                if image:
                    image_attachment = MIMEImage(image)
                    msg.attach(image_attachment)
                server = smtplib.SMTP('smtp.gmail.com', 587)
                server.starttls()
                server.login(email_list[i % len(email_list)], password_list[i % len(password_list)])
                server.sendmail(email_list[i % len(email_list)], spam_email, msg.as_string())
                server.quit()
                sent_counts[admin_id] += 1
                print(f"Email sent to {spam_email}")
            except Exception as e:
                failed_emails[admin_id].append((spam_email, str(e)))
                print(f"Failed to send email to {spam_email}: {e}")
            time.sleep(sleep_time)
        bot.send_message(admin_id, f"تم إرسال {sent_counts[admin_id]} رسالة. الأخطاء: {failed_emails[admin_id]}")

@bot.message_handler(commands=['add_admin'])
def add_admin(message):
    msg = bot.send_message(message.chat.id, "أرسل معرف التليجرام للمسؤول الجديد.")
    bot.register_next_step_handler(msg, process_add_admin_step)

def process_add_admin_step(message):
    try:
        new_admin_id = int(message.text)
        admins.append(new_admin_id)
        bot.send_message(message.chat.id, f"تم إضافة المسؤول بنجاح: {new_admin_id}")
    except ValueError:
        bot.send_message(message.chat.id, "يرجى إرسال معرف تليجرام صالح.")

@bot.message_handler(commands=['remove_admin'])
def remove_admin(message):
    msg = bot.send_message(message.chat.id, "أرسل معرف التليجرام للمسؤول المراد إزالته.")
    bot.register_next_step_handler(msg, process_remove_admin_step)

def process_remove_admin_step(message):
    try:
        remove_admin_id = int(message.text)
        if remove_admin_id in admins:
            admins.remove(remove_admin_id)
            bot.send_message(message.chat.id, f"تمت إزالة المسؤول بنجاح: {remove_admin_id}")
        else:
            bot.send_message(message.chat.id, "المسؤول غير موجود في القائمة.")
    except ValueError:
        bot.send_message(message.chat.id, "يرجى إرسال معرف تليجرام صالح.")

if __name__ == '__main__':
    bot.polling(none_stop=True)
