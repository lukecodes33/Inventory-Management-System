def numberSelection():
    RED = '\033[91m'
    RESET = '\033[0m'
    
    while True:
        try:
            selection = int(input("> "))
            return selection
        except ValueError:
            print(f"{RED}Invalid input.{RESET}")



def topMenu(fullname):
    YELLOW = '\033[93m'
    RESET = '\033[0m'

    print(f"""{YELLOW}
INVENTORY MANAGEMENT SYSTEM                           User: {fullname}

1. Item Management
          
{RESET}""")
    

def itemManagementMenu(fullname):
    YELLOW = '\033[93m'
    RESET = '\033[0m'

    print(f"""{YELLOW}
ITEM MANAGEMENT                                       User: {fullname}

1. Add Item
2. Remove Item
3. Search Item
4. Display All/Export
5. Clear Database (CANNOT BE UNDONE)

0. Back
          
{RESET}""")
    