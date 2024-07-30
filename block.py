import hashlib


class BlockHeader:
    def __init__(self, p_parent_hash, p_block_hash, p_block_time_stamp, p_parent_block_time_stamp):
        self.parent_hash = p_parent_hash
        self.block_hash = p_block_hash
        self.parent_block_time_stamp = p_parent_block_time_stamp
        self.block_time_stamp = p_block_time_stamp


class BlockPayload:
    def __init__(self, p_transactions):
        self.transactions = p_transactions

    def get_payload_string(self):
        payload_string = ""
        for x in self.transactions:
            for y in x.get_transaction_list():
                payload_string + str(y)
        return payload_string.encode('utf-8')

    def compute_transaction_hash(self):
        temp_hash = hashlib.blake2b()
        temp_hash.update(self.get_payload_string())
        return temp_hash.hexdigest()


class Block:
    def __init__(self, p_header, p_payload):
        self.header = p_header
        self.payload = p_payload


class ProofOfWork:
    def __init__(self, p_nonce: int, p_difficulty: int, p_result_hash):
        self.nonce = p_nonce
        self.difficulty = p_difficulty
        self.result_hash = p_result_hash