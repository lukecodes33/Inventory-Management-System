import sqlite3
import csv
import getpass
import os

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

def addItem(username, time):

    YELLOW = '\033[93m'
    RED = '\033[91m'
    RESET = '\033[0m'
    GREEN = '\033[92m'

    itemDatabasePath = "database/itemDatabase.db"
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

            movements = "database/movements.db"
            connection = sqlite3.connect(movements)
            cursor = connection.cursor()

            cursor.execute('''
            INSERT INTO movements ("Item", "Amount", "Type", "User", "Date")
            VALUES (?, ?, ?, ?, ?)
            ''', (itemCode, stockCount, "ADD", username, time))
            connection.commit()
            connection.close() 
            break

        elif answer == "N":
            break

        else: 
            print(f"{RED} Invalid input. Please enter 'Y' to proceed or 'N' to cancel.{RESET}")

def removeItem(adminRights, storedPassword, username, time):

    YELLOW = '\033[93m'
    RED = '\033[91m'
    RESET = '\033[0m'
    GREEN = '\033[92m'

    if adminRights:
        enteredPassword = getpass.getpass(f"{YELLOW}Enter admin password: {RESET}")
        if enteredPassword != storedPassword:
            print(f"{RED}Incorrect password. Access denied.{RESET}")
            return

        itemDatabasePath = "database/itemDatabase.db"
        connection = sqlite3.connect(itemDatabasePath)
        cursor = connection.cursor()

        while True:
            code = input(f"{YELLOW}Enter product code to delete: {RESET}")

            cursor.execute('''SELECT "Item Code", "Item Name" FROM Inventory WHERE "Item Code" = ?''', (code,))
            match = cursor.fetchone()

            cursor.execute('''SELECT "Stock" FROM Inventory WHERE "Item Code" = ?''', (code,))
            count = cursor.fetchone()
            stockCount = count[0]

            if match:
                itemCode, itemName = match
                print(f"{GREEN}Item found: {itemCode} - {itemName}{RESET}")

                while True:
                        confirm = input(f"\n{YELLOW}Are you sure you want to delete this item? (Y/N): {RESET}").strip().upper()
                        if confirm == 'Y' and (stockCount <= 0):
                            cursor.execute('''DELETE FROM Inventory WHERE "Item Code" = ?''', (code,))
                            connection.commit()
                            print(f"\n{GREEN}Item {itemCode} - {itemName} has been deleted.{RESET}")
                            connection.close()

                            movements = "database/movements.db"
                            connection = sqlite3.connect(movements)
                            cursor = connection.cursor()

                            cursor.execute('''
                            INSERT INTO movements ("Item", "Amount", "Type", "User", "Date")
                            VALUES (?, ?, ?, ?, ?)
                            ''', (itemCode, stockCount, "REMOVE", username, time))
                            connection.commit()
                            connection.close() 
                            break
                            return

                        elif confirm == "Y" and (stockCount > 0):
                            print(f"\n{RED}Stock count is greater than 0, cannot delete item.{RESET}")
                            return
                        elif confirm == 'N':
                            print(f"{YELLOW}Item deletion cancelled.{RESET}")
                            connection.close()
                            return
                        else:
                            print(f"\n{RED}Invalid input. Please enter 'Y' to confirm or 'N' to cancel.{RESET}")
            else:
                print(f"\n{RED}No item found{RESET}")
                return
            
    else:
        print(f"{RED}You do not have permission to access this{RESET}")

def searchByProductCode():
    YELLOW = '\033[93m'
    RED = '\033[91m'
    RESET = '\033[0m'
    GREEN = '\033[92m'

    itemDatabasePath = "database/itemDatabase.db"
    connection = sqlite3.connect(itemDatabasePath)
    cursor = connection.cursor()

    productCode = input(f"\n{YELLOW}Product code: {RESET}")

    cursor.execute('''
    SELECT "Item Code", "Item Name", Stock, "On Order", "Purchase Price", "Sale Price"
    FROM Inventory
    WHERE "Item Code" LIKE ?
    ''', ('%' + productCode + '%',))

    matches = cursor.fetchall()

    if matches:
        rows = [("Item Code", "Item Name", "Stock", "On Order", "Purchase Price", "Sale Price")]
        rows.extend(matches)

        print(f"\n{GREEN}{'Item Code':<15}{'Item Name':<20}{'Stock':<10}{'On Order':<10}{'Purchase Price':<15}{'Sale Price':<10}{RESET}")
        print(f"{GREEN}{'-'*15:<15}{'-'*20:<20}{'-'*10:<10}{'-'*10:<10}{'-'*15:<15}{'-'*10:<10}{RESET}")

        for match in matches:
            itemCode, itemName, stock, onOrder, purchasePrice, salePrice = match
            print(f"{GREEN}{itemCode:<15}{itemName:<20}{stock:<10}{onOrder:<10}{purchasePrice:<15}{salePrice:<10}{RESET}")

        export = input(f"\n{YELLOW}Do you want to export the results to a CSV file? (Y/N): {RESET}").strip().upper()
        
        if export == 'Y':
            desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
            filename = os.path.join(desktop_path, f"{productCode}_searchResults.csv")
            with open(filename, 'w', newline='') as csvfile:
                csvwriter = csv.writer(csvfile)
                csvwriter.writerows(rows)
            print(f"{GREEN}Data has been exported to '{filename}'.{RESET}")
        else:
            print(f"{YELLOW}Data was not exported.{RESET}")

    else:
        print(f"{RED}No items found matching the product code: {productCode}{RESET}")

    connection.close()

