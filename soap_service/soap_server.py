import os
import psycopg2
from datetime import date
from fastapi import FastAPI, Request, Response
from fastapi.responses import PlainTextResponse
from starlette.middleware.cors import CORSMiddleware
from lxml import etree

app = FastAPI()

# CORS (opcjonalnie)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Konfiguracja połączenia (ze zmiennych środowiskowych lub domyślnie)
DB_CONFIG = {
    "dbname": os.getenv("POSTGRES_DB", "socialdb"),
    "user": os.getenv("POSTGRES_USER", "user"),
    "password": os.getenv("POSTGRES_PASSWORD", "pass"),
    "host": os.getenv("POSTGRES_HOST", "localhost"),
    "port": os.getenv("POSTGRES_PORT", "5432"),
}

def fetch_unemployment_avg(year: int, month: int) -> str:
    """
    Pobiera średnią stopę bezrobocia dla danego roku/miesiąca (wszystkie regiony).
    Zwraca '-1' jeśli brak danych.
    """
    conn = psycopg2.connect(**DB_CONFIG)
    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT AVG(rate)
              FROM public.unemployment
             WHERE date = %s
        """, (date(year, month, 1),))
        row = cur.fetchone()
        return str(round(row[0], 2)) if row and row[0] is not None else "-1"
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
        rate = fetch_unemployment_avg(year, month)
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
    # zwraca plik WSDL
    wsdl_path = os.path.join(os.path.dirname(__file__), "unemployment.wsdl")
    with open(wsdl_path, "r", encoding="utf-8") as f:
        return PlainTextResponse(f.read(), media_type="text/xml")
