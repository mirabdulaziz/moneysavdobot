# #!/usr/bin/env python3
“””
Kunlik Foyda Hisoblagich Telegram Bot

Valyuta tekshirish, kopiya, paynet tushumi hisobini yuritadi.
“””
import os
BOT_TOKEN = os.environ.get("BOT_TOKEN", "8801816108:AAGBMJ1S06g...")

import logging
from datetime import date
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import (
Application, CommandHandler, MessageHandler,
filters, ContextTypes, ConversationHandler
)

# ── Sozlamalar ──────────────────────────────────────────────────────────────

   # @BotFather dan olingan token

# Holat konstantalari

(
MAIN_MENU,
PAYNET_INPUT,
VALYUTA_INPUT,
KOPIYA_INPUT,
) = range(4)

# ── Valyuta tekshirish narxini hisoblash ────────────────────────────────────

def valyuta_narxi(dollar: float) -> int:
“””
Qoidalar:
• 0 – 5 000 $   → 50 000 so’m (tekis)
• 5 001 – 70 000 $ → 100 000 so’m (10 000 $ uchun narx, lekin siz
“10 ming dollar = 100 000” dedingiz, shuning uchun
bu oraliqda ham 100 000 so’m qilib qo’yamiz)
• 70 000 $+ → har bir “pochka” (1 000 $) uchun 50 000 so’m
“””
if dollar <= 0:
return 0
elif dollar <= 5_000:
return 50_000
elif dollar <= 70_000:
return 100_000
else:
# 70 000 dan oshgan qismni 1 000 $ (pochka) larga bo’lib hisoblaymiz
pochkalar = (dollar / 1_000)   # necha mingta dollar
return int(pochkalar) * 50_000

# ── Yordamchi funksiyalar ───────────────────────────────────────────────────

def fmt(n: int) -> str:
“”“Raqamni o’qilishi oson formatga o’tkazadi: 1_500_000 → 1 500 000”””
return f”{n:,}”.replace(”,”, “ “)

def get_data(context: ContextTypes.DEFAULT_TYPE) -> dict:
“”“Foydalanuvchi ma’lumotlarini olish (session davomida saqlanadi).”””
d = context.user_data
if “sana” not in d or d[“sana”] != str(date.today()):
d[“sana”] = str(date.today())
d[“paynet”] = 0
d[“valyuta”] = 0
d[“kopiya”] = 0
d[“kopiya_dona”] = 0
d[“valyuta_dollar”] = 0.0
return d

def hisobot(d: dict) -> str:
“”“Kunlik hisobot matnini yaratadi.”””
jami = d[“paynet”] + d[“valyuta”] + d[“kopiya”]
return (
f”📊 *Bugungi hisobot* — {d[‘sana’]}\n”
f”━━━━━━━━━━━━━━━━━━━━\n”
f”💳 Paynet tushumi : *{fmt(d[‘paynet’])} so’m*\n”
f”💵 Valyuta tekshirish ({d[‘valyuta_dollar’]:,.0f} $) : *{fmt(d[‘valyuta’])} so’m*\n”
f”🖨 Kopiya ({d[‘kopiya_dona’]} dona) : *{fmt(d[‘kopiya’])} so’m*\n”
f”━━━━━━━━━━━━━━━━━━━━\n”
f”💰 *JAMI FOYDA : {fmt(jami)} so’m*”
)

# ── Asosiy menyu klaviaturasi ───────────────────────────────────────────────

MENU_KB = ReplyKeyboardMarkup(
[
[KeyboardButton(“💳 Paynet tushumi”), KeyboardButton(“💵 Valyuta tekshirish”)],
[KeyboardButton(“🖨 Kopiya”), KeyboardButton(“📊 Hisobot”)],
[KeyboardButton(“🔄 Kunni yangilash”)],
],
resize_keyboard=True,
)

# ── Handlerlar ──────────────────────────────────────────────────────────────

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
get_data(context)
await update.message.reply_text(
“👋 *Assalomu alaykum!*\n\n”
“Men sizning kunlik foydangizni hisoblayman.\n”
“Quyidagi tugmalardan birini tanlang:”,
parse_mode=“Markdown”,
reply_markup=MENU_KB,
)
return MAIN_MENU

async def menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
text = update.message.text
d = get_data(context)

