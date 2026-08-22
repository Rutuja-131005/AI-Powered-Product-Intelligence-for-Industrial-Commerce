import streamlit as st
import os
import sys
import pandas as pd
import io
from pathlib import Path

# Add the Document RAG System directory to the path
sys.path.insert(0, str(Path(__file__).parent / "Document RAG System"))

try:
    from rag import query_rag
    from ingest import ingest_file, get_collection_stats
    from product_intelligence.pipeline import get_pipeline_instance
    from product_intelligence.schema import EXPECTED_OUTPUT_COLUMNS, NUM_OUTPUT_COLUMNS
    from product_intelligence.exporter import export_to_csv_bytes, export_to_xlsx_bytes
    from sample_generator import generate_sample_csv
except ImportError as e:
    st.error(f"Error importing modules: {e}")
    st.stop()

st.set_page_config(
    page_title="AI Product Intelligence & Document RAG Platform",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

pipeline = get_pipeline_instance()

# Mode Navigation in Sidebar
st.sidebar.title("⚡ CATALOG IQ")
st.sidebar.caption("AI Industrial Commerce Intelligence")
mode = st.sidebar.radio("Select Application Mode", ["⚙️ AI Product Intelligence Studio", "📚 Document RAG Assistant"])

if mode == "⚙️ AI Product Intelligence Studio":
    st.title("⚙️ AI-Powered Product Intelligence Studio")
    st.markdown("Enrich sparse industrial product records into **252 commerce-ready columns** with grounded provenance and quality validation.")

    # Ingestion Controls
    col_up, col_demo = st.columns([2, 1])
    with col_up:
        uploaded_catalog = st.file_uploader(
            "Upload Sparse Product Catalog (CSV or XLSX)",
            type=["csv", "xlsx", "xls"],
            help="Requires standard 6-column format (Mfg_Part_Num, Part_Desc, E1_Brand, Unilog_Brand, DIB_Brand, Part_Manuf)"
        )
    with col_demo:
        st.markdown("#### Quick Evaluation Fixtures")
        if st.button("⚡ Load 100 Sample Parts"):
            sample_path = "Document RAG System/data/sample_industrial_input.csv"
            if not os.path.exists(sample_path):
                generate_sample_csv(sample_path, total_rows=1000)
            sample_df = pd.read_csv(sample_path).iloc[:100]
            st.session_state["active_df"] = sample_df
            st.session_state["catalog_source"] = "sample_100.csv"
            st.success("Loaded 100 industrial parts!")

        if st.button("🚀 Load 1,000 Evaluation Set"):
            sample_path = "Document RAG System/data/sample_industrial_input.csv"
            if not os.path.exists(sample_path):
                generate_sample_csv(sample_path, total_rows=1000)
            sample_df = pd.read_csv(sample_path)
            st.session_state["active_df"] = sample_df
            st.session_state["catalog_source"] = "evaluation_1000.csv"
            st.success("Loaded 1,000 industrial parts!")

    if uploaded_catalog is not None:
        try:
            if uploaded_catalog.name.endswith(".csv"):
                df = pd.read_csv(uploaded_catalog)
            else:
                df = pd.read_excel(uploaded_catalog)
            st.session_state["active_df"] = df
            st.session_state["catalog_source"] = uploaded_catalog.name
            st.info(f"Loaded {len(df)} rows from {uploaded_catalog.name}")
        except Exception as e:
            st.error(f"Error parsing file: {e}")

    # Active dataset processing
    if "active_df" in st.session_state:
        df = st.session_state["active_df"]
        st.markdown("---")
        st.subheader(f"📊 Dataset: {st.session_state.get('catalog_source', 'Custom Upload')} ({len(df)} Rows)")
        
        if st.button("🚀 Run AI Batch Enrichment Pipeline", type="primary"):
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            records = []
            for idx, row in df.iterrows():
                row_dict = row.to_dict()
                enriched = pipeline.enrich_single_product(row_dict, row_idx=idx)
                records.append(enriched)
                
                pct = int(((idx + 1) / len(df)) * 100)
                progress_bar.progress(pct)
                status_text.text(f"Enriching row {idx + 1}/{len(df)}: {row_dict.get('Mfg_Part_Num', 'N/A')}")
            
            st.session_state["enriched_records"] = records
            status_text.success(f"✅ Successfully enriched {len(records)} products into 252 columns!")

        # Enriched results & KPIs
        if "enriched_records" in st.session_state:
            records = st.session_state["enriched_records"]
            
            # KPI Metrics
            kpi1, kpi2, kpi3, kpi4 = st.columns(4)
            kpi1.metric("Total Products", len(records))
            kpi2.metric("Output Columns", f"{NUM_OUTPUT_COLUMNS} / 252")
            
            scores = [float(r.get("Overall_Confidence_Score", 0.0)) for r in records if r.get("Overall_Confidence_Score")]
            avg_score = sum(scores) / len(scores) if scores else 0.0
            kpi3.metric("Avg Confidence", f"{avg_score*100:.1f}%")
            
            verified_cnt = sum(1 for r in records if r.get("Validation_Status") == "VERIFIED")
            kpi4.metric("Verified Status", f"{verified_cnt}/{len(records)}")

            # Export Buttons
            st.markdown("### 📥 Commerce Catalog Export")
            col_csv, col_xlsx = st.columns(2)
            
            csv_bytes = export_to_csv_bytes(records)
            col_csv.download_button(
                label="📥 Download 252-Column CSV",
                data=csv_bytes,
                file_name="Enriched_Industrial_Catalog_252_Cols.csv",
                mime="text/csv"
            )
            
            xlsx_bytes = export_to_xlsx_bytes(records)
            col_xlsx.download_button(
                label="📊 Download 252-Column XLSX",
                data=xlsx_bytes,
                file_name="Enriched_Industrial_Catalog_252_Cols.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )

            # Preview Table
            st.markdown("### 🔍 Enriched Catalog Preview")
            display_cols = ["Mfg_Part_Num", "Resolved_Brand", "Product_Title", "Primary_Category", "Voltage_Rating", "Current_Rating", "Overall_Confidence_Score", "Validation_Status"]
            preview_df = pd.DataFrame([{col: r.get(col, "") for col in display_cols} for r in records])
            st.dataframe(preview_df, use_container_width=True)

            # Single Product Deep Dive
            st.markdown("### 🔬 Product Inspector & Provenance Audit")
            selected_idx = st.selectbox("Select product to inspect", range(len(records)), format_func=lambda i: f"Row {i+1}: {records[i].get('Mfg_Part_Num', 'N/A')} - {records[i].get('Resolved_Brand', 'N/A')}")
            
            p = records[selected_idx]
            tab_spec, tab_triplets, tab_prov, tab_raw = st.tabs(["1. Specs & Copy", "2. 50 Attribute Triplets", "3. Provenance & Evidence", "4. Source Input"])
            
            with tab_spec:
                st.markdown(f"#### {p.get('Product_Title', '')}")
                st.write(f"**Short Description:** {p.get('Short_Description', '')}")
                st.write(f"**Long Description:** {p.get('Long_Description', '')}")
                st.write("**Feature Bullets:**")
                for i in range(1, 11):
                    b = p.get(f"Feature_Bullet_{i}")
                    if b:
                        st.markdown(f"- {b}")
                        
            with tab_triplets:
                t_rows = []
                for i in range(1, 51):
                    n = p.get(f"Attribute_Name_{i}", "")
                    v = p.get(f"Attribute_Value_{i}", "")
                    u = p.get(f"Attribute_UOM_{i}", "")
                    if n or v:
                        t_rows.append({"#": i, "Attribute Name": n, "Normalized Value": v, "Standard UOM": u})
                if t_rows:
                    st.table(pd.DataFrame(t_rows))
                else:
                    st.info("No triplets populated")

            with tab_prov:
                st.write(f"**Confidence Score:** {p.get('Overall_Confidence_Score', '')}")
                st.write(f"**Validation Status:** {p.get('Validation_Status', '')}")
                st.write(f"**Manufacturer Portal:** {p.get('Manufacturer_Product_URL', '')}")
                st.write(f"**Datasheet URL:** {p.get('Spec_Sheet_URL', '')}")
                st.write(f"**CAD Drawing:** {p.get('CAD_Drawing_URL', '')}")
                st.json(p.get("Provenance_Log", "{}"))

            with tab_raw:
                st.json({
                    "Mfg_Part_Num": p.get("Mfg_Part_Num", ""),
                    "Part_Desc": p.get("Part_Desc", ""),
                    "E1_Brand": p.get("E1_Brand", ""),
                    "Unilog_Brand": p.get("Unilog_Brand", ""),
                    "DIB_Brand": p.get("DIB_Brand", ""),
                    "Part_Manuf": p.get("Part_Manuf", "")
                })

else:
    st.title("📚 Document RAG Assistant")
    st.markdown("Ask technical questions grounded in uploaded specification documents and manuals.")
    
    with st.sidebar:
        st.subheader("📂 Ingest Manuals & Datasheets")
        uploaded_doc = st.file_uploader("Upload PDF, DOCX, or TXT", type=["pdf", "docx", "txt"])
        if uploaded_doc is not None:
            with st.spinner(f"Ingesting {uploaded_doc.name}..."):
                temp_path = f"/tmp/{uploaded_doc.name}"
                with open(temp_path, "wb") as f:
                    f.write(uploaded_doc.getbuffer())
                ingest_file(temp_path)
                st.success(f"✅ Ingested: {uploaded_doc.name}")
                if os.path.exists(temp_path):
                    os.remove(temp_path)

        st.markdown("---")
        try:
            stats_count = get_collection_stats()
            st.metric("Vector DB Chunks", stats_count)
        except:
            st.metric("Vector DB Chunks", 0)

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if user_input := st.chat_input("Ask a technical question about your documents..."):
        st.session_state.messages.append({"role": "user", "content": user_input})
        with st.chat_message("user"):
            st.markdown(user_input)

        with st.chat_message("assistant"):
            with st.spinner("Searching documents and generating answer..."):
                try:
                    response = query_rag(user_input)
                    if isinstance(response, dict):
                        answer = response.get('answer', 'No answer found.')
                        st.markdown(answer)
                        sources = response.get('sources', [])
                        if sources:
                            with st.expander("📁 Grounding Citations"):
                                for s in sources:
                                    st.write(f"• **{s.get('source')} (Chunk {s.get('chunk_id')}):** {s.get('text')[:200]}...")
                    else:
                        answer = str(response)
                        st.markdown(answer)

                    st.session_state.messages.append({"role": "assistant", "content": answer})
                except Exception as e:
                    err_msg = f"Error: {e}"
                    st.error(err_msg)
                    st.session_state.messages.append({"role": "assistant", "content": err_msg})
