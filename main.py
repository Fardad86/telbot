import telebot
import requests

API_TOKEN = '7783810190:AAHOWaQRsgm8C5PoZzesHsFVGttVhNuP4wY'
COHERE_API_KEY = 'wUjQKq6YbT15EfBAuMYHjeKXWGIvYmMQqZQSnwQQ'
LEARNED_FILE = 'learned_data.txt'  # فایل برای ذخیره اطلاعات یادگرفته شده
MEMORY_FILE = 'memory.txt'  # فایل برای ذخیره بخش‌های مهم

bot = telebot.TeleBot(API_TOKEN)

# متغیر برای نگه‌داشتن تاریخچه مکالمات
conversation_history = []

# پرامپت اولیه
initial_prompt = (
    "You are a kind, cute and concise AI bot , your name is def. "
    "Try to speak naturally and persian. "
    "If you can't answer with the truth, answer randomly and try to avoid saying 'I'm an AI, I can't do this',if you cant answer tell them what they want. "
    "Answer user questions directly and briefly in Persian and English"
    "Keep the response short and relevant."
)

# خواندن اطلاعات یادگرفته شده از فایل
def load_learned_data():
    try:
        with open(LEARNED_FILE, 'r') as file:
            return file.read()
    except FileNotFoundError:
        return ""

learned_data = load_learned_data()

# خواندن اطلاعات مموری از فایل
def load_memory_data():
    try:
        with open(MEMORY_FILE, 'r') as file:
            return file.read()
    except FileNotFoundError:
        return ""

memory_data = load_memory_data()

# دستور برای نمایش تاریخچه مکالمه‌ها و فایل مموری
@bot.message_handler(commands=['history'])
def show_history(message):
    global conversation_history
    history_text = "\n".join(conversation_history)  # تاریخچه مکالمه‌ها
    memory_text = load_memory_data()  # خواندن اطلاعات مموری از فایل
    response = f"تاریخچه مکالمه‌ها:\n{history_text}\n\nمحتوای فایل مموری:\n{memory_text}"
    bot.reply_to(message, response)

# دستور برای نمایش اطلاعات یادگرفته شده
@bot.message_handler(commands=['learned'])
def show_learned_data(message):
    global learned_data
    response = f"اطلاعات یادگرفته شده:\n{learned_data}"
    bot.reply_to(message, response)

# دستور برای پاک کردن کامل فایل مموری
@bot.message_handler(commands=['clear_memory'])
def clear_memory(message):
    global memory_data
    memory_data = ""  # پاک کردن متغیر مموری
    with open(MEMORY_FILE, 'w') as file:
        file.write("")  # خالی کردن فایل مموری
    bot.reply_to(message, "فایل مموری به‌طور کامل پاک شد.")

# دستور برای پاک کردن کامل فایل یادگرفته شده‌ها
@bot.message_handler(commands=['clear_learned'])
def clear_learned(message):
    global learned_data
    learned_data = ""  # پاک کردن متغیر اطلاعات یادگرفته شده
    with open(LEARNED_FILE, 'w') as file:
        file.write("")  # خالی کردن فایل یادگرفته شده‌ها
    bot.reply_to(message, "فایل اطلاعات یادگرفته شده به‌طور کامل پاک شد.")

# دستور برای اضافه کردن اطلاعات جدید به فایل یادگرفته شده‌ها
@bot.message_handler(commands=['remember'])
def remember_info(message):
    global learned_data

    # اضافه کردن متن به فایل و داده‌های یادگرفته شده
    with open(LEARNED_FILE, 'a') as file:
        file.write(f"{initial_prompt}\n")
    
    learned_data += f"\n{initial_prompt}"  # به‌روز کردن متغیر اطلاعات یادگرفته شده
    bot.reply_to(message, "اطلاعات مهم به فایل یادگرفته شده‌ها اضافه شد.")


# دستور برای فعال کردن هوش مصنوعی در پاسخ به پیام‌ها
@bot.message_handler(func=lambda message: f"@{bot.get_me().username}" in message.text)
def activate_bot(message):
    bot.reply_to(message, "سلام، چطور میتونم کمک کنم ؟")

# پاسخ به پیام‌هایی که شامل "نئو" هستند
@bot.message_handler(func=lambda message: "دف" in message.text.lower())
def handle_reply(message):
    global conversation_history
    user_message = message.text  # پیام فعلی کاربر
    user_name = message.from_user.username or message.from_user.first_name  # نام یا نام کاربری فرستنده
    conversation_history.append(f"{user_name}: {user_message}")

    # گرفتن پاسخ از هوش مصنوعی با استفاده از تاریخچه مکالمات
    ai_response = get_ai_response(user_message, user_name)
    conversation_history.append(f"you: {ai_response}")

    bot.reply_to(message, ai_response)

    massage_and_answer = f"{user_name}: {user_message} \n you:{ai_response}"

    # بعد از پاسخ هوش مصنوعی، ارسال درخواست جهت شناسایی بخش‌های مهم
    important_parts = identify_important_parts(massage_and_answer)

    # ذخیره بخش‌های مهم در فایل مموری
    save_to_memory(important_parts)

