import os
import logging
from datetime import date
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import (
Application, CommandHandler, MessageHandler,
filters, ContextTypes, ConversationHandler
)

BOT_TOKEN = os.environ.get(“BOT_TOKEN”)

MAIN_MENU, PAYNET_INPUT, VALYUTA_INPUT, KOPIYA_INPUT = range(4)

def valyuta_narxi(dollar):
if dollar <= 0:
return 0
elif dollar <= 5000:
return 50000
elif dollar <= 70000:
return 100000
else:
pochkalar = int(dollar / 1000)
return pochkalar * 50000

def fmt(n):
return “{:,}”.format(n).replace(”,”, “ “)

def get_data(context):
d = context.user_data
if “sana” not in d or d[“sana”] != str(date.today()):
d[“sana”] = str(date.today())
d[“paynet”] = 0
d[“valyuta”] = 0
d[“kopiya”] = 0
d[“kopiya_dona”] = 0
d[“valyuta_dollar”] = 0.0
return d

def hisobot(d):
jami = d[“paynet”] + d[“valyuta”] + d[“kopiya”]
return (
“Bugungi hisobot - “ + d[“sana”] + “\n”
“————————\n”
“Paynet tushumi : “ + fmt(d[“paynet”]) + “ som\n”
“Valyuta (” + str(int(d[“valyuta_dollar”])) + “ $) : “ + fmt(d[“valyuta”]) + “ som\n”
“Kopiya (” + str(d[“kopiya_dona”]) + “ dona) : “ + fmt(d[“kopiya”]) + “ som\n”
“————————\n”
“JAMI FOYDA : “ + fmt(jami) + “ som”
)

MENU_KB = ReplyKeyboardMarkup(
[
[KeyboardButton(“Paynet tushumi”), KeyboardButton(“Valyuta tekshirish”)],
[KeyboardButton(“Kopiya”), KeyboardButton(“Hisobot”)],
[KeyboardButton(“Kunni yangilash”)],
],
resize_keyboard=True,
)

async def start(update, context):
get_data(context)
await update.message.reply_text(
“Assalomu alaykum!\nKunlik foyda hisoblagichga xush kelibsiz.\nQuyidagi tugmalardan birini tanlang:”,
reply_markup=MENU_KB,
)
return MAIN_MENU

async def menu_handler(update, context):
text = update.message.text
d = get_data(context)

```
if text == "Paynet tushumi":
    await update.message.reply_text("Paynet tushumi qancha? (somda yozing)\nMasalan: 500000")
    return PAYNET_INPUT
elif text == "Valyuta tekshirish":
    await update.message.reply_text("Necha dollar tekshirildi?\nMasalan: 5000")
    return VALYUTA_INPUT
elif text == "Kopiya":
    await update.message.reply_text("Nechta kopiya qilindi?\nMasalan: 3")
    return KOPIYA_INPUT
elif text == "Hisobot":
    await update.message.reply_text(hisobot(d), reply_markup=MENU_KB)
    return MAIN_MENU
elif text == "Kunni yangilash":
    context.user_data.clear()
    get_data(context)
    await update.message.reply_text("Kun yangilandi! Barcha hisoblar nolga tushirildi.", reply_markup=MENU_KB)
    return MAIN_MENU
else:
    await update.message.reply_text("Iltimos tugmalardan birini tanlang.", reply_markup=MENU_KB)
    return MAIN_MENU
```

async def paynet_input(update, context):
d = get_data(context)
try:
miqdor = int(update.message.text.replace(” “, “”).replace(”,”, “”))
d[“paynet”] += miqdor
await update.message.reply_text(
“Paynet qoshildi: “ + fmt(miqdor) + “ som\n\n” + hisobot(d),
reply_markup=MENU_KB,
)
except ValueError:
await update.message.reply_text(“Notogri format. Faqat raqam kiriting:”, reply_markup=MENU_KB)
return MAIN_MENU

async def valyuta_input(update, context):
d = get_data(context)
try:
dollar = float(update.message.text.replace(” “, “”).replace(”,”, “”))
narx = valyuta_narxi(dollar)
d[“valyuta”] += narx
d[“valyuta_dollar”] += dollar
await update.message.reply_text(
str(int(dollar)) + “ $ tekshirildi\nHaq: “ + fmt(narx) + “ som\n\n” + hisobot(d),
reply_markup=MENU_KB,
)
except ValueError:
await update.message.reply_text(“Notogri format. Dollar miqdorini kiriting:”, reply_markup=MENU_KB)
return MAIN_MENU

async def kopiya_input(update, context):
d = get_data(context)
try:
dona = int(update.message.text.replace(” “, “”))
narx = dona * 2500
d[“kopiya”] += narx
d[“kopiya_dona”] += dona
await update.message.reply_text(
str(dona) + “ ta kopiya - “ + fmt(narx) + “ som\n\n” + hisobot(d),
reply_markup=MENU_KB,
)
except ValueError:
await update.message.reply_text(“Notogri format. Dona sonini kiriting:”, reply_markup=MENU_KB)
return MAIN_MENU

def main():
logging.basicConfig(level=logging.INFO)
app = Application.builder().token(BOT_TOKEN).build()
conv = ConversationHandler(
entry_points=[CommandHandler(“start”, start)],
states={
MAIN_MENU: [MessageHandler(filters.TEXT & ~filters.COMMAND, menu_handler)],
PAYNET_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, paynet_input)],
VALYUTA_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, valyuta_input)],
KOPIYA_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, kopiya_input)],
},
fallbacks=[CommandHandler(“start”, start)],
)
app.add_handler(conv)
print(“Bot ishga tushdi…”)
app.run_polling()

if **name** == “**main**”:
main()
