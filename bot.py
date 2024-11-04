import telebot
import marshal
import os

API_TOKEN = os.getenv('API_TOKEN')
bot = telebot.TeleBot(API_TOKEN)

file_name_storage = {}

def encrypt_file(file_path, layers):
    with open(file_path, 'r') as f:
        code = f.read()
    for _ in range(layers):
        code = compile(code, '', 'exec')
        code = marshal.dumps(code)
        code = f"import marshal\nexec(marshal.loads({repr(code)}))"
    base_name = os.path.basename(file_path)
    name, ext = os.path.splitext(base_name)
    encrypted_file_path = os.path.join(os.path.dirname(file_path), f"{name}-encrypted{ext}")
    with open(encrypted_file_path, 'w') as f:
        f.write(code)
    return encrypted_file_path

@bot.message_handler(commands=['start'])
def start_message(message):
    markup = telebot.types.InlineKeyboardMarkup()
    btn = telebot.types.InlineKeyboardButton("🔗", url="https://t.me/ljarl")
    markup.add(btn)
    
    bot.send_message(message.chat.id, "- أهلا عزيزي في بوت تشفير الملفات ارسل الملف الآن بشرط ان يكون py .", reply_markup=markup)

@bot.message_handler(content_types=['document'])
def handle_file(message):
    file_info = bot.get_file(message.document.file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    file_name = message.document.file_name
    with open(file_name, 'wb') as f:
        f.write(downloaded_file)
    file_name_storage[message.chat.id] = file_name
    markup = telebot.types.InlineKeyboardMarkup()
    btn100 = telebot.types.InlineKeyboardButton("100", callback_data='100')
    markup.add(btn100)
    msg = bot.send_message(message.chat.id, "- ارسل الآن عدد طبقات التشفير \n- ملاحظة طبقات التشفير التلقائية هي 100 ⚠️ .", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == '100')
def callback_query(call):
    file_name = file_name_storage.get(call.message.chat.id)
    if file_name:
        process_layers(call.message, file_name, layers=100)
    else:
        bot.send_message(call.message.chat.id, "لم أتمكن من العثور على اسم الملف.")

@bot.message_handler(func=lambda message: message.chat.id in file_name_storage)
def handle_layer_input(message):
    file_name = file_name_storage[message.chat.id]
    try:
        layers = int(message.text)
        if layers < 0 or layers > 100:
            bot.reply_to(message, "الرجاء اختيار عدد طبقات بين 0 و 100.")
            return

        process_layers(message, file_name, layers)
    except ValueError:
        bot.reply_to(message, "الرجاء إدخال عدد صحيح صالح.")

def process_layers(message, file_name, layers):
    encrypted_file_path = encrypt_file(file_name, layers)
    with open(encrypted_file_path, 'rb') as f:
        bot.send_document(message.chat.id, f)

    os.remove(file_name)
    os.remove(encrypted_file_path)
    del file_name_storage[message.chat.id]

bot.infinity_polling()
