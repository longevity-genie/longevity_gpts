import sqlite3
from pathlib import Path
from genetics.links import link_rsID, link_gene, replace_rsid, replace_pmid
from genetics.module_intefrace import ModuleInterface


class Coronary(ModuleInterface):

    def __init__(self, db_path: Path = None):
        if db_path is None:
            self.path: Path = Path(Path(__file__).parent, "data", "coronary.sqlite")
        else:
            self.path: Path = db_path

    def _field_lookup(self, field:str, val:str):
        with sqlite3.connect(self.path) as conn:
            cursor = conn.cursor()
            query:str = f"SELECT rsID, Gene, Conclusion, GWAS_study_design, P_value, Risk_allele, Genotype, Weight, " \
                        f"Population FROM coronary_disease WHERE {field} = '{val}'"
            cursor.execute(query)
            rows = cursor.fetchall()

            if rows is None or len(rows) == 0:
                return "coronary disease: No results found."

            result = "coronary disease:\n"
            result += "rsid; Gene; Conclusion; GWAS study design; Pvalue; Risk allele; Genotype; Weight; " \
                        f" Population\n"
            for row in rows:
                row = [str(i).replace(";", ",") for i in row]
                result += link_rsID(row[0])+ "; " + link_gene(row[1]) + "; " + replace_pmid(replace_rsid(row[2])) +\
                          "; " + replace_pmid(row[3]) + "; " + replace_pmid(row[4]) + "; " + "; ".join(row[5:]) + "\n"
            result += "\n"
            cursor.close()

        return result


    def rsid_lookup(self, rsid:str) -> str:
        return self._field_lookup("rsID", rsid)


    def gene_lookup(self, gene: str) -> str:
        return self._field_lookup("Gene", gene)

# TODO: implement BubMed parsing
