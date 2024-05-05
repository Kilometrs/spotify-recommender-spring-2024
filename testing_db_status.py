from app import config
from sqlalchemy import create_engine, text

conn = None

try:
    print("Starting db connection")
    db_path = f'mysql+pymysql://{config.DBUSER}:{config.DBPASSWORD}@{config.HOST}/{config.DATABASE}'
    engine = create_engine(db_path)
    conn = engine.connect()
    print("### Connection to database established")
except Exception as e:
    print(e)
    print("could not establish connection to db, shutting down...")
    exit()

trans = conn.begin()
phase = 3
statusList = conn.execute(text(f"SELECT status FROM progress WHERE phase = {phase}")).fetchall()[0][0]
print(statusList)
conn.execute(text(f"UPDATE progress SET status = 1 WHERE phase = {phase} "))
statusList = conn.execute(text(f"SELECT status FROM progress WHERE phase = {phase}")).fetchall()[0][0]
print(statusList)
trans.commit()


# if conn is not None:
#     query = text(f"SELECT * FROM progress")
#     try:
#         result = conn.execute(query)
#         for row in result:
#             print("Phase: ",row[0], "Status: ", row[1])
#     except Exception as e:
#         print(f"Failed to execute query: {e}")
# else:
#     print("Connection is not established. Cannot execute the query.")


# if conn is not None:
#     query = text(f"SELECT status FROM progress")
#     try:
#         result = conn.execute(query)
#         rows = result.fetchall()
#         print(rows)
#         print(rows[1][0])
#         for row in result:
#             print("Status: ",row)
#     except Exception as e:
#         print(f"Failed to execute query: {e}")
# else:
#     print("Connection is not established. Cannot execute the query.")