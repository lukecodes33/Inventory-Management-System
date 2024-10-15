import sqlite3
from loginFunctions import get_current_time

def lowStockItems():

    """
    Displays a list of items in the inventory where the stock level is below the reorder trigger.

    - Connects to the inventory database and fetches all items.
    - Calculates the percentage of stock remaining based on the reorder trigger.
    - Identifies items where the stock level is below or equal to the reorder trigger.
    - Stores these items in a dictionary with the item code as the key and a tuple of item name and percentage as the value.
    - If any low stock items are found, prints them in a table format:
        - Columns: Item Code, Item Name, Reserve Stock Remaining (as a percentage).
        - The stock percentage is color-coded:
            - Yellow if the stock is 50% or higher of the reorder trigger.
            - Red if the stock is below 50% of the reorder trigger.
    - If no low stock items are found, prints a message indicating that stock levels are sufficient.

    This function helps identify items that may need to be reordered to avoid running out of stock.
    """

    YELLOW = '\033[93m'
    RED = '\033[91m'
    RESET = '\033[0m'
    GREEN = '\033[92m'

    itemDatabasePath = "database/itemDatabase.db"
    connection = sqlite3.connect(itemDatabasePath)
    cursor = connection.cursor()

    lowStockDictionary = {}

    cursor.execute('SELECT "Item Code", "Item Name", "Stock", "ReOrder Trigger" FROM Inventory')
    rows = cursor.fetchall()

    for row in rows:
        itemCode, itemName, stock, reOrderTrigger = row
        if reOrderTrigger >= stock:
            percentage = int((stock / reOrderTrigger) * 100)

            lowStockDictionary[itemCode] = (itemName, percentage)

    connection.close()

    if lowStockDictionary:

        print(f"\n{GREEN}{'Item Code':<15}{'Item Name':<25}{'Reserve Stock Remaining':<25}{RESET}")
        print(f"{GREEN}{'-'*15:<15}{'-'*25:<25}{'-'*25:<25}{RESET}")

        for itemCode, (itemName, percentage) in lowStockDictionary.items():
            if percentage >= 50:
                color = YELLOW
            else:
                color = RED
            print(f"{GREEN}{itemCode:<15}{itemName:<25}{color}{percentage}%{RESET}")
    else:
        print(f"{GREEN}No stock levels are low!.{RESET}")

def setReOrderLevel(adminRights):

    """
    Allows an admin user to set or update the reorder level for a specific item in the inventory.

    - Checks if the user has admin rights; if not, displays an error message and exits.
    - Prompts the user to enter an item code.
    - Connects to the inventory database and checks if the item exists.
    - If the item exists, retrieves and displays the current reorder level.
    - Prompts the user to enter a new reorder level, with input validation to ensure it is an integer.
    - Updates the reorder level for the item in the database and confirms the change.
    - If the item code is not found, displays an error message.
    - Closes the database connection after the operation.

    This function is used to maintain appropriate stock levels by setting reorder points for items in the inventory.

    Parameters:
    adminRights (bool): Indicates whether the user has administrative privileges.

    Returns:
    None
    """

    YELLOW = '\033[93m'
    RED = '\033[91m'
    RESET = '\033[0m'
    GREEN = '\033[92m'

    if adminRights:

        itemDatabasePath = "database/itemDatabase.db"
        connection = sqlite3.connect(itemDatabasePath)
        cursor = connection.cursor()

        itemCode = input(f"{YELLOW}Enter item code: {RESET}")

        cursor.execute('SELECT "ReOrder Trigger" FROM Inventory WHERE "Item Code" = ?', (itemCode,))
        result = cursor.fetchone()

        if result:
            currentReOrderLevel = result[0]
            print(f"{GREEN}Current Re Order Level: {currentReOrderLevel}{RESET}")

            while True:
                try:
                    newReOrderLevel = int(input(f"{YELLOW}Enter the new re order level: {RESET}"))
                    break
                except ValueError:
                    print(f"{RED}Invalid input. Please enter a valid integer.{RESET}")

            cursor.execute('UPDATE Inventory SET "ReOrder Trigger" = ? WHERE "Item Code" = ?', (newReOrderLevel, itemCode))
            connection.commit()
            print(f"{GREEN}ReOrder Level for {itemCode} has been updated to {newReOrderLevel}.{RESET}")

        else:
            print(f"{RED}Item Code {itemCode} not found in the inventory.{RESET}")

        connection.close()
    else:
        print(f"{RED}You do not have the necessary admin rights to perform this action.{RESET}")

def writeOffStock(adminRights, fullname):

    """
    Allows an admin user to write off a specified amount of stock for a given item.

    - Checks if the user has admin rights; if not, displays an error message and exits.
    - Prompts the user to enter an item code.
    - Connects to the inventory database and checks if the item exists.
    - If the item exists, retrieves and displays the current stock level.
    - Prompts the user to enter the amount of stock to write off, with input validation to ensure:
        - The input is a positive integer.
        - The write-off amount does not exceed the current stock level.
    - Updates the stock level in the inventory database.
    - Records the write-off action in the movements database, logging the item, amount, action type, user, and timestamp.
    - If the item code is not found, displays an error message.
    - Closes the database connections after the operation.

    This function is used to accurately manage inventory levels by allowing authorized users to remove stock that is no longer available or usable.

    Parameters:
    adminRights (bool): Indicates whether the user has administrative privileges.
    fullname (str): The full name of the user performing the write-off, used for logging the action.

    Returns:
    None
    """
    
    YELLOW = '\033[93m'
    RED = '\033[91m'
    RESET = '\033[0m'
    GREEN = '\033[92m'
    
    if adminRights:

        itemDatabasePath = "database/itemDatabase.db"
        connection = sqlite3.connect(itemDatabasePath)
        cursor = connection.cursor()


        itemCode = input(f"{YELLOW}Enter the Item Code to write off stock: {RESET}")

        cursor.execute('SELECT "Stock" FROM Inventory WHERE "Item Code" = ?', (itemCode,))
        result = cursor.fetchone()

        if result:
            currentStock = result[0]
            print(f"{GREEN}Current Stock for {itemCode}: {currentStock}{RESET}")

            while True:
                try:
                    writeOffAmount = int(input(f"{YELLOW}Enter the amount to write off: {RESET}"))

                    if writeOffAmount <= 0:
                        print(f"{RED}Invalid input. Please enter a positive integer.{RESET}")
                    elif writeOffAmount > currentStock:
                        print(f"{RED}Cannot write off more than the current stock. Please enter a smaller amount.{RESET}")
                    else:
                        break
                except ValueError:
                    print(f"{RED}Invalid input. Please enter a valid integer.{RESET}")

            newStock = currentStock - writeOffAmount

            cursor.execute('UPDATE Inventory SET "Stock" = ? WHERE "Item Code" = ?', (newStock, itemCode))
            connection.commit()
            print(f"{GREEN}Stock for {itemCode} has been updated. New stock level: {newStock}.{RESET}")
            connection.close()

            movements = "database/movements.db"
            connection = sqlite3.connect(movements)
            cursor = connection.cursor()

            cursor.execute('''
            INSERT INTO movements ("Item", "Amount", "Type", "User", "Date")
            VALUES (?, ?, ?, ?, ?)
            ''', (itemCode, writeOffAmount, "WRITE OFF", fullname, get_current_time()))
            connection.commit()
            connection.close()             

        else:
            print(f"{RED}Item Code {itemCode} not found in the inventory.{RESET}")

        connection.close()
    else:
        print(f"{RED}You do not have the necessary admin rights to perform this action.{RESET}")


