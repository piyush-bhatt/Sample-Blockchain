from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from wallet import Wallet
from blockchain import Blockchain

app = Flask(__name__)
wallet = Wallet()
blockchain = Blockchain(wallet.public_key)
CORS(app)


@app.route('/', methods=['GET'])
def get_ui():
    return send_from_directory('ui', 'node.html')


@app.route('/wallet', methods=['POST'])
def create_keys():
    if wallet.create_keys():
        global blockchain
        blockchain = Blockchain(wallet.public_key)
        response = {
            'public_key': wallet.public_key,
            'private_key': wallet.private_key,
            'funds': blockchain.get_wallet_balance()
        }
        return jsonify(response), 201
    else:
        response = {
            'message': 'Saving keys failed'
        }
        return jsonify(response), 500


@app.route('/wallet', methods=['GET'])
def load_keys():
    if wallet.load_keys():
        global blockchain
        blockchain = Blockchain(wallet.public_key)
        response = {
            'public_key': wallet.public_key,
            'private_key': wallet.private_key,
            'funds': blockchain.get_wallet_balance()
        }
        return jsonify(response), 201
    else:
        response = {
            'message': 'Loading keys failed'
        }
        return jsonify(response), 500


@app.route('/balance', methods=['GET'])
def get_balance():
    balance = blockchain.get_wallet_balance()
    if balance is not None:
        response = {
            'message': 'Fetching balance successful',
            'funds': balance
        }
        return jsonify(response), 200
    else:
        response = {
            'message': 'Fetching balance failed.',
            'wallet_status': wallet.public_key is not None
        }
        return jsonify(response), 500


@app.route('/transaction', methods=['POST'])
def add_transaction():
    if wallet.public_key is None:
        response = {
            'message': 'No wallet set up'
        }
        return jsonify(response), 500
    values = request.get_json()
    if not values:
        response = {
            'message': 'No data found'
        }
        return jsonify(response), 400
    required_fields = ['recipient', 'amount']
    if not all(field in values for field in required_fields):
        response = {
            'message': 'Required data is missing'
        }
        return jsonify(response), 400
    signature = wallet.sign_transaction(wallet.public_key, values['recipient'], values['amount'])
    transaction = blockchain.add_transaction(values['recipient'], wallet.public_key, signature, values['amount'])
    if transaction is not None:
        response = {
            'message': 'Transaction added successfully',
            'transaction': transaction.__dict__,
            'funds': blockchain.get_wallet_balance()
        }
        return jsonify(response), 201
    else:
        response = {
            'message': 'Transaction failed',
            'funds': blockchain.get_wallet_balance()
        }
        return jsonify(response), 500


@app.route('/transactions', methods=['GET'])
def get_open_transactions():
    transactions = blockchain.get_open_transactions()
    transactions_dict = [tx.__dict__ for tx in transactions]
    return jsonify(transactions_dict), 200


@app.route('/mine', methods=['POST'])
def mine_block():
    block = blockchain.mine_block()
    if block is not None:
        block_dict = block.__dict__.copy()
        block_dict['transactions'] = [tx.__dict__ for tx in block_dict['transactions']]
        response = {
            'message': 'Block added successfully.',
            'block': block_dict,
            'funds': blockchain.get_wallet_balance()
        }
        return jsonify(response), 201
    else:
        response = {
            'message': 'Adding Block failed',
            'wallet_status': wallet.public_key is not None
        }
        return jsonify(response), 500


@app.route('/chain', methods=['GET'])
def get_blockchain():
    chain = blockchain.blockchain
    chain_dict = [block.__dict__.copy() for block in chain]
    for block in chain_dict:
        block['transactions'] = [
            tx.__dict__ for tx in block['transactions']]
    return jsonify(chain_dict), 200


if __name__ == '__main__':
    app.run(debug=True, port=3134)
