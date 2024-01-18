from fastapi import APIRouter

bloody_router = APIRouter()
#https://nikhilyadala-blood-age-app-kc3pe8.streamlitapp.com/

from fastapi import FastAPI, HTTPException, APIRouter
from pydantic import BaseModel
import httpx

class OCRRequest(BaseModel):
    url: str

@bloody_router.post("/blood_ocr")
async def biologicalage_ocr(request_data: OCRRequest):
    async with httpx.AsyncClient(timeout=50) as client:
        response = await client.post(
            "https://asklongevitygpt.com/biologicalage_ocr",
            json=request_data.dict(),
            headers={"Content-Type": "application/json"}
        )

        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="Error from external API")

        return response.json()

"""
@bloody_router.get("/blood_age_15")
async def blood_age_15(
        Platelet: float,
        Redcell: float,
        Mean_cell_volume: float,
        Lymphocyte: float,
        Monocyte: float,
        Red_blood_cell_count: float,
        Lymphocyte_number: float,
        Creatine_Phosphokinase: float,
        Potassium: float,
        Creatinine_refrigerated_serum: float,
        Blood_Urea_Nitrogen: float,
        Alanine_Aminotransferase_ALT: float,
        Alkaline_Phosphatase_ALP: float,
        Glycohemoglobin: float,
        Glucose: float,
        Lactate_Dehydrogenase: float,
        angina: int,
        gallstones: int,
        liver: int,
        cancer: int,
        arthritis: int
):
"""

@bloody_router.get("/blood_age_15")
async def blood_age_15(
    Platelet: float = 300.0,
    Redcell: float = 13.0,
    Mean_cell_volume: float = 80.0,
    Lymphocyte: float = 30.0,
    Monocyte: float = 8.0,
    Red_blood_cell_count: float = 4.9,
    Lymphocyte_number: float = 2.0,
    Creatine_Phosphokinase: float = 300.0,
    Potassium: float = 4.5,
    Creatinine_refrigerated_serum: float = 0.75,
    Blood_Urea_Nitrogen: float = 10.0,
    Alanine_Aminotransferase_ALT: float = 20.5,
    Alkaline_Phosphatase_ALP: float = 71.0,
    Glycohemoglobin: float = 5.0,
    Glucose: float = 100.0,
    Lactate_Dehydrogenase: float = 200.0,
    angina: int = 2,
    gallstones: int = 2,
    liver: int = 2,
    cancer: int = 2,
    arthritis: int = 2):
    query_params = {
        "Platelet": Platelet,
        "Redcell": Redcell,
        "Mean_cell_volume": Mean_cell_volume,
        "Lymphocyte": Lymphocyte,
        "Monocyte": Monocyte,
        "Red_blood_cell_count": Red_blood_cell_count,
        "Lymphocyte_number": Lymphocyte_number,
        "Creatine_Phosphokinase": Creatine_Phosphokinase,
        "Potassium": Potassium,
        "Creatinine_refrigerated_serum": Creatinine_refrigerated_serum,
        "Blood_Urea_Nitrogen": Blood_Urea_Nitrogen,
        "Alanine_Aminotransferase_ALT": Alanine_Aminotransferase_ALT,
        "Alkaline_Phosphatase_ALP": Alkaline_Phosphatase_ALP,
        "Glycohemoglobin": Glycohemoglobin,
        "Glucose": Glucose,
        "Lactate_Dehydrogenase": Lactate_Dehydrogenase,
        "angina": angina,
        "gallstones": gallstones,
        "liver": liver,
        "cancer": cancer,
        "arthritis": arthritis
    }

    async with httpx.AsyncClient(timeout=50) as client:
        response = await client.get(
            "http://ec2-54-90-101-85.compute-1.amazonaws.com/full_aging_15param",
            params=query_params
        )

        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail="Error from external API")

        return response.json()