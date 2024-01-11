import sqlite3
from pathlib import Path

from module_intefrace import ModuleInterface


class DiseaseGenNet(ModuleInterface):

    def __init__(self, db_path:Path):
        self.path:Path = db_path

    def rsid_lookup(self, rsid:str) -> str:
        if not self.path.exists():
            return ""
        with sqlite3.connect(self.path) as conn:
            cursor = conn.cursor()
            query:str = f"SELECT varat.most_severe_consequence, vardis.sentence, disat.diseaseName, disat.type " \
                        f"FROM variantAttributes as varat, variantDiseaseNetwork as vardis, diseaseAttributes as disat " \
                        f"WHERE variantId = '{rsid}' AND varat.variantNID = vardis.variantNID AND vardis.diseaseNID = disat.diseaseNID"
            cursor.execute(query)
            rows = cursor.fetchall()
            if rows is None or len(rows) == 0:
                return ""

            text = f"Diseases asociate with {rsid}:\n"
            text += "most severe consequence; description; disease name; type\n"
            for row in rows:
                text += "; ".join(row)+"\n"
            text += "\n"

            return text



    def gene_lookup(self, gene: str) -> str:
        if not self.path.exists():
            return ""
        with sqlite3.connect(self.path) as conn:
            cursor = conn.cursor()
            query: str = f"SELECT gendis.sentence, disat.diseaseName, disat.type " \
                         f"FROM geneAttributes as genat, geneDiseaseNetwork as gendis, diseaseAttributes as disat " \
                         f"WHERE geneName = '{gene}' AND genat.geneNID = gendis.geneNID AND gendis.diseaseNID = disat.diseaseNID"
            cursor.execute(query)
            rows = cursor.fetchall()

            if rows is None or len(rows) == 0:
                return ""

            text = f"Diseases asociate with {gene}:\n"
            text += "description; disease name; type\n"

            for row in rows:
                text += "; ".join(row)+"\n"
            text += "\n"

            return text