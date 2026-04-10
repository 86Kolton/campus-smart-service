from pathlib import Path
import os
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
os.chdir(ROOT)

from app.services.bootstrap_service import bootstrap_database
from scripts.seed_hbu_kb import seed_local_documents


def main() -> None:
    bootstrap_database()
    seed_local_documents(kb_id=1, ensure_bootstrap=False)
    print("demo data ensured")


if __name__ == "__main__":
    main()
