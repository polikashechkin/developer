import json, datetime, arrow
from domino.core import log
from domino.postgres import Postgres
from sqlalchemy import Column, Integer, String, JSON, DateTime, insert, update

def on_activate(account_id, on_activate_log):
    Postgres.Table(ModuleTable).migrate(account_id, on_activate_log)

class Module(Postgres.Base):

    __tablename__ = 'module'

    id              = Column(String, primary_key=True, nullable=False)
    version         = Column(String, nullable=False)
    name            = Column(String)

    def __pepr__(self):
        return f'<Module(id={self.id}, version={self.version}, name={self.name})>'
    
ModuleTable = Module.__table__