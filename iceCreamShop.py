import psycopg2
from time import sleep
from os import system
from random import choices, choice, randint
from ccard import mastercard
from utility import isMoney

def init(connection):
    # Goal: Create the tables
    createTableCursor = connection.cursor()
    insertValuesCursor = connection.cursor()
    createTableCursor.execute("CREATE TABLE IF NOT EXISTS Customers(Customer_ID SERIAL NOT NULL PRIMARY KEY, Customer_Name VARCHAR(200) NOT NULL, Date_Created timestamp NOT NULL)")
    createTableCursor.execute("CREATE TABLE IF NOT EXISTS Employees(Employee_ID SERIAL NOT NULL PRIMARY KEY, Employee_Name VARCHAR(200) NOT NULL, Date_Created timestamp NOT NULL)")
    createTableCursor.execute("CREATE TABLE IF NOT EXISTS Flavors(Icecream_ID SERIAL NOT NULL PRIMARY KEY, Flavor_Name VARCHAR(200) NOT NULL, Organic Boolean NOT NULL, Contains_Peanuts Boolean NOT NULL, Soft_Serve Boolean NOT NULL, Cost_Per_Serving money NOT NULL, inventory integer NOT NULL, Date_Created timestamp NOT NULL)")
    createTableCursor.execute("CREATE TABLE IF NOT EXISTS Orders(id SERIAL NOT NULL PRIMARY KEY, Order_ID Integer NOT NULL, Customer_ID Integer NOT NULL, Icecream_ID Integer NOT NULL, Employee_ID Integer NOT NULL, Size_ID Integer NOT NULL, Quantity Integer NOT NULL, Total money NOT NULL, Time_Ordered timestamp NOT NULL)")
    createTableCursor.execute("CREATE TABLE IF NOT EXISTS Payment(Payment_ID SERIAL NOT NULL PRIMARY KEY, Customer_ID Integer NOT NULL, Credit_Card_Number bigserial NOT NULL, Card_Holder VARCHAR(200) NOT NULL)")
    createTableCursor.execute("CREATE TABLE IF NOT EXISTS Sizes(Size_ID SERIAL NOT NULL PRIMARY KEY, Size_Name VARCHAR(200) NOT NULL, Price_In_USD money NOT NULL)")
    
    # Insert various sizes and prices
    insertValuesCursor.execute("INSERT INTO Sizes(Size_Name, Price_In_USD) VALUES ('Small', 5.50), ('Medium', 6.50), ('Large', 7.50), ('Giga', 10.00)")
    connection.commit()
    print("Database Initialized!")
    sleep(2)
    return

def addCustomer(connection, cursor):
    # Add the customer to the customer database
    selectCursor = connection.cursor()
    customerName = input("Please enter your name: ")
    cursor.execute("INSERT INTO Customers (Customer_Name, Date_Created) VALUES (%s, clock_timestamp())", [customerName])
    
    # Get the customer id from the table we've just inserted into
    selectCursor.execute("SELECT MAX(Customer_ID) FROM Customers")
    customerID = selectCursor.fetchone()[0]
    # Get the user's credit card info
    print("============= PAYMENT INFO =============")
    creditCardNumber = input("Please enter your credit card number: ")
    
    if creditCardNumber.lower() == 'lazy':
        creditCardNumber = str(mastercard())
        print(f"You're too lazy to generate a credit card number? Fine heres one: {creditCardNumber}")
    else:
        while creditCardNumber.isnumeric() == False or len(creditCardNumber) != 16:
            creditCardNumber = input("Please enter a valid credit card number! (Each CC # Has 16 Digits!) ")
    cardHolder = input("Please enter the name of the card holder: ")
    # Insert the payment information (along with the customer id) into the payment table
    cursor.execute("INSERT INTO Payment (Customer_ID, Credit_Card_Number, Card_Holder) VALUES (%s, %s, %s)", [str(customerID), creditCardNumber, cardHolder])
    selectCursor.execute("SELECT * FROM Payment")
    connection.commit()
    print("Customer Added!")
    return

def addEmployee(connection, cursor):
    # Not too much to add, simply get their name and they work their apparently
    employeeName = input("Please enter your name: ")
    cursor.execute("INSERT INTO Employees (Employee_Name, Date_Created) VALUES (%s, clock_timestamp())", [employeeName])
    connection.commit()
    print("Customer Added!")
    return

