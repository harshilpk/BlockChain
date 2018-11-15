import functools
import hashlib as hl
import json

import pickle

import hash_util
from block import Block
from transaction import Transaction
from verification import Verification

# Initializing our blockchain list
MINING_REWARD = 10


class Blockchain:
    def __init__(self, hosting_node_id):
        genesis_block = Block(0, '', [], 100, 0)
        self.chain = [genesis_block]
        self.open_transactions = []
        self.load_data()
        self.hosting_node = hosting_node_id


# genesis_block = {'previous_hash': '',
#                  'index': 0,
#                  'transactions': [],
#                  'proof': 100
#                  }
# blockchain = []  # removed genesis block
# open_transactions = []
# owner = 'Harshil'
    participants = {'Harshil'}

    def proof_of_work(self):
        last_block = self.chain[-1]
        last_hash = hash_util.hash_block(last_block)
        proof = 0
        verifier = Verification()
        while not verifier.valid_proof(self.open_transactions, last_hash, proof):
            proof += 1
        return proof

    def get_last_blockchain_value(self):
        """ Returns the last value of the current blockchain """
        if len(self.chain) < 1:
            return None
        return self.chain[-1]

    # version 1
    # def add_transaction(transaction_amount, last_trasaction=[1]):
    #     """ Append a new value as well as the last blockchain value to the blockchain

    #     Arguments:
    #         :transaction_amount: The amount that should be added.
    #         :last_transaction: The last blockchain transaction (default [1]).
    #     """
    #     if last_trasaction == None:
    #         last_trasaction = [1]
    #     # blockchain.append([last_trasaction, transaction_amount])

    # version 2

    def get_balance(self):

        participant = self.hosting_node

        tx_sender = [[tx.amount for tx in block.transactions
                      if tx.sender == participant] for block in self.chain]
        print(tx_sender)
        open_tx_sender = [tx.amount
                          for tx in self.open_transactions if tx.sender == participant]
        tx_sender.append(open_tx_sender)
        amount_sent = functools.reduce(
            lambda tx_sum, tx_amt: tx_sum + sum(tx_amt) if len(tx_amt) > 0 else tx_sum + 0, tx_sender, 0)
        # amount_sent = 0
        # for tx in tx_sender:
        #     if len(tx) > 0:
        #         amount_sent += tx[0]

        tx_recipient = [[tx.amount for tx in block.transactions
                         if tx.recipient == participant] for block in self.chain]
        amount_recieved = functools.reduce(lambda tx_sum, tx_amt: tx_sum + sum(
            tx_amt) if len(tx_amt) > 0 else tx_sum + 0, tx_recipient, 0)
        # amount_recieved = 0
        # for tx in tx_recipient:
        #     if len(tx) > 0:
        #         amount_recieved += tx[0]
        return amount_recieved - amount_sent

    def add_transaction(self, recipient, sender, amount=1.0):
        """ Append a new value as well as the last blockchain value to the blockchain

        Arguments:
            :sender: The sender of the coins.
            :recipient: The recipient of the coins.
            :amount: The amount sent by the sender to the recipient (default=1.0).
        """
        # transaction = {'sender': sender, 'recipient': recipient, 'amount': amount}
        transaction = Transaction(sender, recipient, amount)
        # transaction = OrderedDict(
        # [('sender', sender), ('recipient', recipient), ('amount', amount)])
        verifier = Verification()
        if verifier.verify_transaction(transaction, self.get_balance):
            self.open_transactions.append(transaction)
            self.participants.add(sender)
            self.participants.add(recipient)
            self.save_data()
            return True
        else:
            return False

    def mine_block(self):
        last_block = self.chain[-1]
        # hashed_block = ''
        hashed_block = hash_util.hash_block(last_block)
        # print(hashed_block)
        # for key in last_block:
        #     value = last_block[key]
        #     hashed_block = hashed_block + str(value)
        # print(hashed_block)
        proof = self.proof_of_work()
        # reward_transaction = {
        #     'sender': 'MINING',
        #     'recipient': owner,
        #     'amount': MINING_REWARD,
        # }
        reward_transaction = Transaction('MINING', self.hosting_node, MINING_REWARD)
        # reward_transaction = OrderedDict(
        #   [('sender', 'MINING'), ('recipient', owner), ('amount', MINING_REWARD)])
        copied_transactions = self.open_transactions[:]
        copied_transactions.append(reward_transaction)
        block = Block(len(self.chain), hashed_block,
                      copied_transactions, proof)
        # block = {'previous_hash': hashed_block,
        #          'index': len(blockchain),
        #          'transactions': copied_transaction,
        #          'proof': proof
        #          }
        self.chain.append(block)
        self.open_transactions = []
        self.save_data()
        return True

    def load_data(self):
        # global blockchain
        # global open_transactions
        try:
            with open('blockchain.txt', mode='r') as f:
                #file_pickle = pickle.loads(f.read())
                # print(file_pickle)
                file_content = f.readlines()

            # blockchain = file_pickle['chain']
            # open_transactions = file_pickle['ot']
                blockchain = json.loads(file_content[0][:-1])
                # blockchain = [{'previous_hash': block['previous_hash'], 'index': block['index'], 'proof': block['proof'], 'transactions': [OrderedDict(
                # [('sender', tx['sender']), ('recipient', tx['recipient']), ('amount', tx['amount'])]) for tx in block['transactions']]} for block in blockchain]
                updated_blockchain = []
                for block in blockchain:
                    converted_tx = [Transaction(
                        tx['sender'], tx['recipient'], tx['amount']) for tx in block['transactions']]
                    # converted_tx = [OrderedDict([('sender', tx['sender']), ('recipient', tx['recipient']), ('amount', tx['amount'])]) for tx in block['transactions']]
                    updated_block = Block(
                        block['index'], block['previous_hash'], converted_tx, block['proof'], block['timestamp'])
                    # updated_block = {
                    #     'previous_hash': block['previous_hash'],
                    #     'index': block['index'],
                    #     'proof': block['proof'],
                    #     'transactions': [OrderedDict([('sender', tx['sender']), ('recipient', tx['recipient']), ('amount', tx['amount'])]) for tx in block['transactions']]
                    # }
                    updated_blockchain.append(updated_block)
                self.chain = updated_blockchain
                open_transactions = json.loads(file_content[1])
                updated_transactions = []
                for tx in open_transactions:
                    updated_transaction = Transaction(
                        tx['sender'], tx['recipient'], tx['amount'])
                    # updated_transactionn = OrderedDict(
                    # [('sender', tx['sender']), ('recipient', tx['recipient']), ('amount', tx['amount'])])
                    updated_transactions.append(updated_transaction)
                self.open_transactions = updated_transactions

        except (IOError, IndexError):
            print('Handled exception...')
            # genesis_block = {'previous_hash': '',
            #          'index': 0,
            #          'transactions': [],
            #          'proof': 100
            #          }
            # blockchain = [genesis_block]
            # open_transactions = []
        finally:
            print('Cleanup!')

    def save_data(self):
        try:
            with open('blockchain.txt', mode='w') as f:
                savable_chain = [block.__dict__ for block in [Block(block_el.index, block_el.previous_hash, [
                                                                    tx.__dict__ for tx in block_el.transactions], block_el.proof, block_el.timestamp) for block_el in self.chain]]
                f.write(json.dumps(savable_chain))
                f.write('\n')
                savable_tx = [tx.__dict__ for tx in self.open_transactions]
                f.write(json.dumps(savable_tx))
                # f.write(str(blockchain))
                # f.write('\n')
                # f.write(str(open_transactions))
                # save_data = {
                #     'chain': blockchain,
                #     'ot': open_transactions
                # }
                # f.write(pickle.dumps(save_data))
        except IOError:
            print('Saving failed!')

    # tx_amount = get_transaction_value()
    # add_value(tx_amount)
    # tx_amount = get_user_input()
    # add_value(last_trasaction=get_last_blockchain_value(),
    #           transaction_amount=tx_amount)
