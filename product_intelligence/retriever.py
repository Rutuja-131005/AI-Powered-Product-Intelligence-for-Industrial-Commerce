"""
Evidence Retrieval and Source Discovery for Industrial Catalog Intelligence
Queries local ChromaDB vector store and matches authoritative industrial domains.
"""

import os
import urllib.parse
from typing import Dict, Any, List, Optional

CHROMA_PATH = "chroma_db"
COLLECTION_NAME = "rag_collection"
MODEL_NAME = "all-MiniLM-L6-v2"

_GLOBAL_CHROMA_CLIENT = None
_GLOBAL_EF = None

def get_chroma_client_and_ef():
    global _GLOBAL_CHROMA_CLIENT, _GLOBAL_EF
    if _GLOBAL_CHROMA_CLIENT is None:
        try:
            import chromadb
            from chromadb.utils import embedding_functions
            _GLOBAL_CHROMA_CLIENT = chromadb.PersistentClient(path=CHROMA_PATH)
            _GLOBAL_EF = embedding_functions.SentenceTransformerEmbeddingFunction(model_name=MODEL_NAME)
        except Exception as e:
            _GLOBAL_CHROMA_CLIENT = None
            _GLOBAL_EF = None
    return _GLOBAL_CHROMA_CLIENT, _GLOBAL_EF

# Authoritative manufacturer portal templates
MANUFACTURER_PORTALS = {
    "Allen-Bradley": {
        "base_url": "https://www.rockwellautomation.com",
        "search_url": "https://www.rockwellautomation.com/en-us/search.html?q=",
        "spec_sheet_base": "https://literature.rockwellautomation.com/idc/groups/literature/documents/td/",
        "cad_base": "https://www.rockwellautomation.com/en-us/support/documentation/cad-drawings.html"
    },
    "Schneider Electric": {
        "base_url": "https://www.se.com",
        "search_url": "https://www.se.com/us/en/search/?q=",
        "spec_sheet_base": "https://download.schneider-electric.com/files?p_Doc_Ref=",
        "cad_base": "https://www.se.com/us/en/work/products/product-cad.jsp"
    },
    "Square D": {
        "base_url": "https://www.se.com/us/en/brands/squared/",
        "search_url": "https://www.se.com/us/en/search/?q=",
        "spec_sheet_base": "https://download.schneider-electric.com/files?p_Doc_Ref=",
        "cad_base": "https://www.se.com/us/en/work/products/product-cad.jsp"
    },
    "Siemens": {
        "base_url": "https://www.siemens.com",
        "search_url": "https://mall.industry.siemens.com/mall/en/ww/Catalog/Products/?searchTerm=",
        "spec_sheet_base": "https://support.industry.siemens.com/cs/document/",
        "cad_base": "https://support.industry.siemens.com/cs/sc/3118/3d-cad"
    },
    "Eaton": {
        "base_url": "https://www.eaton.com",
        "search_url": "https://www.eaton.com/us/en-us/search.html?q=",
        "spec_sheet_base": "https://www.eaton.com/content/dam/eaton/products/",
        "cad_base": "https://www.eaton.com/us/en-us/support/cad-drawings.html"
    },
    "ABB": {
        "base_url": "https://new.abb.com",
        "search_url": "https://new.abb.com/search/en/results?q=",
        "spec_sheet_base": "https://search.abb.com/library/Download.aspx?DocumentID=",
        "cad_base": "https://new.abb.com/low-voltage/support/3d-cad"
    },
    "Honeywell": {
        "base_url": "https://sps.honeywell.com",
        "search_url": "https://sps.honeywell.com/us/en/search?q=",
        "spec_sheet_base": "https://prod-edam.honeywell.com/content/dam/honeywell-edam/sps/",
        "cad_base": "https://sps.honeywell.com/us/en/resources/drawings"
    },
    "Parker Hannifin": {
        "base_url": "https://www.parker.com",
        "search_url": "https://www.parker.com/us/en/search.html?query=",
        "spec_sheet_base": "https://www.parker.com/content/dam/Parker-com/Literature/",
        "cad_base": "https://www.parker.com/us/en/support/cad-drawings.html"
    },
    "Omron Automation": {
        "base_url": "https://automation.omron.com",
        "search_url": "https://automation.omron.com/en/us/search?q=",
        "spec_sheet_base": "https://assets.omron.com/m/",
        "cad_base": "https://automation.omron.com/en/us/cad-library"
    },
    "Festo": {
        "base_url": "https://www.festo.com",
        "search_url": "https://www.festo.com/us/en/search/?q=",
        "spec_sheet_base": "https://www.festo.com/net/SupportPortal/Files/",
        "cad_base": "https://www.festo.com/us/en/support-portal/cad"
    },
    "Emerson Electric": {
        "base_url": "https://www.emerson.com",
        "search_url": "https://www.emerson.com/en-us/search?q=",
        "spec_sheet_base": "https://www.emerson.com/documents/automation/",
        "cad_base": "https://www.emerson.com/en-us/cad-drawings"
    }
}