def addFlavor(connection, cursor):
    # We want to add a new icecream flavor.
    # Our flavor should have the name, price to produce, and if the flavor is organic/soft serve/ contains peanuts
    acceptedBoolean = {"TRUE", "FALSE"}
    flavorName = input("What is the name of the new flavor? ")
    isOrganic = input("Is this flavor organic? (True/False) ")
    while isOrganic.upper() not in acceptedBoolean:
        isOrganic = input("Please enter a valid input (True/False) ")
    containsPeanuts = input("Does this flavor contain peanuts? (True/False) ")
    while containsPeanuts.upper() not in acceptedBoolean:
        containsPeanuts = input("Please enter a valid input (True/False) ")
    isSoftServe = input("Is this ice cream soft serve? (True/False) ")
    while isSoftServe.upper() not in acceptedBoolean:
        isSoftServe = input("Please enter a valid input (True/False) ")
    money = input("How much does it cost to make each serving? (Format: [Any Number Integer].[Two decimal place integer] ")
    while isMoney(money) != True:
        money = input("Please follow the proper money input format: ([Any Number Integer].[Two decimal place integer]) ")
    cursor.execute("INSERT INTO Flavors(Flavor_Name, Organic, Contains_Peanuts, Soft_Serve, Cost_Per_Serving, inventory, Date_Created) VALUES (%s, %s, %s, %s, %s, 0, clock_timestamp())", [flavorName, isOrganic.upper(), containsPeanuts.upper(), isSoftServe.upper(), money])
    print("Flavor Added!")
    sleep(1)
    connection.commit()
    return
    
def simulation(connection):
    
    # IDEA: Get the employees, ice cream flavors, and customers
    # Using random.choice, the flavors chosen would be picked
    
    # Get ice cream flavors, sizes, customers, and employees and store them each into a list
    selectCursor = connection.cursor()
    addCursor = connection.cursor()
    updateCursor = connection.cursor()
    
    selectCursor.execute("SELECT Size_ID FROM Sizes")
    sizesIDs = []
    for row in selectCursor:
        sizesIDs.append(row[0])
    
    # Get customers ids
    selectCursor.execute("SELECT Customer_ID FROM Customers")
    customerIDs = []
    for row in selectCursor:
        customerIDs.append(row[0])
        
    # Get employees
    selectCursor.execute("SELECT Employee_ID FROM Employees")
    employeeIDs = []
    for row in selectCursor:
        employeeIDs.append(row[0])
    
    # Get last order ID number
    selectCursor.execute("SELECT MAX(Order_ID) FROM Orders")
    nextOrderID = selectCursor.fetchone()[0]
    if nextOrderID == None:
        nextOrderID = 1
    else:
        nextOrderID = nextOrderID + 1
    
    system("cls")
    
    print("Press 'CTRL + C' to stop the simulation!")
    while True:
        
        try:

            # Get number of products
            numProducts = randint(1, 3)
            # Get poor employee that has to make all this
            employeeToSuffer = str(choice(employeeIDs))
            # Get random customer from database
            happyCustomer = str(choice(customerIDs))

            # Create a new order based on the random number generated from 1-3
            for i in range(numProducts):
                quantity = randint(1,1000)
                # Get all flavors that can satisfy this random quantity
                selectCursor.execute("SELECT Icecream_ID FROM Flavors WHERE inventory <> 0 AND inventory >= %s", [quantity])
                flavorIDs = []
                flavors = selectCursor.fetchall()
                # If the request can be met, stop the simulation
                if len(flavors) == 0:
                    print(f"Flavors are out of stock!  Cannot satisfy quantity of {quantity}")
                    return
                # Add the flavors to the list that can make the quantity
                for flavor in flavors:
                    flavorIDs.append(flavor[0])
                # Get the flavors
                flavorChoices = choices(flavorIDs, k=numProducts)
                # Get the random size
                sizeChoice = str(choice(sizesIDs))
                selectCursor.execute("SELECT Price_In_USD FROM Sizes WHERE Sizes.Size_ID = %s", [sizeChoice])
                priceOfSize = float(selectCursor.fetchone()[0][1::])
                # print(priceOfSize)
                addCursor.execute("INSERT INTO orders(Order_ID, Customer_ID, Icecream_ID, Employee_ID, Size_ID, Quantity, Total, Time_Ordered) VALUES(%s, %s, %s, %s, %s, %s, %s, clock_timestamp())", [str(nextOrderID), happyCustomer, str(flavorChoices[i]), employeeToSuffer, sizeChoice, quantity, str(quantity * priceOfSize)])
                updateCursor.execute("UPDATE Flavors SET inventory = inventory - %s WHERE Icecream_ID = %s", [quantity, flavorChoices[i]])
                
            print(f"New order placed! #{nextOrderID}")
            connection.commit()

            ##### INTERVAL TO CHANGE THE FREQUENCY OF ORDERS
            sleep(10)
            nextOrderID += 1
            # selectCursor.execute("SELECT * FROM Orders")
            # print("Current Orders List:")
            # for row in selectCursor:
                # print(f'Order_ID: {row[1]}, Customer_ID: {row[2]}, Icecream_ID: {row[3]}, Employee_ID: {row[4]}, Size_ID: {row[5]}, Quantity: {row[6]}, Total: {row[7]}')
        except KeyboardInterrupt:
            # Once the user presses CTRL + C, end the simulation
            print("Ending simulation...")
            break
    
    return

