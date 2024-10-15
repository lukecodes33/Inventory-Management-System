import sqlite3
import random
from loginFunctions import get_current_time

def processSales(fullName):
    YELLOW = '\033[93m'
    RED = '\033[91m'
    RESET = '\033[0m'
    GREEN = '\033[92m'

    itemDatabasePath = "database/itemDatabase.db"
    movementsDatabasePath = "database/movements.db"
    salesDatabasePath = "database/salesDatabase.db"
    
    # Connect to the inventory database
    connection = sqlite3.connect(itemDatabasePath)
    cursor = connection.cursor()
    
    # Connect to the movements database
    movements_connection = sqlite3.connect(movementsDatabasePath)
    movements_cursor = movements_connection.cursor()

    # Connect to the sales database
    sales_connection = sqlite3.connect(salesDatabasePath)
    sales_cursor = sales_connection.cursor()

    generatedReferenceNumber = ''.join([str(random.randint(0, 9)) for _ in range(10)])
    salesDictionary = {}
    total_price = 0

    while True:
        # Prompt user for the item code
        itemCode = input(f"{YELLOW}Enter the Item Code for the product you want to process a sale for: {RESET}")

        # Check if the item exists in the database
        cursor.execute('SELECT "Item Name", "Sale Price", "Stock", "Purchase Price", "Amount Sold", "Profit" FROM Inventory WHERE "Item Code" = ?', (itemCode,))
        result = cursor.fetchone()

        if result:
            itemName, salePrice, stock, purchasePrice, amountSold, profit = result
            print(f"{GREEN}Product Found: {itemName} - Sale Price: ${salePrice} - Stock: {stock}{RESET}")

            while True:
                try:
                    amount = int(input(f"{YELLOW}Enter the quantity you would like to order: {RESET}"))

                    if amount <= 0:
                        print(f"{RED}Invalid input. Please enter a positive integer.{RESET}")
                    elif amount > stock:
                        print(f"{RED}Insufficient stock. Only {stock} items are available. Please enter a smaller quantity.{RESET}")
                    else:
                        break
                except ValueError:
                    print(f"{RED}Invalid input. Please enter a valid integer.{RESET}")

            # Store the item code, amount, and sale price in the dictionary
            salesDictionary[itemCode] = (itemName, amount, salePrice)

            # Add to the total price
            total_price += amount * salePrice

            # Ask the user if they want to add another item
            add_another = input(f"{YELLOW}Would you like to add another item? (Y/N): {RESET}").strip().upper()

            if add_another != 'Y':
                break
        else:
            print(f"{RED}Item Code {itemCode} not found in the inventory.{RESET}")

    # Update the inventory, movements, and sales database for each item in the sales dictionary
    for itemCode, (itemName, amount, salePrice) in salesDictionary.items():
        # Calculate new stock, amount sold, and profit
        cursor.execute('SELECT "Stock", "Purchase Price", "Amount Sold", "Profit" FROM Inventory WHERE "Item Code" = ?', (itemCode,))
        stock, purchasePrice, amountSold, profit = cursor.fetchone()

        newStock = stock - amount
        newAmountSold = amountSold + amount
        profitPerItem = salePrice - purchasePrice
        newProfit = profit + (profitPerItem * amount)
        itemTotalPrice = amount * salePrice

        # Update the inventory database with the new values
        cursor.execute('''
            UPDATE Inventory 
            SET "Stock" = ?, "Amount Sold" = ?, "Profit" = ?
            WHERE "Item Code" = ?
        ''', (newStock, newAmountSold, newProfit, itemCode))

        # Log the movement in the movements database
        movements_cursor.execute('''
            INSERT INTO movements ("Item", "Amount", "Type", "User", "Date")
            VALUES (?, ?, ?, ?, ?)
        ''', (itemCode, amount, "SOLD", fullName, get_current_time()))

        # Insert a new sale record into the sales database
        sales_cursor.execute('''
            INSERT INTO sales ("Item Code", "Amount", "Reference", "Total Price", "User", "Date")
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (itemCode, amount, generatedReferenceNumber, itemTotalPrice, fullName, get_current_time()))

    # Commit the changes to all databases
    connection.commit()
    movements_connection.commit()
    sales_connection.commit()

    # Close the database connections
    connection.close()
    movements_connection.close()
    sales_connection.close()

    # Print the receipt
    print(f"\n{GREEN}Receipt{RESET}")
    print(f"{'-'*40}")
    for itemCode, (itemName, amount, salePrice) in salesDictionary.items():
        line_total = amount * salePrice
        print(f"{itemName:<20} x {amount:<3} @ ${salePrice:<8} = ${line_total:<8}")
    print(f"{'-'*40}")
    print(f"{GREEN}Total Price: ${total_price}{RESET}\n")
    print(f"\n{GREEN}Order Number: {generatedReferenceNumber}{RESET}")

def viewTransaction():
    YELLOW = '\033[93m'
    RED = '\033[91m'
    RESET = '\033[0m'
    GREEN = '\033[92m'

    salesDatabasePath = "database/salesDatabase.db"
    
    # Connect to the sales database
    connection = sqlite3.connect(salesDatabasePath)
    cursor = connection.cursor()

    # Prompt the user for a reference number
    referenceNumber = input(f"{YELLOW}Enter the reference number to view the transaction: {RESET}")

    # Search for all items with the given reference number
    cursor.execute('''
        SELECT "Item Code", "Amount", "Total Price"
        FROM sales
        WHERE "Reference" = ?
    ''', (referenceNumber,))
    
    rows = cursor.fetchall()

    if rows:
        # Print the transaction details in a receipt format
        print(f"\n{GREEN}Transaction Details for Reference: {referenceNumber}{RESET}")
        print(f"{'-'*40}")
        total_price = 0
        for row in rows:
            itemCode, amount, totalPrice = row
            total_price += totalPrice
            print(f"{itemCode:<15} x {amount:<3} = ${totalPrice:<8}")
        print(f"{'-'*40}")
        print(f"{GREEN}Total Price: ${total_price}{RESET}\n")
    else:
        print(f"{RED}No transactions found for reference number: {referenceNumber}{RESET}")

    # Close the database connection
    connection.close()