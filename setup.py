# setup.py

import subprocess
import sys
import os

RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
END_COLOR = "\033[0m"

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

		if RunShCommand("sudo sh -c \"echo '" + AddSudoRight + "' > " + CustumSudoersFile + "\""):
			print("Add sudo privileges for " + user + " into " + CustumSudoersFile + " file was successfull")
			if RunShCommand("sudo chmod 440 " + CustumSudoersFile):
				print("Set " + CustumSudoersFile + " file permissions for the owner and the group was successfull")
			else:
				print("Error: Set " + CustumSudoersFile + " file permissions for the owner and the group was unsuccessfull!")
				if RunShCommand("sudo rm -f " + CustumSudoersFile):
					print("Remove " + CustumSudoersFile + " was successfull!")
				else:
					print("Error: Remove " + CustumSudoersFile + " was unsuccessfull!")
				return False
		else:
			print("Error: Create " + CustumSudoersFile + " was unsuccessfull!")
			return False
		return True
	else:
		print("Error: Cannot give sudo privileges to " + user + " user!")
		if user not in ReadShCommandOut("cut -d: -f1 /etc/passwd | sort"):
			print(" note: " + user + " does not exist!")
		return False

def SetupOpenSshServer():
	#Install openssh-server
	if RunShCommand("sudo apt install -y openssh-server"):
		print(YELLOW + "Step 4:" + END_COLOR + " Install openssh-server | " + GREEN + "DONE" + END_COLOR)
	else:
		print(YELLOW + "Step 4:" + END_COLOR + " Install openssh-server | " + RED + "FAILED" + END_COLOR)
		print(" note: Installation of openssh-server was unsuccessfull!")
		sys.exit()	
	
	#Setup openssh-server
	CommandResult = ReadShCommandOut("sudo systemctl status ssh")
	if CommandResult and "Active: active (running)" in CommandResult:
		print("SSH server is active (running)")
		if RunShCommand("ufw --version"):
			print("ufw is installed!")
			if RunShCommand("sudo ufw allow ssh"):
				print("Allow SSH through UFW was successfull")
			else:
				print(YELLOW + "Step 5:" + END_COLOR + " Setup openssh-server | " + RED + "FAILED" + END_COLOR)
				print(" note: Allow SSH through UFW was unsuccessfull!")
				sys.exit()
		else:
			print("ufw is not installed!")
		
		print(YELLOW + "Step 5:" + END_COLOR + " Setup openssh-server | " + GREEN + "DONE" + END_COLOR)
	else:
		print(YELLOW + "Step 5:" + END_COLOR + " Setup openssh-server | " + RED + "FAILED" + END_COLOR)
		print(" note: SSH server is not running!")
		sys.exit()

