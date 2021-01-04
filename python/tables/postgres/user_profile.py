import json, datetime, arrow
from domino.core import log
from domino.postgres import Postgres
from sqlalchemy import Column, Integer, String, DateTime, insert, update, BigInteger, Index, Boolean
from sqlalchemy.dialects.postgresql import JSONB

def on_activate(account_id, on_activate_log):
    Postgres.Table(UserProfileTable).migrate(account_id, on_activate_log)

class UserProfile(Postgres.Base):

    __tablename__ = 'user_profile'

    id              = Column(BigInteger, autoincrement=True, primary_key=True, nullable=False)
    ctime           = Column(DateTime, nullable=False)
    user_id         = Column(String, nullable=False)
    module_id       = Column(String)
    info            = Column(JSONB)
    favourite       = Column(Boolean)
    
    Index('', user_id, ctime)

    def __pepr__(self):
        return f'<UserProfile(id={self.id}, user_id={self.user_id}, module_id={self.module_id}), info={self.info}>'

UserProfileTable = UserProfile.__table__