from website import create_app
from threading import Thread
import backend

app = create_app()


def run():
    app.run()


def runmain():
    backend.mainloop()
    
def runsecondary():
    backend.secondaryloop()


def keep_alive():
    t = Thread(target=run)
    m = Thread(target=runmain)
    s = Thread(target=runsecondary)
    s.start()
    t.start()
    m.start()


keep_alive()
