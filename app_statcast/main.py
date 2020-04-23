import azure.cosmos.cosmos_client as cosmos_client
from fastapi import FastAPI
import os


app = FastAPI()

client = cosmos_client.CosmosClient(
    os.environ["COSMOS_URI"], {"masterKey": os.environ["COSMOS_KEY"]},
)
container = client.ReadContainer("dbs/Statcast/colls/RawPitches")


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: str = None):
    return {"item_id": item_id, "q": q}


@app.get("/pitches/{pitch_id}")
def read_pitch(pitch_id: int):
    query = f"""
        SELECT
            p.id,
            p.pitch_type,
            p.game_date,
            p.batter,
            p.pitcher,
            p.stand,
            p.p_throws,
            p.plate_x,
            p.plate_z,
            p.type
        FROM RawPitches as p
        WHERE
            p.id = {pitch_id}
        """

    items = list(
        client.QueryItems(
            "dbs/Statcast/colls/RawPitches", query, {"enableCrossPartitionQuery": True},
        )
    )

    return items
