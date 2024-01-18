import polars as pl
import thefuzz.fuzz as fuzz
from fastapi import APIRouter
from polars import DataFrame

an_age_router = APIRouter() #FastAPI(title="Anage rest", version="0.1", description="API server to handle queries to restful_anage", debug=True)


@an_age_router.get("/")
def read_root():
    return {
    "Avalible commands:":[
    "/animal_information/{column}/{animal}",
    "/animals_min_max_information/{column}/{command}"]
    }

def write_data(frame: DataFrame, max_rows: int = 8) -> str:
    res = ""
    for col in frame.get_columns():
        res += col.name + " ; "
    res = res[:-3] + "\n"
    frame = frame.with_columns(pl.all().fill_null("unknown"))
    rows = frame.rows()
    for row in rows[:min(len(rows), max_rows)]:
        for cel in row:
            res += str(cel) + " ; "
        res = res[:-3] + "\n"

    return res


def get_column(col_name):
    fields = ["Kingdom", "Phylum", "Class", "Order", "Family", "Genus",
              "Species", "Female maturity (days)", "Male maturity (days)",
              "Gestation/Incubation (days)", "Weaning (days)", "Litter/Clutch size",
              "Litters/Clutches per year", "Inter-litter/Interbirth interval",
              "Birth weight (g)", "Weaning weight (g)", "Adult weight (g)",
              "Growth rate (1/days)", "Maximum longevity (yrs)", "IMR (per yr)",
              "MRDT (yrs)", "Metabolic rate (W)", "Body mass (g)", "Temperature (K)"]

    arry = sorted([[fuzz.partial_ratio(col_name, f), f] for f in fields], reverse=True)
    return arry[0][1]


@an_age_router.get("/animal_information/{column}/{animal}", description="""You should use this tool for getting information about animals.""")
def animal_information(column: str, animal: str):
    column_name = get_column(column.strip())
    animal_name = " " + animal.strip() + " "

    def levenshtein_dist(struct: dict) -> int:
        return max(fuzz.partial_ratio(struct["Science name"], animal_name),
                   fuzz.partial_ratio(struct["Common name"], animal_name))

    frame = pl.read_csv("anage_data.csv", infer_schema_length=0)
    frame = frame.with_columns((pl.col("Genus") + " " + pl.col("Species")).alias("Science name"))
    frame = frame.select(
        [pl.struct(["Science name", "Common name"]).apply(levenshtein_dist).alias("dist"), "Science name",
         "Common name", column_name])
    frame = frame.sort(by="dist", descending=True).select(["Science name", "Common name", column_name])

    return write_data(frame)


@an_age_router.get("/animals_min_max_information/{column}/{operation}", description="""You should use this tool for getting minimum and maximum value of animal features among all the animals.""")
def animals_min_max_information(column: str, operation: str):
    column_name = get_column(column.strip())
    operation = operation.strip()

    frame = pl.read_csv("anage_data.csv", infer_schema_length=0)
    frame = frame.with_columns((pl.col("Genus") + " " + pl.col("Species")).alias("Science name"))
    frame = frame.filter(~pl.col(column_name).is_null())
    frame = frame.with_columns([pl.col(column_name).cast(pl.Float32)])
    if operation.lower() == "max":
        return write_data(frame.filter(pl.max(column_name) == pl.col(column_name)).select(
            ["Science name", "Common name", column_name]))
    if operation.lower() == "min":
        return write_data(frame.filter(pl.min(column_name) == pl.col(column_name)).select(
            ["Science name", "Common name", column_name]))

    raise ValueError(
        f"Error wrong operation ({operation}) specified in input to animal_min_max_avg_information() tool.")