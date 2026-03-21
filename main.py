transactions = []

def add_transaction():
    new_id = len(transactions) + 1
    amount = float(input("Podaj kwotę: "))
    category_type = input("Podaj kategorię: ")
    transaction_type = input("Podaj typ transakcji: ")
    transaction_date = input("Podaj datę: ")

    transaction = {
        "id": new_id,
        "amount": amount,
        "category_type": category_type,
        "transaction_type": transaction_type,
        "transaction_date": transaction_date
    }

    transactions.append(transaction)

def show_all():
    for transaction in transactions:
        print(f"Twoje wszystkie transakcje:")
        print(f"ID transakcji: {transaction["id"]}")
        print(f"Kwota: {transaction["amount"]}")
        print(f"Kategoria: {transaction["category_type"]}")
        print(f"Typ: {transaction["transaction_type"]}")
        print(f"Data: {transaction["transaction_date"]}")
        print("----------------------")

def delete_transaction():
    delete = int(input("Którą transakcję chcesz usunąć?(ID)(ta zmiana jest nieodwracalna!): "))

    found = False

    for transaction in transactions:
        if transaction["id"] == delete:
            transactions.remove(transaction)
            found = True
    if not found:
        print("Transakcja nie istnieje!")

def edit_transaction():
    edit = int(input("Którą transakcję chcesz edytować?(ID): "))

    for transaction in transactions:
        if transaction["id"] == edit:
            edit_choice = input("Którą wartość chcesz zedytować? (Całość - wpisz całość!)").strip().lower()
            if edit_choice == "całość":
                transaction["amount"] = float(input("Nowa kwota: "))
                transaction["category_type"] = input("Nowa kategoria: ")
                transaction["transaction_type"] = input("Nowy typ: ")
                transaction["transaction_date"] = input("Nowa data: ")
            elif edit_choice == "kwota":
                transaction["amount"] = float(input("Nowa kwota: "))
            elif edit_choice == "kategoria":
                transaction["category_type"] = input("Nowa kategoria: ")
            elif edit_choice == "typ":
                transaction["transaction_type"] = input("Nowy typ: ")
            elif edit_choice == "data":
                transaction["transaction_date"] = input("Nowa data: ")
            else:
                print("Nie ma takiej wartości!")
