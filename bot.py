from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

users = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    users[user_id] = {"balance": 1000, "awaiting_game": None}
    await update.message.reply_text("Привіт! Вітаю в LuckyBot 🎯 Напиши /game щоб почати гру.")

async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    balance = users.get(user_id, {}).get("balance", 0)
    await update.message.reply_text(f"Ваш баланс: {balance} монет.")

async def game(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [["/darts", "/dice"]]
    await update.message.reply_text("Оберіть гру:", reply_markup=ReplyKeyboardMarkup(keyboard, one_time_keyboard=True))

async def darts(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    users[user_id]["awaiting_game"] = "darts"
    balance = users[user_id]["balance"]
    await update.message.reply_text(f"Ваш баланс: {balance} монет. Введіть ставку:")

async def dice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    users[user_id]["awaiting_game"] = "dice"
    balance = users[user_id]["balance"]
    await update.message.reply_text(f"Ваш баланс: {balance} монет. Введіть ставку:")

async def handle_bet(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user_data = users.get(user_id)
    
    if not user_data or not user_data.get("awaiting_game"):
        return
    
    try:
        bet = int(update.message.text)
    except ValueError:
        await update.message.reply_text("Введіть число!")
        return

    if bet <= 0 or bet > user_data["balance"]:
        await update.message.reply_text("Невірна ставка. Спробуйте ще раз.")
        return

    game = user_data["awaiting_game"]

    if game == "darts":
        import random
        throw = random.randint(1, 100)
        if throw >= 80:
            user_data["balance"] += bet
            await update.message.reply_text(f"🎯 Ви кинули {throw} і виграли! Новий баланс: {user_data['balance']}")
        else:
            user_data["balance"] -= bet
            await update.message.reply_text(f"🎯 Ви кинули {throw} і програли. Новий баланс: {user_data['balance']}")
    elif game == "dice":
        import random
        dice = random.randint(1, 6)
        if dice == 6:
            user_data["balance"] += bet * 5
            await update.message.reply_text(f"🎲 Ви кинули {dice} і виграли 5x! Баланс: {user_data['balance']}")
        else:
            user_data["balance"] -= bet
            await update.message.reply_text(f"🎲 Ви кинули {dice} і програли. Баланс: {user_data['balance']}")
    
    user_data["awaiting_game"] = None

app = ApplicationBuilder().token("API").build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("balance", balance))
app.add_handler(CommandHandler("game", game))
app.add_handler(CommandHandler("darts", darts))
app.add_handler(CommandHandler("dice", dice))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_bet))

app.run_polling()
