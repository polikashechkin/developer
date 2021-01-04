import os, sys
from domino.core import log
from domino.account import Account, find_account
from domino.databases.postgres import Postgres

def on_activate_log(msg):
    print(msg)

if __name__ == "__main__":
    account = find_account(sys.argv[1])
    if account is None:
        error = f'Не найдена учетная запись'
        print(error)
        log.error(error)
        sys.exit(1)

    Postgres.on_activate(account.id, on_activate_log)

