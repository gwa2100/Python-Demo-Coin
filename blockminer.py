import hashlib
from random import randint

from block import Block, BlockPayload
from helperfunctions import get_current_time


class BlockMiner:
    def __init__(self, p_parent_block: Block, p_transactions_list: list, p_difficulty: int):
        self.parent_block = p_parent_block
        self.transactions_list = p_transactions_list
        self.difficulty = p_difficulty
        self.nonce = 0

    def run_miner(self, p_iterations=10):
        iterations = 0
        while True:
            iterations += 1
            if iterations > p_iterations > -1:
                break

            self.nonce = randint(0, 2 ** 64)

            parent_hash = self.parent_block.header.parent_hash
            parent_timestamp = self.parent_block.header.block_time_stamp
            block_timestamp = get_current_time()
            block_payload = BlockPayload(self.transactions_list)
            transactions_hash = block_payload.compute_transaction_hash()
            block_hash_string = parent_hash + \
                                str(parent_timestamp) + \
                                transactions_hash + \
                                str(self.nonce)
            temp_hash = hashlib.blake2b(block_hash_string.encode("utf-8")).hexdigest()
            print("TRY " + str(iterations) + "\t| NONCE: " + str(self.nonce) + "\t| RESULT: " + temp_hash)
            # compute difficulty zeros
            expected_zeros = ""
            for x in range(0, self.difficulty):
                expected_zeros += "0"

            if temp_hash[-self.difficulty:] == expected_zeros:
                return self.nonce, temp_hash