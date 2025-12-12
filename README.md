## MSSE CHEM274B Final Project
## A Banking system implementation with progressive complexity across four levels

# Group 6: 

Trinity Ho, Priscilla Vaskez, Dongwan Kim

---

## Overview

This project implements a simplified banking system that progressively adds functionality across four levels:

1. **Level 1**: Basic account operations (create, deposit, transfer)
2. **Level 2**: Account ranking based on outgoing transactions
3. **Level 3**: Payment scheduling with cashback system
4. **Level 4**: Account merging with transaction history preservation

The goal is to demonstrate software engineering principles including code implementation, data structures & data processing, refactoring and encapsulation, problem solving, and software design patterns. The implementation involves refactoring and adapting to new requirements without highly artificial scenarios.

---

## **What This Project Demonstrates**

- **Progressive Complexity**: Each level builds upon previous functionality while maintaining backward compatibility
- **Data Structure Design**: Efficient storage and retrieval of account balances, transaction history, and payment status
- **Refactoring**: Adapting existing code to support new requirements without breaking previous functionality
- **Time-based Operations**: Handling timestamps, cashback delays, and historical balance queries
- **Account Merging**: Preserving transaction history when merging accounts while maintaining data integrity
- **Binary Search**: Efficient retrieval of account balances at specific timestamps from chronological history

---

## **Repository Structure**

### **Core Implementation Files**

```
banking_system.py              # Abstract base class defining the BankingSystem interface
banking_system_impl.py         # Main implementation file (BankingSystemImpl class)
```

### **Test Files**

```
tests/
level_1_tests.py           # Tests for Level 1 functionality (10 test cases)
level_2_tests.py           # Tests for Level 2 functionality
level_3_tests.py           # Tests for Level 3 functionality
level_4_tests.py           # Tests for Level 4 functionality
sandbox_tests.py           # Additional test cases for development
```

### **Scripts**

```
main.sh                        # Run all test suites
run_single_test.sh             # Run a single test case by name
```

---

## **Level-by-Level Implementation Details**

### **Level 1: Basic Account Operations**

Implements three core operations:

- **`create_account(timestamp, account_id)`**: Create a new account with the given identifier
  - Returns `True` if successful, `False` if account already exists
  
- **`deposit(timestamp, account_id, amount)`**: Deposit money into an account
  - Returns balance after deposit, or `None` if account doesn't exist
  
- **`transfer(timestamp, source_account_id, target_account_id, amount)`**: Transfer money between accounts
  - Returns source account balance after transfer, or `None` if transfer fails
  - Returns `None` if:
    - Either account doesn't exist
    - Accounts are the same
    - Source account has insufficient funds

**Data Structures:**
- `accounts_dict`: Maps account_id to account information (balance)

---

### **Level 2: Account Ranking**

Adds functionality to rank accounts by outgoing transactions:

- **`top_spenders(timestamp, n)`**: Get top `n` accounts that spent the most money
  - Sort accounts by outgoing amount (most first)
  - If two accounts spent the same, sort by account name (A to Z)
  - Returns list of strings in format `"account_id(outgoing_amount)"`

**Data Structures:**
- `outgoing`: Maps account_id to total outgoing transaction amount

**Algorithm:**
- Uses bubble sort for sorting accounts by outgoing amount

---

### **Level 3: Payment Scheduling with Cashback**

Adds payment operations with cashback system:

- **`pay(timestamp, account_id, amount)`**: Withdraw amount from account as payment
  - Returns payment ID (e.g., "payment1", "payment2"), or `None` if payment fails
  - Returns `None` if:
    - Account doesn't exist
    - Account has insufficient funds
  - Cashback: 2% of withdrawal amount (rounded down), refunded 24 hours after payment
  
- **`get_payment_status(timestamp, account_id, payment)`**: Get status of payment
  - Returns `'IN_PROGRESS'` if cashback not yet processed
  - Returns `'CASHBACK_RECEIVED'` if cashback has been processed
  - Returns `None` if account doesn't exist or payment not found

