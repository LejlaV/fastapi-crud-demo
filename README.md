# FastAPI CRUD Demo

Simple CRUD API built with FastAPI and SQLite.

## Features
- Create, read, update, delete tasks
- SQLite persistence
- Typed request & response models
- Server-generated timestamps
- Automatic Swagger documentation

## Tech Stack
- Python
- FastAPI
- SQLite

## Setup

python3 -m venv venv  
source venv/bin/activate  
pip install -r requirements.txt  
uvicorn main:app --reload  

Open:
http://127.0.0.1:8000/docs