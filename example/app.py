from arango import ArangoClient
from random import randint
from flask import Flask, request
import logging

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

client = ArangoClient()
db = client.db("test", username="root", password="password")

@app.route("/random_doc")
def random_doc():
    item_id = str(randint(1, 1000))
    doc = db.aql.execute("FOR doc IN test FILTER doc._key == @item_id RETURN doc", bind_vars={"item_id": item_id})

    try:
        result = doc.pop()
        return {"doc": result}, 200
    except Exception as e:
        return {"error": str(item_id) + " not found"}, 404