def restockSimulation(connection):
   
    # Create two cursors
    selectCursor = connection.cursor()
    addCursor = connection.cursor()
    
    # Get all the ice cream flavors
    selectCursor.execute("SELECT Icecream_ID FROM Flavors")
    flavorIDs = []
    flavors = selectCursor.fetchall()
    
    # If there are none, throw an error and return back to main
    if len(flavors) == 0:
        print("Cannot find any flavors to restock!")
        return
    
    for flavor in flavors:
        flavorIDs.append(flavor[0])
    
    try:
        system('cls')
        print("Press Ctrl + C to Terminate Simulation")
        while True:
            # Get a random amount to restock by
            restockRandom = str(randint(1, 1000))
            # Get the flavor to restock
            flavorChoice = choice(flavorIDs)
            # Restock the flavor
            addCursor.execute("UPDATE Flavors SET inventory = inventory + %s WHERE Icecream_ID = %s", [restockRandom, flavorChoice])
            print(f'Flavor ID {flavorChoice} has been restocked {restockRandom} units!')
            #### X VALUE CAN BE CHANGED
            sleep(1)
            connection.commit()
    except:
        # Exit simulation once CTRL + C pressed
        print("Ending simulation...")
        
    return

def viewSales(connection):
    system("cls")
    selectCursor = connection.cursor()
    # Display menu options
    print("What would you like to monitor?")
    print("1) View Total Revenue")
    print("2) View Top Selling Products")
    print("3) View Top Customers")
    menuChoice = input("Please select an input (1/2/3): ")
    acceptedAnswers = {"1", "2", "3"}
    while menuChoice not in acceptedAnswers:
        menuChoice = input("Please select a valid input! (1/2/3)")
    
    match menuChoice:
        # View Total Revenue Only
        case "1":
            try:
                print("Press Ctrl + C To Stop Viewing")
                while True:
                    system('cls')
                    selectCursor.execute("SELECT SUM((Orders.Total) - (Flavors.Cost_Per_Serving * Orders.Quantity)) as Total_Rev FROM Orders JOIN Sizes ON Orders.Size_ID = Sizes.Size_ID JOIN Flavors ON Orders.Icecream_ID = Flavors.Icecream_ID")
                    print(f'You have made {selectCursor.fetchone()[0]} in revenue so far!')
                    sleep(1)
            except:
                print("Stopping Display..")
        # View Top Selling Products Separately
        case "2":
            try:
                while True:
                    system('cls')
                    print("Press Ctrl + C To Stop Viewing")
                    selectCursor.execute("SELECT SUM(Orders.Total - (Flavors.Cost_Per_Serving * Orders.Quantity)) as Total_Rev, Flavors.Icecream_ID, Flavors.Flavor_Name, SUM(Orders.Quantity) FROM Orders JOIN Sizes ON Orders.Size_ID = Sizes.Size_ID JOIN Flavors ON Orders.Icecream_ID = Flavors.Icecream_ID GROUP BY 2 ORDER BY 1 DESC")
                    print("Top Selling Ice Cream Flavors")
                    for row in selectCursor:
                        print(f"Flavor: {row[2]}; Revenue Made: {row[0]}; Amount of Ice Cream Sold: {row[3]}")
                    sleep(1)
            except:
                print("Stopping Display..")
        # View Most Loyal Customers
        case "3":
            try:
                while True:
                    system('cls') 
                    print("Press Ctrl + C To Stop Viewing")
                    print("Top Customers")
                    selectCursor.execute("SELECT SUM(Orders.Total) as Total, Customers.Customer_ID, Customers.Customer_Name FROM Orders JOIN Sizes ON Orders.Size_ID = Sizes.Size_ID JOIN Flavors ON Orders.Icecream_ID = Flavors.Icecream_ID JOIN Customers ON Orders.Customer_ID = Customers.Customer_ID GROUP BY 2 ORDER BY 1 DESC")
                    for row in selectCursor:
                        print(f"Customer Name: {row[2]}; Amount of Ice Cream Purchased {row[0]}")
                    sleep(1)
            except:
                print("Stopping Display..")
    return

