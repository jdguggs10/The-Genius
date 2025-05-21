# QUICKSTART: Terminal Chat with OpenAI GPT-4.1

This guide will help you set up and run the OpenAI chat script from your terminal.

---

## 1. Create and Activate a Virtual Environment
```sh
cd backend
python3 -m venv venv
source venv/bin/activate
```

## 2. Install Dependencies
```sh
pip install openai python-dotenv
```

## 3. Run the Chat Script
From the `backend` directory, run:
```sh
python -m app.services.openai_client
```
If you see an error like `No module named 'app'`, make sure you are in the `backend` directory when running the command.

---

## 4. Usage
- Type your message and press Enter to chat with GPT-4.1.
- Type `exit` to quit.

---

## Troubleshooting
- **ModuleNotFoundError: No module named 'app'**
  - Make sure you are in the `backend` directory when running the script.
- **Missing dependencies**
  - Run `pip install openai python-dotenv` inside your virtual environment.
- **API Key errors**
  - Ensure your `.env` file contains a valid `OPENAI_API_KEY`.

---

Happy chatting! 