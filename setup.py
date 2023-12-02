# setup.py

import subprocess
import sys
import os
import pexpect
import getpass

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

def RunShExpectCommand(command, exit_str, *args):
	if len(args) == 0:
		print("Error: The function need at least 2 more argument! (command, expect, send, ..., ...)")
		return False
	if len(args) % 2 != 0:
		print("Error: Arguments must be paired after the command! (command, expect, send, ..., ...)")
		return False

	ExpectScript = f"""
set timeout 30

# Disable output to terminal
# For debugging set it to 1
# Attention! In this case, the password can be displayed on the terminal for some errors!
log_user 0

spawn {command}
	"""

	for i in range(0, len(args), 2):
		ExpectScript += f"""
expect -exact "{args[i]}"
send -- "{args[i + 1]}\\r"
		"""

	ExpectScript += f"""
expect -exact "{exit_str}" {
	"exit"
}
expect eof
	"""

	# Run the ExpectScript
	ExpectProcess = pexpect.spawn('/usr/bin/expect', encoding='utf-8')
	ExpectProcess.send(ExpectScript)
	ExpectProcess.expect(pexpect.EOF)
	ExpectProcess.close()
	return True

def GetSudoPassword():
	print(YELLOW + "\nEnter user password" + END_COLOR)
	UserPassword = getpass.getpass("[sudo] password for " + getpass.getuser() + ":")
	return UserPassword

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

def SetupOpenSshServer(step):
	StepName = "Setup openssh-server"

	#Install openssh-server
	if RunShCommand("sudo apt install -y openssh-server"):
		print("Install openssh-server was successfull")
	else:
		FAILED_event(step, StepName, "Installation of openssh-server was unsuccessfull!")
	
	#Setup openssh-server
	CommandResult = ReadShCommandOut("sudo systemctl status ssh")
	if CommandResult and "Active: active (running)" in CommandResult:
		print("SSH server is active (running)")
	else:
		FAILED_event(step, StepName, "SSH server is not running!")

	if RunShCommand("ufw --version"):
		print("ufw is installed!")
		if RunShCommand("sudo ufw allow ssh"):
			print("Allow SSH through UFW was successfull")
		else:
			FAILED_event(step, StepName, "Allow SSH through UFW was unsuccessfull!")
	else:
		print("ufw is not installed!")
	DONE_event(step, StepName)

def SetupRemoteDesktopAccess(step):
	StepName = "Setup remote desktop access"

	if RunShCommand("sudo apt install xrdp"):
		print("Install xrdp was successfull")
	else:
		FAILED_event(step, StepName, "Install xrdp was unsuccessfull!")

	if RunShCommand("sudo systemctl enable --now xrdp"):
		print("Enable and start xrdp service was successfull")
	else:
		FAILED_event(step, StepName, "Enable and start xrdp service was unsuccessfull!")

	if RunShCommand("ufw --version"):
		print("ufw is installed!")
		if RunShCommand("sudo ufw allow from any to any port 3389 proto tcp"):
			print("Allow TCP traffic on port 3389 was successfull")
		else:
			FAILED_event(step, StepName, "Allow TCP traffic on port 3389 was unsuccessfull!")
	else:
		print("ufw is not installed!")

	print(YELLOW + "\nCreate user for remote desktop access" + END_COLOR)
	NewUserName = input("Enter the user name: ")

	if RunInteractiveShCommand("sudo adduser " + NewUserName):
		print("Create " + NewUserName + " user was successfull")
	else:
		FAILED_event(step, StepName, "Create " + NewUserName + " user was unsuccessfull!")

	if CreateLinuxGroup("tsusers"):
		print("Create tsusers group was successfull")
	else:
		FAILED_event(step, StepName, "Create tsusers group was unsuccessfull!")

	if CreateLinuxGroup("tsadmins"):
		print("Create tsadmins group was successfull")
	else:
		FAILED_event(step, StepName, "Create tsadmins group was unsuccessfull!")

	if RunShCommand("sudo usermod -a -G tsusers " + NewUserName):
		print("Add " + NewUserName + " to tsusers was successfull")
	else:
		FAILED_event(step, StepName, "Add " + NewUserName + " to tsusers was unsuccessfull!")

	if RunShCommand("sudo service xrdp restart"):
		print("Restart xrdp service was successfull")
	else:
		FAILED_event(step, StepName, "Restart xrdp service was unsuccessfull!")

	AddSudoPrivileges = input("Do you want to give sudo privileges to " + NewUserName + " user? (y=yes, n=no): ")
	while AddSudoPrivileges not in ("y", "n"):
		AddSudoPrivileges = input("Wrong input! (y=yes, n=no): ")
	if AddSudoPrivileges == "y":
		if AddSudoPrivilegesToUser(NewUserName):
			print("Add sudo privileges to " + NewUserName + " user was successfull!")
		else:
			FAILED_event(step, StepName, "Add sudo privileges to " + NewUserName + " user was unsuccessfull!")
	DONE_event(step, StepName)