```
if text == "💳 Paynet tushumi":
    await update.message.reply_text(
        "💳 *Paynet tushumi* qancha? (so'mda yozing)\nMasalan: `500000`",
        parse_mode="Markdown",
    )
    return PAYNET_INPUT

elif text == "💵 Valyuta tekshirish":
    await update.message.reply_text(
        "💵 Necha *dollar* tekshirildi?\nMasalan: `5000`",
        parse_mode="Markdown",
    )
    return VALYUTA_INPUT

elif text == "🖨 Kopiya":
    await update.message.reply_text(
        "🖨 Nechta *kopiya* qilindi?\nMasalan: `3`",
        parse_mode="Markdown",
    )
    return KOPIYA_INPUT

elif text == "📊 Hisobot":
    await update.message.reply_text(hisobot(d), parse_mode="Markdown", reply_markup=MENU_KB)
    return MAIN_MENU

elif text == "🔄 Kunni yangilash":
    context.user_data.clear()
    get_data(context)
    await update.message.reply_text(
        "✅ Kun yangilandi! Barcha hisoblar nolga tushirildi.",
        reply_markup=MENU_KB,
    )
    return MAIN_MENU

else:
    await update.message.reply_text("❓ Iltimos, tugmalardan birini tanlang.", reply_markup=MENU_KB)
    return MAIN_MENU
```

async def paynet_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
d = get_data(context)
try:
miqdor = int(update.message.text.replace(” “, “”).replace(”,”, “”))
d[“paynet”] += miqdor
await update.message.reply_text(
f”✅ Paynet tushumi qo’shildi: *{fmt(miqdor)} so’m*\n\n” + hisobot(d),
parse_mode=“Markdown”,
reply_markup=MENU_KB,
)
except ValueError:
await update.message.reply_text(“❌ Noto’g’ri format. Faqat raqam kiriting:”, reply_markup=MENU_KB)
return MAIN_MENU

async def valyuta_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
d = get_data(context)
try:
dollar = float(update.message.text.replace(” “, “”).replace(”,”, “”))
narx = valyuta_narxi(dollar)
d[“valyuta”] += narx
d[“valyuta_dollar”] += dollar

```
    # Narx qoidasini tushuntirish
    if dollar <= 5_000:
        qoida = "5 000 $ gacha → 50 000 so'm"
    elif dollar <= 70_000:
        qoida = "5 001 – 70 000 $ → 100 000 so'm"
    else:
        pochka = int(dollar / 1_000)
        qoida = f"70 000 $+ → {pochka} ta pochka × 50 000 so'm"

    await update.message.reply_text(
        f"✅ *{dollar:,.0f} $* tekshirildi\n"
        f"📌 Qoida: {qoida}\n"
        f"💵 Haq: *{fmt(narx)} so'm*\n\n" + hisobot(d),
        parse_mode="Markdown",
        reply_markup=MENU_KB,
    )
except ValueError:
    await update.message.reply_text("❌ Noto'g'ri format. Dollar miqdorini kiriting:", reply_markup=MENU_KB)
return MAIN_MENU
```

async def kopiya_input(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
d = get_data(context)
try:
dona = int(update.message.text.replace(” “, “”))
narx = dona * 2_500
d[“kopiya”] += narx
d[“kopiya_dona”] += dona
await update.message.reply_text(
f”✅ *{dona}* ta kopiya → *{fmt(narx)} so’m* (dona boshi 2 500 so’m)\n\n” + hisobot(d),
parse_mode=“Markdown”,
reply_markup=MENU_KB,
)
except ValueError:
await update.message.reply_text(“❌ Noto’g’ri format. Dona sonini kiriting:”, reply_markup=MENU_KB)
return MAIN_MENU

# ── Botni ishga tushirish ───────────────────────────────────────────────────

def main() -> None:
logging.basicConfig(level=logging.INFO)

```
app = Application.builder().token(BOT_TOKEN).build()

conv = ConversationHandler(
    entry_points=[CommandHandler("start", start)],
    states={
        MAIN_MENU: [MessageHandler(filters.TEXT & ~filters.COMMAND, menu_handler)],
        PAYNET_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, paynet_input)],
        VALYUTA_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, valyuta_input)],
        KOPIYA_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, kopiya_input)],
    },
    fallbacks=[CommandHandler("start", start)],
)

app.add_handler(conv)
print("✅ Bot ishga tushdi...")
app.run_polling()
```

if **name** == “**main**”:
main()
