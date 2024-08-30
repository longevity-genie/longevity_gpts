import os
import hashlib
import requests
import json
import gseapy as gp
from dotenv import load_dotenv
from pathlib import Path

API_URL = "https://cu2s6lgb4jew3tht.us-east-1.aws.endpoints.huggingface.cloud"

load_dotenv()
api_token = os.getenv("HF_PRECIOUS_API_TOKEN")
API_URL = os.getenv("PRECIOUS_API_ENDPOINT", API_URL)
folder_path = Path(os.path.abspath(__file__)).parent.parent.resolve() / "omics"
os.makedirs(folder_path, exist_ok=True)

headers = {
    "Accept" : "application/json",
    "Authorization": f"Bearer {api_token}",
    "Content-Type": "application/json"
}

# tissue_options = ['whole body', ''skin', 'muscle', 'whole blood', 'epithelium', 'artery', 'fat tissue', 'brain', 'liver']
# domain_options = ['methylation', 'proteomics', 'expression']

def filename_to_url(name: str):
    load_dotenv(override=True)
    host = "agingkills.eu" #os.getenv("HOST","0.0.0.0")
    port = os.getenv("CHAT_PORT","5174")
    return f"http://{host}:{port}/omics/{name}"

def get_omics_data(age:float, tissue:str = 'whole body', drug:str = '', gender:str = '', domain:str = 'expression'):
    """ This function retrieves omics data for given parameters.
     age - age in years
     tissue - optional, is tissue name like: 'whole body', 'skin', 'muscle', 'whole blood', 'epithelium', 'artery', 'fat tissue', 'brain', 'liver', 'lung'
     drug - drug or biological active substance name
     gender - optional, 'm' for male and 'f' for female
     domain - must be one of these 'methylation', 'proteomics', 'expression' """
    config_data = {'instruction': ['age_group2diff2age_group'],
                   'tissue': tissue,
                   'age': age,
                   'cell': '',
                   'efo': '',
                   'datatype': domain,
                   'drug': drug,
                   'dose': '',
                   'time': '',
                   'case': '',
                   'control': '',
                   'dataset_type': '',
                   'gender': gender,
                   'species': 'human',
                   'up': [],
                   'down': []
                   }
    request_config = {"inputs": config_data, "mode": "meta2diff", "parameters": {
        "temperature": 0.8,
        "top_p": 0.2,
        "top_k": 3550,
        "n_next_tokens": 50,
        "random_seed": 137
    }}

    try:
        response = requests.post(API_URL, headers=headers, json=request_config)
        response.raise_for_status()
        response_json = response.json()

        response_str = json.dumps(response_json)
        md5 = hashlib.md5(response_str.encode()).hexdigest()
        file_name = f'{md5}.json'
        file_path = os.path.join(folder_path, file_name)

        with open(file_path, 'w') as file:
            json.dump(response_json, file, indent=4)

        response_json['output']['test_info'] = '514'
        response_json['output']['full_info'] = filename_to_url(file_name)
        return json.dumps(response_json, indent=4)

    except requests.exceptions.RequestException as e:
        return json.dumps({"error": str(e)})


def get_enrichment(genes_list:str):
    """
    This function takes the list of genes and returns enrichment results.
    """
    genes = genes_list.split(",")
    try:
        enr = gp.enrichr(gene_list=genes,
                 gene_sets=['MSigDB_Hallmark_2020','KEGG_2021_Human'],
                 organism='human',
                 outdir=None,
                )
        return str(enr.results)
    except Exception as e:
        return "Wasn't able to retrieve enrichment"