# FAO Weather API

Standalone FastAPI service serving daily weather data for the FAO station network.

## Purpose

Provide simple REST APIs to access **temperature min/max**, **rainfall**, and **soil moisture at 30 cm depth** from the daily Campbell Scientific TOA5 `.dat` files for FAO weather stations.

This is a **separate deployment from Kalumbila** — it does not modify or depend on the Kalumbila app.

## Project structure

```
fao_api/
├── main.py            # FastAPI application and endpoints
├── stations.py        # Station ID -> .dat filename mapping
├── requirements.txt   # Python dependencies
├── .gitignore         # Files excluded from git
├── SOP.md             # User Standard Operating Procedure
└── README.md          # Developer documentation (this file)
```

## Endpoints

| Endpoint | Description |
|----------|-------------|
| `GET /` | Health check |
| `GET /api/stations` | List all stations and their filenames |
| `GET /api/daily/{station_id}` | Daily temp min/max, rainfall, soil moisture 30 cm |
| `GET /api/temperature/{station_id}` | Temperature min/max only |
| `GET /api/rainfall/{station_id}` | Rainfall total only |
| `GET /api/soil-moisture-30cm/{station_id}` | Soil moisture at 30 cm depth only |

## Query parameters

| Parameter | Type | Required | Description | Example |
|-----------|------|----------|-------------|---------|
| `station_id` | path | Yes | Station identifier | `Kalabo_Met` |
| `start_date` | query | No | Start date `YYYY-MM-DD` | `2024-01-01` |
| `end_date` | query | No | End date `YYYY-MM-DD` | `2024-01-31` |
| `limit` | query | No | Max records (1–10000, default 100) | `500` |
| `field` | query | No | Soil moisture column override | `VWC_30cm` |

## Soil moisture 30 cm

The soil moisture column name varies by logger program. The API auto-detects it by scanning the `.dat` file header for candidate names (`vwc_30`, `vwc30`, `smc_30`, `sm30`, `soil_moisture_30`, `theta_30`, etc.). If auto-detection fails, pass the exact column name via `?field=<column-name>`.

## Stations

17 stations configured in `stations.py`:

`Kalabo_Met`, `Sesheke_Met`, `Choma_Water`, `Rufunsa`, `Chipata Met`, `023_Chinsali`, `Thendere`, `Nakonde Mwenzo Girls Sch`, `024_Don_Bosco_Mansa`, `Kawambwa_Met`, `021_Kabwe`, `Serenje_Met`, `Fikolongo_Primary`, `Fatima_Secondary`, `Zambezi_Met`, `028_Solwezi`, `Mbala`.

## Running locally

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Configure .env
# DATA_SOURCE_PATH=C:\Campbellsci\LoggerNet

# 3. Run the server
uvicorn main:app --host 0.0.0.0 --port 8123
```

## Interactive docs

Once running, visit:
```
http://localhost:8123/docs
```

## External access

Map external port **8123** → internal port **8123** on the Windows server's LAN IP in your router/firewall. Users then access:

```
http://<public-ip>:8123/api/stations
```

## Data source

The API reads Campbell Scientific TOA5 formatted `.dat` files from the configured `DATA_SOURCE_PATH` (default `C:\Campbellsci\LoggerNet`). Files must be present in that folder for the station to return data.

## Separation from Kalumbila

This API is standalone. It does not import or call any Kalumbila code. It shares only the station filename convention pattern. Both systems can run independently on the same machine.

## License

Internal use.
