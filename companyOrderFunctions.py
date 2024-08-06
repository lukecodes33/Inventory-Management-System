import sqlite3
import random
import os
import csv

def createPendingOrders(fullName, time):

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
            existing_item = cursor.fetchone()
            
            if existing_item:
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
        current_on_order = cursor.fetchone()[0]
        new_on_order = current_on_order + amount
        cursor.execute('UPDATE Inventory SET "On Order" = ? WHERE "Item Code" = ?', (new_on_order, itemCode))
        connection.commit()
        connection.close()

        pendingOrderDatabasePath = "database/pendingOrdersDatabase.db"
        connection = sqlite3.connect(pendingOrderDatabasePath)
        cursor = connection.cursor()

        cursor.execute('''
                INSERT INTO pendingOrders ("Item Code", "Amount", "Reference", "User", "Date")
                VALUES (?, ?, ?, ?, ?)
                ''', (itemCode, amount, reference, fullName, time))
        connection.commit()
        connection.close() 

        movements = "database/movements.db"
        connection = sqlite3.connect(movements)
        cursor = connection.cursor()

        cursor.execute('''
                INSERT INTO movements ("Item", "Amount", "Type", "User", "Date")
                VALUES (?, ?, ?, ?, ?)
                ''', (itemCode, amount, "PENDING ORDER", fullName, time))
        connection.commit()
        connection.close() 

        print(f"{GREEN}\nPending order placed!{RESET}")

        anotherItem = input(f"\n{YELLOW}Are there any more items on this order? (Y/N): {RESET}").strip().upper()

        if confirmation != 'Y':
            break

        break

def showPendingOrders():

    """
    Displays all pending orders and offers an option to export the results to a CSV file.
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
            desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
            filename = os.path.join(desktop_path, "pending_orders.csv")
            with open(filename, 'w', newline='') as csvfile:
                csvwriter = csv.writer(csvfile)
                csvwriter.writerows(rows)
            print(f"{GREEN}Data has been exported to '{filename}'.{RESET}")

    else:
        print(f"{RED}No pending orders found in the database.{RESET}")

    connection.close()

def receiveOrder(fullName, time):
    
    YELLOW = '\033[93m'
    RED = '\033[91m'
    RESET = '\033[0m'
    GREEN = '\033[92m'

    referenceNumber = input(f"\n{YELLOW}Order reference number: {RESET}")

    pendingOrdersDatabasePath = "database/pendingOrdersDatabase.db"
    connection_pending = sqlite3.connect(pendingOrdersDatabasePath)
    cursor_pending = connection_pending.cursor()

    itemDatabasePath = "database/itemDatabase.db"
    connection_item = sqlite3.connect(itemDatabasePath)
    cursor_item = connection_item.cursor()

    movementsDatabasePath = "database/movements.db"
    connection_movements = sqlite3.connect(movementsDatabasePath)
    cursor_movements = connection_movements.cursor()

    cursor_pending.execute('''
    SELECT "Item Code", "Amount"
    FROM pendingOrders
    WHERE "Reference" = ?
    ''', (referenceNumber,))

    matches = cursor_pending.fetchall()

    if matches:

        for match in matches:
            itemCode, amount = match

            cursor_item.execute('SELECT "Stock", "On Order" FROM Inventory WHERE "Item Code" = ?', (itemCode,))
            stock, on_order = cursor_item.fetchone()

            new_stock = stock + amount
            new_on_order = on_order - amount

            cursor_item.execute('UPDATE Inventory SET "Stock" = ?, "On Order" = ? WHERE "Item Code" = ?',
                                (new_stock, new_on_order, itemCode))
            connection_item.commit()

            cursor_movements.execute('INSERT INTO Movements ("Item", "Amount", "Type", "User", "Date") VALUES (?, ?, ?, ?, ?)', (itemCode, amount, "RECIEVED ORDER", fullName, time))
            connection_movements.commit()

            cursor_pending.execute('DELETE FROM pendingOrders WHERE "Reference" = ? AND "Item Code" = ?',
                                   (referenceNumber, itemCode))
            connection_pending.commit()

        print(f"{GREEN}Order with reference {referenceNumber} has been processed and updated.{RESET}")

        connection_item.close()
        connection_movements.close()
        
    else:
        print(f"{RED}No matching orders found for reference {referenceNumber}.{RESET}")

    connection_pending.close()





        

            
