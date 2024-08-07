import sqlite3
import random
import os
import csv
from loginFunctions import get_current_time

def createPendingOrders(fullName):
   
    """
    Creates a pending order in the system.

    - Prompts the user for an order reference number. If the user does not provide one, a random 10-digit reference number is auto-generated.
    - Prompts the user to enter item codes and amounts, validating that the item exists in the inventory.
    - Updates the inventory database to reflect the pending order and stock on order value.
    - Logs the pending order in the pending orders database and records the transaction in the movements database.
    - Allows the user to add multiple items to the same order.
    
    Parameters:
    fullName (str): The full name of the user creating the pending order.
    """

    YELLOW = '\033[93m'
    RED = '\033[91m'
    RESET = '\033[0m'
    GREEN = '\033[92m'

    reference = input(f"\n{YELLOW}Do you have a order reference number? leave blank to auto generate: {RESET}")

    if reference == "":
        generatedReferenceNumber = ''.join([str(random.randint(0, 9)) for _ in range(10)])
        reference = generatedReferenceNumber

    print(f"\n{YELLOW}Generated reference number: {reference} {RESET}")

    while True:
        itemDatabasePath = "database/itemDatabase.db"
        connection = sqlite3.connect(itemDatabasePath)
        cursor = connection.cursor()
        
        while True:
            itemCode = input(f"\n{YELLOW}Item Code: {RESET}")
            cursor.execute('SELECT "Item Code" FROM Inventory WHERE "Item Code" = ?', (itemCode,))
            existingItem = cursor.fetchone()
            
            if existingItem:
                 break
            
            else:
                print(f"{RED} Item code does not exist! (If item is new, create it in the Add Item function first){RESET}")

        while True:
            try:
                amount = int(input(f"{YELLOW}Amount: {RESET}"))
                break
            except ValueError:
                    print(f"{RED} Please enter a valid integer{RESET}")

        while True:
            confirmation = input(f"{YELLOW}Confirm? (Y/N): {RESET}").strip().upper()
            if confirmation in ['Y', 'N']:
                break
            else:
                print(f"{RED}Please enter 'Y' or 'N'{RESET}")

        if confirmation == 'N':
            break
            

        cursor.execute('SELECT "On Order" FROM Inventory WHERE "Item Code" = ?', (itemCode,))
        currentOnOrder = cursor.fetchone()[0]
        newOnOrder = currentOnOrder + amount
        cursor.execute('UPDATE Inventory SET "On Order" = ? WHERE "Item Code" = ?', (newOnOrder, itemCode))
        connection.commit()
        connection.close()

        pendingOrderDatabasePath = "database/pendingOrdersDatabase.db"
        connection = sqlite3.connect(pendingOrderDatabasePath)
        cursor = connection.cursor()

        cursor.execute('''
                INSERT INTO pendingOrders ("Item Code", "Amount", "Reference", "User", "Date")
                VALUES (?, ?, ?, ?, ?)
                ''', (itemCode, amount, reference, fullName, get_current_time()))
        connection.commit()
        connection.close() 

        movements = "database/movements.db"
        connection = sqlite3.connect(movements)
        cursor = connection.cursor()

        cursor.execute('''
                INSERT INTO movements ("Item", "Amount", "Type", "User", "Date")
                VALUES (?, ?, ?, ?, ?)
                ''', (itemCode, amount, "PENDING ORDER", fullName, get_current_time()))
        connection.commit()
        connection.close() 

        print(f"{GREEN}\nPending order placed!{RESET}")

        anotherItem = input(f"\n{YELLOW}Are there any more items on this order? (Y/N): {RESET}").strip().upper()

        if anotherItem != 'Y':
            break