def orderLookup(connection):
    
    selectCursor = connection.cursor()
    system("cls")
    # Display menu
    print("1) View All Orders")
    print("2) View Specific Order")
    acceptedChoices = {"1", "2"}
    optionChoice = input("Please select an option: (1/2) ")
    while optionChoice not in acceptedChoices:
        optionChoice = input("Please enter a valid input! (1/2) ")
    
    # View All Orders Made Onto System
    if optionChoice == "1":
        selectCursor.execute('''SELECT Orders.Order_ID, 
                                Customers.Customer_Name, 
                                Flavors.Flavor_Name, 
                                Employees.Employee_Name, 
                                Sizes.Size_Name, 
                                Orders.Total, 
                                Orders.Quantity,
                                Orders.Time_Ordered 
                                FROM
                                Orders JOIN Customers ON Orders.Customer_ID = Customers.Customer_ID
                                        JOIN Flavors ON Orders.Icecream_ID = Flavors.Icecream_ID
                                        JOIN Employees ON Orders.Employee_ID = Employees.Employee_ID
                                        JOIN Sizes ON Orders.Size_ID = Sizes.Size_ID
                            ''')
        rows = selectCursor.fetchall()
        if len(rows) == 0:
            print("You have no orders in your database!")
            return
        for row in rows:
            print(f'Order ID: {row[0]}; Customer Name: {row[1]}; Flavor Name: {row[2]}; Made by: {row[3]}; Size: {row[4]}; Quantity: {row[6]}; Total Cost: {row[5]}; Date Ordered: {row[7]}  ')    
        quitso = input("Enter anything to continue: ")
    # View a Specific Order
    else:    
        orderNumber = input("Please enter your order number: ")
        try:
            selectCursor.execute("SELECT Orders.Order_ID, Customers.Customer_Name, Flavors.Flavor_Name, Employees.Employee_Name, Sizes.Size_Name, Orders.Total, Orders.Quantity, Orders.Time_Ordered FROM Orders JOIN Customers ON Orders.Customer_ID = Customers.Customer_ID JOIN Flavors ON Orders.Icecream_ID = Flavors.Icecream_ID JOIN Employees ON Orders.Employee_ID = Employees.Employee_ID JOIN Sizes ON Orders.Size_ID = Sizes.Size_ID WHERE Orders.Order_ID = %s ", [orderNumber])
            rows = selectCursor.fetchall()
            if len(rows) == 0:
                print("You have no orders from this order ID!")
                return
            for row in rows:
                print(f'Order ID: {row[0]}; Customer Name: {row[1]}; Flavor Name: {row[2]}; Made by: {row[3]}; Size: {row[4]}; Quantity: {row[6]}; Total Cost: {row[5]}; Date Ordered: {row[7]}  ') 
            quitso = input("Enter anything to continue: ")
        except:
            # If we get an error for being unable to find the order number, we then print that order number invalid
            print("Invalid order number!")
            connection.rollback()
             
    return

def viewIceCreamStats(connection):
    
    selectCursor = connection.cursor()
    try:
        while True:
            system("cls")
            selectCursor.execute("SELECT Flavor_Name, Organic, Contains_Peanuts, Soft_Serve, Cost_Per_Serving, inventory, Date_Created FROM Flavors")
            for row in selectCursor:
                print(f'Flavor: {row[0]}, Organic: {row[1]}, Contains Peanuts: {row[2]}, Soft Serve: {row[3]}, Cost Per Serving: {row[4]}, Current Inventory: {row[5]}, Date Created: {row[6]}')
            sleep(5)
    except:
        return