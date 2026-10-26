"""FAO station configuration for the standalone FAO API.

Maps station IDs to LoggerNet .dat filenames (daily files only).
Separate from the Kalumbila deployment.
"""

# station_id -> { data_type -> filename under DATA_SOURCE_PATH }
STATIONS = {
    "Kalabo_Met": {
        "daily": "Kalabo_Met_TableDay.dat",
    },
    "Sesheke_Met": {
        "daily": "Sesheke_Met_TableDay.dat",
    },
    "Choma_Water": {
        "daily": "Choma_Water_TableDay.dat",
    },
    "Rufunsa": {
        "daily": "Rufunsa_TableDay.dat",
    },
    "Chipata Met": {
        "daily": "Chipata Met_TableDay.dat",
    },
    "023_Chinsali": {
        "daily": "023_Chinsali_TableDay.dat",
    },
    "Thendere": {
        "daily": "Thendere_TableDay.dat",
    },
    "Nakonde Mwenzo Girls Sch": {
        "daily": "Nakonde Mwenzo Girls Sch_TableDay.dat",
    },
    "024_Don_Bosco_Mansa": {
        "daily": "024_Don_Bosco_Mansa_TableDay.dat",
    },
    "Kawambwa_Met": {
        "daily": "Kawambwa_Met_TableDay.dat",
    },
    "021_Kabwe": {
        "daily": "021_Kabwe_TableDay.dat",
    },
    "Serenje_Met": {
        "daily": "Serenje_Met_TableDay.dat",
    },
    "Fikolongo_Primary": {
        "daily": "Fikolongo_Primary_TableDay.dat",
    },
    "Fatima_Secondary": {
        "daily": "Fatima_Secondary_TableDay.dat",
    },
    "Zambezi_Met": {
        "daily": "Zambezi_Met_TableDay.dat",
    },
    "028_Solwezi": {
        "daily": "028_Solwezi_TableDay.dat",
    },
    "Mbala": {
        "daily": "Mbala_TableDay.dat",
    },
}

STATION_IDS = list(STATIONS.keys())
DEFAULT_STATION = STATION_IDS[0]
