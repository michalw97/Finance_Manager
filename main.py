import json


# QUESTION: What attributes should a single transaction have?
# Think about the dictionary you used before: id, amount, category_type, transaction_type, transaction_date
# How would you represent each of those as an attribute in __init__?
class Transaction:
    def __init__(self, transaction_id, amount, category_type, transaction_type, transaction_date):
        # TODO: assign each parameter to self.<attribute>
        pass

    def to_dict(self):
        # QUESTION: What should this method return so we can save it to JSON?
        # Hint: look at the dictionary structure you used before.
        pass

    @staticmethod
    def from_dict(data):
        # QUESTION: This is a factory method — it builds a Transaction from a dict.
        # What arguments does Transaction() need, and where do you get them from `data`?
        pass

    def __str__(self):
        # QUESTION: What should printing a single transaction look like?
        # Hint: look at how show_all() printed each transaction before.
        pass


# QUESTION: What is the responsibility of this class?
# It should manage the *collection* of transactions — not a single one.
# Which of your old functions belong here?
class TransactionManager:
    def __init__(self, filepath="transactions.json"):
        # QUESTION: What data does this class need to remember between method calls?
        # Hint: you need the list of transactions AND the file path.
        pass

    def load(self):
        # QUESTION: How did load_data() work before?
        # Now instead of using a global variable, where do you store the loaded list?
        pass

    def save(self):
        # QUESTION: How did save_data() work before?
        # Now the data is stored in self — how do you access it?
        # Hint: you'll need to convert each Transaction object to a dict first.
        pass

    def add(self, transaction):
        # QUESTION: What should happen to self._transactions when you add?
        # Also — should this method ask for input, or just receive a Transaction object?
        pass

    def delete(self, transaction_id):
        # QUESTION: How do you find the right transaction by ID?
        # What data structure would make this lookup efficient?
        pass

    def edit(self, transaction_id, **kwargs):
        # QUESTION: What does **kwargs allow you to do here?
        # How is this different from having separate methods for each field?
        pass

    def get_all(self):
        # QUESTION: What should this return?
        pass

    def get_by_type(self, transaction_type):
        # QUESTION: How would you filter the list to only return "wpłata" or "wydatek"?
        # Hint: think about list comprehensions.
        pass

    def calculate_balance(self):
        # QUESTION: How did show_balance() calculate the total before?
        # Now that you have Transaction objects, how do you access their attributes?
        pass


# QUESTION: What is the responsibility of this class?
# It should only handle user input/output — nothing else.
class FinanceApp:
    def __init__(self, manager):
        # QUESTION: What does this class need to remember?
        pass

    def run(self):
        # QUESTION: Where should the main while True loop live?
        # And should this method also call manager.load() at the start?
        pass

    def _show_menu(self):
        # QUESTION: What did the menu look like before? Move just the print statements here.
        pass

    def _handle_add(self):
        # QUESTION: This method should: ask for input, create a Transaction, then call manager.add().
        # Where does the new ID come from now?
        pass

    def _handle_delete(self):
        # QUESTION: Ask for ID, call manager.delete(). What if the ID doesn't exist?
        pass

    def _handle_edit(self):
        # QUESTION: Ask for ID and field to edit, call manager.edit(). 
        # How do you pass only the fields the user wants to change?
        pass

    def _handle_show_all(self):
        # QUESTION: Call manager.get_all() and print each transaction. How?
        pass

    def _handle_show_by_type(self, transaction_type):
        # QUESTION: Call manager.get_by_type(), then print results.
        pass

    def _handle_balance(self):
        # QUESTION: Call manager.calculate_balance() and display the result.
        pass


# QUESTION: What should these two lines do?
# Why is it better to put them inside `if __name__ == "__main__":` ?
if __name__ == "__main__":
    manager = TransactionManager()
    app = FinanceApp(manager)
    app.run()