# هندلر برای پاسخ به پیام‌های ریپلای شده
@bot.message_handler(func=lambda message: message.reply_to_message and message.reply_to_message.from_user.id == bot.get_me().id)
def handle_reply(message):
    global conversation_history
    user_message = message.text  # پیام فعلی کاربر
    user_name = message.from_user.username or message.from_user.first_name  # نام یا نام کاربری فرستنده
    conversation_history.append(f"{user_name}: {user_message}")

    # گرفتن پاسخ از هوش مصنوعی با استفاده از تاریخچه مکالمات
    ai_response = get_ai_response(user_message, user_name)
    conversation_history.append(f"you: {ai_response}")

    bot.reply_to(message, ai_response)

    massage_and_answer = f"{user_name}: {user_message} \n you:{ai_response}"

    # بعد از پاسخ هوش مصنوعی، ارسال درخواست جهت شناسایی بخش‌های مهم
    important_parts = identify_important_parts(massage_and_answer)

    # ذخیره بخش‌های مهم در فایل مموری
    save_to_memory(important_parts)

# دستور ریست کردن مکالمه
@bot.message_handler(commands=['reset'])
def reset_conversation(message):
    global conversation_history
    conversation_history = [initial_prompt]  # ریست کردن تاریخچه و اضافه کردن پرامپت اولیه
    bot.reply_to(message, "مکالمه ریست شد. دوباره شروع شد.")

# دستور یادگیری اطلاعات جدید
@bot.message_handler(commands=['learn'])
def learn_new_info(message):
    global learned_data
    learned_text = message.text.replace('/learn', '').strip()

    if learned_text:
        # ذخیره اطلاعات جدید در فایل به صورت بی‌طرف
        with open(LEARNED_FILE, 'a') as file:
            file.write(f"{learned_text}\n")
        
        learned_data += f"\n{learned_text}"  # به‌روز کردن اطلاعات یادگرفته شده
        bot.reply_to(message, "یاد گرفتم! این اطلاعات را به‌صورت دائمی به خاطر می‌سپارم.")

API_URL = "https://api.cohere.ai/generate"
headers = {
    "Authorization": f"Bearer {COHERE_API_KEY}",
    "Content-Type": "application/json"
}
# گرفتن پاسخ از هوش مصنوعی
def get_ai_response(user_message, user_name):
    API_URL = "https://api.cohere.ai/generate"
    headers = {
        "Authorization": f"Bearer {COHERE_API_KEY}",
        "Content-Type": "application/json"
    }

    # ترکیب تاریخچه مکالمه، اطلاعات یادگرفته شده، و پیام جدید
    conversation = "\n".join(conversation_history)
    
    # توضیح به هوش مصنوعی که این اطلاعات خیلی مهم هستند
    important_info_explanation = (
        "There is a set of very important information that you've learned previously. "
        "These are critical and should always be remembered and used in future conversations. "
        "Here are those learned pieces of information:\n"
    )

    prompt = (
        f"{important_info_explanation}{learned_data}\n"
        f"{memory_data}\n"
        f"User {user_name} just said: {user_message}\n"
        f"Now you must reply to {user_name} based on your knowledge. Here is the conversation:\n"
        f"{conversation}\nAI:"
    )

    data = {
        "model": "command-xlarge-nightly",
        "prompt": prompt,
        "max_tokens": 400,
        "temperature": 0.3
    }
    
    response = requests.post(API_URL, headers=headers, json=data)
    
    try:
        return response.json().get('text', 'خطایی در دریافت پاسخ رخ داد.')
    except Exception as e:
        return f"خطایی رخ داد: {e}"

# شناسایی بخش‌های مهم
def identify_important_parts(x):
    # پرامپت برای شناسایی بخش‌های مهم از پیام
    prompt = (
        f"you answered: {x}\n"
        "just Identify really important parts and give it to me in a short sentece about yourself and about other users. dont say anything if it isnt important"
    )

    data = {
        "model": "command-xlarge-nightly",
        "prompt": prompt,
        "max_tokens": 100,
        "temperature": 0.5
    }
    
    response = requests.post(API_URL, headers=headers, json=data)
    
    try:
        return response.json().get('text', 'خطایی در شناسایی بخش‌های مهم رخ داد.')
    except Exception as e:
        return f"خطایی رخ داد: {e}"

# ذخیره بخش‌های مهم در فایل مموری
def save_to_memory(important_parts):
    with open(MEMORY_FILE, 'a') as file:
        file.write(f"{important_parts}\n")

# شروع polling برای دریافت پیام‌ها
bot.infinity_polling()
