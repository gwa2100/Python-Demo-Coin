import hashlib


class TransactionNetworkPackage:
    def __init__(self, p_trans, p_trans_hash):
        self.transaction = ''
        self.hash = hashlib.blake2b(str(self.transaction).encode("utf-8")).hexdigest()