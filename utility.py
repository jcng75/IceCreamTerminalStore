# Check if input for money is valid
def isMoney(s):
    # Base case
    if s == '':
        return False
    # Keep 2 counters
    decimalCounter = 0
    afterDecimalCounter = 0
    # Logic: If there are more than 2 decimals, return false
    # If there are more than two values after the decimal, return false
    # Otherwise, return true
    for char in s:
        if char.isnumeric():
            if decimalCounter > 0 and afterDecimalCounter == 2:
                return False
            elif decimalCounter > 0:
                afterDecimalCounter += 1
        elif char == '.' and decimalCounter == 0:
            decimalCounter += 1
        else:
            return False
    return True