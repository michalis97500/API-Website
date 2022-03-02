import website
import sys

path = '/home/michalis95/API-updater'
if path not in sys.path:
    sys.path.append(path)

application = website.create_app()
application.run()

