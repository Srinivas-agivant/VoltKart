"""Administrator data management and dataset ingestion interface for VoltKart."""

from pathlib import Path
import streamlit as st
import pandas as pd

from backend.file_processor import FileProcessor, COLUMN_ALIASES
from backend.data_validator import DataValidator
from backend.data_importer import DataImporter
from backend.knowledge_base_service import KnowledgeBaseService
from database import get_db, get_db_manager
import config


def render_admin_dashboard():
    """Renders the comprehensive admin data management dashboard."""
    st.title("⚙️ VoltKart Admin Control Center")
    st.caption("Manage laptop catalogs, customer FAQs, store policies, and view ingestion audits.")

    db = get_db()
    importer = DataImporter(db=db)
    kb_service = KnowledgeBaseService(db=db)

    tabs = st.tabs([
        "📤 CSV / Excel Ingestion",
        "📄 PDF Knowledge Base",
        "📋 Live Database Catalog",
        "📜 Ingestion Audit Logs",
    ])

    # TAB 1: File Ingestion
    with tabs[0]:
        st.subheader("Import Catalog, FAQs, or Policies")
        st.markdown(
            "Upload `.csv`, `.xlsx`, or `.xls` files. The system validates fields, "
            "normalizes hardware specifications, and prevents unwanted duplicates."
        )

        col_cat, col_mode = st.columns([1, 1])
        with col_cat:
            cat_display = st.selectbox(
                "Dataset Category",
                options=["Laptop Catalog (products)", "Support FAQs (faqs)", "Store Policies (policies)"],
            )
            cat_map = {
                "Laptop Catalog (products)": "products",
                "Support FAQs (faqs)": "faqs",
                "Store Policies (policies)": "policies",
            }
            dataset_type = cat_map[cat_display]

        with col_mode:
            import_mode = st.radio(
                "Duplicate Handling Strategy",
                options=["Skip duplicates (Default)", "Update/overwrite existing on ID match"],
                index=0,
                help="Skip mode protects existing catalog entries; update mode modifies fields when ID matches.",
            )
            mode_val = "skip" if "Skip" in import_mode else "update"

        # One-click demo loader for convenience
        with st.expander("⚡ Quick Seed: Ingest Bundled Hackathon Sample Datasets"):
            st.info("Quickly populate the database with the verified synthetic datasets from the `data/` directory.")
            if st.button("Ingest All Sample Files Now (Products, FAQs, Policies)", use_container_width=True):
                with st.spinner("Seeding datasets..."):
                    for file_path, dt, name in [
                        ("data/sample_products.csv", "products", "sample_products.csv"),
                        ("data/sample_faqs.csv", "faqs", "sample_faqs.csv"),
                        ("data/sample_policies.csv", "policies", "sample_policies.csv"),
                    ]:
                        if Path(file_path).exists():
                            df_sample = FileProcessor.read_file(file_path, name)
                            mapping = FileProcessor.auto_map_columns(list(df_sample.columns), dt)
                            df_mapped = FileProcessor.apply_mapping(df_sample, mapping)
                            valid, invalid = DataValidator.clean_and_validate(df_mapped, dt, name)
                            importer.import_records(valid, dt, name, mode="update", invalid_records=invalid)
                st.success("Successfully seeded 25 laptops, 15 FAQs, and official policies into MongoDB!")
                st.rerun()

        # Custom File Uploader
        uploaded_file = st.file_uploader(
            "Choose a file to upload (.csv, .xlsx, .xls)",
            type=["csv", "xlsx", "xls"],
        )

        if uploaded_file is not None:
            filename = uploaded_file.name
            try:
                df_raw = FileProcessor.read_file(uploaded_file, filename)
                st.success(f"Loaded **{filename}** ({len(df_raw)} total rows, {len(df_raw.columns)} columns).")

                # Dynamic Column Mapping
                st.markdown("#### 🔍 Dynamic Column Mapping")
                st.caption("Verify or adjust target column alignments before running validation.")

                auto_mapping = FileProcessor.auto_map_columns(list(df_raw.columns), dataset_type)
                canonical_keys = list(COLUMN_ALIASES.get(dataset_type, {}).keys())
                available_cols = ["-- Unmapped --"] + list(df_raw.columns)

                user_mapping: dict[str, str] = {}
                map_cols = st.columns(3)

                for idx, ckey in enumerate(canonical_keys):
                    default_choice = auto_mapping.get(ckey)
                    default_idx = (available_cols.index(default_choice) if default_choice in available_cols else 0)
                    with map_cols[idx % 3]:
                        sel = st.selectbox(
                            f"Target: `{ckey}`",
                            options=available_cols,
                            index=default_idx,
                            key=f"map_{dataset_type}_{ckey}",
                        )
                        if sel != "-- Unmapped --":
                            user_mapping[ckey] = sel

                # Preview Raw Data
                with st.expander("Preview Raw Uploaded Data (First 5 Rows)"):
                    st.dataframe(df_raw.head(5), use_container_width=True)

                if st.button("🚀 Validate & Ingest into MongoDB", type="primary", use_container_width=True):
                    with st.spinner("Validating records and writing to MongoDB..."):
                        # Apply mapping
                        df_mapped = FileProcessor.apply_mapping(df_raw, user_mapping)
                        valid_recs, invalid_recs = DataValidator.clean_and_validate(
                            df_mapped, dataset_type, filename
                        )

                        # Import into MongoDB
                        summary = importer.import_records(
                            valid_records=valid_recs,
                            dataset_type=dataset_type,
                            filename=filename,
                            mode=mode_val,
                            invalid_records=invalid_recs,
                        )

                    # Display Summary Metrics
                    st.markdown("### 📊 Ingestion Results Summary")
                    m1, m2, m3, m4, m5 = st.columns(5)
                    m1.metric("Total Rows", summary["total"])
                    m2.metric("Inserted", summary["inserted"])
                    m3.metric("Updated", summary["updated"])
                    m4.metric("Skipped", summary["skipped"])
                    m5.metric("Failed", summary["failed"])

                    if summary["failed"] > 0:
                        st.warning(f"{summary['failed']} row(s) failed validation. See details below:")
                        for err in summary["errors"][:10]:
                            st.write(f"- ⚠️ {err}")
                    else:
                        st.success(f"Dataset successfully imported with status: **{summary['status'].upper()}**!")

                    if get_db_manager().is_mock:
                        st.warning("⚠️ **Notice**: These records were saved into the temporary In-Memory Mock database because live MongoDB is not connected. To save directly to your real MongoDB, configure `MONGODB_URI` in `.env` or reconnect in the sidebar.")

            except Exception as e:
                st.error(f"Error processing file: {e}")

    # TAB 2: PDF Knowledge Base Manager
    with tabs[1]:
        st.subheader("📄 PDF Document Ingestion & Knowledge Base Manager")
        st.markdown(
            "Upload official store PDF documents (e.g. Return Policies, Warranty Terms, Product Catalogues, Store FAQs). "
            "Multi-page PDFs are parsed using `pypdf`, split into overlapping text chunks, deduplicated via SHA-256 hashes, "
            "and stored in MongoDB for grounded RAG query resolution."
        )

        with st.expander("⚡ Quick Seed: Ingest Bundled Store Policy PDF"):
            st.info("Populate the knowledge base with the verified 3-page synthetic store policy (`data/sample_store_policy.pdf`).")
            if st.button("Ingest data/sample_store_policy.pdf Now", use_container_width=True):
                sample_pdf_path = Path("data/sample_store_policy.pdf")
                if sample_pdf_path.exists():
                    with open(sample_pdf_path, "rb") as f:
                        res = kb_service.ingest_pdf(
                            file_input=f.read(),
                            filename="sample_store_policy.pdf",
                            category="Return Policy",
                            replace=True,
                        )
                    st.success(f"Successfully ingested {res['total_chunks']} chunks from {res['total_pages']} pages of 'sample_store_policy.pdf'!")
                    st.rerun()
                else:
                    st.error("sample_store_policy.pdf not found in data/ directory.")

        pdf_cat_col, pdf_rep_col = st.columns([2, 1])
        with pdf_cat_col:
            pdf_category = st.selectbox(
                "Document Category",
                options=[
                    "FAQs",
                    "Product Catalogue",
                    "Return Policy",
                    "Warranty Policy",
                    "Shipping Policy",
                    "Other Store Information",
                ],
                key="admin_pdf_cat",
            )
        with pdf_rep_col:
            pdf_replace = st.checkbox(
                "Replace existing document on filename match",
                value=False,
                key="admin_pdf_replace",
                help="If enabled, deletes prior chunks for this filename before importing new ones.",
            )

        uploaded_pdf = st.file_uploader(
            "Upload Store Document (.pdf)",
            type=["pdf"],
            key="admin_pdf_uploader",
        )

        if uploaded_pdf is not None:
            st.info(f"Selected PDF: **{uploaded_pdf.name}** ({uploaded_pdf.size:,} bytes)")
            if st.button("🚀 Extract & Ingest PDF into Knowledge Base", type="primary", use_container_width=True):
                with st.spinner("Extracting pages, chunking text, and storing into MongoDB..."):
                    pdf_res = kb_service.ingest_pdf(
                        file_input=uploaded_pdf.getvalue(),
                        filename=uploaded_pdf.name,
                        category=pdf_category,
                        replace=pdf_replace,
                    )

                m1, m2, m3, m4 = st.columns(4)
                m1.metric("Pages Extracted", pdf_res.get("total_pages", 0))
                m2.metric("Chunks Generated", pdf_res.get("total_chunks", 0))
                m3.metric("Chunks Inserted", pdf_res.get("inserted", 0))
                m4.metric("Chunks Skipped", pdf_res.get("skipped", 0))

                if pdf_res.get("status") in ["completed", "skipped"]:
                    st.success(f"Document **{pdf_res['filename']}** processed successfully ({pdf_res.get('status').upper()}).")
                else:
                    st.error(f"Ingestion failed: {pdf_res.get('error', 'Unknown error')}")

        st.markdown("---")
        st.markdown("### 📚 Stored PDF Documents in Knowledge Base")
        stored_docs = kb_service.list_stored_documents()

        if stored_docs:
            df_sdocs = pd.DataFrame(stored_docs)
            df_sdocs.rename(
                columns={
                    "filename": "Filename",
                    "category": "Category",
                    "max_page": "Pages Extracted",
                    "total_chunks": "Total Chunks",
                    "uploaded_at": "Uploaded At",
                },
                inplace=True,
            )
            st.dataframe(df_sdocs, use_container_width=True)

            del_col1, del_col2 = st.columns([3, 1])
            with del_col1:
                target_del = st.selectbox(
                    "Select Document to Remove",
                    options=[d["filename"] for d in stored_docs],
                    key="del_doc_select",
                )
            with del_col2:
                st.write("")
                st.write("")
                if st.button("🗑️ Delete Document", type="secondary", use_container_width=True):
                    del_count = kb_service.delete_document(target_del)
                    st.success(f"Removed document '{target_del}' ({del_count} chunks deleted).")
                    st.rerun()
        else:
            st.info("No PDF documents currently stored in the knowledge base. Upload a PDF above to get started.")

    # TAB 3: Live Database Catalog
    with tabs[2]:
        st.subheader("Live Database Documents")
        col_select = st.selectbox(
            "Select Collection to Inspect",
            options=["products", "faqs", "store_policies", config.COLLECTION_KNOWLEDGE_BASE],
        )

        collection = db[col_select]
        count = collection.count_documents({})
        st.markdown(f"**Total Documents in `{col_select}`**: `{count}`")

        if count > 0:
            docs = list(collection.find({}, {"_id": 0}).limit(100))
            df_docs = pd.DataFrame(docs)
            st.dataframe(df_docs, use_container_width=True)
            if st.button("Refresh Catalog View"):
                st.rerun()
        else:
            st.info(f"Collection `{col_select}` is currently empty. Use the 'File Ingestion' tab or Quick Seed button to load records.")

    # TAB 4: Audit Logs
    with tabs[3]:
        st.subheader("Ingestion Audit Trail")
        history = importer.get_import_history(limit=25)
        if history:
            df_hist = pd.DataFrame(history)
            st.dataframe(df_hist, use_container_width=True)
        else:
            st.info("No import batches recorded yet.")
