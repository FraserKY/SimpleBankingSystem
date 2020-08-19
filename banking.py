# Write your code here
import random
import math
import os.path
import sqlite3


class Account:
    accounts = {}

    def __init__(self, account_number):
        self.balance = 0
        self.acc_number = account_number
        self.pin_ = gen_pin()
        Account.accounts[account_number] = self.pin_


def gen_pin():
    pin = str(random.randint(0, 10000))
    # Add additional digits if generated number is less than 1000
    if len(pin) < 4:
        pin = (4 - len(pin)) * '0' + pin

    return pin


def gen_acc_no():
    bin_ = '400000'
    cid = str(random.randint(0, 1000000000))

    if len(str(cid)) < 9:
        cid = (9 - len(cid)) * '0' + cid

    checksum = check_sum_generator(bin_ + cid)

    return int(bin_ + cid + checksum)


def check_sum_generator(account_no):
    account_number_split = list(account_no)

    sum_ = 0

    for i in range(0, 15, 2):
        account_number_split[i] = int(account_number_split[i]) * 2

    for i in range(0, 15):
        if int(account_number_split[i]) > 9:
            account_number_split[i] = int(account_number_split[i]) - 9

    for x in range(0, 15):
        sum_ += int(account_number_split[x])

    return str(int(round_up(sum_, -1)) - sum_)


def luhn_alg_check(account_no):
    # remove and save last digit
    account_no_nochecksum = account_no[:-1]
    check_sum = account_no[15:16]
    check_sum_gen = check_sum_generator(account_no_nochecksum)

    if check_sum_gen == check_sum:
        return 'equal'
    else:
        return False


def round_up(n, decimals=0):
    multiplier = 10 ** decimals
    return math.ceil(n * multiplier) / multiplier


u_input = 1

# 'card.s3db' not in current directory then create file
if not os.path.isfile('/Users/fraserkearsey/PycharmProjects/Simple Banking System/Simple Banking System/task/card.s3db'):
    # Create Table/File
    conn = sqlite3.connect('/Users/fraserkearsey/PycharmProjects/Simple Banking System/Simple Banking System/task/card.s3db')
    cur = conn.cursor()
    cur.execute('CREATE TABLE card (id INTEGER, number TEXT, pin TEXT, balance INTEGER DEFAULT 0);')
    conn.commit()
else:
    conn = sqlite3.connect('/Users/fraserkearsey/PycharmProjects/Simple Banking System/Simple Banking System/task/card.s3db')
    cur = conn.cursor()

cur.execute("""CREATE TABLE IF NOT EXISTS card
                   (id INTEGER PRIMARY KEY, number TEXT, pin TEXT, balance INTEGER DEFAULT 0)""")
conn.commit()

while u_input != 0:



    print('1. Create an account\n 2. Log into account\n 0. Exit')

    u_input = int(input())

    if u_input == 1:
        # Generate new account number
        acc_no = gen_acc_no()
        # create an instance of account class
        acc_no = Account(acc_no)

        Account_info = [acc_no.acc_number, acc_no.pin_]
        # Add a new record to 'cards' table to store new account information
        cur.execute('INSERT INTO card (number, pin) VALUES (?,?)', Account_info)
        conn.commit()

        print('Your card has been created')
        print('Your card number:')
        print(acc_no.acc_number)
        print('Your card PIN:')
        print(acc_no.pin_)

    elif u_input == 2:
        print('Enter your card number:')
        card_no = int(input())
        print('Enter your pin:')
        pin_no = input()

        if card_no in Account.accounts:
            if Account.accounts[card_no] == pin_no:
                print('You have successfully logged in!')

                u_input = 1

                while u_input != 5 and u_input != 0:
                    print('1. Balance\n 2. Add income\n 3. Do transfer \n 4. Close account \n 5. Log out\n 0. Exit')
                    u_input = int(input())
                    if u_input == 1:
                        # Get the balance from the database
                        print('Balance: ', cur.execute('SELECT balance FROM card WHERE number = ?', [card_no]))

                    if u_input == 2:
                        # Update account balance
                        income = int(input('Enter Income:'))
                        # Update database
                        info_update = [income, card_no]

                        cur.execute('UPDATE card SET balance = balance + ? WHERE number = ?', info_update)
                        conn.commit()

                        print('Income was added!')

                    if u_input == 3:
                        # Transfer
                        print('Transfer \nEnter card number:')
                        to_card = input()

                        cur.execute('SELECT number FROM card WHERE number = ?', [to_card])

                        if luhn_alg_check(to_card):
                            if cur.fetchone() is not None:
                                transfer_amount = int(input("enter how much you'd like to transfer"))
                                cur.execute('SELECT balance FROM card WHERE number = ?', [card_no])
                                balance = cur.fetchone()
                                if transfer_amount <= balance[0]:
                                    # update account balances
                                    transferee = [transfer_amount, card_no]
                                    cur.execute('UPDATE card SET balance = balance - ? WHERE number = ?', transferee)
                                    conn.commit()

                                    transfer_to = [transfer_amount, to_card]
                                    cur.execute('UPDATE card SET balance = balance + ? WHERE number = ?', transfer_to)
                                    conn.commit()
                                    print('Success!')
                                else:
                                    print('Not enough money!')
                            else:
                                print('Such a card does not exist.')
                        else:
                            print('Probably made a mistake in the card number. Please try again!')

                    if u_input == 4:
                        # Delete account
                        cur.execute('DELETE FROM card WHERE number = ?', [card_no])
                        conn.commit()

                        print('The account has been closed!')

            else:
                print('Wrong Pin')
        else:
            print('Wrong Acc No')

    elif u_input == 0:
        print('Bye!')
        break
