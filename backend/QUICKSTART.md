# QUICKSTART: Terminal Chat with OpenAI GPT-4.1

This guide will help you set up and run the OpenAI chat script from your terminal using Poetry.

---

## 0. Prerequisites
- Ensure you have Python 3.11 or newer installed.
- Install Poetry if you haven't already. You can find installation instructions at [https://python-poetry.org/docs/#installation](https://python-poetry.org/docs/#installation).

## 1. Navigate to the Backend Directory
```sh
cd backend
```

## 2. Install Dependencies with Poetry
This command will create a virtual environment if one doesn't exist and install all the project dependencies defined in `pyproject.toml`.
```sh
poetry install
```

## 3. Run the Chat Script
From the `backend` directory, run:
```sh
poetry run python -m app.services.openai_client
```
If you see an error like `No module named 'app'`, make sure you are in the `backend` directory when running the command and that you are using `poetry run`.

---

## 4. Usage
- Type your message and press Enter to chat with GPT-4.1.
- Type `exit` to quit.

---

## Troubleshooting
- **ModuleNotFoundError: No module named 'app'**
  - Ensure you are in the `backend` directory.
  - Ensure you are running the script using `poetry run python -m app.services.openai_client`.
- **Poetry issues**
  - Make sure Poetry is installed correctly and is in your system's PATH.
  - If you encounter issues with a specific Python version, Poetry allows managing Python versions for projects. Refer to Poetry documentation for details.
- **Missing dependencies**
  - Running `poetry install` should handle all dependencies. If you suspect an issue, you can try `poetry lock --no-update && poetry install` to refresh the lock file and reinstall.
- **API Key errors**
  - Ensure your `.env` file (in the `backend` directory) contains a valid `OPENAI_API_KEY`.

---

Happy chatting! 