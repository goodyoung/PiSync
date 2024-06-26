from pathlib import Path
import os

IP = os.environ.get('SERVER_IP')
HOME_PATH = os.environ.get('SERVER_HOME')
USER = os.environ.get('REMOTE_SERVER_USER')
PORT_NUM = os.environ.get('REMOTE_SERVER_PORT')

HOME = Path().home()