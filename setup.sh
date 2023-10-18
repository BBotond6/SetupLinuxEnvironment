#!/usr/bin/bash

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
END_COLOR='\033[0m'

setup_py='setup.py'

#Check the package manager
if command -v apt; then
	echo -e "${YELLOW}Step 1:${END_COLOR} apt update \nRefresh the local package database: sudo apt get update"
	sudo apt update
	echo -e "${YELLOW}Step 1:${END_COLOR} apt update | ${GREEN}DONE${END_COLOR}"

	echo -e "${YELLOW}Step 2:${END_COLOR} apt upgrade \nUpgrade installed packages: sudo apt get ugrade"
	sudo apt upgrade
	echo -e "${YELLOW}Step 2:${END_COLOR} apt upgrade | ${GREEN}DONE${END_COLOR}"

	#Check that python3 is installed
	if command -v python3; then
		echo -e "${YELLOW}Step 3:${END_COLOR} Install Python3 | ${GREEN}DONE${END_COLOR} \n note: Python3 is already installed!"
	else
		echo -e "${YELLOW}Step 3:${END_COLOR} Install Python3 \nPython3 is not installed! Installing..."
		sudo apt install python3
		if command -v python3; then
			echo -e "${YELLOW}Step 3:${END_COLOR} Install Python3 | ${GREEN}DONE${END_COLOR}"
		else
			echo -e "${YELLOW}Step 3:${END_COLOR} Install Python3 | ${RED}FAILED${END_COLOR} \n note: Installation of Python3 was unsuccessful!"
			
		fi
	fi
	
	if [ -e "$setup_py" ]; then
		echo -e "${YELLOW}Step 4:${END_COLOR} Find and run $setup_py | ${GREEN}DONE${END_COLOR} \n\nRun $setup_py for further configurations...\n"
		python3 setup.py
	else
		echo -e "${YELLOW}Step 4:${END_COLOR} Find and run $setup_py | ${RED}FAILED${END_COLOR} \n note: $setup_py does not exist!"
		exit 0
	fi
	
else
	echo -e "${YELLOW}Step 1:${END_COLOR} apt update | ${RED}FAILED${END_COLOR} \n note: Unsupported package manager!"
	exit 0
fi
