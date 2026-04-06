async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    text = update.message.text

    message_id = update.message.message_id

    # Save message
    pending_messages[message_id] = {
        "text": text,
        "user_id": user.id
    }

    # Buttons
    keyboard = [
        [
            InlineKeyboardButton("✅ Approve", callback_data=f"approve_{message_id}"),
            InlineKeyboardButton("❌ Reject", callback_data=f"reject_{message_id}")
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    # Send to admin
    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=f"New message from {user.first_name}:\n\n{text}",
        reply_markup=reply_markup
    )

    await update.message.reply_text("Your message is waiting for approval ⏳")


# When admin clicks button
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data
    action, msg_id = data.split("_")
    msg_id = int(msg_id)

    if msg_id not in pending_messages:
        await query.edit_message_text("Message expired.")
        return

    message_data = pending_messages[msg_id]
    user_id = message_data["user_id"]
    text = message_data["text"]

    if action == "approve":
        # Send message to destination (example: back to user)
        await context.bot.send_message(
            chat_id=user_id,
            text=f"✅ Approved message:\n\n{text}"
        )

        await query.edit_message_text("✅ Message Approved and Sent")

    elif action == "reject":
        await context.bot.send_message(
            chat_id=user_id,
            text="❌ Your message was rejected"
        )

        await query.edit_message_text("❌ Message Rejected")

    # Remove from storage
    del pending_messages[msg_id]


# Run bot
app = ApplicationBuilder().token(BOT_TOKEN).build()

app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
app.add_handler(CallbackQueryHandler(button_handler))

print("Bot running...")
app.run_polling()