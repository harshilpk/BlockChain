# Initializing our blockchain list
genesis_block = {'previous_hash': '',
                 'index': 0,
                 'transactions': []
                 }
blockchain = [genesis_block]
open_transactions = []
owner = 'Harshil'


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


def add_transaction(recipient, amount=1.0, sender=owner):
    """ Append a new value as well as the last blockchain value to the blockchain

    Arguments:
        :sender: The sender of the coins.
        :recipient: The recipient of the coins.
        :amount: The amount sent by the sender to the recipient (default=1.0).
    """
    transaction = {'sender': sender, 'recipient': recipient, 'amount': amount}
    open_transactions.append(transaction)


def mine_block():
    last_block = blockchain[-1]
    # hashed_block = ''
    hashed_block = '-'.join([str(last_block[key]) for key in last_block])
    # for key in last_block:
    #     value = last_block[key]
    #     hashed_block = hashed_block + str(value)
    # print(hashed_block)

    block = {'previous_hash': hashed_block,
             'index': len(blockchain),
             'transactions': open_transactions
             }
    blockchain.append(block)


def get_transaction_value():
    """ Returns the input of the user (a new transaction) as a float. """
    tx_recipient = input('Enter the recipient of the transaction:')
    tx_amount = float(input('Your transaction amount please: '))
    return (tx_recipient, tx_amount)


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
    # block_index = 0
    is_valid = True
    for block_index in range(len(blockchain)):
        if block_index == 0:
            block_index += 1
            continue
        elif blockchain[block_index][0] == blockchain[block_index-1]:
            is_valid = True
        else:
            is_valid = False
            break
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
    return is_valid


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
    print('h: Manipulate the chain')
    print('q: Quit')

    user_choice = get_user_choice()
    if user_choice == '1':
        tx_data = get_transaction_value()
        recipient, amount = tx_data
        # add_transaction(tx_amount, get_last_blockchain_value())
        add_transaction(recipient, amount=amount)
        print(open_transactions)
        print(blockchain)
    elif user_choice == '2':
        mine_block()
    elif user_choice == '3':
        print_blockchain_elements()
    elif user_choice == 'h':
        if len(blockchain) >= 1:
            blockchain[0] = [2]
    elif user_choice == 'q':
        waiting_for_input = False
    else:
        print('Input was invalid, please pick a value from the list!')
    # if not verify_chain():
    #     print_blockchain_elements()
    #     print('Invalid blockchain!')
    #     break

else:
    print('User left!')

print('Done!')
