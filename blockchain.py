import functools
import hashlib as hl
import json
import requests
import pickle

from utility.hash_util import hash_block
from utility.verification import Verification
from block import Block
from transaction import Transaction
from wallet import Wallet

# from verification import Verification

# Initializing our blockchain list
MINING_REWARD = 10


class Blockchain:
    def __init__(self, public_key, node_id):
        genesis_block = Block(0, '', [], 100, 0)
        self.chain = [genesis_block]
        self.__open_transactions = []
        self.__peer_nodes = set()
        self.hosting_node = public_key
        self.node_id = node_id
        self.resolve_conflicts = False
        self.load_data()

    @property
    def chain(self):
        return self.__chain[:]

    @chain.setter
    def chain(self, val):
        self.__chain = val

    # def get_chain(self):
    #     return self.__chain[:]

    def get_open_transactions(self):
        return self.__open_transactions[:]


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
        last_block = self.__chain[-1]
        last_hash = hash_block(last_block)
        proof = 0
        # verifier = Verification()
        while not Verification.valid_proof(self.__open_transactions, last_hash, proof):
            proof += 1
        return proof

    def get_last_blockchain_value(self):
        """ Returns the last value of the current blockchain """
        if len(self.__chain) < 1:
            return None
        return self.__chain[-1]

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

    def get_balance(self, sender=None):

        if sender == None:
            if self.hosting_node == None:
                return None
            participant = self.hosting_node
        else:
            participant = sender
        tx_sender = [[tx.amount for tx in block.transactions
                      if tx.sender == participant] for block in self.__chain]
        print(tx_sender)
        open_tx_sender = [tx.amount
                          for tx in self.__open_transactions if tx.sender == participant]
        tx_sender.append(open_tx_sender)
        amount_sent = functools.reduce(
            lambda tx_sum, tx_amt: tx_sum + sum(tx_amt) if len(tx_amt) > 0 else tx_sum + 0, tx_sender, 0)
        # amount_sent = 0
        # for tx in tx_sender:
        #     if len(tx) > 0:
        #         amount_sent += tx[0]

        tx_recipient = [[tx.amount for tx in block.transactions
                         if tx.recipient == participant] for block in self.__chain]
        amount_recieved = functools.reduce(lambda tx_sum, tx_amt: tx_sum + sum(
            tx_amt) if len(tx_amt) > 0 else tx_sum + 0, tx_recipient, 0)
        # amount_recieved = 0
        # for tx in tx_recipient:
        #     if len(tx) > 0:
        #         amount_recieved += tx[0]
        return amount_recieved - amount_sent

    def add_transaction(self, recipient, sender, signature, amount=1.0, is_receiving=False):
        """ Append a new value as well as the last blockchain value to the blockchain

        Arguments:
            :sender: The sender of the coins.
            :recipient: The recipient of the coins.
            :amount: The amount sent by the sender to the recipient (default=1.0).
        """
        if self.hosting_node == None:
            return False
        # transaction = {'sender': sender, 'recipient': recipient, 'amount': amount}
        transaction = Transaction(sender, recipient, signature, amount)
        # transaction = OrderedDict(
        # [('sender', sender), ('recipient', recipient), ('amount', amount)])
        # verifier = Verification()
        # if not Wallet.verify_transaction(transaction):
        #     return False  #removed code redundancy
        if Verification.verify_transaction(transaction, self.get_balance):
            self.__open_transactions.append(transaction)
            self.participants.add(sender)
            self.participants.add(recipient)
            self.save_data()
            if not is_receiving:
                for node in self.__peer_nodes:
                    url = 'http://{}/broadcast-transaction'.format(node)
                    try:
                        response = requests.post(url, json={
                                                 'sender': sender, 'recipient': recipient, 'amount': amount, 'signature': signature})
                        if response.status_code == 400 or response.status_code == 500:
                            print('Transaction declined, needs resolving.')
                            return False
                    except requests.exceptions.ConnectionError:
                        continue
            return True
        else:
            return False

    def mine_block(self):
        if self.hosting_node == None:
            # return False #Http changes
            return None
        last_block = self.__chain[-1]
        # hashed_block = ''
        hashed_block = hash_block(last_block)
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
        reward_transaction = Transaction(
            'MINING', self.hosting_node, '', MINING_REWARD)
        # reward_transaction = OrderedDict(
        #   [('sender', 'MINING'), ('recipient', owner), ('amount', MINING_REWARD)])
        copied_transactions = self.__open_transactions[:]
        for tx in copied_transactions:
            if not Wallet.verify_transaction(tx):
                # return False #Http changes
                return None
        copied_transactions.append(reward_transaction)
        block = Block(len(self.__chain), hashed_block,
                      copied_transactions, proof)
        # block = {'previous_hash': hashed_block,
        #          'index': len(blockchain),
        #          'transactions': copied_transaction,
        #          'proof': proof
        #          }
        self.__chain.append(block)
        self.__open_transactions = []
        self.save_data()
        # return True #Http changes
        for node in self.__peer_nodes:
            url = 'http://{}/broadcast-block'.format(node)
            converted_block = block.__dict__.copy()
            converted_block['transactions'] = [
                tx.__dict__ for tx in converted_block['transactions']]
            try:
                response = requests.post(url, json={'block': converted_block})
                if response.status_code == 400 or response.status_code == 500:
                    print('Block declined, needs resolving.')
                if response.status_code == 409:
                    self.resolve_conflicts = True
            except requests.exceptions.ConnectionError:
                continue
        return block

    def add_block(self, block):
        transactions = [Transaction(
            tx['sender'], tx['recipient'], tx['signature'], tx['amount']) for tx in block['transactions']]
        proof_is_valid = Verification.valid_proof(
            transactions[:-1], block['previous_hash'], block['proof'])
        hashes_match = hash_block(self.chain[-1]) == block['previous_hash']
        if not proof_is_valid or not hashes_match:
            return False
        converted_block = Block(
            block['index'], block['previous_hash'], transactions, block['proof'], block['timestamp'])
        self.__chain.append(converted_block)
        stored_transactions = self.__open_transactions[:]
        for itx in block['transactions']:
            for opentx in stored_transactions:
                if opentx.sender == itx['sender'] and opentx.recipient == itx['recipient'] and opentx.amount == itx['amount'] and opentx.signature == itx['signature']:
                    try:
                        self.__open_transactions.remove(opentx)
                    except ValueError:
                        print('Item was already removed')
        self.save_data()
        return True

    def resolve(self):
        winner_chain = self.chain
        replace = False
        for node in self.__peer_nodes:
            url = 'http://{}/chain'.format(node)
            try:
                response = requests.get(url)
                node_chain = response.json()
                node_chain = [Block(block['index'], block['previous_hash'], [Transaction(tx['sender'], tx['recipient'], tx['signature'], tx['amount']) for tx in block['transactions']], block['proof'], block['timestamp']) for block in node_chain]
                node_chain_length = len(node_chain)
                local_chain_length = len(winner_chain)
                if node_chain_length > local_chain_length and Verification.verify_chain(node_chain):
                    winner_chain = node_chain
                    replace = True
            except requests.exceptions.ConnectionError:
                continue
        self.resolve_conflicts = False
        self.chain = winner_chain
        if replace:
            self.__open_transactions = []
        self.save_data()
        return replace

    def load_data(self):
        # global blockchain
        # global open_transactions
        try:
            with open('blockchain-{}.txt'.format(self.node_id), mode='r') as f:
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
                        tx['sender'], tx['recipient'], tx['signature'], tx['amount']) for tx in block['transactions']]
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
                open_transactions = json.loads(file_content[1][:-1])
                updated_transactions = []
                for tx in open_transactions:
                    updated_transaction = Transaction(
                        tx['sender'], tx['recipient'], tx['signature'], tx['amount'])
                    # updated_transactionn = OrderedDict(
                    # [('sender', tx['sender']), ('recipient', tx['recipient']), ('amount', tx['amount'])])
                    updated_transactions.append(updated_transaction)
                self.__open_transactions = updated_transactions
                peer_nodes = json.loads(file_content[2])
                self.__peer_nodes = set(peer_nodes)
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
            with open('blockchain-{}.txt'.format(self.node_id), mode='w') as f:
                savable_chain = [block.__dict__ for block in [Block(block_el.index, block_el.previous_hash, [
                                                                    tx.__dict__ for tx in block_el.transactions], block_el.proof, block_el.timestamp) for block_el in self.__chain]]
                f.write(json.dumps(savable_chain))
                f.write('\n')
                savable_tx = [tx.__dict__ for tx in self.__open_transactions]
                f.write(json.dumps(savable_tx))
                f.write('\n')
                f.write(json.dumps(list(self.__peer_nodes)))
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

    def add_peer_node(self, node):
        """Adds a new node to the peer node set.

        Arguments:
            :node: The node URL which should be added.
        """
        self.__peer_nodes.add(node)
        self.save_data()

    def remove_peer_node(self, node):
        """Remove a new node from the peer node set.

        Arguments:
            :node: The node URL which should be added.
        """
        self.__peer_nodes.discard(node)
        self.save_data()

    def get_peer_nodes(self):
        """Return a list of all connected peer nodes."""
        return list(self.__peer_nodes)
