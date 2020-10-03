# app-statcast

A REST API for Statcast data.

This project contains an API for Statcast data. You can check out the docs and try calling the API at the [docs](https://app-statcast.azurewebsites.net/docs). For example, call https://app-statcast.azurewebsites.net/pitchbypitch/?batter=545361 to get data for all pitches thrown to Mike Trout during the 2020 season.

In production, the API uses an Azure MySQL database with data from Baseball Savant. This database is updated daily with [func-statcast](https://github.com/isaacrlee/func-statcast)

## Features
This API allows users to query Statcast pitch by pitch data. You can filter on `game_year`, `game_type`, batter_id, and/or pitcher_id. Information about those parameters can be found at at the [docs](https://app-statcast.azurewebsites.net/docs) and [Baseball Savant](https://baseballsavant.mlb.com/csv-docs). You can find Batter and Pitcher IDs by looking in the URL at player pages in Baseball Savant. For example, the URL for Marco Gonzales' page is https://baseballsavant.mlb.com/savant-player/marco-gonzales-594835?stats=statcast-r-pitching-mlb, and hit ID is 594835.

For example, call https://app-statcast.azurewebsites.net/pitchbypitch/?batter=545361&pitcher=594835 to get data for all the pitches Marco Gonzales threw to Mike Trout during 2020 season.

## Getting Started
These instructions will get you a copy of the project up and running on your local machine for development and testing purposes.

### Installing Requirements
First, clone the repository.

```
$ git clone https://github.com/isaacrlee/app-statcast.git
```

Next, install [poetry](https://python-poetry.org/docs/) and install the requirements.

```
$ poetry install
```

## Setting up MySQL Database
Set up a MySQL database and populate it with data from [Baseball Savant](https://baseballsavant.mlb.com/statcast_search).

Set the `MYSQL_STATCAST` environment variable with the connection string of the MySQL database.

```
$ export MYSQL_STATCAST="mysql+pymysql://<user>:<password>@<host>[:<port>]/<dbname>"
```

## Run the API locally

Start a server with `uvicorn`
```
$ uvicorn app_statcast.main:app --reload
```

## Run Tests
Using `pytest, run unit tests that check that the API is functioning.
```
$ pytest --cov
```

## Update requirements.txt
When you add dependencies with poetry, you have to make sure to update the `requirements.txt` file because that it used by Azure to install dependencies before deploying the API to production.
```
$ poetry export -f requirements.txt > requirements.txt
```