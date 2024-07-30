import hashlib


class TransactionQueue:
    def __init__(self):
        self.transaction_queue = []

    def queue_transaction(self, p_transaction):
        # create list of hashes
        hashes = []
        for trans in self.transaction_queue:
            hashes.append(hashlib.blake2b(str(p_transaction).encode("utf-8")).hexdigest())
        if hashlib.blake2b(str(p_transaction).encode("utf-8")).hexdigest() in hashes:
            print("Hash already queued")
            return False
        else:
            print("New transaction queued")
            self.transaction_queue.append(p_transaction, hashlib.blake2b(str(p_transaction).encode("utf-8")).hexdigest())
            return True