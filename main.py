from iceCreamShop import *

def main():
    # while True:
        # test = input("Enter money: ")
        # print(isMoney(test))
    print("Initializing sequence...")
    
    # TO BE MODIFY 
    # dbname to name of database created in pgadmin
    # user - by default, the user should be postgres.  Unless you changed it, do not modify this parameter
    # password - change to your own pgadmin password (EX: goodyear)
    
    dbname = 'icecreamshop'
    user = 'postgres'
    password = 'goodyear'
    connection = psycopg2.connect(f"dbname={dbname} user={user} password={password}")
    print("Connection established!")
    
    # Create cursors
    addCursor = connection.cursor()
    searchCursor = connection.cursor()
    
    # Ask to initialize database
    acceptedResponse = {"YES", "NO", "Y", "N"}
    gotInitiliazed = input("Have you initialized the database yet? (Yes/Y/No/N) ")        
    while gotInitiliazed.upper() not in acceptedResponse:
        gotInitiliazed = input("Please enter a valid response! (Yes/Y/No/N) ")
    if gotInitiliazed.upper() == "NO" or gotInitiliazed.upper() == "N":
        init(connection)
    
    while True:
        system("cls")
        print("Welcome to the Icecream Database!")
        print("1) Add Customer")
        print("2) Add Employee")
        print("3) Add a new flavor!")
        print("4) Simulate Work!")
        print("5) Simulate Restock!")
        print("6) See Sales")
        print("7) Order Lookup")
        print("8) View Ice Cream Flavors")
        print("X) Quit")
        choice = input("What would you like to do? ") 
        acceptedResponseMenu = {"1", "2", "3", "4", "5", "6", "7", "8", "X", "x"}
        while choice not in acceptedResponseMenu:
            choice = input("Please choose a valid choice! (1, 2, 3, 4, 5, 6, 7, 8, X) ")
            
        match choice:
            case "1":
                addCustomer(connection, addCursor)
            case "2":
                addEmployee(connection, addCursor)
            case "3":
                addFlavor(connection, addCursor)
            case "4":
                simulation(connection)
            case "5":
                restockSimulation(connection)
            case "6":
                viewSales(connection)
            case "7":
                orderLookup(connection)
            case "8":
                viewIceCreamStats(connection)
            case _:
                print("Exiting Database...")
                sleep(3)
                system('cls')
                connection.close()
                break
    
if __name__ == "__main__":
    main()