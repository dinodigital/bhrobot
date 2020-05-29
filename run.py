from pyrogram import Client
from jobs.sheduler import scheduler
import peeweedbevolve
from models import db

# Bot init
app = Client("BithumbBot")

# App launch
if __name__ == "__main__":
    # scheduler.start()
    db.evolve(interactive=False, ignore_tables=['basemodel'])
    app.run()
