import functools
import hashlib as hl
import json
from collections import OrderedDict
import pickle

import hash_util

# Initializing our blockchain list
MINING_REWARD = 10

# genesis_block = {'previous_hash': '',
#                  'index': 0,
#                  'transactions': [],
#                  'proof': 100
#                  }
blockchain = [] # removed genesis block
open_transactions = []
owner = 'Harshil'
participants = {'Harshil'}


def valid_proof(transactions, last_hash, proof):
    guess = (str(transactions) + str(last_hash) + str(proof)).encode()
    guess_hash = hash_util.hash_string_256(guess)
    print(guess_hash)
    return guess_hash[0:2] == '00'


def proof_of_work():
    last_block = blockchain[-1]
    last_hash = hash_util.hash_block(last_block)
    proof = 0
    while not valid_proof(open_transactions, last_hash, proof):
        proof += 1
    return proof


def get_last_blockchain_value():
    """ Returns the last value of the current blockchain """
    if len(blockchain) < 1:
        return None
    return blockchain[-1]

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


def verify_transaction(transaction):
    sender_balance = get_balance(transaction['sender'])
    if sender_balance >= transaction['amount']:
        return True
    else:
        return False


def get_balance(participant):

    tx_sender = [[tx['amount'] for tx in block['transactions']
                  if tx['sender'] == participant] for block in blockchain]
    print(tx_sender)
    open_tx_sender = [tx['amount']
                      for tx in open_transactions if tx['sender'] == participant]
    tx_sender.append(open_tx_sender)
    amount_sent = functools.reduce(
        lambda tx_sum, tx_amt: tx_sum + sum(tx_amt) if len(tx_amt) > 0 else tx_sum + 0, tx_sender, 0)
    # amount_sent = 0
    # for tx in tx_sender:
    #     if len(tx) > 0:
    #         amount_sent += tx[0]

    tx_recipient = [[tx['amount'] for tx in block['transactions']
                     if tx['recipient'] == participant] for block in blockchain]
    amount_recieved = functools.reduce(lambda tx_sum, tx_amt: tx_sum + sum(
        tx_amt) if len(tx_amt) > 0 else tx_sum + 0, tx_recipient, 0)
    # amount_recieved = 0
    # for tx in tx_recipient:
    #     if len(tx) > 0:
    #         amount_recieved += tx[0]
    return amount_recieved - amount_sent


def add_transaction(recipient, amount=1.0, sender=owner):
    """ Append a new value as well as the last blockchain value to the blockchain

    Arguments:
        :sender: The sender of the coins.
        :recipient: The recipient of the coins.
        :amount: The amount sent by the sender to the recipient (default=1.0).
    """
    # transaction = {'sender': sender, 'recipient': recipient, 'amount': amount}
    transaction = OrderedDict(
        [('sender', sender), ('recipient', recipient), ('amount', amount)])
    if verify_transaction(transaction):
        open_transactions.append(transaction)
        participants.add(sender)
        participants.add(recipient)
        save_data()
        return True
    else:
        return False


def mine_block():
    last_block = blockchain[-1]
    # hashed_block = ''
    hashed_block = hash_util.hash_block(last_block)
    # print(hashed_block)
    # for key in last_block:
    #     value = last_block[key]
    #     hashed_block = hashed_block + str(value)
    # print(hashed_block)
    proof = proof_of_work()
    # reward_transaction = {
    #     'sender': 'MINING',
    #     'recipient': owner,
    #     'amount': MINING_REWARD,
    # }
    reward_transaction = OrderedDict(
        [('sender', 'MINING'), ('recipient', owner), ('amount', MINING_REWARD)])
    copied_transaction = open_transactions[:]
    copied_transaction.append(reward_transaction)
    block = {'previous_hash': hashed_block,
             'index': len(blockchain),
             'transactions': copied_transaction,
             'proof': proof
             }
    blockchain.append(block)
    return True


def get_transaction_value():
    """ Returns the input of the user (a new transaction) as a float. """
    tx_recipient = input('Enter the recipient of the transaction:')
    tx_amount = float(input('Your transaction amount please: '))
    return (tx_recipient, tx_amount)


