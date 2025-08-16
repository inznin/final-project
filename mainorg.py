import json
import logging
import os
import re
from datetime import datetime
from functools import wraps
from typing import Any, Dict, List, Optional, Callable

import dateparser
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, ContextTypes, CallbackQueryHandler,
    MessageHandler, filters, BaseHandler
)

# ..:: Configure logging to display info and errors in the console ::..
logging.basicConfig(
    level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ..:: Define constant filenames for data storage ::..
TASKS_FILE = "tasks.json"
ROLES_FILE = "roles.json"


# ..:: Data Management Class ::..
class DataManager:
    """A class to manage reading, writing, and handling data in JSON files."""

    # ..:: Loads data files upon initialization. ::..
    def __init__(self, tasks_file: str, roles_file: str):
        self.tasks_file = tasks_file
        self.roles_file = roles_file
        self.tasks: List[Dict[str, Any]] = self._load_json(self.tasks_file, default_factory=list)
        self.user_roles: Dict[str, str] = self._load_json(self.roles_file, default_factory=dict)

    # ..:: Safely loads a JSON file, returning a default value (e.g., empty list/dict) on error. ::..
    def _load_json(self, file_path: str, default_factory: Callable) -> Any:
        if os.path.exists(file_path):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except json.JSONDecodeError:
                logger.error(f"Error reading {file_path}. File is empty or malformed.")
        return default_factory()

    # ..:: Saves data to a JSON file with readable UTF-8 formatting. ::..
    def _save_json(self, data: Any, file_path: str):
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    # ..:: Helper method to save the current list of tasks. ::..
    def save_tasks(self):
        self._save_json(self.tasks, self.tasks_file)

    # ..:: Helper method to save the current user roles. ::..
    def save_roles(self):
        self._save_json(self.user_roles, self.roles_file)

    # ..:: Adds a new task to the list and saves it. ::..
    def add_task(self, task: Dict[str, Any]):
        self.tasks.append(task)
        self.save_tasks()

    # ..:: Deletes a task by its index. ::..
    def delete_task(self, index: int) -> bool:
        if 0 <= index < len(self.tasks):
            del self.tasks[index]
            self.save_tasks()
            return True
        return False

    # ..:: Marks a task's status as 'done'. ::..
    def complete_task(self, index: int) -> Optional[Dict[str, Any]]:
        if 0 <= index < len(self.tasks):
            self.tasks[index]["done"] = True
            self.save_tasks()
            return self.tasks[index]
        return None

# ..:: Task Information Extraction Class ::..
class TaskParser:
    """A class to parse raw user text and intelligently extract task details (user ID, text, deadline)."""
    
    # ..:: Regex patterns are defined as class constants for clarity and maintainability. ::..
    USER_ID_PATTERN = r"\b(\d{5,})\b"
    DATE_PATTERNS = [
        r"by\s+(\d{1,2}[-/]\d{1,2}[-/]\d{4})",
        r"by\s+(\d{4}[-/]\d{1,2}[-/]\d{1,2})",
        r"by\s+(tomorrow|today|next week|next month|next year)",
        r"(\d{1,2}\s+(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4})",
    ]
    
    def __init__(self, text: str):
        self.original_text = text
        self.processed_text = text

    # ..:: Finds a number with at least 5 digits and interprets it as a user ID. ::..
    def _extract_user_id(self) -> Optional[int]:
        match = re.search(self.USER_ID_PATTERN, self.processed_text)
        if match:
            user_id = int(match.group(1))
            self.processed_text = self.processed_text.replace(match.group(0), "").strip()
            return user_id
        return None

    # ..:: Extracts a date from the text using various common patterns. ::..
    def _extract_deadline(self) -> Optional[str]:
        found_date_str = None
        for pattern in self.DATE_PATTERNS:
            match = re.search(pattern, self.processed_text, re.IGNORECASE)
            if match:
                found_date_str = match.group(1) if match.groups() else match.group(0)
                self.processed_text = self.processed_text.replace(match.group(0), "").strip()
                break

        if found_date_str:
            # ..:: Uses the dateparser library to convert natural language strings to a standard date format. ::..
            parsed_date = dateparser.parse(
                found_date_str, settings={'PREFER_DATES_FROM': 'future', 'DATE_ORDER': 'DMY'}
            )
            if parsed_date:
                return parsed_date.strftime("%Y-%m-%d")
        return None

    # ..:: Removes extra keywords to isolate the core task description. ::..
    def _extract_task_text(self) -> str:
        keywords_to_remove = ["for user", "task", "deadline", ":", "by", "project"]
        temp_text = self.processed_text
        for keyword in keywords_to_remove:
            temp_text = temp_text.replace(keyword, "").strip()
        
        return re.sub(r'\s+', ' ', temp_text).strip()

    # ..:: Main method to run all extraction steps and return a structured task dictionary or an error. ::..
    def parse(self) -> (Optional[Dict[str, Any]], Optional[str]):
        user_id = self._extract_user_id()
        if user_id is None:
            return None, "❌ User ID not found. Please include the numeric ID in your message."

        deadline = self._extract_deadline()
        task_text = self._extract_task_text()
        if not task_text:
            return None, "❌ Please provide the task description."

        return {
            "user_id": user_id,
            "text": task_text,
            "deadline": deadline,
            "done": False
        }, None

# ..:: Simple AI Response Class ::..
class SimpleAI:
    """A very simple class to answer common questions based on pattern matching."""
    def __init__(self):
        # ..:: A dictionary of regex patterns and their corresponding responses. ::..
        self.qa_patterns = {
            r"(hello|hi)": "Hello there!",
            r"(how are you|how's it going)": "I'm a bot, but I'm doing great! How about you?",
            r"(what can you do|help|features)": "I can manage tasks, generate reports, and add users. Use the main menu to see the options.",
            r"(what is your name)": "I am a Task Management Bot!",
            r"(thank you|thanks)": "You're welcome! Happy to help.",
            r"(bye|goodbye)": "Goodbye! Have a great day.",
        }

    # ..:: Compares user text against patterns and returns a response if a match is found. ::..
    def get_response(self, text: str) -> Optional[str]:
        text_lower = text.lower().strip()
        for pattern, response in self.qa_patterns.items():
            if re.search(pattern, text_lower):
                return response
        return None

# ..:: A decorator that checks if the executing user is an admin before running a function. ::..
def admin_required(func: Callable):
    """Decorator for admin-only commands."""
    @wraps(func)
    async def wrapper(self: 'TaskBot', update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        user_id = str(update.effective_user.id)
        if self.data_manager.user_roles.get(user_id) != "admin":
            error_message = "⛔️ You do not have the necessary permissions for this action."
            query = update.callback_query
            if query:
                await query.answer(error_message, show_alert=True)
            else:
                await update.message.reply_text(error_message)
            return
        return await func(self, update, context, *args, **kwargs)
    return wrapper

# ..:: Main Bot Class ::..
class TaskBot:
    """The main class that manages all the logic for the Telegram bot."""

    # ..:: User States for Conversation Handling ::..
    AWAITING_TASK_TEXT = "adding_task"
    AWAITING_MEMBER_ID = "adding_member"
    
    # ..:: Callback Data Prefixes for Inline Buttons ::..
    ROLE_PREFIX = "role_"
    MENU_PREFIX = "menu_"
    DONE_PREFIX = "done_"
    DELETE_PREFIX = "delete_"

    # ..:: Initializes helper classes and builds the bot application. ::..
    def __init__(self, token: str):
        self.data_manager = DataManager(TASKS_FILE, ROLES_FILE)
        self.simple_ai = SimpleAI()
        self.app = ApplicationBuilder().token(token).build()
        self._setup_handlers()

    # ..:: Registers all handlers for commands, buttons, and messages. ::..
    def _setup_handlers(self):
        handlers: List[BaseHandler] = [
            CommandHandler("start", self.start),
            CallbackQueryHandler(self.role_handler, pattern=f"^{self.ROLE_PREFIX}"),
            CallbackQueryHandler(self.menu_handler, pattern=f"^{self.MENU_PREFIX}"),
            CallbackQueryHandler(self.button_handler, pattern=f"^(?:{self.DONE_PREFIX}|{self.DELETE_PREFIX})"),
            MessageHandler(filters.TEXT & ~filters.COMMAND, self.text_handler),
        ]
        for handler in handlers:
            self.app.add_handler(handler)

    # ..:: Responds to the /start command and shows role selection buttons. ::..
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        keyboard = [
            [InlineKeyboardButton("👑 I am an Admin", callback_data=f"{self.ROLE_PREFIX}admin")],
            [InlineKeyboardButton("🙋 I am a Member", callback_data=f"{self.ROLE_PREFIX}member")]
        ]
        await update.message.reply_text("Welcome! Please select your role:", reply_markup=InlineKeyboardMarkup(keyboard))

    # ..:: Processes the user's role selection, saves it, and displays the main menu. ::..
    async def role_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        
        role = query.data.replace(self.ROLE_PREFIX, "")
        user_id = str(query.from_user.id)
        
        self.data_manager.user_roles[user_id] = role
        self.data_manager.save_roles()

        await query.edit_message_text(f"✅ Your role as **{role}** has been saved.")
        await self._send_main_menu(user_id, context)

    # ..:: Sends the main menu with buttons tailored to the user's role (admin or member). ::..
    async def _send_main_menu(self, user_id: str, context: ContextTypes.DEFAULT_TYPE):
        role = self.data_manager.user_roles.get(user_id)
        if not role:
            await context.bot.send_message(chat_id=user_id, text="Please use /start and select a role first.")
            return

        if role == "admin":
            keyboard = [
                [InlineKeyboardButton("➕ Add Task", callback_data=f"{self.MENU_PREFIX}add_task")],
                [InlineKeyboardButton("👥 Add Member", callback_data=f"{self.MENU_PREFIX}add_member")],
                [InlineKeyboardButton("📊 Task Report", callback_data=f"{self.MENU_PREFIX}report")],
                [InlineKeyboardButton("🗑️ Delete Task", callback_data=f"{self.MENU_PREFIX}delete_task")]
            ]
        else:  # member
            keyboard = [[InlineKeyboardButton("📌 My Tasks", callback_data=f"{self.MENU_PREFIX}my_tasks")]]

        await context.bot.send_message(chat_id=user_id, text="📋 Main Menu:", reply_markup=InlineKeyboardMarkup(keyboard))

    # ..:: Handles main menu button presses by dispatching to the appropriate method. ::..
    async def menu_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        
        menu_actions = {
            f"{self.MENU_PREFIX}add_task": self._menu_add_task,
            f"{self.MENU_PREFIX}add_member": self._menu_add_member,
            f"{self.MENU_PREFIX}report": self._menu_report,
            f"{self.MENU_PREFIX}delete_task": self._menu_delete_task,
            f"{self.MENU_PREFIX}my_tasks": self._menu_my_tasks,
        }
        
        action = menu_actions.get(query.data)
        if action:
            await action(update, context)

    # ..:: Prepares the bot to receive task text from an admin. ::..
    @admin_required
    async def _menu_add_task(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        context.user_data["state"] = self.AWAITING_TASK_TEXT
        await update.callback_query.message.reply_text(
            "Please enter the task details. The bot will intelligently extract the user ID and deadline.\n\n"
            "Examples:\n- `New project for 123456789 by 15/12/2025: Finish the report.`\n"
            "- `Prepare the presentation for 987654321 by tomorrow.`"
        )

    # ..:: Prepares the bot to receive a new member's ID from an admin. ::..
    @admin_required
    async def _menu_add_member(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        context.user_data["state"] = self.AWAITING_MEMBER_ID
        await update.callback_query.message.reply_text("Please enter the numeric ID of the new member:")

    # ..:: Displays a full report of all tasks for the admin. ::..
    @admin_required
    async def _menu_report(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not self.data_manager.tasks:
            await update.callback_query.message.reply_text("📭 No tasks have been created yet.")
            return
        report = self._format_task_report(self.data_manager.tasks)
        await update.callback_query.message.reply_text(report)

    # ..:: Shows a list of tasks with delete buttons for the admin. ::..
    @admin_required
    async def _menu_delete_task(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        if not self.data_manager.tasks:
            await update.callback_query.message.reply_text("📭 There are no tasks to delete.")
            return
        
        keyboard = []
        for i, task in enumerate(self.data_manager.tasks):
            status = "✅" if task.get("done") else "❌"
            button_text = f"{i+1}. 👤 {task['user_id']} | {status} | {task['text'][:25]}..."
            keyboard.append([InlineKeyboardButton(button_text, callback_data=f"{self.DELETE_PREFIX}{i}")])
        
        await update.callback_query.message.reply_text("Which task would you like to delete?", reply_markup=InlineKeyboardMarkup(keyboard))

    # ..:: Displays tasks assigned specifically to the requesting user (member). ::..
    async def _menu_my_tasks(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = str(update.effective_user.id)
        my_tasks = [t for t in self.data_manager.tasks if str(t.get("user_id")) == user_id]
        if not my_tasks:
            await update.callback_query.message.reply_text("You have no assigned tasks.")
            return
        report = self._format_task_report(my_tasks)
        await update.callback_query.message.reply_text(report)

    # ..:: Handles general text messages that are not commands. ::..
    async def text_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        user_id = str(update.effective_user.id)
        state = context.user_data.get("state")
        
        # ..:: Checks if the user is in a specific conversation state (e.g., adding a task). ::..
        if state == self.AWAITING_TASK_TEXT:
            await self._handle_add_task_text(update, context)
        elif state == self.AWAITING_MEMBER_ID:
            await self._handle_add_member_text(update, context)
        else:
            # ..:: If not in a state, the message is passed to the simple AI for a possible response. ::..
            ai_response = self.simple_ai.get_response(update.message.text.strip())
            if ai_response:
                await update.message.reply_text(ai_response)
            else:
                await update.message.reply_text("I'm not sure how to respond to that. Please use /start or the main menu.")
            
        # ..:: Clears the user's state after processing and reshows the menu if they were in a state. ::..
        if state:
            context.user_data.clear()
            await self._send_main_menu(user_id, context)

    # ..:: Parses task text, saves the task, and notifies the assigned user. ::..
    @admin_required
    async def _handle_add_task_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        parser = TaskParser(update.message.text)
        task_data, error = parser.parse()

        if error:
            await update.message.reply_text(error)
            return

        target_user_id = str(task_data["user_id"])
        # ..:: Ensures the target user is a registered member before assigning a task. ::..
        if self.data_manager.user_roles.get(target_user_id) != "member":
            await update.message.reply_text(f"❌ User **{target_user_id}** is not a member. Please add them first via the 'Add Member' menu.")
            return
            
        self.data_manager.add_task(task_data)
        task_index = len(self.data_manager.tasks) - 1

        deadline_info = f"\n🕒 Deadline: {task_data['deadline']}" if task_data.get('deadline') else ""

        try:
            keyboard = [[InlineKeyboardButton("✅ Mark as Done", callback_data=f"{self.DONE_PREFIX}{task_index}")]]
            await context.bot.send_message(
                chat_id=target_user_id,
                text=f"📌 New Task Assigned:\n**{task_data['text']}**{deadline_info}",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            await update.message.reply_text(f"✅ Task **created and sent to user {target_user_id}.**")
        except Exception as e:
            logger.error(f"Failed to send task notification to {target_user_id}: {e}")
            await update.message.reply_text(f"✅ Task created, but failed to send notification (Error: {e}). The user may have blocked the bot.")

    # ..:: Receives a numeric ID and saves it as a new member. ::..
    @admin_required
    async def _handle_add_member_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        try:
            new_user_id = str(int(update.message.text.strip()))
            if new_user_id in self.data_manager.user_roles:
                await update.message.reply_text("❌ This user has already been added.")
            else:
                self.data_manager.user_roles[new_user_id] = "member"
                self.data_manager.save_roles()
                await update.message.reply_text(f"✅ User **{new_user_id}** has been added as a member.")
        except ValueError:
            await update.message.reply_text("❌ The ID must be a numeric value.")

    # ..:: Handles button presses on task messages, like 'Done' or 'Delete'. ::..
    async def button_handler(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        query = update.callback_query
        await query.answer()
        
        data = query.data
        if data.startswith(self.DONE_PREFIX):
            index = int(data.replace(self.DONE_PREFIX, ""))
            await self._handle_done_action(query, context, index)
        elif data.startswith(self.DELETE_PREFIX):
            index = int(data.replace(self.DELETE_PREFIX, ""))
            await self._handle_delete_action(query, index)

    # ..:: Logic for when a user marks a task as done. ::..
    async def _handle_done_action(self, query, context, index):
        completed_task = self.data_manager.complete_task(index)
        if completed_task:
            await query.edit_message_text(f"✅ Task completed:\n{completed_task['text']}")
            # ..:: Notifies all admins that a task was completed. ::..
            admins = [uid for uid, role in self.data_manager.user_roles.items() if role == "admin"]
            for admin_id in admins:
                try:
                    await context.bot.send_message(
                        chat_id=admin_id,
                        text=f"📬 User **{completed_task['user_id']}** completed a task:\n{completed_task['text']}"
                    )
                except Exception as e:
                    logger.error(f"Failed to notify admin {admin_id}: {e}")
        else:
            await query.edit_message_text("❌ Could not find the task to mark as complete.")

    # ..:: Logic for when an admin deletes a task. ::..
    async def _handle_delete_action(self, query, index):
        if self.data_manager.delete_task(index):
            await query.edit_message_text("🗑️ Task has been successfully deleted.")
        else:
            await query.edit_message_text("❌ Could not find the task to delete.")

    # ..:: Generates a readable text report from a list of tasks, including deadline info. ::..
    def _format_task_report(self, tasks_list: List[Dict]) -> str:
        if not tasks_list:
            return "📭 No tasks found."

        report_lines = []
        today = datetime.now().date()
        
        for i, t in enumerate(tasks_list):
            status = "✅" if t.get("done") else "❌"
            user_id = t.get("user_id", "Unknown")
            text = t.get("text", "No description")
            deadline_str = t.get("deadline")
            
            deadline_info = "No deadline"
            if deadline_str:
                try:
                    deadline_date = datetime.strptime(deadline_str, "%Y-%m-%d").date()
                    days_left = (deadline_date - today).days
                    if days_left > 0:
                        deadline_info = f"{days_left} days left"
                    elif days_left == 0:
                        deadline_info = "Due today"
                    else:
                        deadline_info = f"Overdue by {abs(days_left)} days"
                    deadline_info += f" ({deadline_str})"
                except ValueError:
                    deadline_info = f"Invalid date ({deadline_str})"

            line = f"{i+1}. 👤 {user_id} | {status} | {text} | 🕒 {deadline_info}"
            report_lines.append(line)

        return "📊 Task Report:\n" + "\n".join(report_lines)

    # ..:: Starts the bot in polling mode to receive continuous updates. ::..
    def run(self):
        logger.info("Bot is running...")
        self.app.run_polling()

# ..:: Main function to read the token from a file and run the bot. ::..
def main():
    try:
        with open("token.txt") as f:
            token = f.read().strip()
    except FileNotFoundError:
        logger.error("Error: 'token.txt' file not found. Please create this file and place your bot token inside.")
        return

    bot = TaskBot(token)
    bot.run()

if __name__ == "__main__":
    main()