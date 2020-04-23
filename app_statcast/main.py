import azure.cosmos.cosmos_client as cosmos_client
from fastapi import FastAPI, Query, Response, status
import pandas as pd
import os
from typing import List


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
            p.id = '{pitch_id}' AND IS_NULL(p.pitch_type) = false AND p.pitch_type != "FO" AND IS_NULL(p.type) = false
        """

    pitches = list(
        client.QueryItems(
            "dbs/Statcast/colls/RawPitches", query, {"enableCrossPartitionQuery": True},
        )
    )

    return pitches_json(items)


@app.get("/pitches/")
def read_pitches(
    response: Response,
    game_year: int = Query([2019]),
    game_type: str = Query(["R"]),
    batter: List[int] = Query(None),
    pitcher: List[int] = Query(None),
):
    if not batter and not pitcher:
        response.status_code = status.HTTP_400_BAD_REQUEST
        return

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
            IS_NULL(p.pitch_type) = false AND
            p.pitch_type != "FO" AND
            IS_NULL(p.type) = false AND
            p.game_year IN ({','.join(map(str, game_year))}) AND
            p.game_type IN ({','.join([f"'{g}'" for g in game_type])})
        """

    if batter:
        query += f"AND p.batter IN ({','.join(map(str, batter))})"

    if pitcher:
        query += f"AND p.pitcher IN ({','.join(map(str, pitcher))})"

    pitches = list(
        client.QueryItems(
            "dbs/Statcast/colls/RawPitches", query, {"enableCrossPartitionQuery": True},
        )
    )

    return pitches_json(items)


def pitches_json(pitches):
    df = pd.DataFrame(pitches)

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
