import hashlib
import json
import requests

from time import time
from urllib.parse import urlparse


# The Blockchain class is responsible for managing the chain.
# It will store transactions and have some helper methods for adding new blocks to the chain.
class Blockchain:
    def __init__(self):
        self.chain = []
        self.current_transactions = []
        # We consider the nodes as a set cause they must appear just once.
        self.nodes = set()

        # When our Blockchain is instantiated we’ll need to seed it with a genesis block (a block with no predecessors).
        self.new_block(proof=100, previous_hash=1)

    def new_block(self, proof, previous_hash=None):
        """
        Creates a new block in the Blockchain

        :param proof: <int> the proof given by the Proof-of-Work algorithm
        :param previous_hash: (Optional) <str> Hash of previous block
        :return: <dict> New block
        """

        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'transactions': self.current_transactions,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.last_block)
        }

        # Reset the current list of transactions.
        self.current_transactions = []

        self.chain.append(block)

        return block

    def new_transaction(self, sender, recipient, amount):
        """
        Creates a new transaction to go into the next mined block

        :param sender: <str> Address of the sender
        :param recipient: <str> Address of the recipient
        :param amount: <int> Amount transferred
        :return: <int> The index of the block that will hold this transaction
        """

        self.current_transactions.append({
            'sender': sender,
            'recipient': recipient,
            'amount': amount
        })

        return self.last_block['index'] + 1

    def register_node(self, address):
        """
        Add a new node to the list of nodes (network)

        :param address: <str> Address of a node, e.g., 'http://192.168.208.16:8080'
        :return: None
        """

        parsed_url = urlparse(address)
        self.nodes.add(parsed_url.netloc)

    # In a Blockchain the nodes must reach a consensus: a conflict is when one node has a different chain to another
    # node. To resolve this, we’ll make the rule that the longest valid chain is authoritative.
    # Using this algorithm, we reach consensus amongst the nodes in our network.
    def valid_chain(self, chain):
        """
        Determine if a given Blockchain is valid (cause this root code must run in every node on the network)

        :param chain: <list> A Blockchain
        :return: <bool> True if valid, False if not
        """

        last_block = chain[0]
        current_index = 1

        while current_index < len(chain):
            block = chain[current_index]

            print(f'{last_block}')
            print(f'{block}', end='\n-----------\n')

            # Check that the PoW is correct.
            if block['previous_hash'] != self.hash(last_block):
                return False

            last_block = block
            current_index += 1

        return True

    def consensus(self):
        """
        This consensus algorithm resolves conflicts by replacing our chain with the longest one in the network

        :return: <bool> True if our chain was replaced, False if not
        """

        neighbours = self.nodes
        new_chain = None

        # We're only looking for chains longer than ours.
        max_length = len(self.chain)

        # Grab and verify the chains from all the nodes in our network
        for node in neighbours:
            response = requests.get(f'http://{node}/chain')

            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']

                # Check if the length is longer and the chain is valid.
                if length > max_length and self.valid_chain(chain):
                    max_length = length
                    new_chain = chain

        # Replace our chain if we discovered a new, valid and longer than ours.
        if new_chain:
            self.chain = new_chain

            return True

        return False

    # A Proof-of-Work algorithm (PoW) is how new blocks are created or mined on the Blockchain. The goal of PoW is to
    # discover a number which solves a problem. The number must be difficult to find but easy to verify by anyone on
    # the network More details in '../extras/proof-of-work.py'.
    def proof_of_work(self, last_proof):
        """
        Simple Proof-of-Work algorithm:
            - Goal: find a number p' such that hash(pp') contains leading 4 zeroes, where p is the previous p'.
            - p is the previous proof and p' is the new proof.

        :param last_proof: <int> p
        :return: <int> p' (solution for the PoW algorithm)
        """

        proof = 0
        while not self.valid_proof(last_proof, proof):
            proof += 1

        return proof

    @property
    def last_block(self):
        return self.chain[-1]

    @staticmethod
    def valid_proof(last_proof, proof):
        """
        Validates the proof: does hash(last_proof, proof) contain 4 leading zeroes?

        :param last_proof: <int> Previous proof
        :param proof: <int> Current proof
        :return: True if correct, False if not
        """

        guess_hash = f'{last_proof}{proof}'.encode()

        return hashlib.sha256(guess_hash).hexdigest()[:4] == "0000"

        # Note 1: To adjust the difficulty of the algorithm, we could modify the number of leading zeroes.
        # But 4 is sufficient. You’ll find out that the addition of a single leading zero makes a mammoth difference
        # to the time required to find a solution.

        # Note 2: The parameter of sha256() is a string. So we need to format our two int values (last_proof and
        # proof) using the f'{variable}' standard string format.

    @staticmethod
    def hash(block):
        """
        Creates a SHA-256 hash of a block

        :param block: <dict> Block to be hashed
        :return: <str> Cryptographic key
        """

        # We must make sure that the dictionary is ordered or we'll have inconsistent hashes.
        block_string = json.dumps(block, sort_keys=True).encode()

        return hashlib.sha256(block_string).hexdigest()
