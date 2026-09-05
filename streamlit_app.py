import streamlit as st
import os
import sys
import pandas as pd
import io
from pathlib import Path

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

favicon_path = "static/favicon.png" if os.path.exists("static/favicon.png") else "⚡"

st.set_page_config(
    page_title="ProdIntellix — Product & Payment Intelligence Platform",
    page_icon=favicon_path,
    layout="wide",
    initial_sidebar_state="expanded"
)

pipeline = get_pipeline_instance()

# Custom Sidebar Branding
st.sidebar.title("🌐 ProdIntellix")
st.sidebar.caption("AI Product & Payment Intelligence Platform")

mode = st.sidebar.radio(
    "Select Application Mode",
    [
        "⚙️ AI Product Intelligence Studio",
        "📷 Photo & PDF Multimodal Inspector",
        "💳 Razorpay Fintech & Risk Hub",
        "🧾 RazorpayX B2B Reconciler",
        "📚 Document RAG Assistant"
    ]
)




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
            sample_path = "data/sample_industrial_input.csv"
            if not os.path.exists(sample_path):
                generate_sample_csv(sample_path, total_rows=1000)
            sample_df = pd.read_csv(sample_path).iloc[:100]
            st.session_state["active_df"] = sample_df
            st.session_state["catalog_source"] = "sample_100.csv"
            st.success("Loaded 100 industrial parts!")

        if st.button("🚀 Load 1,000 Evaluation Set"):
            sample_path = "data/sample_industrial_input.csv"
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

elif mode == "📷 Photo & PDF Multimodal Inspector":
    st.title("📷 Photo & PDF Multimodal Product Inspector")
    st.markdown("Upload a **product photo (nameplate, label, package)** or a **technical PDF (manual, datasheet)** to automatically analyze specs and retrieve **live accessible research links**.")

    from product_intelligence.multimodal_analyzer import MultimodalProductAnalyzer

    col_up, col_sample = st.columns([2, 1])

    with col_up:
        uploaded_media = st.file_uploader("Upload Product Photo or Technical PDF", type=["png", "jpg", "jpeg", "pdf"])

    with col_sample:
        st.markdown("#### Sample Media Fixture")
        if st.button("🚀 Run Sample Nameplate Photo Analysis"):
            filename = "Allen_Bradley_140U_J0D3_C40_Nameplate.jpg"
            file_bytes = b"Sample Nameplate Image 140U-J0D3-C40 Allen-Bradley"
            res = MultimodalProductAnalyzer.analyze_and_research(filename, file_bytes)
            st.session_state["multimodal_result"] = res
            st.success("Sample Photo Analyzed Successfully!")

    if uploaded_media is not None:
        if st.button("⚡ Analyze Media & Discover Accessible Links", type="primary"):
            with st.spinner("Analyzing image/PDF text, extracting Part Number & Brand, and running multi-website research..."):
                file_bytes = uploaded_media.read()
                res = MultimodalProductAnalyzer.analyze_and_research(uploaded_media.name, file_bytes)
                st.session_state["multimodal_result"] = res
                st.success("Analysis Complete!")

    if "multimodal_result" in st.session_state:
        res = st.session_state["multimodal_result"]
        st.markdown("---")
        st.subheader(f"🔍 Product Identity Detected: {res['brand']} {res['mpn']}")

        mcol1, mcol2, mcol3 = st.columns(3)
        mcol1.metric("Manufacturer Part #", res["mpn"])
        mcol2.metric("Detected Brand", res["brand"])
        mcol3.metric("Product Trust Score", f"{res['trust_score']} / 100")

        st.markdown("### 🌐 Discovered Accessible Live Research Links")
        links = res.get("accessible_links", [])
        if links:
            for l in links:
                st.markdown(f"• **[{l['label']}]({l['url']})** — `{l['category']}` ({l['status']})")

        st.markdown("---")
        st.subheader("📋 Razorpay Fintech Metadata")
        fcol1, fcol2 = st.columns(2)
        fcol1.metric("Predicted HSN Code", res["fintech_hsn"])
        fcol2.metric("GST Tax Slab", f"{res['fintech_gst']}%")

