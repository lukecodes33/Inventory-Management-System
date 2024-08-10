import shutil

def numberSelection():

    """
    - Prompts the user to enter a number. If the input is not a valid integer, displays an error message and prompts again.
    """

    RED = '\033[91m'
    RESET = '\033[0m'
    
    while True:
        try:
            selection = int(input("> "))
            return selection
        except ValueError:
            print(f"{RED}Invalid input.{RESET}")

def get_terminal_size():

    """
    - Retrieves the width of the terminal window in columns.
    - Uses a default size of 80 columns and 20 rows if the size cannot be determined.
    """

    size = shutil.get_terminal_size((80, 20))
    return size.columns

def center_text(text, width):

    """
    - Centers the given text within the specified width.
    
    Parameters:
    text (str): The text to be centered.
    width (int): The width within which to center the text.
    
    Returns:
    str: The centered text.
    """

    return text.center(width)

def topMenu(fullname):

    """
    - Displays the top menu of the inventory management system.
    
    Parameters:
    fullname (str): The full name of the user.
    """

    YELLOW = '\033[93m'
    RESET = '\033[0m'
    width = get_terminal_size()

    header = "INVENTORY MANAGEMENT SYSTEM"
    underline = "-" * len(header)
    
    print(f"{YELLOW}")
    print(center_text(header, width))
    print(center_text(underline, width))
    print("")
    print("1. Item Management".center(width))
    print("2. Stock Order Management".center(width))
    print("3. Inventory Management".center(width))
    print("")
    print(f"User: {fullname}".center(width))
    print(f"{RESET}")

def itemManagementMenu(fullname):

    """
    - Displays the item management menu of the inventory management system.
    
    Parameters:
    fullname (str): The full name of the user.
    """
    
    YELLOW = '\033[93m'
    RESET = '\033[0m'
    width = get_terminal_size()

    header = "ITEM MANAGEMENT"
    underline = "-" * len(header)
    
    print(f"{YELLOW}")
    print(center_text(header, width))
    print(center_text(underline, width))
    print("")
    print("1. Add Item".center(width))
    print("2. Remove Item".center(width))
    print("3. Search Item By Code".center(width))
    print("4. Search Item By Name".center(width))
    print("5. Search All Items".center(width))
    print("")
    print("0. Back".center(width))
    print("")
    print(f"User: {fullname}".center(width))
    print(f"{RESET}")

def stockOrderMenu(fullname):

    """
    - Displays the stock order menu of the inventory management system.
    
    Parameters:
    fullname (str): The full name of the user.
    """
    
    YELLOW = '\033[93m'
    RESET = '\033[0m'
    width = get_terminal_size()

    header = "STOCK ORDER MANAGEMENT"
    underline = "-" * len(header)
    
    print(f"{YELLOW}")
    print(center_text(header, width))
    print(center_text(underline, width))
    print("")
    print("1. Create Pending Order".center(width))
    print("2. View Pending Orders".center(width))
    print("3. Recieve Order".center(width))
    print("4. Cancel Order".center(width))
    print("")
    print("0. Back".center(width))
    print("")
    print(f"User: {fullname}".center(width))
    print(f"{RESET}")


def inventoryManagamentMenu(fullname):

    YELLOW = '\033[93m'
    RESET = '\033[0m'
    width = get_terminal_size()

    header = "INVENTORY MANAGEMENT"
    underline = "-" * len(header)
    
    print(f"{YELLOW}")
    print(center_text(header, width))
    print(center_text(underline, width))
    print("")
    print("1. Low Stock Check".center(width))
    print("2. Reset Re Order Amounts".center(width))
    print("3. Write Off Stock".center(width))
    print("")
    print("0. Back".center(width))
    print("")
    print(f"User: {fullname}".center(width))
    print(f"{RESET}")