def SetupRemoteDesktopAccess():
	if RunShCommand("sudo apt install xrdp"):
		print("Install xrdp was successfull")
		if RunShCommand("sudo systemctl enable --now xrdp"):
			print("Enable and start xrdp service was successfull")
			if RunShCommand("ufw --version"):
				print("ufw is installed!")
				if RunShCommand("sudo ufw allow from any to any port 3389 proto tcp"):
					print("Allow TCP traffic on port 3389 was successfull")
				else:
					print(YELLOW + "Step 6:" + END_COLOR + " Setup remote desktop access | " + RED + "FAILED" + END_COLOR)
					print(" note: Allow TCP traffic on port 3389 was unsuccessfull!")
					sys.exit()
			else:
				print("ufw is not installed!")

			print(YELLOW + "\nCreate user for remote desktop access" + END_COLOR)
			NewUserName = input("Enter the user name: ")
			if RunInteractiveShCommand("sudo adduser " + NewUserName):
				print("Create " + NewUserName + " user was successfull")
				if CreateLinuxGroup("tsusers"):
					print("Create tsusers group was successfull")
					if CreateLinuxGroup("tsadmins"):
						print("Create tsadmins group was successfull")
						if RunShCommand("sudo usermod -a -G tsusers " + NewUserName):
							print("Add " + NewUserName + " to tsusers was successfull")
							if RunShCommand("sudo service xrdp restart"):
								print("Restart xrdp service was successfull")

								AddSudoPrivileges = input("Do you want to give sudo privileges to " + NewUserName + " user? (y=yes, n=no): ")
								while AddSudoPrivileges not in ("y", "n"):
									AddSudoPrivileges = input("Wrong input! (y=yes, n=no): ")

								if AddSudoPrivileges == "y":
									if AddSudoPrivilegesToUser(NewUserName):
										print("Add sudo privileges to " + NewUserName + " user was successfull!")
									else:
										print(YELLOW + "Step 6:" + END_COLOR + " Setup remote desktop access | " + RED + "FAILED" + END_COLOR)
										print(" note: Add sudo privileges to " + NewUserName + " user was unsuccessfull!")
										sys.exit()

							else:
								print(YELLOW + "Step 6:" + END_COLOR + " Setup remote desktop access | " + RED + "FAILED" + END_COLOR)
								print(" note: Restart xrdp service was unsuccessfull!")
								sys.exit()
						else:
							print(YELLOW + "Step 6:" + END_COLOR + " Setup remote desktop access | " + RED + "FAILED" + END_COLOR)
							print(" note: Add " + NewUserName + " to tsusers was unsuccessfull!")
							sys.exit()

					else:
						print(YELLOW + "Step 6:" + END_COLOR + " Setup remote desktop access | " + RED + "FAILED" + END_COLOR)
						print(" note: Create tsadmins group was unsuccessfull!")
						sys.exit()
				else:
					print(YELLOW + "Step 6:" + END_COLOR + " Setup remote desktop access | " + RED + "FAILED" + END_COLOR)
					print(" note: Create tsusers group was unsuccessfull!")
					sys.exit()
			else:
				print(YELLOW + "Step 6:" + END_COLOR + " Setup remote desktop access | " + RED + "FAILED" + END_COLOR)
				print(" note: Create " + NewUserName + " user was unsuccessfull!")
				sys.exit()

		else:
			print(YELLOW + "Step 6:" + END_COLOR + " Setup remote desktop access | " + RED + "FAILED" + END_COLOR)
			print(" note: Enable and start xrdp service was unsuccessfull!")
			sys.exit()

		print(YELLOW + "Step 6:" + END_COLOR + " Setup remote desktop access | " + GREEN + "DONE" + END_COLOR)
	else:
		print(YELLOW + "Step 6:" + END_COLOR + " Setup remote desktop access | " + RED + "FAILED" + END_COLOR)
		print(" note: Install xrdp was unsuccessfull!")
		sys.exit()

def SetupSQLite():
	if RunShCommand("sudo apt install sqlite3"):
		print("Install SQLite was successfull")
		print(YELLOW + "Step 7:" + END_COLOR + " Setup SQLite database | " + GREEN + "DONE" + END_COLOR)
	else:
		print(YELLOW + "Step 7:" + END_COLOR + " Setup SQLite database | " + RED + "FAILED" + END_COLOR)
		print(" note: Install SQLite was unsuccessfull!")
		sys.exit()

def SetupCppEnvironment():
	if RunShCommand("sudo apt install build-essential"):
		print("Install build-essential was successfull")

		print(YELLOW + "Step 8:" + END_COLOR + " Install build-essential | " + GREEN + "DONE" + END_COLOR)
	else:
		print(YELLOW + "Step 8:" + END_COLOR + " Install build-essential | " + RED + "FAILED" + END_COLOR)
		print(" note: Install build-essential was unsuccessfull!")
		sys.exit()

	if RunShCommand("sudo apt install libpoppler-glib-dev"):
		print("Install Poppler was successfull")

		print(YELLOW + "Step 9:" + END_COLOR + " Install Poppler | " + GREEN + "DONE" + END_COLOR)
	else:
		print(YELLOW + "Step 9:" + END_COLOR + " Install Poppler | " + RED + "FAILED" + END_COLOR)
		print(" note: Install Poppler was unsuccessfull!")
		sys.exit()

	if RunShCommand("sudo apt-get install libglib2.0-dev"):
		print("Install GLib was successfull")

		print(YELLOW + "Step 10:" + END_COLOR + " Install GLib | " + GREEN + "DONE" + END_COLOR)
	else:
		print(YELLOW + "Step 10:" + END_COLOR + " Install GLib | " + RED + "FAILED" + END_COLOR)
		print(" note: Install GLib was unsuccessfull!")
		sys.exit()

def main():
	SetupOpenSshServer()
	SetupRemoteDesktopAccess()
	SetupSQLite()
	SetupCppEnvironment()

if __name__ == "__main__":
	main()
