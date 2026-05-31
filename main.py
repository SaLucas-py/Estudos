from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import models
from database import engine, get_db
from pydantic import BaseModel


models.Base.metadata.create_all(bind=engine) # Cria as tabelas no banco de dados, se ainda não existirem

app = FastAPI() # Cria uma instância do FastAPI para definir as rotas e a lógica da API

@app.get("/") # Define uma rota GET para a raiz da API, que retorna uma mensagem de teste para verificar se a API está funcionando
def hello(): # Define a função que será executada quando a rota GET for acessada, retornando um dicionário com uma mensagem de teste
    return {"mensagem": "API funcionando"} # Retorna um dicionário com a chave "mensagem" e o valor "API funcionando" para indicar que a API está operando corretamente

@app.get("/tarefas") # Define uma rota GET para "/tarefas", que será usada para listar as tarefas
def listar(db: Session = Depends(get_db)): # Define a função que será executada quando a rota GET for acessada, recebendo uma sessão do banco de dados como dependência
    tarefas = db.query(models.Tarefa).all() # Consulta todas as tarefas no banco de dados usando a sessão e o modelo Tarefa
    if tarefas is None:
        raise HTTPException(status_code=404, detail="Nenhuma tarefa encontrada") # Se nenhuma tarefa for encontrada no banco de dados, levanta uma exceção HTTP 404 com uma mensagem indicando que nenhuma tarefa foi encontrada
    return tarefas # Retorna a lista de tarefas obtida do banco de dados para o cliente que fez a requisição GET para "/tarefas"

@app.get("/tarefas/{id}") # Define uma rota GET para "/tarefas/{id}", que será usada para obter uma tarefa específica com base no ID fornecido
def buscar(id: int, db: Session = Depends(get_db)): 
    tarefas = db.query(models.Tarefa).filter(models.Tarefa.id == id).first() # Consulta a tarefa com o ID fornecido no banco de dados usando a sessão e o modelo Tarefa
    if tarefas is None:
        raise HTTPException(status_code=404, detail="Tarefa não encontrada") # Se a tarefa com o ID fornecido não for encontrada no banco de dados, levanta uma exceção HTTP 404 com uma mensagem indicando que a tarefa não foi encontrada
    return tarefas # Retorna a tarefa encontrada para o cliente que fez a requisição GET para "/tarefas/{id}"
    

class TarefaSchema(BaseModel):
    titulo: str
    concluida: bool = False

@app.post("/tarefas") # Define uma rota POST para "/tarefas", que será usada para criar novas tarefas
def criar(tarefa: TarefaSchema, db: Session = Depends(get_db)): # Define a função que será executada quando a rota POST for acessada, recebendo um objeto TarefaSchema e uma sessão do banco de dados como dependência
    nova = models.Tarefa(titulo=tarefa.titulo, concluida=tarefa.concluida) # Cria uma nova instância do modelo Tarefa usando os dados fornecidos no objeto TarefaSchema
    db.add(nova) # Adiciona a nova tarefa à sessão do banco de dados
    db.commit() # Salva as alterações no banco de dados, persistindo a nova tarefa
    db.refresh(nova) # Atualiza a instância da nova tarefa com os dados do banco de dados, incluindo o ID gerado automaticamente
    return nova # Retorna a nova tarefa criada para o cliente que fez a requisição POST para "/tarefas"

@app.delete("/tarefas/{id}") # Define uma rota DELETE para "/tarefas/{id}", que será usada para excluir tarefas com base no ID fornecido
def excluir(id: int, db: Session = Depends(get_db)): # Define a função que será executada quando a rota DELETE for acessada, recebendo o ID da tarefa a ser excluída e uma sessão do banco de dados como dependência
    tarefas = db.query(models.Tarefa).filter(models.Tarefa.id == id).first()
    if tarefas is None:
        raise HTTPException(status_code=404, detail="Tarefa não encontrada") # Se a tarefa com o ID fornecido não for encontrada no banco de dados, levanta uma exceção HTTP 404 com uma mensagem indicando que a tarefa não foi encontrada
    db.delete(tarefas) # Exclui a tarefa encontrada da sessão do banco de dados
    db.commit() # Salva as alterações no banco de dados, removendo a tarefa
    return {"mensagem": "Tarefa excluída com sucesso"} # Retorna uma mensagem indicando que a tarefa foi excluída com sucesso do banco de dados

@app.put("/tarefas/{id}") # Define uma rota PUT para "/tarefas/{id}", que será usada para atualizar tarefas com base no ID fornecido
def atualizar(id: int, tarefa: TarefaSchema, db: Session = Depends(get_db)):
    tarefas = db.query(models.Tarefa).filter(models.Tarefa.id == id).first() # Cria uma nova instância do modelo Tarefa usando os dados fornecidos no objeto TarefaSchema
    if tarefas is None:
        raise HTTPException(status_code=404, detail="Tarefa não encontrada") # Se a tarefa com o ID fornecido não for encontrada no banco de dados, levanta uma exceção HTTP 404 com uma mensagem indicando que a tarefa não foi encontrada
    tarefas.titulo = tarefa.titulo # Atualiza o título da tarefa encontrada com o novo título fornecido no objeto TarefaSchema
    tarefas.concluida = tarefa.concluida # Atualiza o status de conclusão
    db.commit() # Salva as alterações no banco de dados, persistindo a nova tarefa
    db.refresh(tarefas) # Atualiza a instância da nova tarefa com os dados do banco de dados, incluindo o ID gerado automaticamente
    return tarefas # Retorna a nova tarefa criada para o cliente que fez a requisição PUT