# app-statcast

## Installation
```
$ poetry install
```

## Run It
```
$ uvicorn app_statcast.main:app --reload
```

## Check It
Open your browser at http://127.0.0.1:8000/items/5?q=somequery.

You will see the JSON response as:
```
{"item_id": 5, "q": "somequery"}
```

Update requirements.txt
```
$ poetry export -f requirements.txt > requirements.txt
```