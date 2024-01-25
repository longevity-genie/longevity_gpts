def link_rsID(rsid:str) -> str:
    return f"<a href='https://www.ncbi.nlm.nih.gov/snp/?term={rsid}'>" + rsid + "</a>"

def link_PubMed(pubmed_id:str) -> str:
    return f"<a href='https://pubmed.ncbi.nlm.nih.gov/{pubmed_id}'>" + pubmed_id + "</a>"

def link_gene(gene:str) -> str:
    return f"<a href='https://www.ncbi.nlm.nih.gov/gene/?term={gene}'>" + gene + "</a>"