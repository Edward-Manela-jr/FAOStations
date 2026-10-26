"""Standalone FAO Weather API.

Serves daily weather data (temperature min/max, rainfall, soil moisture 30 cm)
for the FAO station network by reading Campbell Scientific TOA5 .dat files.

Separate from the Kalumbila deployment.
"""

import csv
import io
import logging
import os
from datetime import datetime
from io import StringIO
from typing import List, Optional

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException, Path, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from stations import STATIONS, STATION_IDS, DEFAULT_STATION

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("fao_api")

load_dotenv()

DATA_SOURCE_PATH = os.getenv("DATA_SOURCE_PATH", r"C:\Campbellsci\LoggerNet")


class DailyRecord(BaseModel):
    timestamp: str
    station_id: str
    airtemp_min: Optional[float] = None
    airtemp_max: Optional[float] = None
    rainfall: Optional[float] = None
    soil_moisture_30cm: Optional[float] = None


class StationInfo(BaseModel):
    station_id: str
    filename: str


def _to_float(value: str) -> Optional[float]:
    if value is None:
        return None
    value = str(value).strip()
    if value == "" or value.lower() == "nan":
        return None
    try:
        return float(value)
    except (ValueError, TypeError):
        return None


def _parse_csv_line(line: str) -> List[str]:
    reader = csv.reader(StringIO(line))
    return next(reader)


def _parse_toa5(content: str) -> dict:
    lines = content.strip().split("\n")
    if len(lines) < 4:
        raise ValueError("Invalid TOA5 file - insufficient lines")

    header_info = _parse_csv_line(lines[0])
    field_names = _parse_csv_line(lines[1])
    units = _parse_csv_line(lines[2])
    processing = _parse_csv_line(lines[3])

    records = []
    for line in lines[4:]:
        if not line.strip():
            continue
        values = _parse_csv_line(line)
        if len(values) != len(field_names):
            continue
        records.append(dict(zip(field_names, values)))

    return {
        "header_info": header_info,
        "field_names": field_names,
        "units": units,
        "processing": processing,
        "records": records,
    }


def _read_file(filename: str) -> str:
    file_path = os.path.join(DATA_SOURCE_PATH, filename)
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    encodings = ["utf-8", "utf-16", "utf-16-le", "utf-16-be", "latin-1"]
    for encoding in encodings:
        try:
            with open(file_path, "r", encoding=encoding) as f:
                return f.read()
        except (UnicodeDecodeError, UnicodeError):
            continue

    with open(file_path, "rb") as f:
        raw = f.read()
    return raw.replace(b"\x00", b"").decode("utf-8", errors="replace")


def _find_field(field_names: List[str], candidates: List[str]) -> Optional[str]:
    """Find a field name matching any of the candidate substrings (case-insensitive)."""
    lower_fields = [(i, f.lower()) for i, f in enumerate(field_names)]
    for cand in candidates:
        cl = cand.lower()
        for i, f in lower_fields:
            if cl in f:
                return field_names[i]
    return None


SOIL_MOISTURE_CANDIDATES = [
    "vwc_30",
    "vwc30",
    "smc_30",
    "smc30",
    "sm_30",
    "sm30",
    "soil_moisture_30",
    "soil_moist_30",
    "moisture_30",
    "swc_30",
    "swc30",
    "theta_30",
    "theta30",
]


def _build_records(parsed: dict, station_id: str, soil_field: Optional[str] = None) -> List[DailyRecord]:
    field_names = parsed["field_names"]
    records = parsed["records"]

    # Determine soil moisture field
    soil_name = soil_field
    if not soil_name:
        soil_name = _find_field(field_names, SOIL_MOISTURE_CANDIDATES)

    out: List[DailyRecord] = []
    for row in records:
        out.append(
            DailyRecord(
                timestamp=row.get("TIMESTAMP", row.get("timestamp", "")),
                station_id=station_id,
                airtemp_min=_to_float(row.get("AirTemp_Min")),
                airtemp_max=_to_float(row.get("AirTemp_Max")),
                rainfall=_to_float(row.get("Rain_Tot")),
                soil_moisture_30cm=_to_float(row.get(soil_name)) if soil_name else None,
            )
        )
    return out


app = FastAPI(
    title="FAO Weather API",
    description="FAO weather station data API - Temperature Min/Max, Rainfall, Soil Moisture 30 cm",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {
        "status": "healthy",
        "service": "FAO Weather API",
        "version": "1.0.0",
        "endpoints": [
            "/api/stations",
            "/api/daily/{station_id}",
            "/api/temperature/{station_id}",
            "/api/rainfall/{station_id}",
            "/api/soil-moisture-30cm/{station_id}",
        ],
    }


@app.get("/api/stations", response_model=List[StationInfo])
def list_stations():
    return [
        StationInfo(station_id=sid, filename=STATIONS[sid]["daily"])
        for sid in STATION_IDS
    ]


@app.get("/api/daily/{station_id}", response_model=List[DailyRecord])
def get_daily(
    station_id: str = Path(..., description="Station ID"),
    start_date: Optional[str] = Query(None, description="Start date YYYY-MM-DD"),
    end_date: Optional[str] = Query(None, description="End date YYYY-MM-DD"),
    limit: int = Query(100, ge=1, le=10000, description="Max records"),
    soil_field: Optional[str] = Query(None, description="Soil moisture field name override"),
):
    if station_id not in STATIONS:
        raise HTTPException(status_code=404, detail=f"Unknown station: {station_id}")

    filename = STATIONS[station_id]["daily"]
    try:
        content = _read_file(filename)
    except FileNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))

    try:
        parsed = _parse_toa5(content)
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))

    records = _build_records(parsed, station_id, soil_field=soil_field)

    # Date filtering
    if start_date or end_date:
        filtered = []
        for r in records:
            ts = r.timestamp
            if start_date and ts < start_date:
                continue
            if end_date and ts > end_date:
                continue
            filtered.append(r)
        records = filtered

    return records[:limit]


@app.get("/api/temperature/{station_id}", response_model=List[DailyRecord])
def get_temperature(
    station_id: str = Path(..., description="Station ID"),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=10000),
):
    return get_daily(
        station_id=station_id,
        start_date=start_date,
        end_date=end_date,
        limit=limit,
    )


@app.get("/api/rainfall/{station_id}", response_model=List[DailyRecord])
def get_rainfall(
    station_id: str = Path(..., description="Station ID"),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=10000),
):
    return get_daily(
        station_id=station_id,
        start_date=start_date,
        end_date=end_date,
        limit=limit,
    )


@app.get("/api/soil-moisture-30cm/{station_id}", response_model=List[DailyRecord])
def get_soil_moisture(
    station_id: str = Path(..., description="Station ID"),
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=10000),
    field: Optional[str] = Query(
        None,
        description="Soil moisture column name (auto-detected if omitted)",
    ),
):
    return get_daily(
        station_id=station_id,
        start_date=start_date,
        end_date=end_date,
        limit=limit,
        soil_field=field,
    )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8123)
