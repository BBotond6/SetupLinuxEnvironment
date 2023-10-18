# setup.py

import subprocess
import sys
import os

RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
END_COLOR = "\033[0m"

def DONE_event(step, message, note=None):
	if note != None:
		print(note)
	print(YELLOW + "Step " + str(step) + ": " + END_COLOR + message + " | " + GREEN + "DONE" + END_COLOR)

def FAILED_event(step, message, note):
	print(YELLOW + "Step " + str(step) + ": " + END_COLOR + message + " | " + RED + "FAILED" + END_COLOR)
	print(" note: " + note)
	sys.exit()

def RunShCommand(command):
	try:
		print("<" + command + "> Command result:")
		result = subprocess.run(command, shell=True, check=True, stderr=subprocess.PIPE, text=True)
		return True
	except subprocess.CalledProcessError as e:
		print("<" + command + f"> Command failed with return code {e.returncode}.")
		print("Error output:")
		print(e.stderr)
		return False

def RunInteractiveShCommand(command):
	try:
		print("<" + command + "> Command result:")
		result = subprocess.run(command, shell=True)
		return True
	except subprocess.CalledProcessError as e:
		return False

def ReadShCommandOut(command):
	try:
		print("<" + command + "> Command result:")
		result = subprocess.run(command, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
		return result.stdout
	except subprocess.CalledProcessError as e:
		print("<" + command + f"> Command failed with return code {e.returncode}.")
		print("Error output:")
		print(e.stderr)
		return False

def CreateLinuxGroup(group):
	try:
		print("<sudo addgroup " + group + "> Command result:")
		result = subprocess.run("sudo addgroup " + group, shell=True, check=True, stderr=subprocess.PIPE, text=True)
		return True
	except subprocess.CalledProcessError as e:
		if e.returncode == 1:
			print(e.stderr)
			return True
		else:
			print("<sudo addgroup " + group + f"> Command failed with return code {e.returncode}.")
			print("Error output:")
			print(e.stderr)
			return False

def AddSudoPrivilegesToUser(user):
	if user in ReadShCommandOut("cut -d: -f1 /etc/passwd | sort") and user in ReadShCommandOut("ls /home/"):
		CustumSudoersFile = "/etc/sudoers.d/custum_sudoers"
		AddSudoRight = user + " ALL=(ALL) ALL"

		#Check that /etc/sudoers.d/custum_sudoers file does not exist
		if ReadShCommandOut("ls " + CustumSudoersFile):
			print("Error: " + CustumSudoersFile + " file already exist!")
			return False
		else:
			print(CustumSudoersFile + " does not exist, continue to create it:")
	else:
		print("Error: Cannot give sudo privileges to " + user + " user!")
		if user not in ReadShCommandOut("cut -d: -f1 /etc/passwd | sort"):
			print(" note: " + user + " does not exist!")
		return False

	if RunShCommand("sudo sh -c \"echo '" + AddSudoRight + "' > " + CustumSudoersFile + "\""):
		print("Add sudo privileges for " + user + " into " + CustumSudoersFile + " file was successfull")
	else:
		print("Error: Create " + CustumSudoersFile + " was unsuccessfull!")
		return False

	if RunShCommand("sudo chmod 440 " + CustumSudoersFile):
		print("Set " + CustumSudoersFile + " file permissions for the owner and the group was successfull")
	else:
		print("Error: Set " + CustumSudoersFile + " file permissions for the owner and the group was unsuccessfull!")
		if RunShCommand("sudo rm -f " + CustumSudoersFile):
			print("Remove " + CustumSudoersFile + " was successfull!")
		else:
			print("Error: Remove " + CustumSudoersFile + " was unsuccessfull!")
		return False
	return True

def SetupOpenSshServer():
	#Install openssh-server
	if RunShCommand("sudo apt install -y openssh-server"):
		DONE_event(5, "Install openssh-server")
	else:
		FAILED_event(5, "Install openssh-server", "Installation of openssh-server was unsuccessfull!")
	
	#Setup openssh-server
	CommandResult = ReadShCommandOut("sudo systemctl status ssh")
	if CommandResult and "Active: active (running)" in CommandResult:
		print("SSH server is active (running)")
	else:
		FAILED_event(6, "Setup openssh-server", "SSH server is not running!")

	if RunShCommand("ufw --version"):
		print("ufw is installed!")
		if RunShCommand("sudo ufw allow ssh"):
			print("Allow SSH through UFW was successfull")
		else:
			FAILED_event(6, "Setup openssh-server", "Allow SSH through UFW was unsuccessfull!")
	else:
		print("ufw is not installed!")
	DONE_event(6, "Setup openssh-server")

def SetupRemoteDesktopAccess():
	if RunShCommand("sudo apt install xrdp"):
		print("Install xrdp was successfull")
	else:
		FAILED_event(7, "Setup remote desktop access", "Install xrdp was unsuccessfull!")

	if RunShCommand("sudo systemctl enable --now xrdp"):
		print("Enable and start xrdp service was successfull")
	else:
		FAILED_event(7, "Setup remote desktop access", "Enable and start xrdp service was unsuccessfull!")

	if RunShCommand("ufw --version"):
		print("ufw is installed!")
		if RunShCommand("sudo ufw allow from any to any port 3389 proto tcp"):
			print("Allow TCP traffic on port 3389 was successfull")
		else:
			FAILED_event(7, "Setup remote desktop access", "Allow TCP traffic on port 3389 was unsuccessfull!")
	else:
		print("ufw is not installed!")

	print(YELLOW + "\nCreate user for remote desktop access" + END_COLOR)
	NewUserName = input("Enter the user name: ")

	if RunInteractiveShCommand("sudo adduser " + NewUserName):
		print("Create " + NewUserName + " user was successfull")
	else:
		FAILED_event(7, "Setup remote desktop access", "Create " + NewUserName + " user was unsuccessfull!")

	if CreateLinuxGroup("tsusers"):
		print("Create tsusers group was successfull")
	else:
		FAILED_event(7, "Setup remote desktop access", "Create tsusers group was unsuccessfull!")

	if CreateLinuxGroup("tsadmins"):
		print("Create tsadmins group was successfull")
	else:
		FAILED_event(7, "Setup remote desktop access", "Create tsadmins group was unsuccessfull!")

	if RunShCommand("sudo usermod -a -G tsusers " + NewUserName):
		print("Add " + NewUserName + " to tsusers was successfull")
	else:
		FAILED_event(7, "Setup remote desktop access", "Add " + NewUserName + " to tsusers was unsuccessfull!")

	if RunShCommand("sudo service xrdp restart"):
		print("Restart xrdp service was successfull")
	else:
		FAILED_event(7, "Setup remote desktop access", "Restart xrdp service was unsuccessfull!")

	AddSudoPrivileges = input("Do you want to give sudo privileges to " + NewUserName + " user? (y=yes, n=no): ")
	while AddSudoPrivileges not in ("y", "n"):
		AddSudoPrivileges = input("Wrong input! (y=yes, n=no): ")
	if AddSudoPrivileges == "y":
		if AddSudoPrivilegesToUser(NewUserName):
			print("Add sudo privileges to " + NewUserName + " user was successfull!")
		else:
			FAILED_event(7, "Setup remote desktop access", "Add sudo privileges to " + NewUserName + " user was unsuccessfull!")
	DONE_event(7, "Setup remote desktop access")

def SetupSQLite():
	if RunShCommand("sudo apt install sqlite3"):
		DONE_event(8, "Setup SQLite database", "Install SQLite was successfull")
	else:
		FAILED_event(8, "Setup SQLite database", "Install SQLite was unsuccessfull!")

def SetupCppEnvironment():
	if RunShCommand("sudo apt install build-essential"):
		DONE_event(9, "Install build-essential", "Install build-essential was successfull")
	else:
		FAILED_event(9, "Install build-essential", "Install build-essential was unsuccessfull!")

	if RunShCommand("sudo apt install libpoppler-glib-dev"):
		DONE_event(10, "Install Poppler", "Install Poppler was successfull")
	else:
		FAILED_event(10, "Install Poppler", "Install Poppler was unsuccessfull!")

	if RunShCommand("sudo apt install libglib2.0-dev"):
		DONE_event(11, "Install GLib", "Install GLib was successfull")
	else:
		FAILED_event(11, "Install GLib", "Install GLib was unsuccessfull!")

def InstallBashCompletion():
	if RunShCommand("sudo apt install bash-completion"):
		DONE_event(12, "Install bash completion", "Install bash completion was successfull")
	else:
		FAILED_event(12, "Install bash completion", "Install bash completion was unsuccessfull!")

def main():
	SetupOpenSshServer()
	SetupRemoteDesktopAccess()
	SetupSQLite()
	SetupCppEnvironment()
	InstallBashCompletion()

if __name__ == "__main__":
	main()
