# Advanced Task Management Telegram Bot

[![Python Version](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg)](CONTRIBUTING.md)

A sophisticated, role-based Telegram bot for managing tasks within a team. It features an intelligent parser for natural language task creation and provides distinct interfaces for admins and members.

---

<details>
<summary>🇮🇷 **توضیحات به زبان فارسی (Farsi Description)**</summary>

این پروژه یک ربات تلگرام پیشرفته برای مدیریت وظایف است که بر اساس نقش کاربران (مدیر و عضو) عمل می‌کند. مدیران می‌توانند برای اعضا وظیفه تعریف کنند، اعضای جدید اضافه کنند و گزارش عملکرد بگیرند. ربات به صورت هوشمند متن پیام را برای استخراج آیدی کاربر و مهلت انجام وظیفه تحلیل می‌کند. اعضا نیز می‌توانند لیست وظایف خود را مشاهده و آن‌ها را به‌عنوان "انجام شده" علامت‌گذاری کنند.

</details>

---

## ✨ Key Features

-   **✅ Role-Based Access Control**: Separate menus and permissions for **Admins** and **Members**.
-   **🤖 Intelligent Task Parsing**: Automatically extracts user IDs and deadlines from natural language messages (e.g., "task for user `123456` by `tomorrow`").
-   **📋 Interactive Menus**: User-friendly navigation with inline keyboard buttons.
-   **💾 Data Persistence**: All tasks and user roles are saved locally in JSON files (`tasks.json`, `roles.json`).
-   **🔔 Admin Notifications**: Admins are notified when a user marks a task as complete.
-   **💬 Simple AI Responder**: Provides answers to basic conversational queries like "hello" or "how are you?".
-   **🔒 Secure**: Ignores sensitive files like `token.txt` and databases via `.gitignore`.

## 🚀 Getting Started

Follow these instructions to get a copy of the project up and running on your local machine.

### Prerequisites

-   Python 3.9+
-   A Telegram Bot Token. You can get one from [@BotFather](https://t.me/BotFather) on Telegram.

### Installation & Setup

1.  **Clone the repository:**
    ```sh
    git clone https://github.com/YOUR_USERNAME/YOUR_REPOSITORY_NAME.git
    cd YOUR_REPOSITORY_NAME
    ```

2.  **Create and activate a virtual environment:**
    ```sh
    # For macOS/Linux
    python3 -m venv venv
    source venv/bin/activate

    # For Windows
    python -m venv venv
    venv\Scripts\activate
    ```

3.  **Install the required dependencies:**
    ```sh
    pip install -r requirements.txt
    ```

4.  **Configure your Bot Token:**
    -   Create a file named `token.txt` in the root directory.
    -   Paste your Telegram Bot Token inside this file. The file should *only* contain the token string.

### Running the Bot

Execute the main script to start the bot:
```sh
python main.py
```
The bot is now running and will start listening for commands on Telegram.

## 🤖 How to Use

### 1. First-Time Start
-   Open a chat with your bot on Telegram and send the `/start` command.
-   The bot will ask you to select your role: **Admin** or **Member**. This choice determines the menu you will see.

### 2. Admin Workflow
As an admin, you have access to the following commands via the main menu:
-   **➕ Add Task**: Prompts you to send a message containing the task details. The bot will parse the user's numeric ID, the deadline, and the task description.
    -   *Example*: `Assign project alpha to user 123456789 by next Friday`
-   **👥 Add Member**: Prompts you to enter the numeric Telegram ID of a new user to grant them "Member" access.
-   **📊 Task Report**: Displays a formatted list of all tasks, including their status, assigned user, and deadline information.
-   **🗑️ Delete Task**: Shows a list of all tasks with buttons to delete them individually.

### 3. Member Workflow
As a member, you have a simplified interface:
-   **📌 My Tasks**: Displays a list of all tasks assigned to you.
-   **✅ Mark as Done**: Each task notification you receive includes a "Mark as Done" button. Clicking it updates the task status and notifies all admins.

## 📁 Project Structure

```
.
├── main.py             # The main application script to run the bot.
├── tasks.json          # Database for tasks (auto-generated, ignored by Git).
├── roles.json          # Database for user roles (auto-generated, ignored by Git).
├── requirements.txt    # A list of Python packages required for the project.
├── token.txt           # File for your private Telegram Bot token (create manually).
├── .gitignore          # Specifies files and folders to be ignored by Git.
└── README.md           # This file.
```

## 🤝 Contributing

Contributions are what make the open-source community such an amazing place to learn, inspire, and create. Any contributions you make are **greatly appreciated**.

1.  Fork the Project
2.  Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3.  Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4.  Push to the Branch (`git push origin feature/AmazingFeature`)
5.  Open a Pull Request

## 📄 License

This project is distributed under the MIT License.# final project
manager telegram bot