def load_data():
    global blockchain
    global open_transactions
    try:
        with open('blockchain.txt', mode='r') as f:
        #file_pickle = pickle.loads(f.read())
        # print(file_pickle)
            file_content = f.readlines()
           
        # blockchain = file_pickle['chain']
        # open_transactions = file_pickle['ot']
            blockchain = json.loads(file_content[0][:-1])
            blockchain = [{'previous_hash': block['previous_hash'], 'index': block['index'], 'proof': block['proof'], 'transactions': [OrderedDict(
            [('sender', tx['sender']), ('recipient', tx['recipient']), ('amount', tx['amount'])]) for tx in block['transactions']]} for block in blockchain]
            open_transactions = json.loads(file_content[1])
            updated_transactions = []
            for tx in open_transactions:
                 updated_transactionn = OrderedDict(
                [('sender', tx['sender']), ('recipient', tx['recipient']), ('amount', tx['amount'])])
                 updated_transactions.append(updated_transactionn)
            open_transactions = updated_transactions

    except IOError:
        genesis_block = {'previous_hash': '',
                 'index': 0,
                 'transactions': [],
                 'proof': 100
                 }
        blockchain = [genesis_block]
        open_transactions = []
    finally:
        print('Cleanup!')

load_data()


def save_data():
    try:
        with open('blockchain.txt', mode='w') as f:
            f.write(json.dumps(blockchain))
            f.write('\n')
            f.write(json.dumps(open_transactions))
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


def get_user_choice():
    user_input = input('Your choice: ')
    return user_input


def print_blockchain_elements():
    for block in blockchain:
        print('Outputting Block')
        print(block)
    else:
        print('-' * 20)


def verify_chain():
    """ Verify the current blockchain and return True if it is valid, alse otherwise"""
    # block_index = 0
    # version 2
    # is_valid = True
    # for block_index in range(len(blockchain)):
    #     if block_index == 0:
    #         block_index += 1
    #         continue
    #     elif blockchain[block_index][0] == blockchain[block_index-1]:
    #         is_valid = True
    #     else:
    #         is_valid = False
    #         break
    # version 1
    # for block in blockchain:
    #     if block_index == 0:
    #         block_index += 1
    #         continue
    #     elif block[0] == blockchain[block_index-1]:
    #         is_valid = True
    #     else:
    #         is_valid = False
    #         break
    #     block_index += 1
    # version 3
    for (index, block) in enumerate(blockchain):
        if index == 0:
            continue
        if block['previous_hash'] != hash_util.hash_block(blockchain[index - 1]):
            return False
        if not valid_proof(block['transactions'][:-1], block['previous_hash'], block['proof']):
            return False
    return True


def verify_transactions():
    # is_valid = True
    # for tx in open_transactions:
    #     if verify_transaction(tx):
    #         is_valid = True
    #     else:
    #         is_valid = False
    # return is_valid
    return all([verify_transaction(tx) for tx in open_transactions])

# tx_amount = get_transaction_value()
# add_value(tx_amount)

# tx_amount = get_user_input()
# add_value(last_trasaction=get_last_blockchain_value(),
#           transaction_amount=tx_amount)


waiting_for_input = True

while waiting_for_input:
    print('Please choose')
    print('1: Add a new transaction value')
    print('2: Mine a new block')
    print('3: Output the blockchain blocks')
    print("4: Output participants")
    print("5: Check transaction validity")
    print('h: Manipulate the chain')
    print('q: Quit')

    user_choice = get_user_choice()
    if user_choice == '1':
        tx_data = get_transaction_value()
        recipient, amount = tx_data
        # add_transaction(tx_amount, get_last_blockchain_value())
        if add_transaction(recipient, amount=amount):
            print('Added transaction!')
        else:
            print('Transaction failed!')
        print(open_transactions)
        # print(blockchain)
    elif user_choice == '2':
        if mine_block():
            open_transactions = []
            save_data()
    elif user_choice == '3':
        print_blockchain_elements()
    elif user_choice == '4':
        print(participants)
    elif user_choice == '5':
        if verify_transactions():
            print('All transactions are valid')
        else:
            print("There are invalid transactions")
    elif user_choice == 'h':
        if len(blockchain) >= 1:
            blockchain[0] = {'previous_hash': '',
                             'index': 0,
                             'transactions': [{'sender': 'Chris', 'recipient': 'Harshil', 'amount': 100}]
                             }
    elif user_choice == 'q':
        waiting_for_input = False
    else:
        print('Input was invalid, please pick a value from the list!')
    if not verify_chain():
        print_blockchain_elements()
        print('Invalid blockchain!')
        break
    print('Balance of {}: {:6.2f}'.format('Harshil', get_balance('Harshil')))

else:
    print('User left!')

print('Done!')
