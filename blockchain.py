from utility.hash_util import hash_block
import json
from utility.verification_util import Verification
from block import Block
from transaction import Transaction

MINING_REWARD = 10.0


class Blockchain:
    def __init__(self, host_id):
        genesis_block = Block(0, '', [], 0, 0)
        self.blockchain = [genesis_block]
        self.__open_transactions = []
        self.load_data()
        self.host_id = host_id

    @property
    def blockchain(self):
        return self.__blockchain[:]

    @blockchain.setter
    def blockchain(self, val):
        self.__blockchain = val

    def get_open_transactions(self):
        return self.__open_transactions[:]

    def load_data(self):
        try:
            with open('blockchain.txt', mode='r') as f:
                blockchain = json.loads(f.readline()[:-1])
                updated_blockchain = []
                for block in blockchain:
                    converted_tx = [Transaction(tx['sender'], tx['recipient'], tx['amount']) for tx in block['transactions']]
                    updated_block = Block(block['index'], block['previous_hash'], converted_tx, block['proof'], block['timestamp'])
                    updated_blockchain.append(updated_block)
                self.blockchain = updated_blockchain
                open_transactions = json.loads(f.readline())
                updated_transactions = [Transaction(tx['sender'], tx['recipient'], tx['amount']) for tx in open_transactions]
                self.__open_transactions = updated_transactions
        except (IOError, IndexError):
            pass

    def save_data(self):
        try:
            with open('blockchain.txt', mode='w') as f:
                saveable_chain = [block.__dict__ for block in [
                    Block(block_el.index, block_el.previous_hash, [tx.__dict__ for tx in block_el.transactions],
                          block_el.proof, block_el.timestamp) for block_el in self.__blockchain]]
                f.write(json.dumps(saveable_chain))
                f.write("\n")
                saveable_tx = [tx.__dict__ for tx in self.__open_transactions]
                f.write(json.dumps(saveable_tx))
        except IOError:
            print("Save Failed!")

    def get_last_blockchain_value(self):
        """ Returns the last value of current Blockchain """
        if len(self.__blockchain) < 1:
            return None
        return self.__blockchain[-1]

    def add_transaction(self, recipient, sender, amount=1.0):
        transaction = Transaction(sender, recipient, amount)
        if Verification.verify_transaction(transaction, self.get_balance):
            self.__open_transactions.append(transaction)
            self.save_data()
            return True
        return False

    def proof_of_work(self):
        last_block = self.__blockchain[-1]
        last_block_hash = hash_block(last_block)
        proof = 0
        while not Verification.valid_proof(self.__open_transactions, last_block_hash, proof):
            proof += 1
        return proof

    def mine_block(self):
        last_block = self.__blockchain[-1]
        last_block_hash = hash_block(last_block)
        proof = self.proof_of_work()
        reward_transaction = Transaction('MINING', self.host_id, MINING_REWARD)
        open_transactions_copy = self.__open_transactions[:]
        open_transactions_copy.append(reward_transaction)
        block = Block(len(self.__blockchain), last_block_hash, open_transactions_copy, proof)
        self.__blockchain.append(block)
        self.__open_transactions.clear()
        self.save_data()

    def get_balance(self):
        participant = self.host_id
        amount_sent = 0
        amount_received = 0
        tx_sent = [[tx.amount for tx in block.transactions if tx.sender == participant] for block in self.__blockchain]
        open_tx_sent = [tx.amount for tx in self.__open_transactions if tx.sender == participant]
        tx_sent.append(open_tx_sent)
        for tx in tx_sent:
            if len(tx) > 0:
                amount_sent += sum(tx)
        tx_received = [[tx.amount for tx in block.transactions if tx.recipient == participant] for block in self.__blockchain]
        for tx in tx_received:
            if len(tx) > 0:
                amount_received += sum(tx)
        return amount_received - amount_sent




