from utility.verification_util import Verification
from blockchain import Blockchain
from wallet import Wallet


class Node:
    def __init__(self):
        self.wallet = Wallet()
        self.blockchain = Blockchain(None)

    @staticmethod
    def get_transaction_value():
        tx_recipient = input("Enter the recipient: ")
        tx_amount = float(input("Enter the transaction amount: "))
        return tx_recipient, tx_amount

    @staticmethod
    def get_user_choice():
        return int(input("Your choice: "))

    def print_blockchain_elements(self):
        for block in self.blockchain.blockchain:
            print(block)

    def listen_for_input(self):
        waiting_for_input = True
        while waiting_for_input:
            print("*" * 20)
            print("Please enter a value")
            print("*" * 20)
            print("1. Add a new transaction value")
            print("2. Output the blockchain blocks")
            print("3. Mine a block")
            print("4. Output open transactions")
            print("5. Verify Transactions")
            print("6. Create Wallet")
            print("7. Load Wallet")
            print("8. Quit")
            user_choice = self.get_user_choice()
            if user_choice == 1:
                if self.wallet.public_key is not None:
                    tx_data = self.get_transaction_value()
                    recipient, amount = tx_data
                    signature = self.wallet.sign_transaction(self.wallet.public_key, recipient, amount)
                    if self.blockchain.add_transaction(recipient, self.wallet.public_key, signature, amount=amount):
                        print("Transaction Added.")
                    else:
                        print("Transaction Failed! Insufficient Balance")
                else:
                    print("Please add a wallet before adding transaction")
            elif user_choice == 2:
                self.print_blockchain_elements()
            elif user_choice == 3:
                if not self.blockchain.mine_block():
                    print("Mining Failed")
                else:
                    print("New block mined.")
            elif user_choice == 4:
                print(self.blockchain.get_open_transactions())
            elif user_choice == 5:
                if Verification.verify_transactions(self.blockchain.get_open_transactions(), self.blockchain.get_balance):
                    print("All Transactions are valid")
                else:
                    print("Invalid Transactions!")
            elif user_choice == 6:
                self.wallet.create_keys()
                self.blockchain = Blockchain(self.wallet.public_key)
            elif user_choice == 7:
                self.wallet.load_keys()
                self.blockchain = Blockchain(self.wallet.public_key)
            elif user_choice == 8:
                break
            else:
                print("Please enter a valid value.")
            if not Verification.verify_blockchain(self.blockchain.blockchain):
                print("Invalid Blockchain!")
                waiting_for_input = False
            print(f"{self.wallet.public_key} balance: {self.blockchain.get_balance():6.2f}")
        print("Done")


if __name__ == '__main__':
    node = Node()
    node.listen_for_input()