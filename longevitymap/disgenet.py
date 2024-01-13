import sqlite3
from pathlib import Path

from module_intefrace import ModuleInterface


class DiseaseGenNet(ModuleInterface):

    def __init__(self, db_path:Path):
        self.path:Path = db_path

    def _agragate_last_field(self, rows):
        current = list(rows[0])
        current[-1] = str(current[-1])
        res:list = []
        for row in rows[1:]:
            row = list(row)
            if current[:-1] != row[:-1]:
                res.append(current)
                current = row
                current[-1] = str(current[-1])
            else:
                current[-1] += ", " + str(row[-1]).strip()

        res.append(current)

        return res


    def rsid_lookup(self, rsid:str) -> str:
        if not self.path.exists():
            return ""
        with sqlite3.connect(self.path) as conn:
            cursor = conn.cursor()
            query:str = f"SELECT vdnet.pmid, varat.most_severe_consequence, vdnet.sentence, disat.diseaseName, disat.type, dclass.diseaseClassName " \
                        f"FROM variantAttributes AS varat " \
                        f"JOIN variantDiseaseNetwork AS vdnet ON varat.variantNID = vdnet.variantNID " \
                        f"JOIN diseaseAttributes AS disat ON vdnet.diseaseNID = disat.diseaseNID " \
                        f"LEFT JOIN disease2class AS d2c ON disat.diseaseNID = d2c.diseaseNID " \
                        f"LEFT JOIN diseaseClass AS dclass ON d2c.diseaseClassNID = dclass.diseaseClassNID " \
                        f"WHERE varat.variantId = '{rsid}' ORDER BY disat.diseaseName"
            cursor.execute(query)
            rows = cursor.fetchall()
            if rows is None or len(rows) == 0:
                return ""

            text = f"Diseases asociate with {rsid}:\n"
            text += "Pub Med ID; most severe consequence; description; disease name; type; disease class\n"

            rows = self._agragate_last_field(rows)

            if len(rows) > 1000:
                rows = rows[:1000]

            for row in rows:
                text += "; ".join([str(i) for i in row])+"\n"
            text += "\n"

            return text


    def gene_lookup(self, gene: str) -> str:
        if not self.path.exists():
            return ""
        with sqlite3.connect(self.path) as conn:
            cursor = conn.cursor()
            query: str = f"SELECT gendis.pmid, gendis.sentence, disat.diseaseName, disat.type, dclass.diseaseClassName " \
                        f"FROM geneAttributes AS genat " \
                        f"JOIN geneDiseaseNetwork AS gendis ON genat.geneNID = gendis.geneNID " \
                        f"JOIN diseaseAttributes AS disat ON gendis.diseaseNID = disat.diseaseNID " \
                        f"LEFT JOIN disease2class AS d2c ON disat.diseaseNID = d2c.diseaseNID " \
                        f"LEFT JOIN diseaseClass AS dclass ON d2c.diseaseClassNID = dclass.diseaseClassNID " \
                        f"WHERE genat.geneName = '{gene}' ORDER BY disat.diseaseName"
            cursor.execute(query)
            rows = cursor.fetchall()

            if rows is None or len(rows) == 0:
                return ""

            text = f"Diseases asociate with {gene}:\n"
            text += "Pub Med ID; description; disease name; type; disease class\n"

            rows = self._agragate_last_field(rows)

            if len(rows) > 1000:
                rows = rows[:1000]

            for row in rows:
                text += "; ".join([str(i) for i in row])+"\n"
            text += "\n"

            return text


    def disease_lookup(self, disease: str) -> str:
        if not self.path.exists():
            return ""
        with sqlite3.connect(self.path) as conn:
            cursor = conn.cursor()
            query: str = f"SELECT genat.geneName, varat.variantId, varat.most_severe_consequence " \
                        f"FROM variantDiseaseNetwork as vardis, variantAttributes as varat, " \
                        f"diseaseAttributes as disat, variantGene as vargen, geneAttributes as genat " \
                        f"WHERE disat.diseaseName = '{disease}' AND " \
                        f"disat.diseaseNID = vardis.diseaseNID AND vardis.variantNID = varat.variantNID AND " \
                        f"vargen.variantNID = vardis.variantNID AND genat.geneNID = vargen.geneNID " \
                        f"ORDER BY genat.geneNID "
            cursor.execute(query)
            rows = cursor.fetchall()

            if rows is None or len(rows) == 0:
                return ""

            if len(rows) > 1000:
                rows = rows[:1000]

            text = f"Variants associate with disease '{disease}' grouped by gene:\n"
            gene = ""
            for row in rows:
                if gene != row[0]:
                    text += row[0]+":\n"
                    gene = row[0]
                text += "  " + row[1] + ", " + row[2] + "\n"
            text += "\n"

            return text