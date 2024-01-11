import sqlite3
from pathlib import Path

from module_intefrace import ModuleInterface


class Longevitymap(ModuleInterface):

    def __init__(self, db_path:Path):
        self.path:Path = db_path

    def rsid_lookup(self, rsid:str) -> str:
        with sqlite3.connect(self.path) as conn:
            cursor = conn.cursor()
            query:str = f"SELECT identifier, study_design, conclusions, association, population.name as population, gene_id " \
                        f"FROM variant, population WHERE population.id = population_id AND identifier = '{rsid}'"
            cursor.execute(query)
            rows = cursor.fetchall()

            if rows is None or len(rows) == 0:
                return "longevity map: No results found."

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

            query = f"SELECT rsid, allele, state, zygosity, weight, categories.description, categories.recommendation, categories.name as category FROM allele_weights, categories " \
                    f"WHERE categories.id = category_id AND rsid = '{rsid}'"
            cursor.execute(query)
            rows = cursor.fetchall()
            result += "longevity map weights:\n"
            result += "rsid; allele; state; zygosity; weight; category_description; cetagory_recommendation; category\n"
            for row in rows:
                row = [str(i).replace(";", ",") for i in row]
                result += "; ".join(row) + "\n"
            result += "\n"
            cursor.close()

        return result


    def gene_lookup(self, gene: str) -> str:
        with sqlite3.connect(self.path) as conn:
            cursor = conn.cursor()
            query: str = f"SELECT identifier, study_design, conclusions, association, population.name as population, gene_id " \
                         f"FROM variant, population, gene WHERE population.id = population_id AND gene.id = gene_id AND gene.symbol = '{gene}'"
            cursor.execute(query)
            rows = cursor.fetchall()

            if rows is None or len(rows) == 0:
                return "longevity map: No results found."

            gene_ids = set([r[5] for r in rows])
            rsids = set([r[0] for r in rows])

            result: str = "longevity map:\n"
            result += "rsid; study design; conclusions; association; population\n"
            for row in rows:
                row = [str(i).replace(";", ",") for i in row[:5]]
                result += "; ".join(row) + "\n"
            result += "\n"

            result += "longevity map genes:\n"
            result += "symbol; gene name; alias; description\n"
            for gene_id in gene_ids:
                query = f"SELECT symbol, name, symbol, alias, description FROM gene WHERE id = '{gene_id}'"
                cursor.execute(query)
                row = cursor.fetchone()

                row = [str(i).replace(";", ",") for i in row]
                result += "; ".join(row) + "\n"
            result += "\n"

            result += "longevity map weights:\n"
            result += "rsid; allele; state; zygosity; weight; category\n"
            for rsid in rsids:
                query = f"SELECT rsid, allele, state, zygosity, weight, categories.name as category FROM allele_weights, categories " \
                        f"WHERE categories.id = category_id AND rsid = '{rsid}'"
                cursor.execute(query)
                rows = cursor.fetchall()

                for row in rows:
                    row = [str(i).replace(";", ",") for i in row]
                    result += "; ".join(row) + "\n"
            result += "\n"
            cursor.close()

        return result


    def pathway_lookup(self, pathway:str) -> str:
        with sqlite3.connect(self.path) as conn:
            cursor = conn.cursor()
            query:str = f"SELECT name, description, recommendation FROM categories " \
                        f"WHERE name = '{pathway}'"
            cursor.execute(query)
            rows = cursor.fetchall()

            if rows is None or len(rows) == 0:
                return "pathway: No results found."

            result += "name; description; recommendation\n"
            for row in rows:
                row = [str(i).replace(";", ",") for i in row]
                result += "; ".join(row)+"\n"
            result += "\n"

            query: str = f"SELECT rsid, allele, state, zygosity, weight, priority " \
                         f"FROM allele_weights WHERE category_id IN (SELECT id FROM categories WHERE name = '{pathway}')"
            cursor.execute(query)
            rows = cursor.fetchall()

            rsids = set([r[0] for r in rows])

            positive_rsid = 0
            negative_rsid = 0

            for row in rows:
                if row[4] > 0:
                    positive_rsid += 1
                else:
                    negative_rsid += 1

            result: str = f"Amount of rsIDs in the pathways: {len(rsids)}, pro-longevity: {positive_rsid},"
            f" anti-longevity: {negative_rsid}), the list of rsids: {rsids}. rsID table:\n"
            result += "rsid; allele; state; zygosity; weight, priority\n"
            for row in rows:
                row = [str(i).replace(";", ",") for i in row]
                result += "; ".join(row) + "\n"
            result += "\n"

            cursor.close()

        return result


