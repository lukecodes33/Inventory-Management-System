import shutil

def numberSelection():
    RED = '\033[91m'
    RESET = '\033[0m'
    
    while True:
        try:
            selection = int(input("> "))
            return selection
        except ValueError:
            print(f"{RED}Invalid input.{RESET}")

def get_terminal_size():
    size = shutil.get_terminal_size((80, 20))
    return size.columns

def center_text(text, width):
    return text.center(width)

def topMenu(fullname):
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
    print("")
    print(f"User: {fullname}".center(width))
    print(f"{RESET}")

def itemManagementMenu(fullname):
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
    print("3. Search Item".center(width))
    print("")
    print("0. Back".center(width))
    print("")
    print(f"User: {fullname}".center(width))
    print(f"{RESET}")

def searchItemMenu(fullname):
    YELLOW = '\033[93m'
    RESET = '\033[0m'
    width = get_terminal_size()

    header = "SEARCH BY"
    underline = "-" * len(header)
    
    print(f"{YELLOW}")
    print(center_text(header, width))
    print(center_text(underline, width))
    print("")
    print("1. Item Code".center(width))
    print("2. Item Name".center(width))
    print("3. Show All".center(width))
    print("")
    print("0. Back".center(width))
    print("")
    print(f"User: {fullname}".center(width))
    print(f"{RESET}")
