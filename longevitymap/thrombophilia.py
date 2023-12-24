import sqlite3
from pathlib import Path

from module_intefrace import ModuleInterface


class Thrombophilia(ModuleInterface):

    def __init__(self, db_path:Path):
        self.path:Path = db_path

    def parse_PMID(self, text:str):
        parts = text.split(";")
        pmids = []
        for part in parts:
            if part.strip() != "":
                step1 = part.split("]")[0].strip()
                step2 = step1.split(" ")[1]
                pmids.append("'"+step2+"'")

        return set(pmids)


    def rsid_lookup(self, rsid:str) -> str:
        with sqlite3.connect(self.path) as conn:
            cursor = conn.cursor()
            query:str = f"SELECT rsid, gene, rsid_conclusion, population FROM rsids WHERE rsid = '{rsid}'"
            cursor.execute(query)
            row = cursor.fetchone()

            if row is None:
                return "thrombophilia: No results found."

            result: str = "thrombophilia:\n"
            result += "rsid; gene; conclusion; population\n"
            row = [str(i).replace(";", ",") for i in row]
            result += "; ".join(row)+"\n\n"

            query = f"SELECT p_value, genotype, weight, genotype_specific_conclusion FROM weight WHERE rsid = '{rsid}'"
            cursor.execute(query)
            rows = cursor.fetchall()
            result += "thrombophilia weights:\n"
            result += "PMID with p-pvalue; genotype; weight; genotype_specific_conclusion\n"
            pmids:set = set()
            for row in rows:
                pmids = pmids.union(self.parse_PMID(row[0]))
                row = [str(i).replace(";", ",") for i in row]
                result += "; ".join(row) + "\n"
            result += "\n"

            text_pmids = ", ".join(pmids)
            query = f"SELECT pubmed_id, populations, p_value FROM studies WHERE pubmed_id IN ({text_pmids}) "
            cursor.execute(query)
            rows = cursor.fetchall()
            result += "thrombophilia studies:\n"
            result += "PMID; description; pvalue\n"
            for row in rows:
                row = [str(i).replace(";", ",") for i in row]
                result += "; ".join(row)+"\n"
            result += "\n"
            cursor.close()

        return result


    def gene_lookup(self, gene: str) -> str:
        return ""







