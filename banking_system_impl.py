from banking_system import BankingSystem


class BankingSystemImpl(BankingSystem):

    def __init__(self):
        # TODO: implement
        #pass
        self.accounts_dict = {}
        self.record = {} # added for level 4 to keep track of balance
        self.outgoing = {} # added for level2
        self.payments = {} # added for level3 pay method
        self.payment_counter = 1  # added for level 3 to generate payment1, payment2
        self.aliases = {} # for level 4 merged account redirection
    
    # Level 4
    def _binary_search_record(self, balance_record: list[tuple[int, int]], time_at: int) -> int | None:
        """Calls binary search for balance history to find balance at or before time_at"""

        lo, hi = 0, len(balance_record) - 1
        result = None

        while lo <= hi:
            mid = lo + (hi - lo) // 2
            mid_time, mid_balance = balance_record[mid]

            if time_at < mid_time:
                hi = mid - 1
            else:  # mid_time <= time_at
                result = mid_balance  
                lo = mid + 1  

        return result
    
    # Level 4
    def _record_balance(self, account_id: str, timestamp: int):
        """Stores a history of balance"""
        record_balance = self.accounts_dict[account_id]["account balance"]
        self.record[account_id].append((timestamp, record_balance))
        
    
    # Level 3
    def _process_cashback(self, timestamp: int):
        for account_id in self.payments:
            for payment_id, record in self.payments[account_id].items():
                if not record["refunded"] and timestamp >= record["cashback_timestamp"]:
                    self.accounts_dict[account_id]["account balance"] += record["cashback"]
                    record["refunded"] = True

                    # update balance record
                    self._record_balance(account_id, timestamp)


    def create_account(self, timestamp: int, account_id: str) -> bool:
        # TODO (TH)
        if account_id in self.accounts_dict:
            return False # Return False if account exists
        
        # Create new account, add timestamp and account balance as nested dict of account_id
        self.accounts_dict[account_id] = {"time": timestamp, "account balance": 0}

        # store balance record
        self.record[account_id] = [(timestamp, 0)]

        return True


    def deposit(self, timestamp: int, account_id: str, amount: int) -> int | None:
        # TODO (DK)
        # Give cashback (level 3)
        self._process_cashback(timestamp)
        if account_id not in self.accounts_dict:
            return None  # Return None if there is no account_id
        self.accounts_dict[account_id]["account balance"] += amount
        # update balance record
        self._record_balance(account_id, timestamp)

        return self.accounts_dict[account_id]["account balance"]


    def transfer(self, timestamp: int, source_account_id: str, target_account_id: str, amount: int) -> int | None:
        # TODO (Priscilla)
        # Give cashback (level 3)
        self._process_cashback(timestamp) 
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

        ###
        #Level 4
        # Update balance record
        self._record_balance(source_account_id, timestamp)
        self._record_balance(target_account_id, timestamp)

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

        # Return cashbacks first from previous withdrawal (level 3)
        self._process_cashback(timestamp)

        # Returns None if account_id doesn't exist
        if account_id not in self.accounts_dict:
            return None
        
        # Returns None if account_id has insufficient funds to perform payment
        if self.accounts_dict[account_id]["account balance"] < amount:
            return None
        
        # Withdraw money
        self.accounts_dict[account_id]["account balance"] -= amount

        # update new balance record after withdrawal (level 4)
        self._record_balance(account_id, timestamp)

        # Keep track in outgoing for top_spenders accounting for the total amount of money withdrawn from accounts
        if account_id not in self.outgoing:
            self.outgoing[account_id] = 0
        self.outgoing[account_id] += amount

        # Track payment and assign payment number
        payment = "payment" + str(self.payment_counter)
        self.payment_counter += 1


        # Calculate cashback for current payment (2% round down)
        cashback = amount * 2 // 100
        cashback_timestamp = timestamp + 86400000

        if account_id not in self.payments:
            self.payments[account_id] = {}

        self.payments[account_id][payment] = {"cashback_timestamp": cashback_timestamp, "refunded": False, "cashback": cashback}

        return payment
    

    def get_payment_status(self, timestamp: int, account_id: str, payment: str) -> str | None:
        # Give cashback (level 3)
        self._process_cashback(timestamp)
        
        # Return None if account_id doesn't exist
        if account_id not in self.accounts_dict:
            return None

        # Return None if account has no payments or payment not found
        if account_id not in self.payments or payment not in self.payments[account_id]:
            return None

        # Return the status of the payment
        if self.payments[account_id][payment]["refunded"]:
            return "CASHBACK_RECEIVED"
        else:
            return "IN_PROGRESS"
    
    def merge_accounts(self, timestamp: int, account_id_1: str, account_id_2: str) -> bool:
        #Prevent an account merging into itself
        if account_id_1 == account_id_2:
            return False
        
        # Follow alias chian if already merged
        while account_id_1 in self.aliases:
            account_id_1 = self.aliases[account_id_1]
        while account_id_2 in self.aliases:
            account_id_2 = self.aliases[account_id_2]
        
        # Check both accounts exist
        if account_id_1 not in self.accounts_dict or account_id_2 not in self.accounts_dict:
            return False
        
        # Add balances
        self.accounts_dict[account_id_1]["account balance"] += self.accounts_dict[account_id_2]["account balance"]

        # Add outgoing totals
        outgoing_1 = self.outgoing.get(account_id_1, 0)
        outgoing_2 = self.outgoing.get(account_id_2, 0)
        self.outgoing[account_id_1] = outgoing_1 + outgoing_2
        if account_id_2 in self.outgoing:
            del self.outgoing[account_id_2]

        # Move payment to account_id_1
        if account_id_2 in self.payments:
            if account_id_1 not in self.payments:
                self.payments[account_id_1] = {}
            self.payments[account_id_1].update(self.payments[account_id_2])
            del self.payments[account_id_2]
        # Set up alias for account_id_2 --> account_id_1
        self.aliases[account_id_2] = account_id_1

        # Removing account_id_3 from account_dict
        del self.accounts_dict[account_id_2]

        return True
        

    def get_balance(self, timestamp: int, account_id: str, time_at: int) -> int | None:
        """
        Should return the total amount of money in the account
        `account_id` at the given timestamp `time_at`.
        If the specified account did not exist at a given time
        `time_at`, returns `None`.
          * If queries have been processed at timestamp `time_at`,
          `get_balance` must reflect the account balance **after** the
          query has been processed.
          * If the account was merged into another account, the merged
          account should inherit its balance history.
        """
        # check if account exists
        if account_id not in self.accounts_dict:
            return None
        
        # Returns None if account_id does not exist at given time_at       
        if time_at < self.accounts_dict[account_id]["time"]:
            return None
        
        # Call binary search to find balance at or before time_at
        balance_history = self.record[account_id]

        return self._binary_search_record(balance_history, time_at)

        

        


