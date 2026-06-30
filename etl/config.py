# ============================================
# CONFIGURACIÓN GENERAL DEL PROYECTO
# ============================================

from pathlib import Path

# ---------- Rutas ----------

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = BASE_DIR / "data_sources"

LOG_DIR = BASE_DIR / "logs"

OUTPUT_DIR = BASE_DIR / "output"

# ---------- SQL SERVER ----------

SERVER = "DESKTOP-0T6NDS3"

DATABASE = "DM_MediAnalytics"

DRIVER = "ODBC Driver 17 for SQL Server"

CONNECTION_STRING = (
    f"DRIVER={{{DRIVER}}};"
    f"SERVER={SERVER};"
    f"DATABASE={DATABASE};"
    "Trusted_Connection=yes;"
)