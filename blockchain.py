import hashlib
import json

from textwrap import dedent
from time 	  import time
from uuid 	  import uuid4
from flask 	  import Flask, jsonify, request
from urllib.parse import urlparse

class Blockchain(object):
	def __init__(self):
			#constructor class variables
			self.block_chain = []
			self.current_transactions = []

			#create the genesis block
			self.new_block(100, 1)

	def new_block(self, proof, previous_hash=None):
		#creates new block in chain

		#proof <int>  -- proof provided by 'Proof of work' algorithm
		#previous_hash <str>  -- hash of previous block
		
		#return <dict> -- new block

		block = {
			'index': len(self.block_chain) + 1,
			'timestamp': time(),
			'transactions': self.current_transactions,
			'proof': proof,
			'previous_hash': previous_hash or self.hash(self.block_chain[-1])
		}

		#reset current list of transactions
		self.current_transactions = []

		self.block_chain.append(block)
		return block
		

	def new_transaction(self, sender, recipient, amount):
		#creates transaction for next mined block
		
		# sender 	<str> -- sender address
		# recipient <str> -- recipient address 
		# amount	<int> -- transaction amount

		#return block index <int>

		self.current_transactions.append({
				'sender': sender,
				'recipient': recipient,
				'amount': amount,
			})

		return self.last_block['index'] + 1

	@staticmethod
	def hash(block):
		#create a SHA-256 hash of a block

		#block <dict> -- a block from block chain
		#return <str> -- block hashed in hashing algorithm

		block_string = json.dumps(block, sort_keys=True).encode()
		return hashlib.sha256(block_string).hexdigest()

	def register_node(self, address):
		"""
		Add a new node to the list of nodes
		:param address: <str> Address of node. Eg. 'http://192.168.0.5:5000'
		:return: None
		"""

		parsed_url = urlparse(address)
		self.nodes.add(parsed_url.netloc)

	@property
	def last_block(self):
		return self.block_chain[-1]


	################################################################
	######################## Proofs ################################
	################################################################

	def find_proof(self, last_proof):
		#proof found when hash of previous proof and proposed proof 
		#starts with 4 leading 0's

		#last_proof <int> - last block proof

		proof = 0
		while not self.check_proof(last_proof, proof):
		  proof += 1

		return proof

	def check_proof(self, last_proof, proof):
		#last_proof <int> - last block proof
		#proof    <int> - proposed proof

		guess = f'{last_proof}{proof}'.encode()
		guess_hash = hashlib.sha256(guess).hexdigest()
		return guess_hash[:4] == "0000"


################################################################
################### FLASK API SERVICE ##########################
################################################################

# Instantiate our Node
app = Flask(__name__)

# Generate globally unique address for this node
node_identifier = str(uuid4()).replace('-','')

# Intantiate the Blockchain
blockchain = Blockchain()

@app.route('/mine', methods=['GET'])
def mine():
	# We run the proof of work algorithm to get the next proof...
	last_block = blockchain.last_block
	last_proof = last_block['proof']
	proof = blockchain.find_proof(last_proof)

	# We must receive a reward for finding the proof.
	# The sender is "0" to signify that this node has mined a new coin.
	blockchain.new_transaction(
	  sender="0",
	  recipient=node_identifier,
	  amount=1
	)

	# Forge the new Block by adding it to the chain
	previous_hash = blockchain.hash(last_block)
	block = blockchain.new_block(proof, previous_hash)

	response = {
	  'message': "New Block Forged",
	  'index': block['index'],
	  'transactions': block['transactions'],
	  'proof': block['proof'],
	  'previous_hash': block['previous_hash'],
	}
	return jsonify(response), 200

@app.route('/transactions/new', methods=['POST'])
def new_transaction():
	values = request.get_json()

	# Check that the required fields are in the POST'ed data
	required = ['sender', 'recipient', 'amount']
	if not all(k in values for k in required):
	  return 'Missing values', 400

	# Create a new Transaction
	index = blockchain.new_transaction(values['sender'], values['recipient'], values['amount'])

	response = {'message': f'Transaction will be added to Block {index}'}
	return jsonify(response), 201

@app.route('/chain', methods=['GET'])
def full_chain():
  response = {
    'chain': blockchain.block_chain,
    'length': len(blockchain.block_chain),
  }
  return jsonify(response), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