# Trusted industrial distributor reference endpoints
DISTRIBUTOR_PORTALS = {
    "Grainger": "https://www.grainger.com/search?searchQuery=",
    "DigiKey": "https://www.digikey.com/en/products/result?keywords=",
    "Mouser": "https://www.mouser.com/c/?q=",
    "Radwell": "https://www.radwell.com/en-US/Buy?SearchTerm="
}

def retrieve_rag_evidence(
    part_number: str,
    brand: str,
    part_desc: str,
    n_results: int = 3
) -> List[Dict[str, Any]]:
    """
    Retrieves grounded evidence from local ChromaDB vector store matching the product.
    Returns list of source snippets with metadata and chunk citations.
    """
    evidence = []
    if not os.path.exists(CHROMA_PATH):
        return evidence

    try:
        client, ef = get_chroma_client_and_ef()
        if not client or not ef:
            return evidence
            
        collection = client.get_collection(name=COLLECTION_NAME, embedding_function=ef)
        if collection.count() == 0:
            return evidence
            
        query_text = f"{brand} {part_number} {part_desc}".strip()
        results = collection.query(query_texts=[query_text], n_results=n_results)
        
        if results and results.get('documents') and results['documents'][0]:
            docs = results['documents'][0]
            metas = results['metadatas'][0]
            distances = results.get('distances', [[0.5] * len(docs)])[0]
            
            for doc, meta, dist in zip(docs, metas, distances):
                source = meta.get("source", "Uploaded_Document")
                chunk_id = meta.get("chunk_id", 0)
                relevance = max(0.1, min(0.99, 1.0 - (dist / 2.0) if dist is not None else 0.85))
                
                evidence.append({
                    "source_type": "ChromaDB_RAG",
                    "source_title": f"{source} (Chunk {chunk_id})",
                    "url": f"/files_static/{source}",
                    "content_snippet": doc[:400],
                    "confidence_score": round(relevance, 2)
                })
    except Exception as e:
        # ChromaDB collection not initialized or empty
        pass

    return evidence

def discover_authoritative_sources(brand: str, part_number: str) -> Dict[str, str]:
    """
    Constructs deterministic authoritative and reference URLs for manufacturer,
    spec sheets, manuals, CAD drawings, and distributors.
    """
    encoded_pn = urllib.parse.quote_plus(part_number)
    encoded_brand_pn = urllib.parse.quote_plus(f"{brand} {part_number}")
    
    brand_config = MANUFACTURER_PORTALS.get(brand, None)
    
    if brand_config:
        manuf_url = f"{brand_config['search_url']}{encoded_pn}"
        spec_sheet_url = f"{brand_config['search_url']}{encoded_pn}+datasheet"
        manual_url = f"{brand_config['search_url']}{encoded_pn}+manual"
        cad_url = f"{brand_config.get('cad_base', brand_config['base_url'])}?q={encoded_pn}"
    else:
        manuf_url = f"https://www.google.com/search?q={urllib.parse.quote_plus(brand + ' ' + part_number + ' official website')}"
        spec_sheet_url = f"https://www.google.com/search?q={urllib.parse.quote_plus(brand + ' ' + part_number + ' datasheet pdf')}"
        manual_url = f"https://www.google.com/search?q={urllib.parse.quote_plus(brand + ' ' + part_number + ' user manual pdf')}"
        cad_url = f"https://www.google.com/search?q={urllib.parse.quote_plus(brand + ' ' + part_number + ' 3D CAD model')}"

    # Distributor links
    distributor_1 = f"{DISTRIBUTOR_PORTALS['Grainger']}{encoded_pn}"
    distributor_2 = f"{DISTRIBUTOR_PORTALS['Radwell']}{encoded_pn}"
    reference_source = f"https://www.globalspec.com/search/all?query={encoded_brand_pn}"

    return {
        "Manufacturer_Product_URL": manuf_url,
        "Spec_Sheet_URL": spec_sheet_url,
        "User_Manual_URL": manual_url,
        "CAD_Drawing_URL": cad_url,
        "SDS_MSDS_URL": f"https://www.msdsdigital.com/search?q={encoded_brand_pn}",
        "Installation_Guide_URL": f"{manual_url}+installation",
        "Brochure_URL": f"{spec_sheet_url}+brochure",
        "Video_URL": f"https://www.youtube.com/results?search_query={urllib.parse.quote_plus(brand + ' ' + part_number)}",
        "Distributor_URL_1": distributor_1,
        "Distributor_URL_2": distributor_2,
        "Reference_Source_URL": reference_source
    }
