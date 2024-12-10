import json
from typing import Any

from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler

from fastapi.responses import JSONResponse
from fastapi import APIRouter, Request, BackgroundTasks, Response, status, HTTPException

from app import crud
from app.api.deps import SessionDep
from app.core.config import settings
from app.core.db import AsyncSessionLocal
from app.core.security import verify_password
from app.models import UserUpdate, UserCreate, TaskUserResponse, TaskRequest, AdsRequest


router = APIRouter()

BOT_TOKEN = settings.BOT_TOKEN

# Initialize Telegram bot
bot_app = Application.builder().token(BOT_TOKEN).build()

"""User bot commands"""
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Welcome to Auto Nabavka, please link your account and set your URL to begin. Type /help to get help remembering the commands.")


async def seturl(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles the /seturl command for the clients to use to set their search URL of choice
    
    Takes 1 argument: The URL itself and then it sets that to their record."""

    # Return an error if URL was not provided
    if not context.args:
        await update.message.reply_text("Please provide a URL using /demo <urlhere>.")
        return

    if len(context.args) > 1:
        await update.message.reply_text("Too many arguments, please provide only one argument.")
        return

    # Process URL passed as an argument
    url = context.args[0]
    if not url.startswith("https://") or not "polovniautomobili" in url:
         await update.message.reply_text("Invalid URL, please provide a URL from the correct website.")
         return
    
    # Get chat ID from update
    chat_id = update.message.chat_id
    
    async with AsyncSessionLocal() as session:
        db_user = await crud.get_user_by_chat_id(session=session, chat_id=chat_id)
        # Abort if user not found
        if not db_user:
            await update.message.reply_text("User not found, please use /link if you have an account.")
            return
        # Abort if user is disabled, preventing them from changing their URL
        if not db_user.is_active:
            await update.message.reply_text("Account is disabled, please contact an admin to enable it.")
            return
        
        """Set URL for user"""
        user_in = UserUpdate(mobili_url=url, is_task_active=True)
        await crud.update_user(session=session, db_user=db_user, user_in=user_in)
        await update.message.reply_text("URL set! Ads will be sent periodically, thank you for using this service.")
        return


async def link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles the /link command. A single argument which is the user's email is passed and this links the user's account to their chat enabling the bot to send notifications here."""

    # Return an error if URL was not provided
    if not context.args:
        await update.message.reply_text("Please include your account email in the command argument.")
        return

    if len(context.args) > 1:
        await update.message.reply_text("Too many arguments, please provide only one argument.")
        return

    # Get email and chat ID from context
    email = context.args[0]
    chat_id = update.message.chat_id

    async with AsyncSessionLocal() as session:
        db_user = await crud.get_user_by_email(session=session, email=email)
        # Abort if user not found
        if not db_user:
            await update.message.reply_text("User not found.")
            return
        # Check if user account is tied to a chat ID already
        if db_user.chat_id:
            await update.message.reply_text("Your Telegram is already linked to an account, remove it wth /unlink.")
            return
        
        """Link user with current chat ID"""
        user_in = UserUpdate(chat_id=chat_id)
        await crud.update_user(session=session, db_user=db_user, user_in=user_in)
        await update.message.reply_text("Account linked successfully! Set your URL with the /seturl command.")
        return


async def unlink(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles the /unlink command. A single argument which is the user's email is passed and this unlinks the user's account to their chat."""

    if len(context.args) > 0:
        await update.message.reply_text("The unlink command takes no arguments.")
        return

    # Get chat ID from update
    chat_id = update.message.chat_id

    async with AsyncSessionLocal() as session:
        db_user = await crud.get_user_by_chat_id(session=session, chat_id=chat_id)
        # Abort if user is not found.
        if not db_user:
            await update.message.reply_text("Chat not linked with any account, please link before unlinking.")
            return

        """Unlink account and set is_task_active to False to prevent checking in Celery"""
        user_in = UserUpdate(chat_id=None, is_task_active=False)
        await crud.update_user(session=session, db_user=db_user, user_in=user_in)
        await update.message.reply_text("Account unlinked successfully! You will no longer receive notifications in this chat.")
        return


async def enable(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Return an error if URL was not provided
    if not context.args:
        await update.message.reply_text("Please include a user email in your request.")
        return

    if len(context.args) > 1:
        await update.message.reply_text("Too many arguments, please provide only one email.")
        return
    
    email = context.args[0]
    async with AsyncSessionLocal() as session:
        db_user = await crud.get_user_by_email(session=session, email=email)
        # Abort if user is not found
        if not db_user:
            await update.message.reply_text("User not found.")
            return
        # Deny non superuser
        if not db_user.is_superuser:
            await unknown(update, context)
            return
        # Abort if user is already active
        if db_user.is_active:
            await update.message.reply_text("User account is already enabled.")
            return

        """Enable user"""
        user_in = UserUpdate(is_active=True)
        # Turn on task if user already has a URL
        if db_user.mobili_url:
            user_in.is_task_active = True
        await crud.update_user(session=session, db_user=db_user, user_in=user_in)
        await update.message.reply_text("User account enabled!")
        return


async def disable(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Return an error if URL was not provided
    if not context.args:
        await update.message.reply_text("Please include a user email in your request.")
        return

    if len(context.args) > 1:
        await update.message.reply_text("Too many arguments, please provide only one email.")
        return
    
    email = context.args[0]
    async with AsyncSessionLocal() as session:
        db_user = await crud.get_user_by_email(session=session, email=email)
        # Abort if user is not found
        if not db_user:
            await update.message.reply_text("User not found.")
            return
        # Deny non superuser
        if not db_user.is_superuser:
            await unknown(update, context)
            return
        # Abort if user is already active
        if not db_user.is_active:
            await update.message.reply_text("User account is already disabled.")
            return
        
        """Disable user"""
        user_in = UserUpdate(is_active=False, is_task_active=False)
        await crud.update_user(session=session, db_user=db_user, user_in=user_in)
        await update.message.reply_text("User account disabled.")
        return


async def help(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles the /help command."""
    await update.message.reply_text("Here is a list of available commands:\n/start - Start the bot\n/seturl - Set a URL\n/link - Link the bot to your chat and platform account by passing your registerd account email\n/help - Show this help message")


async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles unknown commands."""
    await update.message.reply_text("Unknown command. Use /help to see available commands.")


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Operation canceled.")
    return ConversationHandler.END


"""Admin bot commands for user registration"""
# States for the registration process
ASK_EMAIL, ASK_PASSWORD, ASK_CODE = range(3)

async def start_registration(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Retrieve the chat ID of the user
    chat_id = update.message.chat_id

    # Query user and check if they are an admin
    async with AsyncSessionLocal() as session:
        user = await crud.get_user_by_chat_id(session=session, chat_id=chat_id)
        if user:
            if user.is_superuser:
                # Store admin password hash for verification at the end
                context.user_data['password_hash'] = user.password_hash

                # Allow superuser and admin to carry out registration
                await update.message.reply_text(
                    "Welcome to registration! Please enter the user's email:"
                )
                return ASK_EMAIL
    
    # Deny all other users
    await update.message.reply_text("Command unauthorized.")
    return ConversationHandler.END

async def ask_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Save email to context.user_data
    email = update.message.text.strip()
    context.user_data['email'] = email

    # Abort if user is already registered
    async with AsyncSessionLocal() as session:
        db_user = await crud.get_user_by_email(session=session, email=email)
        if db_user:
            await update.message.reply_text("A user with this email already exists.")
            return ConversationHandler.END
    
    await update.message.reply_text("User password:")
    return ASK_PASSWORD

async def ask_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Save password to context.user_data
    context.user_data['password'] = update.message.text.strip()
    await update.message.reply_text("Please enter your admin password:")
    return ASK_CODE

async def ask_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Verify admin password
    admin_password = update.message.text.strip()
    password_hash = context.user_data['password_hash']

    if not verify_password(admin_password, password_hash):
        await update.message.reply_text("Incorrect admin password.")
        return ConversationHandler.END

    # Register user in database
    user_password = context.user_data['password']
    email = context.user_data['email']

    async with AsyncSessionLocal() as session:
        user = await crud.get_user_by_email(session=session, email=email)
        if not user:
            user_in = UserCreate(
                email=email,
                password=user_password,
            )
            user = await crud.create_user(session=session, user_create=user_in)
            await update.message.reply_text(f"Registration complete!\nEmail: {email}\nPassword: {user_password}\n")
        else:
            await update.message.reply_text("User already registerd.")
    return ConversationHandler.END


"""Conversation for linking account"""
EMAIL, PASSWORD = range(2)

async def start_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Welcome, link your chat to your account by entering your registered email:")
    return EMAIL

async def handle_email(update: Update, context: ContextTypes.DEFAULT_TYPE):
    email = await update.message.text.strip()
    context.user_data['email'] = email

    update.message.reply_text("Enter your password:")
    return PASSWORD

async def handle_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    password = update.message.text.strip()
    email = context.user_data['email']

    # Verify user's claim and account
    async with AsyncSessionLocal() as session:
        db_user = crud.authenticate(session=session, email=email, password=password)
        if db_user:
            await update.message.reply_text("Account linked successfully!")
        else:
            await update.message.reply_text("Invalid email or password. Please also ensure you have an account.")

    return ConversationHandler.END


# Add handlers to the Bot
registration_handler = ConversationHandler(
    entry_points=[CommandHandler("register", start_registration)],
    states={
        ASK_EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_email)],
        ASK_PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_password)],
        ASK_CODE: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_code)],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
)
link_handler = ConversationHandler(
    entry_points=[CommandHandler("link", start_link)],
    states={
        EMAIL: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_email)],
        PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_password)],
    },
    fallbacks=[CommandHandler("cancel", cancel)],
)

bot_app.add_handler(registration_handler)
bot_app.add_handler(link_handler)
bot_app.add_handler(CommandHandler("start", start))
bot_app.add_handler(CommandHandler("seturl", seturl))
bot_app.add_handler(CommandHandler("enable", enable))
bot_app.add_handler(CommandHandler("disable", disable))
bot_app.add_handler(CommandHandler("help", help))
# bot_app.add_handler(CommandHandler("link", link))
bot_app.add_handler(CommandHandler("unlink", unlink))
bot_app.add_handler(MessageHandler(filters.COMMAND, unknown))


@router.post("/webhook")
async def webhook(
    request: Request, 
    background_task: BackgroundTasks
) -> Response:
    # Get telegram update
    update = Update.de_json(await request.json(), bot_app.bot)
    # Add update processer to the background
    background_task.add_task(bot_app.process_update, update)
    return JSONResponse(content={"message": "Response sent to user"}, status_code=status.HTTP_200_OK)


@router.get("/setwebhook", status_code=status.HTTP_204_NO_CONTENT)
async def set_webhook() -> Response:
    WEBHOOK_URL = "https://auto-nabavka.onrender.com/api/webhook"

    bot = Bot(BOT_TOKEN)
    bot_set = await bot.set_webhook(WEBHOOK_URL)
    return bot_set


@router.post("/queue-tasks", response_model=TaskUserResponse)
async def queue_tasks(
    request: TaskRequest, session: SessionDep
) -> Any:
    # Verify if request is from one of our workers
    if request.celery_auth != settings.CELERY_AUTH:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid request."
        )

    users = await crud.get_task_active_users(session=session)

    return JSONResponse(
        content={"users": users},
        status_code=status.HTTP_200_OK
    )


@router.post("/send-ads", response_model=int, status_code=200)
async def send_ads(
    request: AdsRequest,
    session: SessionDep
) -> Any:
    # Verify if request is from one of our workers
    if request.celery_auth != settings.CELERY_AUTH:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            ddetail="Invalid request."
        )
    
    # Bot instance
    bot = Bot(BOT_TOKEN)

    # Data from request
    ads = request.ads
    chat_id = request.chat_id

    # Get previous ads from requesting user
    db_user = await crud.get_user_by_chat_id(session=session, chat_id=chat_id)
    previous_ads: list[str] = json.loads(db_user.previous_ads)
    ads_json = json.dumps(ads)
    user_in = UserUpdate(previous_ads=ads_json)

    # Store ads if none found and return
    if not previous_ads:
        await crud.update_user(session=session, db_user=db_user, user_in=user_in)
        return JSONResponse(
            content={"message": f"Ads set: {chat_id}"},
            status_code=status.HTTP_200_OK
        )

    # Send only new ads and rewrite previous ads
    new_ads = [ad for ad in ads if ad not in previous_ads]
    if any(new_ads):
        for ad in new_ads:
            try:
                await bot.send_message(chat_id=chat_id, text=ad)
            except Exception:
                continue
        await crud.update_user(session=session, db_user=db_user, user_in=user_in)
        return JSONResponse(
            content={"message": f"Ads sent to: {chat_id}"},
            status_code=status.HTTP_200_OK
        )
    return JSONResponse(
        content={"message": f"No new ads for: {chat_id}"},
        status_code=status.HTTP_200_OK
    )
