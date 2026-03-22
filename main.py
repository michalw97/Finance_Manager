import json

transactions = []

def load_data():
    try:
        global transactions
        with open('transactions.json', 'r') as f:
            transactions = json.load(f)
    except FileNotFoundError:
        transactions = []

def save_data():
    with open('transactions.json', 'w') as f:
        json.dump(transactions, f)

def add_transaction():
    new_id = len(transactions) + 1
    while True:
        try:
            amount = float(input("Podaj kwotę: ").strip())
            category_type = input("Podaj kategorię: ").strip()
            transaction_type = input("Podaj typ transakcji('wpłata'/'wydatek'): ").lower().strip()
            transaction_date = input("Podaj datę: ").strip()
            print("Dodano transakcje.")
            print()

            transaction = {
                "id": new_id,
                "amount": amount,
                "category_type": category_type,
                "transaction_type": transaction_type,
                "transaction_date": transaction_date
            }

            transactions.append(transaction)
            break
        except ValueError:
            print("Kwota musi być liczbą!")

def show_all():
    print(f"Twoje wszystkie transakcje:\n")
    for transaction in transactions:
        print()
        print(f"ID transakcji: {transaction['id']}")
        print(f"Kwota: {transaction['amount']}")
        print(f"Kategoria: {transaction['category_type']}")
        print(f"Typ: {transaction['transaction_type']}")
        print(f"Data: {transaction['transaction_date']}")
        print("----------------------\n")

def delete_transaction():
    while True:
        try:
            delete = int(input("Którą transakcję chcesz usunąć?(ID)(ta zmiana jest nieodwracalna!): "))

            found = False

            for transaction in transactions:
                if transaction["id"] == delete:
                    transactions.remove(transaction)
                    found = True
                    print("Transakcja usunięta.")
                    print()
                    break
            if not found:
                print("Transakcja nie istnieje!")
                continue
            break
        except ValueError:
            print("ID musi być liczbą!")

#all edit_transaction for refactoring
def edit_transaction():
    while True:
        try:
            edit = int(input("Którą transakcję chcesz edytować?(ID): "))

            found = False

            for transaction in transactions:
                if transaction["id"] == edit:
                    while True:
                        edit_choice = input(
                            "Którą wartość chcesz zedytować? (Całość - wpisz całość!): ").strip().lower()
                        if edit_choice == "całość":
                            transaction["amount"] = float(input("Nowa kwota: ").strip())
                            transaction["category_type"] = input("Nowa kategoria: ").strip()
                            transaction["transaction_type"] = input("Nowy typ('wpłata'/'wydatek'): ").lower().strip()
                            transaction["transaction_date"] = input("Nowa data: ").strip()
                            found = True
                            print("Zmieniono całość.")
                            print()
                            break
                        elif edit_choice == "kwota":
                            transaction["amount"] = float(input("Nowa kwota: ").strip())
                            found = True
                            print("Zmieniono kwotę.")
                            print()
                            break
                        elif edit_choice == "kategoria":
                            transaction["category_type"] = input("Nowa kategoria: ").strip()
                            found = True
                            print("Zmieniono kategorię.")
                            print()
                            break
                        elif edit_choice == "typ":
                            transaction["transaction_type"] = input("Nowy typ('wpłata'/'wydatek'): ").lower().strip()
                            found = True
                            print("Zmieniono typ.")
                            print()
                            break
                        elif edit_choice == "data":
                            transaction["transaction_date"] = input("Nowa data: ").strip()
                            found = True
                            print("Zmieniono datę.")
                            print()
                            break
                        else:
                            print("Nie ma takiej wartośći!")
                            continue
                    break
            if not found:
                print("Nie ma takiej transakcji!")
                continue
            break
        except ValueError:
            print("ID/Kwota musi być liczbą!")

def show_incomes():
    print(f"Twoje wszystkie WPŁATY:\n")
    for transaction in transactions:
        if transaction["transaction_type"] == "wpłata":
            print(f"ID transakcji: {transaction['id']}")
            print(f"Kwota: {transaction['amount']}")
            print(f"Kategoria: {transaction['category_type']}")
            print(f"Typ: {transaction['transaction_type']}")
            print(f"Data: {transaction['transaction_date']}")
            print("----------------------")

def show_expenses():
    print("Twoje wszystkie WYDATKI:\n")
    for transaction in transactions:
        if transaction["transaction_type"] == "wydatek":
            print(f"ID transakcji: {transaction['id']}")
            print(f"Kwota: {transaction['amount']}")
            print(f"Kategoria: {transaction['category_type']}")
            print(f"Typ: {transaction['transaction_type']}")
            print(f"Data: {transaction['transaction_date']}")
            print("----------------------")

def show_balance():
    total_balance = 0

    for transaction in transactions:
        if transaction["transaction_type"] == "wpłata":
            total_balance += transaction["amount"]
        elif transaction["transaction_type"] == "wydatek":
            total_balance -= transaction["amount"]
    print(f"Suma Twoich wpłat i wydatków: {total_balance}")
    print()

load_data()

while True:
    print("1. Dodaj nową transakcję.")
    print("2. Pokaż wszystkie transakcje.")
    print("3. Usuń nową transakcję.")
    print("4. Edytuj transakcję.")
    print("5. Pokaż wszystkie wpłaty.")
    print("6. Pokaż wszystkie wydatki.")
    print("7. Pokaż stan konta.")
    print("0. Zakończ.")
    print()

    user_choice = int(input("Którą opcję wybierasz?: "))
    print()

    if user_choice == 1:
        add_transaction()
        save_data()
    elif user_choice == 2:
        show_all()
    elif user_choice == 3:
        delete_transaction()
        save_data()
    elif user_choice == 4:
        edit_transaction()
        save_data()
    elif user_choice == 5:
        show_incomes()
    elif user_choice == 6:
        show_expenses()
    elif user_choice == 7:
        show_balance()
    elif user_choice == 0:
        break
    else:
        print("Wybrana opcja nie istnieje!")
save_data()