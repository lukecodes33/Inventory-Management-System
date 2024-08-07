from userConstructor import userConstructor
import sqlite3
import sys
import getpass
from loginFunctions import get_current_time, successful_login
from menus import topMenu, numberSelection, itemManagementMenu, stockOrderMenu
from itemManagementFunctions import addItem, removeItem, searchByProductCode, searchByProductName, showAllProducts
from stockOrderFunctions import createPendingOrders, showPendingOrders, receiveOrder, cancelOrder

"""
This program is something i have decided to try and create based on my experience working with various warehouse
environment applications. It is a barebones small scale inventory management system that would be effective for 
small scale bussinesses to use to keep track of inventory, orders and allow specific permissions to the required
users.
"""

"""
Establishes a connection to the user database.
"""
userDatabasePath = "database/userDatabase.db"
connection = sqlite3.connect(userDatabasePath)
cursor = connection.cursor()

"""
Initializes the attempts counter and login loop.
"""
loginLoop = True
attempts = 4


"""
Handles user login process:
- Prompts for username and password input.
- Validates credentials against the database.
- If no match is found, prompts the user.
- If the password is incorrect, prompts the user and decrements the attempts counter. Locks the account if attempts reach 0.
- If the account is locked, instructs the user to contact IT and exits.
- If credentials are correct and the account is not locked, updates last login time and exits the loop to proceed to the next menu.
"""
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

"""
Checks if the user has admin rights and sets adminRights to True or False.
This value will be used throughout the program to control access to certain functions.
Creates a fullName variable from the user's database details and passes it, along with the current time, to the successful_login function.
"""

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


"""
Main program loop:
- Displays the top menu and handles user navigation between various functions.
- Continues to run until the user selects 'exit'.
- Navigates back to the parent menu upon completing each function.
"""
while True:

    topMenu(fullName)

    topMenuSelection = numberSelection()

    while topMenuSelection == 1:
        itemManagementMenu(fullName)
        itemManagementSelection = numberSelection()

        if itemManagementSelection == 1:
            addItem(fullName, time)

        elif itemManagementSelection == 2:
            removeItem(adminRights, stored_password, fullName.username, time)

        elif itemManagementSelection == 3:
            searchByProductCode()

        elif itemManagementSelection == 4:       
            searchByProductName()

        elif itemManagementSelection == 5:       
            showAllProducts()
            
        elif itemManagementSelection == 0:
            break

        else:
            print(f"{RED}Invalid input.{RESET}")
    
    while topMenuSelection == 2:
        stockOrderMenu(fullName)
        stockOrderManagementSelection = numberSelection()

        if stockOrderManagementSelection == 1:
            createPendingOrders(fullName, time)

        elif stockOrderManagementSelection == 2:
            showPendingOrders()

        elif stockOrderManagementSelection == 3:
            receiveOrder(fullName, time)
        
        elif stockOrderManagementSelection == 4:
            cancelOrder(fullName, time)
        
        elif stockOrderManagementSelection == 0:
            break

        else:
            print(f"{RED}Invalid input.{RESET}")
