import json, datetime, arrow
from domino.core import log
from domino.databases.postgres import Postgres
from sqlalchemy import Column, Integer, String, JSON, DateTime

#def on_activate(account_id, on_activate_log):
#    Postgres.Table(TestAccountTable).migrate(account_id, on_activate_log)

class TestAccount(Postgres.Base):
    __tablename__ = 'testaccount'
    
    id = Column(Integer, primary_key=True, nullable=False, autoincrement=True)
    account_id  = Column(String, nullable=False)
    user_id  = Column(String, nullable=False)
    account_name    = Column(String)
    info            = Column(JSON)

TestAccountTable = TestAccount.__table__
Postgres.Table(TestAccountTable)