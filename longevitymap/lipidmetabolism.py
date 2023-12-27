import sqlite3
from pathlib import Path

from module_intefrace import ModuleInterface


class Lipidmetabolism(ModuleInterface):

    def __init__(self, db_path:Path):
        self.path:Path = db_path

    def rsid_lookup(self, rsid:str) -> str:
        with sqlite3.connect(self.path) as conn:
            cursor = conn.cursor()
            query:str = f"SELECT rsid, gene, rsid_conclusion, population, p_value FROM rsids WHERE rsid = '{rsid}'"
            cursor.execute(query)
            row = cursor.fetchone()

            if row is None:
                return "lipid metabolism: No results found."

            result: str = "lipid metabolism:\n"
            result += "rsid; gene; conclusion; population; pvalue\n"
            row = [str(i).replace(";", ",") for i in row]
            result += "; ".join(row)+"\n\n"

            query = f"SELECT populations, p_value FROM studies WHERE snp = '{rsid}'"
            cursor.execute(query)
            rows = cursor.fetchall()
            result += "lipid metabolism studies:\n"
            result += "description; pvalue\n"
            for row in rows:
                row = [str(i).replace(";", ",") for i in row]
                result += "; ".join(row)+"\n"
            result += "\n"


            query = f"SELECT genotype, weight, genotype_specific_conclusion FROM weight WHERE rsid = '{rsid}'"
            cursor.execute(query)
            rows = cursor.fetchall()
            result += "lipid metabolism weights:\n"
            result += "genotype; weight; genotype_specific_conclusion\n"
            for row in rows:
                row = [str(i).replace(";", ",") for i in row]
                result += "; ".join(row) + "\n"
            result += "\n"
            cursor.close()

        return result


    def gene_lookup(self, gene: str) -> str:
        with sqlite3.connect(self.path) as conn:
            cursor = conn.cursor()
            query: str = f"SELECT rsid, gene, rsid_conclusion, population, p_value FROM rsids WHERE gene = '{gene}'"
            cursor.execute(query)
            rows = cursor.fetchall()

            if rows is None or len(rows) == 0:
                return "lipid metabolism: No results found."

            result: str = "lipid metabolism:\n"
            result += "rsid; gene; conclusion; population; pvalue\n"
            for row in rows:
                row = [str(i).replace(";", ",") for i in row]
                result += "; ".join(row) + "\n"
            result += "\n"

            rsids = set([row[0] for row in rows])

            result += "lipid metabolism studies:\n"
            result += "rsid; description; pvalue\n"
            for rsid in rsids:
                query = f"SELECT snp, populations, p_value FROM studies WHERE snp = '{rsid}'"
                cursor.execute(query)
                rows = cursor.fetchall()
                for row in rows:
                    row = [str(i).replace(";", ",") for i in row]
                    result += "; ".join(row) + "\n"
            result += "\n"

            result += "lipid metabolism weights:\n"
            result += "rsid; genotype; weight; genotype_specific_conclusion\n"
            for rsid in rsids:
                query = f"SELECT rsid, genotype, weight, genotype_specific_conclusion FROM weight WHERE rsid = '{rsid}'"
                cursor.execute(query)
                rows = cursor.fetchall()
                for row in rows:
                    row = [str(i).replace(";", ",") for i in row]
                    result += "; ".join(row) + "\n"
            result += "\n"
            cursor.close()

        return result