**Key Constraints:**
- Cashback must be processed BEFORE other transactions at the same timestamp
- Cashback is automatically processed when timestamp reaches payment_time + 24 hours

**Data Structures:**
- `payments`: Maps account_id to dictionary of payment records
- `payment_counter`: Tracks payment ID generation

---

### **Level 4: Account Merging with History Preservation**

Adds account merging functionality while preserving transaction history:

- **`merge_accounts(timestamp, account_id_1, account_id_2)`**: Merge `account_id_2` into `account_id_1`
  - Returns `True` if successful, `False` otherwise
  - Returns `False` if:
    - `account_id_1` equals `account_id_2`
    - Either account doesn't exist
  - On merge:
    - `account_id_2`'s balance is added to `account_id_1`
    - `account_id_2`'s cashback refunds go to `account_id_1`
    - `account_id_2`'s payment status can be checked via `account_id_1`
    - `account_id_2` is removed from the system
  
- **`get_balance(timestamp, account_id, time_at)`**: Return account balance at timestamp `time_at`
  - Returns balance after operations at `time_at` have been processed
  - Returns `None` if account didn't exist at that time
  - Merged accounts inherit balance history from merged account
  - Handles queries before and after merge timestamps correctly

**Data Structures:**
- `aliases`: Maps merged account_id to current account_id
- `merge_times`: Maps account_id to merge timestamp
- `merged_history`: Maps merged account_id to original balance history before merge
- `record`: Maps account_id to chronological balance history as `(timestamp, balance)` tuples

**Algorithm:**
- Binary search on sorted balance history to find balance at or before `time_at`
- Filtering logic handles both accounts that were merged and accounts that merged others

---

## **Key Constraints and Assumptions**

- All timestamps are in milliseconds (range: 1 to 10^9)
- Timestamps are strictly increasing (operations arrive in chronological order)
- Cashback: 2% of withdrawal amount (rounded down), processed 24 hours after withdrawal
- Cashback must be processed BEFORE other transactions at the same timestamp
- Account balances reflect state AFTER operations at the query timestamp have been processed
- Merged accounts cannot be used for new operations (deposit, transfer, pay) but can be queried for historical data

---

## **How to Run Tests**

Execute a single test case by running the following command in the terminal:

```bash
bash run_single_test.sh "<test_case_name>"
```

---

## **Implementation Highlights**

### **Level 1**
- Dictionary-based account storage
- Balance tracking and validation
- Transfer validation (existence, sufficient funds, different accounts)

### **Level 2**
- Outgoing transaction tracking
- Bubble sort implementation for account ranking
- Tie-breaking by account name (alphabetical order)

### **Level 3**
- Payment ID generation
- Cashback calculation and scheduling
- Payment status tracking
- Cashback processing before other operations at same timestamp

### **Level 4**
- Account aliasing for merged accounts
- Balance history preservation using chronological tuples
- Binary search for efficient balance retrieval
- Handling of merged accounts in all operations
- Original history storage for queries before merge timestamp

---


## **Project Deliverables**

### **Delivery I:**
- Repository with full software library distribution
- Implementation files for all four levels
- UML diagram (at minimum reflects implementation details of at least 1 level)
- All team members submit solutions to Gradescope for each level

### **Delivery II:**
- Software engineering reflection PDF from each team member
- Description of individual role in the project
- Contribution details (lead work, help others, coordinated meetings, etc.)
- Challenges/problems faced and solutions

---

## **References**

### **Course Materials**
- **CHEM 274B – Software Engineering Fundamentals for Molecular Science**
- UC Berkeley Chem274B bCourses lecture materials
- Discussion materials on data structures and algorithms


### **Algorithm Resources**
- Binary search algorithm for efficient timestamp queries
- Dictionary-based data structures for O(1) account lookups
- Chronological tuple storage for balance history
- https://www.geeksforgeeks.org/python-program-for-bubble-sort/


