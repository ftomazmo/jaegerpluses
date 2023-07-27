from flask import Flask
from tracer import initialize_tracer
from metric import initialize_metric

app = Flask(__name__)
initialize_tracer(app)
#initialize_metric()

@app.route("/")
def hello():
    return "Hello!"

@app.route("/blab")
def blab():
    return "Blab! =P"

if __name__ == "__main__":
    app.run(debug=True)