elif mode == "💳 Razorpay Fintech & Risk Hub":

    st.title("💳 Razorpay Magic Checkout & Merchant Risk Hub")
    st.markdown("Enrich merchant catalog data with **HSN/GST compliance**, **Shipping Specs**, **Product Authenticity Risk Scores**, and **Razorpay Orders**.")


    from services.razorpay_service import RazorpayService
    from product_intelligence.risk_scoring import MerchantRiskScorer
    from product_intelligence.fintech_enricher import FintechEnricher

    razorpay_svc = RazorpayService()
    risk_scorer = MerchantRiskScorer()
    fintech_enricher = FintechEnricher()

    col1, col2 = st.columns([1, 1])

    with col1:
        st.subheader("🔍 Single Product Risk & Tax Inspector")
        product_title = st.text_input("Product Description", "Diablo 1/2 in. x 18 in. Sanding Belt 6pc (8536 Breaker)")
        part_number = st.text_input("Manufacturer Part Number (MPN)", "DCB518ASTS06G")
        price_inr = st.number_input("Catalog Listing Price (INR)", value=1499.0, step=100.0)
        brand_input = st.text_input("Merchant Claimed Brand", "Freud / Diablo")

        if st.button("🚀 Evaluate Product Risk & Tax Slabs", type="primary"):
            fintech_data = fintech_enricher.enrich_fintech_metadata({
                "Part_Desc": product_title,
                "Mfg_Part_Num": part_number
            })
            risk_report = risk_scorer.evaluate_merchant_product_risk({
                "Part_Desc": product_title,
                "Mfg_Part_Num": part_number,
                "claimed_price": price_inr,
                "E1_Brand": brand_input
            })

            st.session_state["evaluated_product"] = {
                "title": product_title,
                "part_number": part_number,
                "price": price_inr,
                "fintech": fintech_data,
                "risk": risk_report
            }

    with col2:
        st.subheader("📊 Merchant Risk & Authenticity Score")
        if "evaluated_product" in st.session_state:
            ep = st.session_state["evaluated_product"]
            risk = ep["risk"]
            fintech = ep["fintech"]

            score = risk["product_trust_score"]
            if score >= 85:
                st.success(f"🟢 Product Trust Score: **{score} / 100** ({risk['risk_level']})")
            elif score >= 65:
                st.warning(f"🟡 Product Trust Score: **{score} / 100** ({risk['risk_level']})")
            else:
                st.error(f"🔴 Product Trust Score: **{score} / 100** ({risk['risk_level']})")

            st.write(f"**Action Recommendation:** {risk['action_recommendation']}")
            if risk.get("risk_flags"):
                st.markdown("**Risk Indicators Flagged:**")
                for f in risk["risk_flags"]:
                    st.write(f"• `{f}`")

            st.markdown("---")
            st.subheader("📋 Razorpay Magic Checkout Metadata")
            mcol1, mcol2 = st.columns(2)
            mcol1.metric("Predicted HSN Code", fintech["hsn_sac_code"])
            mcol2.metric("GST Tax Slab", f"{fintech['gst_rate_pct']}%")

            scol1, scol2 = st.columns(2)
            scol1.metric("Est. Net Weight", f"{fintech['net_weight_kg']} kg")
            scol2.metric("Freight Class", fintech["freight_class"])

            st.markdown("---")
            st.subheader("💳 Instant Razorpay Payment Gateway Modal")
            if st.button("⚡ Generate Razorpay Order & Payment Link"):
                order = razorpay_svc.create_order(
                    product_title=ep["title"],
                    unit_price=ep["price"],
                    hsn_code=fintech["hsn_sac_code"],
                    gst_rate=fintech["gst_rate_pct"],
                    part_number=ep["part_number"]
                )
                plink = razorpay_svc.create_payment_link(
                    product_title=ep["title"],
                    total_amount=order["calculated_breakdown"]["total_amount"]
                )

                st.success(f"✅ Razorpay Order Created! Order ID: `{order['id']}`")
                st.json(order["calculated_breakdown"])
                st.markdown(f"👉 **[Click to Pay via Razorpay Checkout Link]({plink['short_url']})**")

elif mode == "🧾 RazorpayX B2B Reconciler":
    st.title("🧾 RazorpayX B2B Invoice & PO Reconciliation Engine")

    st.markdown("Automated RAG-powered line-item matching between supplier invoices and catalog part numbers for **RazorpayX Vendor Payouts**.")

    from services.reconciliation import InvoiceReconciliationEngine
    reconciler = InvoiceReconciliationEngine()

    uploaded_inv = st.file_uploader("Upload B2B Invoice or Purchase Order (PDF / TXT)", type=["txt", "pdf", "csv"])
    sample_text = st.text_area(
        "Or paste Invoice Text directly:",
        value="""INVOICE #INV-2026-9081
Vendor: Jam Industrial Supply LLC
Line 1: 3MABR-7100075678 - 3M 775L Stikit Film P150 Cubitron II  Qty: 10  Amount: ₹14,990.00
Line 2: DCB518ASTS06G - Diablo 1/2 in x 18 in Sanding Belt 6pc Qty: 5   Amount: ₹7,495.00
Line 3: 140U-J0D3-C40 - Allen Bradley Circuit Breaker 40A     Qty: 2   Amount: ₹12,500.00
TOTAL PAYABLE: ₹34,985.00""",
        height=150
    )

    if st.button("🚀 Run RAG Line-Item Reconciliation", type="primary"):
        with st.spinner("Parsing invoice line items and verifying against catalog vector store..."):
            report = reconciler.reconcile_invoice(sample_text)
            
            st.success(f"✅ Reconciliation Status: **{report['reconciliation_status']}**")
            
            kcol1, kcol2, kcol3 = st.columns(3)
            kcol1.metric("Processed Line Items", report["total_items_processed"])
            kcol2.metric("Discrepancies Found", report["total_discrepancies"])
            kcol3.metric("Total Approved Payout", f"₹{report['total_payout_inr']:,.2f}")

            st.markdown("### 📋 Reconciled Line Items Audit")
            st.dataframe(pd.DataFrame(report["reconciled_line_items"]), use_container_width=True)

            st.markdown("### 🚀 Generated RazorpayX Vendor Payout API Payload")
            st.json(report["razorpayx_payout_payload"])

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
