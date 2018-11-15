from uuid import uuid4

from blockchain import Blockchain
from verification import Verification

class Node:

    def __init__(self):
        #self.id = str(uuid4())
        self.id = "HARSHIL"
        self.blockchain = Blockchain(self.id)
        

    def listen_for_input(self):

        waiting_for_input = True
        while waiting_for_input:
            print('Please choose')
            print('1: Add a new transaction value')
            print('2: Mine a new block')
            print('3: Output the blockchain blocks')
            print("4: Output participants")
            print("5: Check transaction validity")
            #print('h: Manipulate the chain')
            print('q: Quit')

            user_choice = self.get_user_choice()
            if user_choice == '1':
                tx_data = self.get_transaction_value()
                recipient, amount = tx_data
                # add_transaction(tx_amount, get_last_blockchain_value())
                if self.blockchain.add_transaction(recipient, self.id, amount=amount):
                    print('Added transaction!')
                else:
                    print('Transaction failed!')
                print(self.blockchain.open_transactions)
                # print(blockchain)
            elif user_choice == '2':
                self.blockchain.mine_block()
            elif user_choice == '3':
                self.print_blockchain_elements()
            elif user_choice == '4':
                print(self.blockchain.participants)
            elif user_choice == '5':
                verifier = Verification()
                if verifier.verify_transactions(self.blockchain.open_transactions, self.blockchain.get_balance):
                    print('All transactions are valid')
                else:
                    print("There are invalid transactions")
            # elif user_choice == 'h':
            #     if len(blockchain) >= 1:
            #         blockchain[0] = {'previous_hash': '',
            #                          'index': 0,
            #                          'transactions': [{'sender': 'Chris', 'recipient': 'Harshil', 'amount': 100}]
            #                          }
            elif user_choice == 'q':
                waiting_for_input = False
            else:
                print('Input was invalid, please pick a value from the list!')
            verifier = Verification()
            if not verifier.verify_chain(self.blockchain):
                self.print_blockchain_elements()
                print('Invalid blockchain!')
                break
            print('Balance of {}: {:6.2f}'.format(
                self.id, self.blockchain.get_balance()))

        else:
            print('User left!')

        print('Done!')

    def get_user_choice(self):
        user_input = input('Your choice: ')
        return user_input

    def print_blockchain_elements(self):
        for block in self.blockchain.chain:
            print('Outputting Block')
            print(block)
        else:
            print('-' * 20)

    def get_transaction_value(self):
        """ Returns the input of the user (a new transaction) as a float. """
        tx_recipient = input('Enter the recipient of the transaction:')
        tx_amount = float(input('Your transaction amount please: '))
        return (tx_recipient, tx_amount)

node = Node()

node.listen_for_input()