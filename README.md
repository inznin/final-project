<p align="center">
  <img src="./assets/bot-cover.png" alt="Task Manager Bot Cover" width="400"/>
</p>

<h1 align="center">Task Management Telegram Bot</h1>

<p align="center">
  <a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/Python-3.9+-blue.svg" alt="Python Version"></a>
  <a href="https://opensource.org/licenses/MIT"><img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License: MIT"></a>
  <a href="#"><img src="https://img.shields.io/badge/Status-In%20Development-orange.svg" alt="Status"></a>
  <a href="#"><img src="https://img.shields.io/badge/PRs-welcome-brightgreen.svg" alt="PRs Welcome"></a>
</p>

This is a functional, role-based Telegram bot designed for task management. This project is currently in its foundational stage and serves as a solid starting point for a more comprehensive tool. It is open for contributions, improvements, and feature expansions.

---

## ✨ Current Features

-   **✅ Role-Based Access Control**: Separate menus and permissions for **Admins** and **Members**.
-   **🤖 Intelligent Task Parsing**: Automatically extracts user IDs and deadlines from natural language messages (e.g., "task for user `123456` by `tomorrow`").
-   **📋 Interactive Menus**: User-friendly navigation with inline keyboard buttons.
-   **💾 Data Persistence**: All tasks and user roles are saved locally in JSON files.
-   **🔔 Admin Notifications**: Admins are notified when a user marks a task as complete.
-   **💬 Simple AI Responder**: Provides answers to basic conversational queries.

## 🚀 Getting Started

Follow these instructions to get a copy of the project up and running on your local machine.

### Prerequisites

-   Python 3.9+
-   A Telegram Bot Token from [@BotFather](https://t.me/BotFather).

### Installation & Setup

1.  **Clone the repository:**
    ```sh
    git clone https://github.com/YOUR_USERNAME/YOUR_REPOSITORY_NAME.git
    cd YOUR_REPOSITORY_NAME
    ```
    *Remember to replace `YOUR_USERNAME/YOUR_REPOSITORY_NAME` with your actual GitHub details.*

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
    -   Paste your Telegram Bot Token inside this file.

### Running the Bot

Execute the main script to start the bot:
```sh
python main.py
```

## 🤖 How to Use

-   **/start**: Initializes the bot and prompts for role selection (Admin/Member).
-   **Admin Menu**: Admins can add new tasks, add new members, view a full task report, and delete tasks.
-   **Member Menu**: Members can view their assigned tasks and mark them as complete.

## 🛣️ Roadmap & Future Ideas

This project has plenty of room for growth. Contributions are highly encouraged! Some ideas for future development include:

-   [ ] **Database Integration**: Migrating from JSON files to a more robust database like SQLite or PostgreSQL.
-   [ ] **Task Editing**: Allowing admins to edit existing tasks.
-   [ ] **Deadline Reminders**: Automatically sending reminders to users before a task deadline.
-   [ ] **Recurring Tasks**: Adding support for daily, weekly, or monthly tasks.
-   [ ] **Improved Analytics**: A dashboard or report for tracking user productivity.
-   [ ] **Localization**: Adding support for multiple languages.

## 🤝 Contributing

This project is in active development and welcomes contributions of all kinds. Whether it's a new feature, a bug fix, or documentation improvement, your help is welcome. Please feel free to fork the repository and submit a pull request.

1.  Fork the Project
2.  Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3.  Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4.  Push to the Branch (`git push origin feature/AmazingFeature`)
5.  Open a Pull Request

## 📄 License

This project is distributed under the MIT License.