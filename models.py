from database import Base
from sqlalchemy import Column, Integer, String, Boolean

class Tarefa(Base):
    __tablename__ = "tarefas"

    id = Column(Integer, primary_key=True, index=True)
    titulo = Column(String)
    concluida = Column(Boolean, default=False)