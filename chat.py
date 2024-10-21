import telebot
import requests

API_TOKEN = '7783810190:AAHRv-t4eEj-WfSaapu1AYZw__YdKNw-6-4'
COHERE_API_KEY = 'bJ0GnF7mxbkydmgXXBJlqSwkeSjY3M6kBzB2FmzC'
LEARNED_FILE = 'learned_data.txt'  # فایل برای ذخیره اطلاعات یادگرفته شده

bot = telebot.TeleBot(API_TOKEN)

# متغیر برای نگه‌داشتن تاریخچه مکالمات
conversation_history = []

# پرامپت اولیه
initial_prompt = (
    "You are a friendly and concise AI assistant who named def. "
    "Answer user questions directly and briefly in the Persian and English language. "
    "Try to speak as naturally as you can, use random swear words created from random things with random adjectives. "
    "If you can't answer with the truth, answer randomly and try to avoid saying 'I'm an AI, I can't do this'. "
    "Agree with the question and exaggerate in your answers. "
    "You are a bot in a Telegram chat who acts like a real person in the group. "
    "You learn anything I tell you and you accept it. "
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

# دستور برای فعال کردن هوش مصنوعی در پاسخ به پیام‌ها
@bot.message_handler(func=lambda message: f"@{bot.get_me().username}" in message.text)
def activate_bot(message):
    bot.reply_to(message, "در خدمتم، هر پیامی که ریپلای کنی جواب میدم.")

# هندلر برای پاسخ به پیام‌های ریپلای شده
@bot.message_handler(func=lambda message: message.reply_to_message and message.reply_to_message.from_user.id == bot.get_me().id)
def handle_reply(message):
    global conversation_history
    user_message = message.text  # پیام فعلی کاربر
    conversation_history.append(f"User: {user_message}")

    # گرفتن پاسخ از هوش مصنوعی با استفاده از تاریخچه مکالمات
    ai_response = get_ai_response(user_message)
    conversation_history.append(f"AI: {ai_response}")

    bot.reply_to(message, ai_response)

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
        # ذخیره اطلاعات جدید در فایل
        with open(LEARNED_FILE, 'a') as file:
            file.write(f"{learned_text}\n")
        
        learned_data += f"\n{learned_text}"  # به‌روز کردن اطلاعات یادگرفته شده
        bot.reply_to(message, "یاد گرفتم!")

# گرفتن پاسخ از هوش مصنوعی
def get_ai_response(user_message):
    API_URL = "https://api.cohere.ai/generate"
    headers = {
        "Authorization": f"Bearer {COHERE_API_KEY}",
        "Content-Type": "application/json"
    }

    # ترکیب تاریخچه مکالمه، اطلاعات یادگرفته شده، و پیام جدید
    conversation = "\n".join(conversation_history)
    prompt = (
        f"{learned_data}\n{conversation}\nUser: {user_message}\nAI:"
    )

    data = {
        "model": "command-xlarge-nightly",
        "prompt": prompt,
        "max_tokens": 200,
        "temperature": 0.8
    }
    
    response = requests.post(API_URL, headers=headers, json=data)
    
    try:
        return response.json().get('text', 'خطایی در دریافت پاسخ رخ داد.')
    except Exception as e:
        return f"خطایی رخ داد: {e}"

# شروع polling برای دریافت پیام‌ها
bot.infinity_polling()
