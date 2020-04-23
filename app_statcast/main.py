import azure.cosmos.cosmos_client as cosmos_client
from fastapi import FastAPI
import pandas as pd
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
def read_pitch(pitch_id: str):
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
            p.id = '{pitch_id}'
        """

    items = list(
        client.QueryItems(
            "dbs/Statcast/colls/RawPitches", query, {"enableCrossPartitionQuery": True},
        )
    )

    df = pd.DataFrame(items)

    df.loc[df.pitch_type == "SI", "pitch_type"] = "FT"
    df.loc[df.pitch_type == "KC", "pitch_type"] = "CU"
    df.loc[df.pitch_type == "FS", "pitch_type"] = "CH"

    df["swing"] = df.apply(
        lambda row: int(row.type in ["D", "E", "F", "L", "M", "O", "S", "T", "W", "X"]),
        axis=1,
    ).astype(bool)

    df["miss"] = df.apply(
        lambda row: int(row.type in ["O", "S", "T", "W"]), axis=1
    ).astype(bool)

    return df.to_json(orient="records")
