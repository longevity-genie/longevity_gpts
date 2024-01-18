import sqlite3
from pathlib import Path

from genetics.module_intefrace import ModuleInterface


class Coronary(ModuleInterface):

    def __init__(self, db_path:Path):
        self.path:Path = db_path

    def _field_lookup(self, field:str, val:str):
        with sqlite3.connect(self.path) as conn:
            cursor = conn.cursor()
            query:str = f"SELECT rsID, Gene, Risk_allele, Genotype, Conclusion, Weight, " \
                        f"Population, GWAS_study_design, P_value FROM coronary_disease WHERE {field} = '{val}'"
            cursor.execute(query)
            rows = cursor.fetchall()

            if rows is None or len(rows) == 0:
                return "coronary disease: No results found."

            result = "coronary disease:\n"
            result += "rsid; Gene; Risk allele; Genotype; Conclusion; Weight; " \
                        f" Population; GWAS study design; Pvalue\n"
            for row in rows:
                row = [str(i).replace(";", ",") for i in row]
                result += "; ".join(row) + "\n"
            result += "\n"
            cursor.close()

        return result


    def rsid_lookup(self, rsid:str) -> str:
        return self._field_lookup("rsID", rsid)


    def gene_lookup(self, gene: str) -> str:
        return self._field_lookup("Gene", gene)
