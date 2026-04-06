async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # This function runs when a user sends a message

    user = update.message.from_user  
    # Get details about the user who sent the message

    text = update.message.text  
    # Get the message text

    message_id = update.message.message_id  
    # Get a unique ID for this message

    # Save message
    pending_messages[message_id] = {
        "text": text,
        "user_id": user.id
    }
    # Store the message and user ID in memory (temporary storage)

    # Buttons
    keyboard = [
        [
            InlineKeyboardButton("✅ Approve", callback_data=f"approve_{message_id}"),
            # Create an "Approve" button

            InlineKeyboardButton("❌ Reject", callback_data=f"reject_{message_id}")
            # Create a "Reject" button
        ]
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)
    # Turn the buttons into a format Telegram understands

    # Send to admin
    await context.bot.send_message(
        chat_id=ADMIN_ID,
        # Send this message to the admin

        text=f"New message from {user.first_name}:\n\n{text}",
        # Show who sent the message and what they wrote

        reply_markup=reply_markup
        # Attach the buttons to the message
    )

    await update.message.reply_text("Your message is waiting for approval ⏳")
    # Tell the user to wait for approval


# When admin clicks button
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # This function runs when admin clicks a button

    query = update.callback_query  
    # Get the button click data

    await query.answer()  
    # Stop the loading animation on the button

    data = query.data  
    # Get the data from the button (like "approve_123")

    action, msg_id = data.split("_")  
    # Split into action (approve/reject) and message ID

    msg_id = int(msg_id)  
    # Convert message ID into number

    if msg_id not in pending_messages:
        # Check if the message still exists

        await query.edit_message_text("Message expired.")
        # Show message expired if not found

        return  

    message_data = pending_messages[msg_id]  
    # Get stored message details

    user_id = message_data["user_id"]  
    # Get the user's ID

    text = message_data["text"]  
    # Get the message text

    if action == "approve":
        # If admin clicks approve

        await context.bot.send_message(
            chat_id=user_id,
            # Send message back to the user

            text=f"✅ Approved message:\n\n{text}"
            # Show approved message
        )

        await query.edit_message_text("✅ Message Approved and Sent")
        # Update admin message

    elif action == "reject":
        # If admin clicks reject

        await context.bot.send_message(
            chat_id=user_id,
            # Inform the user

            text="❌ Your message was rejected"
        )

        await query.edit_message_text("❌ Message Rejected")
        # Update admin message

    # Remove from storage
    del pending_messages[msg_id]  
    # Delete the message after handling


# Run bot
app = ApplicationBuilder().token(BOT_TOKEN).build()
# Create the bot using your bot token

app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
# Handle only normal text messages (not commands)

app.add_handler(CallbackQueryHandler(button_handler))
# Handle button clicks

print("Bot running...")
# Show in console that bot started

app.run_polling()
# Start the bot and keep
