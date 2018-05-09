import hashlib
import json

from textwrap import dedent
from time 	  import time
from uuid 	  import uuid4
from flask 	  import Flask

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
		

	def new_transaction(self, sender, recipient, memo):
		#creates transaction for next mined block
		
		# sender 	<str> -- sender address
		# recipient <str> -- recipient address 
		# memo 		<str> -- transaction data

		#return block index <int>

		self.current_transactions.append({
				'sender': sender,
				'recipient': recipient,
				'memo': memo,
			})

		return self.last_block['index'] + 1

	@staticmethod
	def hash(block):
		#create a SHA-256 hash of a block

		#block <dict> -- a block from block chain
		#return <str> -- block hashed in hashing algorithm

		block_string = json.dumps(block, sort_keys=True).encode()

		return hashlib.sha256(block_string).hexdigest()

	@property
	def last_block(self):
		return self.block_chain[-1]


	################################################################
	######################### PROOF ################################
	################################################################

	def find_proof(self, last_proof):
		#proof found when hash of previous proof and proposed proof 
		#starts with 4 leading 0's

		#last_proof <int> - last block proof

		proof = 0
		while check_proof(last_proof, proof) is False:
			proof += 1

		return proof

	@staticmethod
	def check_proof(last_proof, proof):
		#last_proof <int> - last block proof
		#proof 		<int> - proposed proof

		guess = f'{last_proof}{proof}'.encode()
		guess_hash = hashlib.sha256(guess).hexdigest()
		return guess_hash[:4] == "0000"


################################################################
################### FLASK API SERVICE ##########################
################################################################

# Instantiate our Node
app = Flask(__name__)

# Generate a globally unique address for this node
node_identifier = str(uuid4()).replace('-', '')

# Instantiate the Blockchain
blockchain = Blockchain()

@app.route('/mine', methods=['GET'])
def mine():
    #Get proof for this new block we are mining
    last_block = blockchain.last_block
    last_proof = last_block['proof']
    proof = blockchain.proof_of_work(last_proof)

    # We must receive a reward for finding the proof.
    # The sender is "0" to signify that this node has mined a new coin.
    blockchain.new_transaction(
        sender="0",
        recipient=node_identifier,
        memo="hello",
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
	data = requests.get_json()

	required = ['sender', 'recipient', 'memo']

	if not all (keys in data for keys in required):
		return "missing required data for trasaction", 400

	index = blockchain.new_transaction(data['sender'], data['recipient'], data['memo'])

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