def searchByProductName():
    YELLOW = '\033[93m'
    RED = '\033[91m'
    RESET = '\033[0m'
    GREEN = '\033[92m'

    itemDatabasePath = "database/itemDatabase.db"
    connection = sqlite3.connect(itemDatabasePath)
    cursor = connection.cursor()

    productName = input(f"\n{YELLOW}Product name: {RESET}")

    cursor.execute('''
    SELECT "Item Code", "Item Name", Stock, "On Order", "Purchase Price", "Sale Price"
    FROM Inventory
    WHERE "Item Name" LIKE ?
    ''', ('%' + productName + '%',))

    matches = cursor.fetchall()

    if matches:
        rows = [("Item Code", "Item Name", "Stock", "On Order", "Purchase Price", "Sale Price")]
        rows.extend(matches)

        print(f"\n{GREEN}{'Item Code':<15}{'Item Name':<20}{'Stock':<10}{'On Order':<10}{'Purchase Price':<15}{'Sale Price':<10}{RESET}")
        print(f"{GREEN}{'-'*15:<15}{'-'*20:<20}{'-'*10:<10}{'-'*10:<10}{'-'*15:<15}{'-'*10:<10}{RESET}")

        for match in matches:
            itemCode, itemName, stock, onOrder, purchasePrice, salePrice = match
            print(f"{GREEN}{itemCode:<15}{itemName:<20}{stock:<10}{onOrder:<10}{purchasePrice:<15}{salePrice:<10}{RESET}")

        export = input(f"\n{YELLOW}Do you want to export the results to a CSV file? (Y/N): {RESET}").strip().upper()
        
        if export == 'Y':
            desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
            filename = os.path.join(desktop_path, f"{productName}_searchResults.csv")
            with open(filename, 'w', newline='') as csvfile:
                csvwriter = csv.writer(csvfile)
                csvwriter.writerows(rows)
            print(f"{GREEN}Data has been exported to '{filename}'.{RESET}")
        else:
            print(f"{YELLOW}Data was not exported.{RESET}")

    else:
        print(f"{RED}No items found matching the product name: {productName}{RESET}")

    connection.close()

def showAllProducts():
    YELLOW = '\033[93m'
    RED = '\033[91m'
    RESET = '\033[0m'
    GREEN = '\033[92m'

    itemDatabasePath = "database/itemDatabase.db"
    connection = sqlite3.connect(itemDatabasePath)
    cursor = connection.cursor()

    cursor.execute('''
    SELECT "Item Code", "Item Name", Stock, "On Order", "Purchase Price", "Sale Price"
    FROM Inventory
    ''')

    matches = cursor.fetchall()

    if matches:
        rows = [("Item Code", "Item Name", "Stock", "On Order", "Purchase Price", "Sale Price")]
        rows.extend(matches)

        print(f"\n{GREEN}{'Item Code':<15}{'Item Name':<20}{'Stock':<10}{'On Order':<10}{'Purchase Price':<15}{'Sale Price':<10}{RESET}")
        print(f"{GREEN}{'-'*15:<15}{'-'*20:<20}{'-'*10:<10}{'-'*10:<10}{'-'*15:<15}{'-'*10:<10}{RESET}")

        for match in matches:
            itemCode, itemName, stock, onOrder, purchasePrice, salePrice = match
            print(f"{GREEN}{itemCode:<15}{itemName:<20}{stock:<10}{onOrder:<10}{purchasePrice:<15}{salePrice:<10}{RESET}")

        export = input(f"\n{YELLOW}Do you want to export the results to a CSV file? (Y/N): {RESET}").strip().upper()
        
        if export == 'Y':
            desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
            filename = os.path.join(desktop_path, "all_products.csv")
            with open(filename, 'w', newline='') as csvfile:
                csvwriter = csv.writer(csvfile)
                csvwriter.writerows(rows)
            print(f"{GREEN}Data has been exported to '{filename}'.{RESET}")
        else:
            print(f"{YELLOW}Data was not exported.{RESET}")

    else:
        print(f"{RED}No products found in the inventory.{RESET}")

    connection.close()