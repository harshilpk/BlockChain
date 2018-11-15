import hash_util


class Verification:

    @classmethod
    def verify_chain(cls, blockchain):
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
     #         else:
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
        for (index, block) in enumerate(blockchain.chain):
            if index == 0:
                continue
            if block.previous_hash != hash_util.hash_block(blockchain.chain[index - 1]):
                return False
            if not cls.valid_proof(block.transactions[:-1], block.previous_hash, block.proof):
                return False
        return True

    @classmethod
    def verify_transactions(cls, open_transactions, get_balance):
        # is_valid = True
        # for tx in open_transactions:
        #     if verify_transaction(tx):
        #         is_valid = True
        #     else:
        #         is_valid = False
        # return is_valid
        return all([cls.verify_transaction(tx, get_balance) for tx in open_transactions])

    @staticmethod
    def verify_transaction(transaction, get_balance):
        sender_balance = get_balance()
        if sender_balance >= transaction.amount:
            return True
        else:
            return False

    @staticmethod
    def valid_proof(transactions, last_hash, proof):
        guess = (str([tx.to_ordered_dict() for tx in transactions]) +
                 str(last_hash) + str(proof)).encode()
        guess_hash = hash_util.hash_string_256(guess)
        print(guess_hash)
        return guess_hash[0:2] == '00'
