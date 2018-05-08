import hashlib
import json
from time import time

from uuid import uuid4

class Blockchain(object):
	def __init__(self):
			#constructor class variables
			self.block_chain = []
			self.current_transaction = []

			#create the genesis block
			self.new_block(1, 100)

	def new_block(self, previous_hash=None, proof):
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
	######################## Proofs ################################
	################################################################

	def find_proof(self, last_proof):
		#proof found when hash of previous proof and proposed proof 
		#starts with 4 leading 0's

		#last_proof <int> - last block proof

		proof = 0
		while !check_proof(last_proof, proof):
			proof += 1

		return proof

	def check_proof(last_proof, proof):
		#last_proof <int> - last block proof
		#proof 		<int> - proposed proof

		guess = f'{last_proof}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        return guess_hash[:4] == "0000"

