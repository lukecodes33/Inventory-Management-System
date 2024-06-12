import sqlite3

def get_decimal_input(prompt):

    RED = '\033[91m'
    RESET = '\033[0m'

    while True:
        try:
            value = float(input(prompt))
            if round(value, 2) == value:
                return value
            else:
                print(f"{RED}Invalid input. Please enter a number with up to 2 decimal places.{RESET}")
        except ValueError:
            print(f"{RED}Invalid input. Please enter a valid number.{RESET}")


def addItem():

    YELLOW = '\033[93m'
    RED = '\033[91m'
    RESET = '\033[0m'
    GREEN = '\033[92m'

    itemDatabasePath = "Inventory-Management-System/database/itemDatabase.db"
    connection = sqlite3.connect(itemDatabasePath)
    cursor = connection.cursor()


    itemCode = input(f"\n{YELLOW}Item Code: {RESET}")
    itemName = input(f"{YELLOW}Item Name: {RESET}")
    stockCount = input(f"{YELLOW}Stock: {RESET}")
    reOrderTrigger = get_decimal_input(f"{YELLOW}Re-Order Trigger: {RESET}")
    purchasePrice = get_decimal_input(f"{YELLOW}Purchase Price: {RESET}")
    salesPrice = get_decimal_input(f"{YELLOW}Sales Price: {RESET}")

    print(f"""
            CREATED ITEM
          
Item Code - {itemCode}
Item Name - {itemName}
Stock - {stockCount}
Order Trigger - {reOrderTrigger}
Purchase Price - {purchasePrice}
Sales Price - {salesPrice}\n""")
        
    while True:
        answer = input(f"{YELLOW}Select Y to proceed or N to cancel: {RESET}").strip().upper()

        if answer == "Y":
            cursor.execute('''
            INSERT INTO Inventory ("Item Code", "Item Name", Stock, "On Order", "ReOrder Trigger", "Purchase Price", "Sale Price", "Amount Sold", Profit)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (itemCode, itemName, stockCount, 0, reOrderTrigger, purchasePrice, salesPrice, 0, 0))  

            connection.commit()
            connection.close()
            print(f"\n{GREEN} {itemCode} successfully added!")
            break

        elif answer == "N":
            break

        else: 
            print(f"{RED} Invalid input. Please enter 'Y' to proceed or 'N' to cancel.{RESET}")

def removeItem(adminRights, storedPassword):

    YELLOW = '\033[93m'
    RED = '\033[91m'
    RESET = '\033[0m'
    GREEN = '\033[92m'

    if adminRights:
        enteredPassword = input(f"{YELLOW}Enter admin password: {RESET}")
        if enteredPassword != storedPassword:
            print(f"{RED}Incorrect password. Access denied.{RESET}")
            return

        itemDatabasePath = "Inventory-Management-System/database/itemDatabase.db"
        connection = sqlite3.connect(itemDatabasePath)
        cursor = connection.cursor()

        while True:
            code = input(f"{YELLOW}Enter product code to delete: {RESET}")

            cursor.execute('''SELECT "Item Code", "Item Name" FROM Inventory WHERE "Item Code" = ?''', (code,))
            match = cursor.fetchone()

            if match:
                itemCode, itemName = match
                print(f"{GREEN}Item found: {itemCode} - {itemName}{RESET}")

                while True:
                        confirm = input(f"{YELLOW}Are you sure you want to delete this item? (Y/N): {RESET}").strip().upper()
                        if confirm == 'Y':
                            cursor.execute('''DELETE FROM Inventory WHERE "Item Code" = ?''', (code,))
                            connection.commit()
                            print(f"{GREEN}Item {itemCode} - {itemName} has been deleted.{RESET}")
                            connection.close()
                            return
                        elif confirm == 'N':
                            print(f"{YELLOW}Item deletion cancelled.{RESET}")
                            connection.close()
                            return
                        else:
                            print(f"{RED}Invalid input. Please enter 'Y' to confirm or 'N' to cancel.{RESET}")
            else:
                print(f"{RED}Item not found{RESET}")
                break

        connection.close()
    else:
        print(f"{RED}You do not have permission to access this{RESET}")
