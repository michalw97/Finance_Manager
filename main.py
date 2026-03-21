transactions = []

def add_transaction():
    amount = float(input("Podaj kwotę: "))
    category_type = input("Podaj kategorię: ")
    transaction_type = input("Podaj typ transakcji: ")
    transaction_date = input("Podaj datę: ")

    transaction = {
        "amount": amount,
        "category_type": category_type,
        "transaction_type": transaction_type,
        "transaction_date": transaction_date
    }

    transactions.append(transaction)

def show_all():
    for transaction in transactions:
        print(f"Twoje wszystkie transakcje:")
        print(f"Kwota: {transaction["amount"]}")
        print(f"Kategoria: {transaction["category_type"]}")
        print(f"Typ: {transaction["transaction_type"]}")
        print(f"Data: {transaction["transaction_date"]}")
        print("----------------------")