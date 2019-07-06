from uuid import uuid4
from flask import Flask, jsonify, request  # Micro-framework

from blockchain import *

# Our “server” will form a single node in our Blockchain network.

# Instantiate our node.
app = Flask(__name__)

# Generate a globally unique address for this node (create a random name for our node).
node_id = str(uuid4()).replace('-', '')

# Instantiate the Blockchain.
blockchain = Blockchain()


# Tell our "server" to mine a new block.
@app.route('/mine', methods=['GET'])
def mine():
    # Run the PoW algorithm to get the next proof.
    last_block = blockchain.last_block
    last_proof = last_block['proof']
    proof = blockchain.proof_of_work(last_proof)

    # We must receive a reward for finding the proof.
    # The sender is "0" to signify that this node has mined a new coin.
    blockchain.new_transaction(sender=0, recipient=node_id, amount=1)

    # Forge the new block by adding it to the chain.
    previous_hash = blockchain.hash(last_block)
    block = blockchain.new_block(proof, previous_hash)

    response = {
        'message': 'New block forged',
        'index': block['index'],
        'transactions': block['transactions'],
        'proof': block['proof'],
        'previous_hash': block['previous_hash']
    }

    return jsonify(response), 200


# Creates a new transaction to the block.
@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    values = request.get_json()

    # Check that the required fields are in the posted data.
    required = ['sender', 'recipient', 'amount']
    if not all(key in values for key in required):
        return 'Missing values', 400  # Returns the http response, as well as its code.

    # Create a new transaction.
    index = blockchain.new_transaction(values['sender'], values['recipient'], values['amount'])

    response = {'message': f'Transaction will be added to block {index}'}

    return jsonify(response), 201


# Returns the full Blockchain as a JSON.
@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        'chain': blockchain.chain,
        'length': len(blockchain.chain)
    }

    return jsonify(response), 200


@app.route('/nodes/register', methods=['POST'])
def register_node():
    values = request.get_json()

    nodes = values.get('nodes')
    if nodes is None:
        return 'Error: please supply a valid list of nodes', 400

    for node in nodes:
        blockchain.register_node(node)

    response = {
        'message': 'New nodes have been added',
        'total_nodes': list(blockchain.nodes)
    }

    return jsonify(response), 201


@app.route('/nodes/resolve', methods=['GET'])
def consensus():
    replaced = blockchain.consensus()

    if replaced:
        response = {
            'message': 'Our chain was replaced',
            'new_chain': blockchain.chain
        }
    else:
        response = {
            'message': 'Our chain is authoritative',
            'chain': blockchain.chain
        }

    return jsonify(response), 200


if __name__ == '__main__':
    # Run the server on port 5000.
    app.run(host='0.0.0.0', port=5000)
