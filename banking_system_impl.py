from banking_system import BankingSystem


class BankingSystemImpl(BankingSystem):

    def __init__(self):
        # TODO: implement
        #pass
        self.accounts_dict = {}


    # TODO: implement interface methods here

    def create_account(self, timestamp: int, account_id: str) -> bool:
        # TODO
        pass


    def deposit(self, timestamp: int, account_id: str, amount: int) -> int | None:
        # TODO (DK)
        if account_id not in self.accounts_dict:
            return None  # Return None if there is no account_id
        self.accounts_dict[account_id] += amount 
        return self.accounts_dict[account_id]


    def transfer(self, timestamp: int, source_account_id: str, target_account_id: str, amount: int) -> int | None:
        # TODO
        pass
