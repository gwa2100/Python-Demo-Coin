import hashlib

class Transaction:
    def __init__(self, p_from_account, p_to_account, p_amount, p_transfer_bonus):
        self.from_account = p_from_account
        self.to_account = p_to_account
        self.amount = p_amount
        self.transfer_bonus = p_transfer_bonus

    def get_transaction_list(self):
        transaction_list = [str(self.from_account), str(self.to_account), str(self.amount), str(self.transfer_bonus)]
        return transaction_list

    def get_transaction_hash(self):
        transaction_string = ""
        #transaction_string = str(self.from_account) + str(self.to_account) + str(self.amount) + str(self.transfer_bonus)
        for item in self.get_transaction_list():
            transaction_string += item
        return hashlib.blake2b(transaction_string.encode("utf-8")).hexdigest()