def showPendingOrders():
    
    """
    Displays all pending orders from the database and offers the option to export the results to a CSV file.

    - Connects to the pending orders database.
    - Fetches all pending orders and displays them in a formatted table.
    - Prompts the user to export the displayed results to a CSV file.
    - Handles user input validation for the export option.
    - Exports the results to a CSV file on the user's desktop if requested.
    """
    
    YELLOW = '\033[93m'
    RED = '\033[91m'
    RESET = '\033[0m'
    GREEN = '\033[92m'

    pendingOrdersDatabasePath = "database/pendingOrdersDatabase.db"
    connection = sqlite3.connect(pendingOrdersDatabasePath)
    cursor = connection.cursor()

    cursor.execute('''
    SELECT "Item Code", "Amount", "Reference", "User", "Date"
    FROM pendingOrders
    ''')

    matches = cursor.fetchall()

    if matches:
        rows = [("Item Code", "Amount", "Reference", "User", "Date")]
        rows.extend(matches)

        print(f"\n{GREEN}{'Item Code':<15}{'Amount':<10}{'Reference':<20}{'User':<20}{'Date':<15}{RESET}")
        print(f"{GREEN}{'-'*15:<15}{'-'*10:<10}{'-'*20:<20}{'-'*20:<20}{'-'*15:<15}{RESET}")

        for match in matches:
            itemCode, amount, reference, user, date = match
            print(f"{GREEN}{itemCode:<15}{amount:<10}{reference:<20}{user:<20}{date:<15}{RESET}")

        while True:
            export = input(f"\n{YELLOW}Do you want to export the results to a CSV file? (Y/N): {RESET}").strip().upper()
            if export in ['Y', 'N']:
                break
            else:
                print(f"{RED}Please enter 'Y' or 'N'{RESET}")
        
        if export == 'Y':
            desktopPath = os.path.join(os.path.expanduser("~"), "Desktop")
            filename = os.path.join(desktopPath, "pending_orders.csv")
            with open(filename, 'w', newline='') as csvfile:
                csvwriter = csv.writer(csvfile)
                csvwriter.writerows(rows)
            print(f"{GREEN}Data has been exported to '{filename}'.{RESET}")

    else:
        print(f"{RED}No pending orders found in the database.{RESET}")

    connection.close()

def receiveOrder(fullName):

    """
    Processes the receiving of a pending order.

    - Takes input from the user for the order reference number.
    - Retrieves all matches for that reference number from the pending orders database.
    - Prompts the user to confirm the receipt of each item in the order.
    - Updates the stock and on order values in the item database.
    - Removes the processed order from the pending orders database.
    - Logs the transaction in the movements database.

    Parameters:
    fullName (str): The full name of the user processing the order.
    """
    
    YELLOW = '\033[93m'
    RED = '\033[91m'
    RESET = '\033[0m'
    GREEN = '\033[92m'

    referenceNumber = input(f"\n{YELLOW}Order reference number: {RESET}")

    pendingOrdersDatabasePath = "database/pendingOrdersDatabase.db"
    connectionPendingOrders = sqlite3.connect(pendingOrdersDatabasePath)
    cursorPendingOrders = connectionPendingOrders.cursor()

    itemDatabasePath = "database/itemDatabase.db"
    connectionItem = sqlite3.connect(itemDatabasePath)
    cursorItem = connectionItem.cursor()

    movementsDatabasePath = "database/movements.db"
    connectionMovements = sqlite3.connect(movementsDatabasePath)
    cursorMovements = connectionMovements.cursor()

    cursorPendingOrders.execute('''
    SELECT "Item Code", "Amount"
    FROM pendingOrders
    WHERE "Reference" = ?
    ''', (referenceNumber,))

    matches = cursorPendingOrders.fetchall()

    if matches:

        for match in matches:
            itemCode, amount = match

            while True:
                useLine = input(f"\n{YELLOW}Have you recieved {itemCode} - {amount}? (Y/N){RESET}").strip().upper()
                if useLine in ['Y', 'N']:
                    break
                else:
                    print(f"{RED}Please enter 'Y' or 'N'{RESET}")

            if useLine == "Y":
                
                cursorItem.execute('SELECT "Stock", "On Order" FROM Inventory WHERE "Item Code" = ?', (itemCode,))
                stock, on_order = cursorItem.fetchone()

                newStock = stock + amount
                newOnOrder = on_order - amount

                cursorItem.execute('UPDATE Inventory SET "Stock" = ?, "On Order" = ? WHERE "Item Code" = ?',
                                    (newStock, newOnOrder, itemCode))
                connectionItem.commit()

                cursorMovements.execute('INSERT INTO Movements ("Item", "Amount", "Type", "User", "Date") VALUES (?, ?, ?, ?, ?)', (itemCode, amount, "RECIEVED ORDER", fullName, get_current_time()))
                connectionMovements.commit()

                cursorPendingOrders.execute('DELETE FROM pendingOrders WHERE "Reference" = ? AND "Item Code" = ?',
                                    (referenceNumber, itemCode))
                connectionPendingOrders.commit()

                print(f"{GREEN}Order with reference {referenceNumber} has been processed and updated.{RESET}")

        connectionItem.close()
        connectionMovements.close()
        
    else:
        print(f"{RED}No matching orders found for reference {referenceNumber}.{RESET}")

    connectionPendingOrders.close()

