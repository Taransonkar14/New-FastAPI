from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
import pyodbc
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv("pass.env")

app = FastAPI(title="SQL Server Data Fetch API")

# ✅ CORS enable
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  #call 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DB_SERVER = os.getenv("DB_SERVER")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

conn_str = (
    "DRIVER={ODBC Driver 17 for SQL Server};"
    f"SERVER={DB_SERVER};"
    f"DATABASE={DB_NAME};"
    f"UID={DB_USER};"
    f"PWD={DB_PASSWORD}"
)

@app.get("/")
def root():
    return {"message": "Welcome! Use /fetch_data to get SQL Server data."}

@app.get("/fetch_data")
def fetch_data():
    conn = None
    try:
        conn = pyodbc.connect(conn_str)
        query = """
        SELECT lg.DocId, lg.V_No, lg.V_Type, lg.V_Prefix, lg.V_Date, 
               lg.SubCode, lg.Site_Code, lg.AmtDr
        FROM dbo.Ledger lg
        LEFT JOIN dbo.voucher_type vt ON lg.V_Type = vt.V_Type
        WHERE vt.V_Type IN ('PMT') AND lg.AmtDr > 0
        """
        df = pd.read_sql(query, conn)
        data = df.to_dict(orient="records")
        return {"status": "success", "row_count": len(data), "data": data}
    except Exception as e:
        return {"status": "error", "message": str(e)}
    finally:
        if conn:
            conn.close()



