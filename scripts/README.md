"""
# FindMovies Setup Guide

This guide provides instructions on how to set up and run the FindMovies application using PowerShell, Windows CMD, and Bash.

## 1. Prerequisites: Check for Python

First, verify that you have Python 3.10 or newer installed.

### PowerShell or CMD (Windows)
```shell
python --version
```

### Bash (Linux/macOS)
```shell
python3 --version
```

If a version number is displayed (e.g., `Python 3.10.x`), you can proceed to the next step.

## 2. Installing Python (If Needed)

If Python is not installed, download it from the official website:

- **[python.org/downloads](https://www.python.org/downloads/)**

**Important for Windows users:** During installation, make sure to check the box that says **"Add Python to PATH"**.

## 3. Setup Virtual Environment

A virtual environment isolates the application's dependencies from your main system.

### PowerShell (Windows)
```powershell
# Create the virtual environment
python -m venv venv

# Activate the virtual environment
.\venv\Scripts\Activate.ps1
```
*Note: If you get an error, you may need to set the execution policy: `Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process`*

### CMD (Windows)
```shell
# Create the virtual environment
python -m venv venv

# Activate the virtual environment
.\venv\Scripts\activate.bat
```

### Bash (Linux/macOS)
```shell
# Create the virtual environment
python3 -m venv venv

# Activate the virtual environment
source venv/bin/activate
```

You'll know the environment is active when you see `(venv)` at the beginning of your command prompt.

## 4. Install Dependencies

Once the virtual environment is active, install the required Python packages.

```shell
pip install -r requirements.txt
```

This command works for PowerShell, CMD, and Bash.

## 5. Configuration (Optional)

Before starting the application, you can customize the settings.

- **`.env` file:** Copy the `.env.example` file and rename it to `.env`. Open the `.env` file in a text editor and adjust the values as needed.
- **`app.yaml` file:** If necessary, you can also adjust the `server_url` in the `app.yaml` file.

## 6. Start the Application

Finally, start the FindMovies server.

```shell
python backend/main.py
```
The server is now running. You can access the application by opening your web browser and navigating to:

**[http://localhost:8000](http://localhost:8000)**

To stop the server, press `Ctrl + C` in the terminal.
""