import sqlite3
from pathlib import Path

from genetics.module_intefrace import ModuleInterface
from genetics.links import link_rsID, link_gene, link_PubMed, replace_pmid, replace_rsid


class Thrombophilia(ModuleInterface):

    def __init__(self, db_path: Path = None):
        if db_path is None:
            self.path: Path = Path(Path(__file__).parent, "data", "thrombophilia.sqlite")
        else:
            self.path: Path = db_path

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
            result += link_rsID(row[0]) + "; " + link_gene(row[1]) + "; " + replace_pmid(replace_rsid(row[2])) + "; " + row[3]+"\n\n"

            query = f"SELECT p_value, genotype, weight, genotype_specific_conclusion FROM weight WHERE rsid = '{rsid}'"
            cursor.execute(query)
            rows = cursor.fetchall()
            result += "thrombophilia weights:\n"
            result += "PMID with p-pvalue; genotype; weight; genotype_specific_conclusion\n"
            pmids:set = set()
            for row in rows:
                pmids = pmids.union(self.parse_PMID(row[0]))
                row = [str(i).replace(";", ",") for i in row]
                result += replace_pmid(row[0]) + "; " + "; ".join(row[1:]) + "\n"
            result += "\n"

            text_pmids = ", ".join(pmids)
            query = f"SELECT pubmed_id, populations, p_value FROM studies WHERE pubmed_id IN ({text_pmids}) "
            cursor.execute(query)
            rows = cursor.fetchall()
            result += "thrombophilia studies:\n"
            result += "PMID; description; pvalue\n"
            for row in rows:
                row = [str(i).replace(";", ",") for i in row]
                result += link_PubMed(row[0]) + "; " + "; ".join(row[1:])+"\n"
            result += "\n"
            cursor.close()

        return result


    def gene_lookup(self, gene: str) -> str:
        with sqlite3.connect(self.path) as conn:
            cursor = conn.cursor()
            query: str = f"SELECT rsid, gene, rsid_conclusion, population FROM rsids WHERE gene = '{gene}'"
            cursor.execute(query)
            rows = cursor.fetchall()

            if rows is None or len(rows) == 0:
                return "thrombophilia: No results found."

            rsids = set([row[0] for row in rows])

            result: str = "thrombophilia:\n"
            result += "rsid; gene; conclusion; population\n"
            for row in rows:
                row = [str(i).replace(";", ",") for i in row]
                result += link_rsID(row[0]) + "; " + link_gene(row[1]) + "; " + replace_pmid(replace_rsid(row[2])) + "; " + row[3] + "\n"
            result += "\n"

            pmids: set = set()
            result += "thrombophilia weights:\n"
            result += "PMID with p-pvalue; genotype; weight; genotype_specific_conclusion\n"
            for rsid in rsids:
                query = f"SELECT p_value, genotype_specific_conclusion, genotype, weight FROM weight WHERE rsid = '{rsid}'"
                cursor.execute(query)
                rows = cursor.fetchall()
                for row in rows:
                    pmids = pmids.union(self.parse_PMID(row[0]))
                    row = [str(i).replace(";", ",") for i in row]
                    result += replace_pmid(row[0]) + "; " + replace_pmid(row[1]) + "; " + "; ".join(row[2:]) + "\n"
            result += "\n"

            text_pmids = ", ".join(pmids)
            query = f"SELECT pubmed_id, populations, p_value FROM studies WHERE pubmed_id IN ({text_pmids}) "
            cursor.execute(query)
            rows = cursor.fetchall()
            result += "thrombophilia studies:\n"
            result += "PMID; description; pvalue\n"
            for row in rows:
                row = [str(i).replace(";", ",") for i in row]
                result += link_PubMed(row[0]) + "; " + "; ".join(row[1:]) + "\n"
            result += "\n"
            cursor.close()

        return result

# TODO: Pars pub med ids in "PMID with p-pvalue"








