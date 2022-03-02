from website import create_app
from threading import Thread
import backend

app = create_app()


def run():
    app.run()


def runback():
    backend.mainloop()


def keep_alive():
    t = Thread(target=run)
    m = Thread(target=runback)
    t.start()
    m.start()


keep_alive()