def cancelOrder(fullName):

    """
    Cancels a pending order or partial order based on user input.

    - Takes input from the user for the order reference number.
    - Retrieves all matches for that reference number from the pending orders database.
    - Prompts the user to confirm the cancellation of each item in the order.
    - Updates the inventory database to reflect the cancellation.
    - Removes the cancelled order from the pending orders database.
    - Logs the cancellation transaction in the movements database.

    Parameters:
    fullName (str): The full name of the user performing the cancellation.
    """
    
    YELLOW = '\033[93m'
    RED = '\033[91m'
    RESET = '\033[0m'
    GREEN = '\033[92m'

    referenceNumber = input(f"\n{YELLOW}Order reference number: {RESET}")

    pendingOrdersDatabasePath = "database/pendingOrdersDatabase.db"
    connectionPending = sqlite3.connect(pendingOrdersDatabasePath)
    cursorPending = connectionPending.cursor()

    itemDatabasePath = "database/itemDatabase.db"
    connectionItem = sqlite3.connect(itemDatabasePath)
    cursorItem = connectionItem.cursor()

    movementsDatabasePath = "database/movements.db"
    connectionMovements = sqlite3.connect(movementsDatabasePath)
    cursorMovements = connectionMovements.cursor()

    cursorPending.execute('''
    SELECT "Item Code", "Amount"
    FROM pendingOrders
    WHERE "Reference" = ?
    ''', (referenceNumber,))

    matches = cursorPending.fetchall()

    if matches:

        for match in matches:
            itemCode, amount = match

            while True:
                useLine = input(f"\n{YELLOW}Do you want to cancel {itemCode} - {amount}? (Y/N){RESET}").strip().upper()
                if useLine in ['Y', 'N']:
                    break
                else:
                    print(f"{RED}Please enter 'Y' or 'N'{RESET}")

            if useLine == "Y":
                
                cursorItem.execute('SELECT "On Order" FROM Inventory WHERE "Item Code" = ?', (itemCode,))
                onOrder = cursorItem.fetchone()[0]

                newOnOrder = onOrder - amount

                cursorItem.execute('UPDATE Inventory SET "On Order" = ? WHERE "Item Code" = ?',
                                    (newOnOrder, itemCode))
                connectionItem.commit()

                cursorMovements.execute('INSERT INTO Movements ("Item", "Amount", "Type", "User", "Date") VALUES (?, ?, ?, ?, ?)', (itemCode, amount, "CANCELLED ORDER", fullName, get_current_time()))
                connectionMovements.commit()

                cursorPending.execute('DELETE FROM pendingOrders WHERE "Reference" = ? AND "Item Code" = ?',
                                    (referenceNumber, itemCode))
                connectionPending.commit()

                print(f"{GREEN}Order with reference {referenceNumber} has been cancelled.{RESET}")

        connectionItem.close()
        connectionMovements.close()
        
    else:
        print(f"{RED}No matching orders found for reference {referenceNumber}.{RESET}")

    connectionPending.close()






        

            
