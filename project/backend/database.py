import sqlite3
import datetime
import os
import pandas as pd

BASE_DIR = os.getcwd()
DB_DATA = os.path.join(BASE_DIR,'data.db')
DB_HISTORY = os.path.join(BASE_DIR,'history.db')

def create_table():
 conn = sqlite3.connect(DB_DATA)
 curs = conn.cursor()


 curs.execute("""
   create table if not exists data(
      id integer primary key,
      file text,
      pages integer,
      uploaded_time text
      ) """)
 conn.commit()

 conn_h = sqlite3.connect(DB_HISTORY)
 curs_h = conn_h.cursor()

 curs_h.execute("""
     create table if not exists chat_history(
         id integer primary key,
         query text,
         answer text) """)
 conn_h.commit()

def insert_pdf(file_name: str, pages: int):
    with sqlite3.connect(DB_DATA) as conn:

      curs = conn.cursor()
      uploaded_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
      curs.execute("insert into data (file,pages,uploaded_time) values (?,?,?)",
                (file_name,pages,uploaded_time))
      conn.commit()

def insert_chat(query,answer):

  with sqlite3.connect(DB_HISTORY) as con:
    cur = con.cursor()
  
    cur.execute("insert into chat_history (query,answer) values (?,?)",
                  (query,answer))
    con.commit()

def get_chat_history():
   with sqlite3.connect(DB_HISTORY) as con:
     
      df = pd.read_sql_query("select * from chat_history",con)
      return df

def delete_pdf(file_name):

   with sqlite3.connect(DB_DATA) as conn:
      curs = conn.cursor()
     
      curs.execute("delete from data where file = ?",(file_name,))
      return "The data is deleted"

def show_files():
         conn = sqlite3.connect(DB_DATA)
         curs = conn.cursor()
         curs.execute("select * from data")
         rows = curs.fetchall()
         return rows

if __name__ == "__main__":
   show_files()