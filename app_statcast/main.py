from fastapi import FastAPI, Query, Response, status
import pandas as pd
import pymysql
import os
from sqlalchemy import create_engine
from typing import List


app = FastAPI()

engine = create_engine(os.environ["MYSQL_STATCAST"], pool_pre_ping=True,)


@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: str = None):
    return {"item_id": item_id, "q": q}


@app.get("/pitchbypitch/{pitch_id}")
def read_pitch(pitch_id: str):
    query = f"""
        SELECT
            p.sv_id,
            p.pitch_type,
            p.game_date,
            p.batter,
            p.pitcher,
            p.stand,
            p.p_throws,
            p.plate_x,
            p.plate_z,
            p.type
        FROM pitchbypitch as p
        WHERE
            ISNULL(p.pitch_type) = false AND
            p.pitch_type != "FO" AND
            ISNULL(p.type) = false AND
            p.sv_id = '{pitch_id}'
        """

    return pitches_json(pd.read_sql(query, engine))


@app.get("/pitchbypitch/")
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
            p.sv_id,
            p.pitch_type,
            p.game_date,
            p.batter,
            p.pitcher,
            p.stand,
            p.p_throws,
            p.plate_x,
            p.plate_z,
            p.type
        FROM pitchbypitch as p
        WHERE
            ISNULL(p.pitch_type) = false AND
            p.pitch_type != "FO" AND
            ISNULL(p.type) = false AND
            p.game_year IN ({','.join(map(str, game_year))}) AND
            p.game_type IN ({','.join([f"'{g}'" for g in game_type])})
        """

    if batter:
        query += f"AND p.batter IN ({','.join(map(str, batter))})"

    if pitcher:
        query += f"AND p.pitcher IN ({','.join(map(str, pitcher))})"

    return pitches_json(pd.read_sql(query, engine))


def pitches_json(df):
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
