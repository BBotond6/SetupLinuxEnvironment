# Raspberry Pi Environment Setup Scripts

These scripts are designed to streamline the setup process for a development environment on a Raspberry Pi.
Tested on Raspberry Pi 4 (4GB) running both Ubuntu and Raspberry Pi OS, the scripts cover various essential
configurations and installations to enhance your Raspberry Pi for development tasks.

## Features

- **OpenSSH Server Setup:** Securely access your Raspberry Pi remotely via SSH.
- **Remote Desktop Access:** Configure and enable remote desktop access for convenient graphical interaction.
- **SQLite Database Setup:** Install SQLite for lightweight local database operations.
- **C++ Development Environment:** Set up the necessary tools for C++ development, including build essentials and the Poppler library.
- **Bash Completion Installation:** Enhance your shell experience with bash completion for efficient command-line usage.
- **MariaDB Server Setup:** Install and secure MariaDB, a powerful open-source relational database server.
- **Arduino Installation:** Simplify the installation of the Arduino IDE for embedded systems development.

## Scripts

- **setup.sh:** A Bash script orchestrating the overall setup process. It checks for Python installation, updates packages,
  installs dependencies, and initiates the ```setup.py``` Python script for further configurations.
- **setup.py:** A Python script complementing the Bash script. It provides a modular approach to specific tasks,
  such as adding sudo privileges and configuring services.

## Usage

- Clone the repository to your Raspberry Pi.
- Make ```setup.sh``` executable:
  
  ```chmod +x setup.sh```
- Run the ```setup.sh``` script to automate the environment setup:
  
  ```./setup.sh```
