# ​<p align="center">SortifyV1</p>

<p align="center">
  <img src="assets/sortify.ico" alt="SortifyV1 Icon">
</p>

SortifyV1 is a Python-based application with a Tkinter GUI that allows users to sort photos into categorized folders. This application is designed to run on Windows and can be packaged into an .exe file using PyInstaller.

## Overview

SortifyV1 simplifies the process of organizing images by allowing users to select a folder and automatically sort its contents into categorized subfolders. The application supports common image formats such as JPG, PNG, GIF, and RAW formats. The intuitive interface ensures ease of use, with options for previewing and managing files before finalizing the sorting process.

## Features

- Splash screen when opening the application
- Image folder selection
- Automatic category folder creation
- Button to start the sorting process
- Image preview with category and delete buttons
- Option to return to the folder selection menu

## How to Run the Application

For users who only want to run the application without development, simply open the `.exe` file located in the [`dist`](./dist)[ folder](./dist).

## How to Develop the Application

If you want to develop or modify the application, follow these steps:

1. **Create a virtual environment (.venv)**

   ```sh
   python -m venv .venv
   ```

2. **Activate the virtual environment**

   - Windows (Command Prompt):
     ```sh
     .venv\Scripts\activate
     ```
   - Windows (PowerShell):
     ```sh
     .venv\Scripts\Activate.ps1
     ```
   - Linux/Mac:
     ```sh
     source .venv/bin/activate
     ```

3. **Install required dependencies**

   ```sh
   pip install -r requirements.txt
   ```

4. **Run the application in development mode**

   ```sh
   python src/main.py
   ```

## How to Create an .exe File

If you want to package the application into an .exe file, run the following command:

```sh
pyinstaller --onefile --windowed --icon=assets/sortify.ico --name=SortifyV1 src/main.py
```

The output will be in the [`dist`](./dist)[ folder](./dist).

## License

This project is licensed under the MIT License. See the [LICENSE](./LICENSE) file for details.

## Contribution

If you want to contribute, please submit a pull request or report bugs in this repository.

---

Developed by Putu Arka Adiana.

