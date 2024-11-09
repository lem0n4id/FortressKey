from block import Block
import time

class Blockchain:
    def __init__(self):
        self.chain = [self.create_genesis_block()]
        self.pending_transactions = []
        self.difficulty = 2  # Number of leading zeros required in the hash

    def create_genesis_block(self):
        return Block(0, [], int(time.time()), "0")

    def get_latest_block(self):
        return self.chain[-1]

    def add_block(self, block):
        block.previous_hash = self.get_latest_block().hash
        block.hash = block.calculate_hash()
        self.chain.append(block)

    def add_transaction(self, transaction):
        self.pending_transactions.append(transaction)

    def mine_pending_transactions(self):
        block = Block(len(self.chain), self.pending_transactions, int(time.time()), self.get_latest_block().hash)
        self.proof_of_work(block)
        self.add_block(block)
        self.pending_transactions = []

    def proof_of_work(self, block):
        target = "0" * self.difficulty
        while block.hash[:self.difficulty] != target:
            block.nonce += 1
            block.hash = block.calculate_hash()
        print(f"Block mined: {block.hash}")

    def print_all_transactions(self):
        for block in self.chain:
            print(f"Block {block.index}:")
            for transaction in block.transactions:
                print(f"  Transaction:")
                # pretty print the transaction
                for key, value in transaction.items():
                    print(f"    {key}: {value}")
            print(f"  Hash: {block.hash}\n")


