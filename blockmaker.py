from block import Block, BlockPayload, BlockHeader
from helperfunctions import get_current_time


class BlockMaker:
    def __init__(self, p_parent_block: Block, p_transactions_list: list, p_proof_of_work):
        self.parent_block = p_parent_block
        self.transactions_list = p_transactions_list
        self.proof_of_work = p_proof_of_work
        self.block = ''
        self.generate_block()

    def generate_block(self):
        parent_hash = self.parent_block.header.block_hash
        parent_timestamp = self.parent_block.header.block_time_stamp
        block_timestamp = get_current_time()
        block_payload = BlockPayload(self.transactions_list)
        block_header = BlockHeader(parent_hash, self.proof_of_work.result_hash, block_timestamp, parent_timestamp)
        self.block = Block(block_header, block_payload)