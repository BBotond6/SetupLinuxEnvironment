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
		if RunShCommand("sudo ufw allow ssh"):
			print("Allow SSH through UFW was successfull")
		else:
			print(YELLOW + "Step 5:" + END_COLOR + " Setup openssh-server | " + RED + "FAILED" + END_COLOR)
			print(" note: Allow SSH through UFW was unsuccessfull!")
			sys.exit()
		
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
			if RunShCommand("sudo ufw allow from any to any port 3389 proto tcp"):
				print("Allow TCP traffic on port 3389 was successfull")
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
				print(" note: Allow TCP traffic on port 3389 was unsuccessfull!")
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

def main():
	SetupOpenSshServer()
	SetupRemoteDesktopAccess()
	
if __name__ == "__main__":
	main()
