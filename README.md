# app-statcast

## Installation
```
$ poetry install
```

## Run It
```
$ uvicorn app_statcast.main:app --reload
```

## Run Tests
```
$ pytest --cov
```

## Update requirements.txt
```
$ poetry export -f requirements.txt > requirements.txt
```