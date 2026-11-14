import json
import os
from pathlib import Path
from threading import Lock

from fastapi import FastAPI
from pydantic import BaseModel, Field

app = FastAPI(title="Notes API")

data_dir = Path(os.getenv("DATA_DIR", "data"))
data_dir.mkdir(parents=True, exist_ok=True)
notes_file = data_dir / "notes.jsonl"
file_lock = Lock()


class Note(BaseModel):
    text: str = Field(min_length=1, max_length=1000)


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/notes")
def get_notes():
    with file_lock:
        if not notes_file.exists():
            return []

        with notes_file.open(encoding="utf-8") as file:
            return [json.loads(line) for line in file if line.strip()]


@app.post("/notes", status_code=201)
def add_note(note: Note):
    with file_lock:
        with notes_file.open("a", encoding="utf-8") as file:
            file.write(json.dumps({"text": note.text}, ensure_ascii=False) + "\n")

    return note