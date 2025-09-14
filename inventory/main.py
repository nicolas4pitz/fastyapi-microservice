

from fastapi import FastAPI  # Framework para criação de APIs web rápidas e modernas
from fastapi.middleware.cors import CORSMiddleware  # Middleware para habilitar CORS (Cross-Origin Resource Sharing)
from redis_om import get_redis_connection, HashModel  # ORM para Redis, facilita operações CRUD usando modelos Python

app = FastAPI()  # Instancia a aplicação FastAPI

app.add_middleware(
  CORSMiddleware,  # Adiciona o middleware CORS para permitir requisições do frontend
  allow_origins=['http://localhost:3000'],  # Permite requisições vindas do frontend local
  allow_methods=['*'],
  allow_headers=['*']
)

redis = get_redis_connection(
  host="closed",
  port = 0,
  password = "closed",
  decode_responses=True
)  # Cria conexão com o banco Redis

class Product(HashModel):
  """
  Modelo de produto, salvo como hash no Redis usando redis_om.HashModel.
  Permite operações CRUD automáticas no Redis.
  """
  name: str      # Nome do produto
  price: float   # Preço do produto
  quantity: int  # Quantidade disponível
  
  class Meta:
    database = redis  # Define qual conexão Redis será usada para esse modelo

@app.get("/products")
def all():
  """
  Endpoint GET para listar todos os produtos.
  Retorna uma lista formatada de todos os produtos salvos no Redis.
  """
  return [format(pk) for pk in Product.all_pks()]

def format(pk: str):
  """
  Função auxiliar para formatar os dados de um produto recuperado do Redis.
  """
  product = Product.get(pk)

  return{
    "id": product.pk,
    "name": product.name,
    "price": product.price,
    "quantity": product.quantity
  }

@app.post('/products')
def create(product: Product):
  """
  Endpoint POST para criar um novo produto.
  Recebe os dados do produto e salva no Redis.
  """
  return product.save()

@app.get('/products/{pk}')
def get(pk: str):
  """
  Endpoint GET para buscar um produto pelo ID (pk).
  Utiliza o método get do HashModel para recuperar o produto do Redis.
  """
  return Product.get(pk)

@app.delete('/products/{pk}')
def delete(pk: str):
  """
  Endpoint DELETE para remover um produto pelo ID (pk).
  Utiliza o método delete do HashModel para excluir o produto do Redis.
  """
  return Product.delete(pk)