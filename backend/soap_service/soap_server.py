from fastapi import FastAPI, Request, Response
from fastapi.responses import PlainTextResponse
from starlette.middleware.cors import CORSMiddleware
from lxml import etree
import psycopg2
from datetime import date
import os

app = FastAPI()

# CORS (opcjonalnie)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Połączenie z bazą (dopasuj do swojego .env)
DB_CONFIG = {
    "dbname": os.getenv("POSTGRES_DB", "socialdb"),
    "user": os.getenv("POSTGRES_USER", "postgres"),
    "password": os.getenv("POSTGRES_PASSWORD", "postgres"),
    "host": os.getenv("POSTGRES_HOST", "localhost"),
    "port": os.getenv("POSTGRES_PORT", "5432"),
}

def fetch_unemployment(year, month):
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        cur = conn.cursor()
        cur.execute("""
            SELECT rate FROM unemployment
            WHERE date = %s
            ORDER BY imported_at DESC
            LIMIT 1
        """, (date(year, month, 1),))
        row = cur.fetchone()
        return str(row[0]) if row else "-1"
    finally:
        cur.close()
        conn.close()

@app.post("/ws/unemployment")
async def soap_endpoint(request: Request):
    body = await request.body()
    tree = etree.fromstring(body)

    try:
        year = int(tree.xpath("//*[local-name()='year']/text()")[0])
        month = int(tree.xpath("//*[local-name()='month']/text()")[0])
        rate = fetch_unemployment(year, month)
    except Exception:
        rate = "-1"

    response = f"""<?xml version="1.0" encoding="UTF-8"?>
<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
                  xmlns:ns="http://example.com/unemployment">
  <soapenv:Body>
    <ns:get_unemployment_rateResponse>
      <ns:rate>{rate}</ns:rate>
    </ns:get_unemployment_rateResponse>
  </soapenv:Body>
</soapenv:Envelope>"""

    return Response(content=response, media_type="text/xml")

@app.get("/ws/unemployment")
def wsdl():
    with open("soap_service/unemployment.wsdl", "r", encoding="utf-8") as f:
        return PlainTextResponse(f.read(), media_type="text/xml")
