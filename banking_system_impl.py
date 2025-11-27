from banking_system import BankingSystem


class BankingSystemImpl(BankingSystem):

    def __init__(self):
        # TODO: implement
        #pass
        self.accounts_dict = {}
        self.outgoing = {} # added for level2


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

        #Return the new balance of the source account
        return self.accounts_dict[source_account_id]["account balance"]
        
    def top_spenders(self, timestamp: int, limit: int) -> list[str]:
        pass