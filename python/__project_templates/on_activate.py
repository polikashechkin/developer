import os, sys, sqlite3
from domino.core import log, Version
from domino.account import Account, find_account
from domino.postgres import Postgres

if __name__ == "__main__":
    account = find_account(sys.argv[1])
    print(account.id)
    if account is None:
        error = f'Не найдена учетная запись'
        print(error)
        log.error(error)
        sys.exit(1)

    Postgres.create_database(account.id, print)

