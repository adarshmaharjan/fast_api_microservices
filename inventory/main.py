from fastapi import FastAPI
from redis_om import get_redis_connection, HashModel
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

redis = get_redis_connection(
    host="redis-17699.c54.ap-northeast-1-2.ec2.redns.redis-cloud.com",
    port=17699,
    password="kkPkS1zgYMIp9DMRPq8uq3z4fQC0GYCT",
    decode_responses=True,
)


class Product(HashModel):
    name: str
    price: float
    quantity: int

    class Meta:
        database = redis


@app.get("/products")
def all():
    return [format(pk) for pk in Product.all_pks()]


def format(primaryKey: str):
    product: Product = Product.get(primaryKey)
    return {"id": product.pk, "name": product.name, "quantity": product.quantity}


@app.post("/products")
def create(product: Product):
    return Product.save(product)


@app.get("/products/{pk}")
def get(pk):
    return Product.get(pk)


@app.delete("/products/{pk}")
def delete(pk: str):
    return Product.delete(pk)
