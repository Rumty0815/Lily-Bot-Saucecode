from flask import Flask
from threading import Thread

app = Flask("")

@app.route("/")
def main():
  return "Bot is alive!"

def run():
  app.run("0.0.0.0", port=8080)

def keep_alive():
  t = Thread(target=run)
  t.start()
