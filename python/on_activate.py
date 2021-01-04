import os, sys
from domino.core import log
from domino.databases.postgres import Postgres

import tables.postgres.user_profile
import tables.postgres.test_account
import tables.postgres.module

def on_activate_log(msg):
    print(msg)

if __name__ == "__main__":
    account_id = sys.argv[1]

    Postgres.on_activate(account_id, on_activate_log)
    #Postgres.create_database(account_id, on_activate_log)

    tables.postgres.user_profile.on_activate(account_id, on_activate_log)
    #tables.postgres.test_account.on_activate(account_id, on_activate_log)
    tables.postgres.module.on_activate(account_id, on_activate_log)


