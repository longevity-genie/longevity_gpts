import sqlite3
from pathlib import Path

class Longevitymap():

    def __init__(self, db_path:Path):
        self.path:Path = db_path

    def rsid_lookup(self, rsid:str):
        with sqlite3.connect(self.path) as conn:
            cursor = conn.cursor()
            query:str = f"SELECT identifier, study_design, conclusions, association, population.name as population, gene_id " \
                        f"FROM variant, population WHERE population.id = population_id AND identifier = '{rsid}'"
            cursor.execute(query)
            rows = cursor.fetchall()

            if rows is None or len(rows) == 0:
                return "No results found."

            gene_ids = set([r[5] for r in rows])

            result: str = "longevity map:\n"
            result += "identifier; study design; conclusions; association; population\n"
            for row in rows:
                row = [str(i).replace(";", ",") for i in row[:5]]
                result += "; ".join(row)+"\n"
            result += "\n"

            result += "longevity map genes:\n"
            result += "symbol; gene name; alias; description\n"
            for gene_id in gene_ids:
                query = f"SELECT symbol, name, symbol, alias, description FROM gene WHERE id = '{gene_id}'"
                cursor.execute(query)
                row = cursor.fetchone()

                row = [str(i).replace(";", ",") for i in row]
                result += "; ".join(row)+"\n"
            result += "\n"

            query = f"SELECT rsid, allele, state, zygosity, weight, categories.name as category FROM allele_weights, categories " \
                    f"WHERE categories.id = category_id AND rsid = '{rsid}'"
            cursor.execute(query)
            rows = cursor.fetchall()
            result += "longevity map weights:\n"
            result += "rsid; allele; state; zygosity; weight; category\n"
            for row in rows:
                row = [str(i).replace(";", ",") for i in row]
                result += "; ".join(row) + "\n"
            result += "\n"
            cursor.close()

        return result

# print(Longevitymap(Path("data", "longevitymap.sqlite")).rsid_lookup("rs7412"))




