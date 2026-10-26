# FAO Weather API — User SOP

**Purpose:** Retrieve FAO weather station data (temperature min/max, rainfall, soil moisture 30 cm) from the daily data table via REST API.

---

## 1. Base URL

```
http://41.72.104.142:8123
```

All requests are made to this host. No API key or authentication is required.

Interactive documentation (Swagger UI):
```
http://41.72.104.142:8123/docs
```

---

## 2. Available Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /api/stations` | List all available FAO stations |
| `GET /api/daily/{station_id}` | Daily records: temperature min/max, rainfall, soil moisture 30 cm |
| `GET /api/temperature/{station_id}` | Temperature min/max only |
| `GET /api/rainfall/{station_id}` | Rainfall total only |
| `GET /api/soil-moisture-30cm/{station_id}` | Soil moisture at 30 cm depth only |

---

## 3. List Stations

**Request**
```
GET /api/stations
```

**Response**
```json
[
  {"station_id":"Kalabo_Met","filename":"Kalabo_Met_TableDay.dat"},
  {"station_id":"Sesheke_Met","filename":"Sesheke_Met_TableDay.dat"},
  ...
  {"station_id":"Mbala","filename":"Mbala_TableDay.dat"}
]
```

Use the `station_id` value in all other requests.

---

## 4. Query Parameters

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `station_id` | path | Yes | Station identifier | `Kalabo_Met` |
| `start_date` | query | No | Start date `YYYY-MM-DD` | `2024-01-01` |
| `end_date` | query | No | End date `YYYY-MM-DD` | `2024-01-31` |
| `limit` | query | No | Max records returned (1–10000, default 100) | `500` |
| `field` | query | No | Soil moisture column name override | `VWC_30cm` |

---

## 5. Get Daily Data (All Parameters)

Returns temperature min/max, rainfall total, and soil moisture 30 cm for the station.

**Request**
```
GET /api/daily/{station_id}?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD&limit=100
```

**Example**
```
GET http://41.72.104.142:8123/api/daily/Kalabo_Met?start_date=2024-01-01&end_date=2024-01-31&limit=500
```

**Response**
```json
[
  {
    "timestamp": "2024-01-01 00:00:00",
    "station_id": "Kalabo_Met",
    "airtemp_min": 15.2,
    "airtemp_max": 28.4,
    "rainfall": 0.0,
    "soil_moisture_30cm": 0.23
  },
  {
    "timestamp": "2024-01-02 00:00:00",
    "station_id": "Kalabo_Met",
    "airtemp_min": 16.1,
    "airtemp_max": 29.0,
    "rainfall": 12.5,
    "soil_moisture_30cm": 0.31
  }
]
```

If a value is missing in the source file it will be `null`.

---

## 6. Temperature Min/Max Only

**Request**
```
GET /api/temperature/{station_id}?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD&limit=100
```

Returns `timestamp`, `station_id`, `airtemp_min`, `airtemp_max` (other fields are null).

---

## 7. Rainfall Only

**Request**
```
GET /api/rainfall/{station_id}?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD&limit=100
```

Returns `timestamp`, `station_id`, `rainfall` (other fields are null).

---

## 8. Soil Moisture 30 cm Only

**Request**
```
GET /api/soil-moisture-30cm/{station_id}?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD&limit=100&field=<column-name>
```

- The API auto-detects the soil moisture column from the station's `.dat` file header.
- If detection fails or you need a specific column, pass the exact column name via `field`.
- Returns `timestamp`, `station_id`, `soil_moisture_30cm`.

---

## 9. Example Curl Commands

**List stations**
```bash
curl http://41.72.104.142:8123/api/stations
```

**Daily data for a station**
```bash
curl "http://41.72.104.142:8123/api/daily/Mbala?start_date=2024-01-01&end_date=2024-01-07&limit=10"
```

**Temperature only**
```bash
curl "http://41.72.104.142:8123/api/temperature/Kawambwa_Met?limit=30"
```

**Rainfall only**
```bash
curl "http://41.72.104.142:8123/api/rainfall/028_Solwezi?start_date=2024-02-01&end_date=2024-02-29"
```

**Soil moisture 30 cm with custom field**
```bash
curl "http://41.72.104.142:8123/api/soil-moisture-30cm/Serenje_Met?limit=20&field=VWC_30cm"
```

---

## 10. Example Python Script

```python
import requests

BASE = "http://41.72.104.142:8123"

# List stations
stations = requests.get(f"{BASE}/api/stations").json()
print(stations)

# Get daily data for a station
params = {"start_date": "2024-01-01", "end_date": "2024-01-31", "limit": 100}
data = requests.get(f"{BASE}/api/daily/Kalabo_Met", params=params).json()
for row in data:
    print(row["timestamp"], row["airtemp_min"], row["airtemp_max"], row["rainfall"], row["soil_moisture_30cm"])
```

---

## 11. Notes

- **Date format:** `YYYY-MM-DD` (e.g. `2024-03-15`).
- **Timezone:** Timestamps are as recorded by the logger (local station time).
- **Missing data:** Fields with no recorded value return `null`.
- **Soil moisture:** Column names vary by logger program. Use `field=` to specify the exact column if the default auto-detect returns `null`.
- **Rate limiting:** None enforced, but please limit concurrent requests.
- **Support:** Contact the system administrator for access or data issues.

---

## 12. Station IDs Reference

```
Kalabo_Met, Sesheke_Met, Choma_Water, Rufunsa, "Chipata Met",
023_Chinsali, Thendere, "Nakonde Mwenzo Girls Sch", "024_Don_Bosco_Mansa",
Kawambwa_Met, 021_Kabwe, Serenje_Met, Fikolongo_Primary, Fatima_Secondary,
Zambezi_Met, 028_Solwezi, Mbala
```

Station IDs with spaces must be URL-encoded in requests (e.g. `Chipata%20Met`).
