import os
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import google.generativeai as genai
from flask import Flask
import threading

# API Keys များကို Environment Variables မှ ယူမည်
BOT_TOKEN = os.environ.get("BOT_TOKEN")
genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))

bot = telebot.TeleBot(BOT_TOKEN)
ai_model = genai.GenerativeModel('gemini-1.5-flash')
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

@bot.message_handler(func=lambda message: message.text and any(kw in message.text.lower() for kw in ["how to reply", "how to answer", "ဘလိုဖြေရမလဲ"]))
def handle_support(message):
    prompt = f"Customer support assistant အနေနဲ့ ဒီမေးခွန်းကို အကောင့်ဖွင့်ခြင်းနှင့် ဗွီဒီယိုအကြောင်းအရာများအတွက် အကောင်းဆုံးဖြေပေးပါ: {message.text}"
    
    response = ai_model.generate_content(prompt)
    
    markup = InlineKeyboardMarkup()
    markup.row(InlineKeyboardButton("🔄 နောက်ထပ်အဖြေ (More)", callback_data="more_answer"))
    
    bot.reply_to(message, response.text, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "more_answer")
def callback_more(call):
    prompt = "အရင်ပေးခဲ့တဲ့ အဖြေနဲ့မတူဘဲ တခြားသော ပိုကောင်းတဲ့ ဖောက်သည်ဝန်ဆောင်မှုအဖြေ တစ်ခုကို ထပ်ပေးပါ။"
    response = ai_model.generate_content(prompt)
    bot.answer_callback_query(call.id, "အဖြေအသစ် ထပ်ထုတ်နေပါပြီ...")
    bot.send_message(call.message.chat.id, response.text)

def run_bot():
    bot.infinity_polling()

if __name__ == "__main__":
    t = threading.Thread(target=run_bot)
    t.start()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
