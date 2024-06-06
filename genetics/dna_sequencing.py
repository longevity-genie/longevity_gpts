import sqlite3
from pathlib import Path

from genetics.module_intefrace import ModuleInterface


class DnaSequencing(ModuleInterface):

    def __init__(self, db_path:Path = None):
        if db_path is None:
            self.path:Path = Path(Path(__file__).parent, "data", "dna_sequencing.txt")
        else:
            self.path: Path = db_path

    def sequencing_info(self) -> str:
        with open(self.path) as f:
            info = f.readlines()
        return info