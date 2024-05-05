from flask import Flask
from sqlalchemy import create_engine, text

app = Flask(__name__)

from app import config

engine = create_engine(f"mysql+pymysql://{config.DBUSER}:{config.DBPASSWORD}@{config.HOST}:{config.PORT}/{config.DATABASE}")
conn = engine.connect()

try:
    if conn.execute(text(f"SELECT status FROM progress WHERE phase = 6")).fetchall()[0][0] == 0:
        print("Database has not been properly filled with data. Try running data_mining.py")
        exit()
except Exception as e:
    print("There is something wrong with you database: ", e)
    exit()

from app import routes