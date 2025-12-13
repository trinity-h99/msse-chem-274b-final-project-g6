from banking_system import BankingSystem


class BankingSystemImpl(BankingSystem):

    def __init__(self):
        """
        Initialize all data structure for account storage and transaction tracking. 
        - accounts_dict: Maps account_id to account info (timestamp, balance)
        - record: Balance history per account for timestamp queries
        - outgoing: Total outgoing transactions per account
        - payments: Stores all payment transactions per account
        - aliases: Account ID redirection for merged accounts
        - merge_times: Records the timestamp at which an account was merged
        - merged_history: Stores pre-merge balance history of merged accounts
        """
        # TODO: implement
        self.accounts_dict = {}
        self.record = {} # added for level 4 to keep track of balance
        self.outgoing = {} # added for level2
        self.payments = {} # added for level3 pay method
        self.payment_counter = 1  # added for level 3 to generate payment1, payment2
        self.aliases = {} # Level 4: merged account redirection
        self.merge_times = {}  # Level 4: Store when each account was merged (account_id -> merge_timestamp)
        self.merged_history = {}  # Level 4: Store merged account's original history before merge
    
    def _resolve(self, account_id: str) -> str:
        """Resolve merged account to its current account"""
        while account_id in self.aliases:
            account_id = self.aliases[account_id]
        return account_id
    
    def _is_merged_account(self, account_id: str) -> bool:
        """Check if account was merged into another account"""
        # Merged account: deleted from accounts_dict but still has alias pointing to merged account
        # Both conditions must be true: deleted AND has alias
        is_deleted = account_id not in self.accounts_dict
        has_alias = account_id in self.aliases
        return is_deleted and has_alias
    
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
        """Process pending cashback refunds up to timestamp"""
        for account_id in self.payments:
            for payment_id, record in self.payments[account_id].items():
                if not record["refunded"] and timestamp >= record["cashback_timestamp"]:
                    self.accounts_dict[account_id]["account balance"] += record["cashback"]
                    record["refunded"] = True

                    # update balance record
                    self._record_balance(account_id, timestamp)


    def create_account(self, timestamp: int, account_id: str) -> bool:
        """
        Create a new account with the given identifier if it doesn't already exist.
        Returns True if successful, False if account already exists.
        
        Level 4: Clears alias and merge_times if recreating a previously merged account.
        """
        if account_id in self.accounts_dict:
            return False # Return False if account exists
        
        # Level 4:Clear alias if recreating merged account
        if account_id in self.aliases:
            del self.aliases[account_id]
        if account_id in self.merge_times:
            del self.merge_times[account_id]
        
        # Create new account, add timestamp and account balance as nested dict of account_id
        self.accounts_dict[account_id] = {"time": timestamp, "account balance": 0}

        # Level 4: store balance record
        self.record[account_id] = [(timestamp, 0)]

        return True


    def deposit(self, timestamp: int, account_id: str, amount: int) -> int | None:
        """
        Deposit amount to account_id.
        Returns balance after deposit, or None if account doesn't exist.
        
        Level 3: Processes cashback before deposit.
        Level 4: Handles merged accounts.
        """
        # Give cashback (level 3)
        self._process_cashback(timestamp)
        
        # Level4: Check if original account was merged before resolving
        if self._is_merged_account(account_id):
            return None
        
        # level4 for aliasing - use _resolve
        account_id = self._resolve(account_id)

        if account_id not in self.accounts_dict:
            return None  # Return None if there is no account_id
        self.accounts_dict[account_id]["account balance"] += amount
        # update balance record
        self._record_balance(account_id, timestamp)

        return self.accounts_dict[account_id]["account balance"]


    def transfer(self, timestamp: int, source_account_id: str, target_account_id: str, amount: int) -> int | None:
        """
        Transfer amount from source_account_id to target_account_id.
        Returns source account balance after transfer, or None if transfer fails.
        
        Returns None if:
        - Either account doesn't exist
        - Accounts are the same
        - Source account has insufficient funds
        
        Level 3: Processes cashback before transfer.
        Level 4: Handles merged accounts.
        """
        # Give cashback (level 3)
        self._process_cashback(timestamp) 

        # Level 4: Check if original accounts were merged before resolving
        if self._is_merged_account(source_account_id) or self._is_merged_account(target_account_id):
            return None

        # Level 4 for aliasing - use _resolve
        source_account_id = self._resolve(source_account_id)
        target_account_id = self._resolve(target_account_id)
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
        """
        Withdraw amount from account_id as payment.
        Returns payment ID, or None if payment fails.
        
        Returns None if:
        - Account doesn't exist
        - Account has insufficient funds
        
        Level 3: Processes cashback before payment. Cashback (2% rounded down) 
        is refunded 24 hours after payment.
        Level 4: Handles merged accounts.
        """
        # Return cashbacks first from previous withdrawal (level 3)
        self._process_cashback(timestamp)

        # Level 4: Check if original account was merged before resolving
        if self._is_merged_account(account_id):
            return None

        # Level 4 for aliasing - use _resolve
        account_id = self._resolve(account_id)

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
        """
        Get status of payment for account_id.
        Returns 'IN_PROGRESS', 'CASHBACK_RECEIVED', or None if payment doesn't exist.
        
        Returns None if:
        - Account doesn't exist
        - Payment not found
        
        Level 3: Processes cashback before checking status.
        Level 4: Handles merged accounts.
        """
        # Give cashback (level 3)
        self._process_cashback(timestamp)
        
        # Level 4: Check if original account was merged before resolving
        if self._is_merged_account(account_id):
            return None
        
        # Level 4 for aliasing - use _resolve
        account_id = self._resolve(account_id)
        
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
        """
        Merge account_id_2 into account_id_1.
        Returns True if successful, False otherwise.
        
        Returns False if:
        - account_id_1 equals account_id_2
        - Either account doesn't exist
        
        On merge:
        - account_id_2's balance is added to account_id_1
        - account_id_2's cashback refunds go to account_id_1
        - account_id_2's payment status can be checked via account_id_1
        - account_id_2 is removed from the system
        
        Level 4: Stores original balance histories before merging for get_balance queries.
        """
        self._process_cashback(timestamp)
        
        # Level 4: Resolve accounts to handle chain merges
        account_id_1 = self._resolve(account_id_1)
        account_id_2 = self._resolve(account_id_2)
        
        # Requirement 1: Prevent account merging into itself
        if account_id_1 == account_id_2:
            return False
        
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
        
        # Level 4: Merge balance records and store original histories
        if account_id_2 in self.record:
            # Store original histories before merging (preserve if already stored)
            # Use .copy() to create independent copy: after del self.record[account_id_2],
            # merged_history still needs the original history for get_balance queries
            if account_id_2 not in self.merged_history:
                self.merged_history[account_id_2] = self.record[account_id_2].copy()
            if account_id_1 not in self.merged_history:
                if account_id_1 not in self.record:
                    self.record[account_id_1] = []
                self.merged_history[account_id_1] = self.record[account_id_1].copy()
            
            # Merge histories: combine account_id_2's history into account_id_1
            if account_id_1 not in self.record:
                self.record[account_id_1] = []
            self.record[account_id_1].extend(self.record[account_id_2])
            self.record[account_id_1].sort()
            del self.record[account_id_2]  # Remove account_id_2 from system
        
        # Level 4: Store merge timestamp for get_balance filtering
        self.merge_times[account_id_2] = timestamp
        
        # Level 4: Set up alias for account_id_2 -> account_id_1 
        self.aliases[account_id_2] = account_id_1
        
        # Record balance after merge and remove account_id_2
        self._record_balance(account_id_1, timestamp)
        del self.accounts_dict[account_id_2]

        return True
        

    def get_balance(self, timestamp: int, account_id: str, time_at: int) -> int | None:
        """
        Return account balance at timestamp time_at.
        Returns None if account didn't exist at that time.
        
        Balance reflects state after operations at `time_at`.
        Merged accounts inherit balance history from merged account.
        
        Level 4: Handles merged accounts and processes cashback at `time_at.
        """
        # Level 4: Process cashback at time_at first
        self._process_cashback(time_at)

        # Level 4: Handle merged accounts
        original_id = account_id
        if original_id in self.aliases:
            merge_time = self.merge_times.get(original_id)
            if merge_time and time_at >= merge_time:
                return None  # Account was merged, doesn't exist after merge_time
            if merge_time and time_at < merge_time:
                # Before merge: use original history
                if original_id in self.merged_history:
                    history = [(t, b) for t, b in self.merged_history[original_id] if t < merge_time]
                    return self._binary_search_record(history, time_at) if history else None
        
        # Resolve merged account and check existence
        account_id = self._resolve(account_id)
        if account_id not in self.accounts_dict or time_at < self.accounts_dict[account_id]["time"]:
            return None
        
        # Check if account merged others before time_at
        for merged_id, mt in self.merge_times.items():
            if self._resolve(merged_id) == account_id and time_at < mt:
                if account_id in self.merged_history:
                    history = [(t, b) for t, b in self.merged_history[account_id] if t < mt]
                    return self._binary_search_record(history, time_at) if history else None

        # Use current balance history
        return self._binary_search_record(self.record[account_id], time_at)

        

        


