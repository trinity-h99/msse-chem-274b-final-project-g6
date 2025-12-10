from banking_system import BankingSystem


class BankingSystemImpl(BankingSystem):

    def __init__(self):
        # TODO: implement
        #pass
        self.accounts_dict = {}
        self.outgoing = {} # added for level2
        self.cashbacks = {} # added for level3 pay method
        self.withdrawals = 0 # added for level3 pay method
        self.payments = {} # added for level3 pay method
        self.payment_counter = 1  # added for level 3 to generate payment1, payment2
    
    # Level 3
    def _process_cashback(self, timestamp: int):
        """
        Internal helper method to check all scheduled payments for cashback refund.
        """
        for account_id in self.payments:
            for payment in self.payments[account_id]:
                if not payment["refunded"] and timestamp >= payment["scheduled_time"]:
                    self.accounts_dict[account_id]["account balance"] += payment["cashback"]
                    payment["refunded"] = True

    # TODO: implement interface methods here

    def create_account(self, timestamp: int, account_id: str) -> bool:
        # TODO (TH)
        if account_id in self.accounts_dict:
            return False # Return False if account exists
        
        # Create new account, add timestamp and account balance as nested dict of account_id
        self.accounts_dict[account_id] = {"time": timestamp, "account balance": 0}

        return True


    def deposit(self, timestamp: int, account_id: str, amount: int) -> int | None:
        # TODO (DK)
        if account_id not in self.accounts_dict:
            return None  # Return None if there is no account_id
        self.accounts_dict[account_id]["account balance"] += amount 
        return self.accounts_dict[account_id]["account balance"]


    def transfer(self, timestamp: int, source_account_id: str, target_account_id: str, amount: int) -> int | None:
        # TODO (Priscilla)
        #Checking if both accounts exist
        if source_account_id not in self.accounts_dict or target_account_id not in self.accounts_dict:
            return None
        #Cant transfer  to the same account
        if source_account_id == target_account_id:
            return None
        #Cant transfer if there is insuffcient funds
        if self.accounts_dict[source_account_id]["account balance"] < amount:
            return None
        # Performing the transfer
        self.accounts_dict[source_account_id]["account balance"] -= amount
        self.accounts_dict[target_account_id]["account balance"] += amount

        #######
        #Level2
        # accrue the "outgoing" from the spending from the source account
        current_outgoing = self.outgoing.get(source_account_id, 0)
        self.outgoing[source_account_id] = current_outgoing + amount
        ######

        #Return the new balance of the source account
        return self.accounts_dict[source_account_id]["account balance"]
        
    def top_spenders(self, timestamp: int, n: int) -> list[str]:
        """
        LEVEL2
        Get top n accounts that spent the most money.
        
        Sort accounts by how much they spent (most first).
        If two accounts spent the same, sort by account name (A to Z).
        Use bubble sort to do the sorting.
        
        Algorithm source:
        - Bubble Sort: GeeksforGeeks. "Python Program for Bubble Sort."
          https://www.geeksforgeeks.org/python-program-for-bubble-sort/
        
        Args:
            timestamp: Current timestamp (not used in Level 2 yet)
            n: Number of top spenders to return
            
        Returns:
            List of strings for result
        """
        # make list of all accounts and how much they spent
        account_outgoing_list = []
        for account_id in self.accounts_dict.keys():
            outgoing_amount = self.outgoing.get(account_id, 0)
            account_outgoing_list.append((account_id, outgoing_amount))
        
        # sort using bubble sort
        # compare two accounts next to each other and swap if needed
        for i in range(len(account_outgoing_list)):
            for j in range(len(account_outgoing_list) - 1):
                # check if first account spent less than second account
                if account_outgoing_list[j][1] < account_outgoing_list[j + 1][1]:
                    # swap them
                    account_outgoing_list[j], account_outgoing_list[j + 1] = account_outgoing_list[j + 1], account_outgoing_list[j]
                elif account_outgoing_list[j][1] == account_outgoing_list[j + 1][1]:
                    # if they spent same amount, check account names
                    if account_outgoing_list[j][0] > account_outgoing_list[j + 1][0]:
                        # swap them
                        account_outgoing_list[j], account_outgoing_list[j + 1] = account_outgoing_list[j + 1], account_outgoing_list[j]
        
        # get first n accounts from sorted list
        top_n = account_outgoing_list[:n]
        
        # result
        result = []
        for account_id, amount in top_n:
            result.append(f"{account_id}({amount})")
        
        return result
    


    def pay(self, timestamp: int, account_id: str, amount: int) -> str | None:

        # Return cashbacks first from previous withdrawal
        if timestamp in self.cashbacks:
            for record in self.cashbacks[timestamp]:
                account = record["account_id"]
                self.accounts_dict[account]["account balance"] += record["cashback"]
            del self.cashbacks[timestamp] # remove action after completion

        # Returns None if account_id doesn't exist
        if account_id not in self.accounts_dict:
            return None
        
        # Returns None if account_id has insufficient funds to perform payment
        if self.accounts_dict[account_id]["account balance"] < amount:
            return None
        
        # Withdraw money
        self.accounts_dict[account_id]["account balance"] -= amount

        # Keep track in outgoing for top_spenders accounting for the total amount of money withdrawn from accounts
        if account_id not in self.outgoing:
            self.outgoing[account_id] = 0
        self.outgoing[account_id] += amount

        # Track payment and assign payment number
        self.withdrawals += 1
        payment = "payment" + str(self.withdrawals)

        # Calculate cashback for current payment (2% round down)
        cashback = amount * 2 // 100
        cashback_timestamp = timestamp + 86400000

        # Reserve for when cashback time comes
        if cashback_timestamp not in self.cashbacks:
            self.cashbacks[cashback_timestamp] = []
        self.cashbacks[cashback_timestamp].append({"account_id": account_id, "cashback": cashback, "payment_num": payment})

        return payment

