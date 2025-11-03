import time

import requests
from fastapi import FastAPI
from fastapi.background import BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from redis_om import HashModel, get_redis_connection
from starlette.requests import Request

"""
  Should be different database
"""
redis = get_redis_connection(
    host="redis-17699.c54.ap-northeast-1-2.ec2.redns.redis-cloud.com",
    port=17699,
    password="kkPkS1zgYMIp9DMRPq8uq3z4fQC0GYCT",
    decode_responses=True,
)

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)


class Order(HashModel):
    product_id: str
    price: float
    fee: float
    total: float
    quantity: int
    status: str

    class Meta:
        database = redis


@app.get("/orders/{pk}")
def get(pk: str):
    return Order.get(pk)


@app.post("/orders")
async def create(request: Request, background_tasks:BackgroundTasks):
    body = await request.json()

    req = requests.get(f"http://localhost:8000/products/{body['id']}")
    product = req.json()

    print(product)

    order = Order(
        product_id=body["id"],
        price=product["price"],
        fee=0.2 * product["price"],
        total=1.2 * product["price"],
        quantity=body["quantity"],
        status="pending",
    )

    order.save()
    background_tasks.add_task(order_completed, order)
    return order


def order_completed(order: Order):
    time.sleep(5)
    order.status = "completed"
    order.save()
    redis.xadd("order_completed", order.dict(), "*")
