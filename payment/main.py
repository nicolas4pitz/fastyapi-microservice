import time  # Biblioteca padrão para manipulação de tempo (usado para simular delays)
from fastapi import FastAPI  # Framework para criação de APIs web rápidas e modernas
from fastapi.middleware.cors import CORSMiddleware  # Middleware para habilitar CORS (Cross-Origin Resource Sharing)
from redis_om import get_redis_connection, HashModel  # ORM para Redis, facilita operações CRUD usando modelos Python
from starlette.requests import Request  # Classe para acessar dados da requisição HTTP
import requests  # Biblioteca para fazer requisições HTTP para outros serviços/microserviços

from fastapi.background import BackgroundTasks  # Permite executar tarefas em segundo plano após a resposta da API



app = FastAPI()  # Instancia a aplicação FastAPI

app.add_middleware(
  CORSMiddleware,  # Adiciona o middleware CORS para permitir requisições do frontend
  allow_origins=['http://localhost:3000'],  # Permite requisições vindas do frontend local
  allow_methods=['*'],
  allow_headers=['*']
)

# Conexão com o banco Redis (deveria ser um banco diferente para cada microserviço)
redis = get_redis_connection(
  host="redis-10788.c308.sa-east-1-1.ec2.redns.redis-cloud.com",
  port = 10788,
  password = "RY9rjhlFDkqAAP5QdAOghOJfGuOGIv5w",
  decode_responses=True
)

class Order(HashModel):
  """
  Modelo de pedido, salvo como hash no Redis usando redis_om.HashModel.
  Permite operações CRUD automáticas no Redis.
  """
  product_id: str  # ID do produto comprado
  price: float     # Preço do produto
  fee: float       # Taxa cobrada
  total:float      # Valor total (preço + taxa)
  quantity: int    # Quantidade comprada
  status: str      # Status do pedido (pending, completed, refunded)

  class Meta:
    database = redis  # Define qual conexão Redis será usada para esse modelo


@app.get('/orders/{pk}')
def get(pk: str):
  """
  Endpoint GET para buscar um pedido pelo ID (pk).
  Utiliza o método get do HashModel para recuperar o pedido do Redis.
  """
  return Order.get(pk)

@app.post('/orders')
async def create(request: Request, background_tasks: BackgroundTasks):
  """
  Endpoint POST para criar um novo pedido.
  Recebe dados via JSON, busca informações do produto em outro microserviço,
  cria o pedido e salva no Redis. Inicia uma tarefa em background para completar o pedido.
  """
  body = await request.json()  # Recebe o corpo da requisição como JSON

  # Busca informações do produto no microserviço de inventário
  req = requests.get('http://localhost:8000/products/%s' % body['id'])
  product = req.json()

  # Cria o pedido usando os dados recebidos e os dados do produto
  order = Order(
    product_id=body['id'],
    price=product['price'],
    fee=0.2 * product['price'],
    total=1.2 * product['price'],
    quantity=body['quantity'],
    status='pending'
  )
  order.save()  # Salva o pedido no Redis

  # Adiciona uma tarefa em background para simular processamento do pedido
  background_tasks.add_task(order_completed, order)
  
  return order


def order_completed(order: Order):
  """
  Função executada em background para simular o processamento do pedido.
  Após 5 segundos, atualiza o status do pedido para 'completed' e salva no Redis.
  """
  time.sleep(5)
  order.status = 'completed'
  order.save()
  redis.xadd('order_completed', order.dict(), '*')