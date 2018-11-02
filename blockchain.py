import hashlib
import json
from collections import OrderedDict
MINING_REWARD = 10.0
GENESIS_BLOCK = {
    'previous_hash': '',
    'index': 0,
    'transactions': [],
    'proof': 100
}
blockchain = [GENESIS_BLOCK]
open_transactions = []
owner = 'Piyush'
participants = {owner}


def save_data():
    with open('blockchain.txt', mode='w') as f:
        f.write(json.dumps(blockchain))
        f.write("\n")
        f.write(json.dumps(open_transactions))


def load_data():
    try:
        with open('blockchain.txt', mode='r') as f:
            global blockchain
            global open_transactions
            blockchain = json.loads(f.readline()[:-1])
            updated_blockchain = []
            for block in blockchain:
                updated_block = {
                    'previous_hash': block['previous_hash'],
                    'index': block['index'],
                    'transactions': [OrderedDict([('sender', tx['sender']), ('recipient', tx['recipient']), ('amount', tx['amount'])]) for tx in block['transactions']],
                    'proof': block['proof']
                }
                updated_blockchain.append(updated_block)
            blockchain = updated_blockchain
            open_transactions = json.loads(f.readline())
            updated_transactions = [OrderedDict([('sender', tx['sender']), ('recipient', tx['recipient']), ('amount', tx['amount'])]) for tx in open_transactions]
            open_transactions = updated_transactions
    except IOError:
        print("File Not Found!")


load_data()


def get_last_blockchain_value():
    """ Returns the last value of current Blockchain """
    if len(blockchain) < 1:
        return None
    return blockchain[-1]


def add_transaction(recipient, sender=owner, amount=1.0):
    transaction = OrderedDict(
        [('sender', sender), ('recipient', recipient), ('amount', amount)])
    if verify_transaction(transaction):
        open_transactions.append(transaction)
        participants.add(sender)
        participants.add(recipient)
        save_data()
        return True
    return False


def hash_block(block):
    return hashlib.sha256(json.dumps(block, sort_keys=True).encode()).hexdigest()


def valid_proof(transactions, last_hash, proof):
    guess = (str(transactions) + str(last_hash) + str(proof)).encode()
    guess_hash = hashlib.sha256(guess).hexdigest()
    return  guess_hash[:2] == '00'


def proof_of_work():
    last_block = blockchain[-1]
    last_block_hash = hash_block(last_block)
    proof = 0
    while not valid_proof(open_transactions, last_block_hash, proof):
        proof += 1
    return proof


def mine_block():
    last_block = blockchain[-1]
    last_block_hash = hash_block(last_block)
    proof = proof_of_work()
    reward_transaction = OrderedDict(
        [('sender', 'MINING'), ('recipient', owner), ('amount', MINING_REWARD)])
    open_transactions_copy = open_transactions[:]
    open_transactions_copy.append(reward_transaction)
    block = {
        'previous_hash': last_block_hash,
        'index': len(blockchain),
        'transactions': open_transactions_copy,
        'proof': proof
    }
    blockchain.append(block)
    open_transactions.clear()
    save_data()


def get_balance(participant):
    amount_sent = 0
    amount_received = 0
    tx_sent = [[tx['amount'] for tx in block['transactions'] if tx['sender'] == participant] for block in blockchain]
    open_tx_sent = [tx['amount'] for tx in open_transactions if tx['sender'] == participant]
    tx_sent.append(open_tx_sent)
    for tx in tx_sent:
        if len(tx) > 0:
            amount_sent += sum(tx)
    tx_received = [[tx['amount'] for tx in block['transactions'] if tx['recipient'] == participant] for block in blockchain]
    for tx in tx_received:
        if len(tx) > 0:
            amount_received += sum(tx)
    return amount_received - amount_sent


def get_transaction_value():
    tx_recipient = input("Enter the recipient: ")
    tx_amount = float(input("Enter the transaction amount: "))
    return tx_recipient, tx_amount


def verify_transaction(transaction):
    sender_balance = get_balance(transaction['sender'])
    return sender_balance >= transaction['amount']


def get_user_choice():
    return int(input("Your choice: "))


def print_blockchain_elements():
    for block in blockchain:
        print(block)


def verify_blockchain():
    for (index, block) in enumerate(blockchain):
        if index == 0:
            continue
        if block['previous_hash'] != hash_block(blockchain[index-1]):
            return False
        if not valid_proof(block['transactions'][:-1], block['previous_hash'], block['proof']):
            return False
    return True


def verify_transactions():
    return all([verify_transaction(tx) for tx in open_transactions])


waiting_for_input = True


while waiting_for_input:
    print("Please enter a value")
    print("1. Add a new transaction value")
    print("2. Output the blockchain blocks")
    print("3. Mine a block")
    print("4. Output open transactions")
    print("5. Verify Transactions")
    print("6. Output participants")
    print("7. Hack Blockchain")
    print("8. Quit")
    user_choice = get_user_choice()
    if user_choice == 1:
        tx_data = get_transaction_value()
        recipient, amount = tx_data
        if add_transaction(recipient, amount=amount):
            print("Transaction Added.")
        else:
            print("Transaction Failed! Insufficient Balance.")
    elif user_choice == 2:
        print_blockchain_elements()
    elif user_choice == 3:
        mine_block()
    elif user_choice == 4:
        print(open_transactions)
    elif user_choice == 5:
        if verify_transactions():
            print("All Transactions are valid")
        else:
            print("Invalid Transactions!")
    elif user_choice == 6:
        print(participants)
    elif user_choice == 7:
        blockchain[0] = {
            'previous_hash': '123',
            'index': 0,
            'transactions': [],
            'proof': 23
        }
    elif user_choice == 8:
        break
    else:
        print("Please enter a valid value.")
    if not verify_blockchain():
        print("Invalid Blockchain!")
        waiting_for_input = False
    print(f"Piyush's balance: {get_balance(owner):6.2f}")
print("Done")