def SetupSQLite(step):
	StepName = "Setup SQLite database"

	if RunShCommand("sudo apt install sqlite3"):
		DONE_event(step, StepName, "Install SQLite was successfull")
	else:
		FAILED_event(step, StepName, "Install SQLite was unsuccessfull!")

def SetupCppEnvironment(step):
	StepName = "Setup C++ environment"

	if RunShCommand("sudo apt install build-essential"):
		print("Install build-essential was successfull")
	else:
		FAILED_event(step, StepName, "Install build-essential was unsuccessfull!")

	if RunShCommand("sudo apt install libpoppler-glib-dev"):
		print("Install Poppler was successfull")
	else:
		FAILED_event(step, StepName, "Install Poppler was unsuccessfull!")

	if RunShCommand("sudo apt install libglib2.0-dev"):
		print("Install GLib was unsuccessfull!")
	else:
		FAILED_event(step, StepName, "Install GLib was unsuccessfull!")
	DONE_event(step, StepName)

def InstallBashCompletion(step):
	StepName = "Install bash completion"

	if RunShCommand("sudo apt install bash-completion"):
		DONE_event(step, StepName, "Install bash completion was successfull")
	else:
		FAILED_event(step, StepName, "Install bash completion was unsuccessfull!")

def SetupMariaDB(step):
	StepName = "Setup MariaDB server"

	if RunShCommand("sudo apt install mariadb-server"):
		print("Install MariaDB server was successfull")
	else:
		FAILED_event(step, StepName, "Install MariaDB server was unsuccessfull!")

	print(YELLOW + "\nSet new password for the root user" + END_COLOR)
	RootUserPassword = getpass.getpass("New password: ")
	PasswordCounter = 0
	while 1:
		ReRootUserPassword = getpass.getpass("Re-enter new password :")
		PasswordCounter += 1
		if PasswordCounter >= 6:
			FAILED_event(step, StepName, "Setup new password for the root user was unsuccessfull!")
		if RootUserPassword == ReRootUserPassword:
			break
		print("The two passwords do not match. Try again!")
		RootUserPassword = getpass.getpass("(" + str(PasswordCounter + 1) + ". try) New password: ")

	if RunShExpectCommand("sudo mysql_secure_installation", "Thanks for using MariaDB!",
							"[sudo] password for " + getpass.getuser() + ":", GetSudoPassword(),
							"Enter current password for root (enter for none):", "",
							"Switch to unix_socket authentication [Y/n]", "y",
							"Change the root password? [Y/n]", "y",
							"New password:", RootUserPassword,
							"Re-enter new password:", RootUserPassword,
							"Remove anonymous users?", "y",
							"Disallow root login remotely?", "y",
							"Remove test database and access to it?", "y",
							"Reload privilege tables now?", "y"):
		print("Setup root access was successfull")
	else:
		FAILED_event(step, StepName, "Setup root access was unsuccessfull!")
	DONE_event(step, StepName)

def main():
	SetupOpenSshServer(5)
	SetupRemoteDesktopAccess(6)
	SetupSQLite(7)
	SetupCppEnvironment(8)
	InstallBashCompletion(9)
	SetupMariaDB(10)

if __name__ == "__main__":
	main()
