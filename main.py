from userConstructor import userConstructor
import sqlite3
import sys
import getpass
from loginFunctions import get_current_time, successful_login
from menus import topMenu, numberSelection, itemManagementMenu, searchItemMenu
from itemManagementFunctions import addItem, removeItem, searchByProductCode, searchByProductName, showAllProducts

userDatabasePath = "database/userDatabase.db"
connection = sqlite3.connect(userDatabasePath)
cursor = connection.cursor()

loginLoop = True
attempts = 4

while loginLoop == True:
    if attempts == 0:
        sys.exit(0)

    userNameInput = input("Username: ")
    passwordInput = getpass.getpass("Password: ")

    user = userConstructor(userNameInput, passwordInput)

    cursor.execute("SELECT password, locked FROM users WHERE username = ?", (user.username,))
    match = cursor.fetchone()

    if match is not None:
        stored_password = match[0]
        lockStatus = match[1]
        
        if stored_password == user.password and lockStatus != 1:
            time = get_current_time()
            cursor.execute("UPDATE users SET last_login = ? WHERE username = ?", (time, user.username))
            connection.commit()
            loginLoop = False

        elif stored_password == user.password and lockStatus == 1:
            print("Account is locked, contact IT to unlock")
            
        elif stored_password != user.password:
            attempts -= 1
            if attempts > 0:
                print(f"Incorrect password - {attempts} attempts remaining!")
            
            else:
                print("Account is now locked, contact IT to unlock")
                cursor.execute("UPDATE users SET locked = ? WHERE username = ?", (1, user.username))
                connection.commit()
    
    if match == None:
        print("Username not found")

cursor.execute("SELECT first_name, last_name, admin_rights FROM users WHERE username = ?", (user.username,))
match = cursor.fetchone()
firstName = match[0]
lastName = match[1]
admin_rights_value = match[2]
fullName = firstName + " " + lastName
adminRights = False

if admin_rights_value == 1:
    adminRights = True

successful_login(fullName, time)

connection.close()

RED = '\033[91m'
RESET = '\033[0m'


while True:

    topMenu(fullName)

    topMenuSelection = numberSelection()

    while topMenuSelection == 1:
        itemManagementMenu(fullName)
        itemManagementSelection = numberSelection()

        if itemManagementSelection == 1:
            addItem()

        elif itemManagementSelection == 2:
            removeItem(adminRights, stored_password)

        elif itemManagementSelection == 3:

            itemManagementLoop = True

            while itemManagementLoop == True:
            
                searchItemMenu(fullName)
                
                searchItemSelection = numberSelection()

                if searchItemSelection == 1:
                    searchByProductCode()
                
                elif searchItemSelection == 2:
                    searchByProductName()
                
                elif searchItemSelection == 3:
                    showAllProducts()

                elif searchItemSelection == 0:
                    itemManagementLoop == False
                    break

                else:
                    print(f"{RED}Invalid input. Please enter 'Y' to confirm or 'N' to cancel.{RESET}")
            
        elif itemManagementSelection == 0:
            break

        else:
            print(f"{RED}Invalid input.{RESET}")