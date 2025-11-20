"""
Docling Document Processing Pipeline - Streamlit Application
Transforms unorganized files into AI-readable data using Docling (v2.62+)
"""

import streamlit as st
import os
import json
from pathlib import Path
from datetime import datetime
import tempfile
from typing import List, Dict, Any
import logging
import time

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Import Docling components (latest API)
from docling.document_converter import DocumentConverter, PdfFormatOption, WordFormatOption
from docling.datamodel.base_models import InputFormat
from docling.pipeline.standard_pdf_pipeline import StandardPdfPipeline
from docling.pipeline.simple_pipeline import SimplePipeline
from docling.backend.pypdfium2_backend import PyPdfiumDocumentBackend

class DoclingPipeline:
    """Pipeline for processing documents with Docling"""

    def __init__(self):
        self.converter = None
        self._initialize_converter()

    def _initialize_converter(self):
        """Initialize the document converter with multi-format support"""
        try:
            # Configure format options with default pipelines
            format_options = {
                InputFormat.PDF: PdfFormatOption(
                    pipeline_cls=StandardPdfPipeline,
                    backend=PyPdfiumDocumentBackend
                ),
                InputFormat.DOCX: WordFormatOption(
                    pipeline_cls=SimplePipeline
                ),
            }

            # Initialize converter with supported formats
            self.converter = DocumentConverter(
                allowed_formats=[
                    InputFormat.PDF,
                    InputFormat.DOCX,
                    InputFormat.PPTX,
                    InputFormat.HTML,
                    InputFormat.IMAGE,
                    InputFormat.XLSX,
                ],
                format_options=format_options
            )
            logger.info("Docling converter initialized successfully")
        except Exception as e:
            logger.error(f"Error initializing converter: {e}")
            # Fallback to default converter
            self.converter = DocumentConverter()

    def process_file(self, file_path: str) -> Dict[str, Any]:
        """Process a single document file"""
        try:
            start_time = time.time()
            result = self.converter.convert(file_path)
            processing_time = time.time() - start_time

            doc = result.document

            # Extract statistics
            stats = self._extract_statistics(doc)

            return {
                "status": "success",
                "file_name": Path(file_path).name,
                "markdown": doc.export_to_markdown(),
                "json": doc.export_to_dict(),
                "page_count": len(doc.pages),
                "processing_time": processing_time,
                "statistics": stats
            }
        except Exception as e:
            logger.error(f"Error processing file: {e}")
            return {
                "status": "error",
                "file_name": Path(file_path).name,
                "message": str(e)
            }

    def _extract_statistics(self, doc) -> Dict[str, Any]:
        """Extract document statistics"""
        stats = {
            "page_count": len(doc.pages),
            "table_count": 0,
            "image_count": 0,
            "figure_count": 0,
            "total_blocks": 0,
            "total_tokens": 0
        }

        try:
            for page in doc.pages:
                stats["total_blocks"] += len(page.blocks)
                for block in page.blocks:
                    # Check block kind
                    if hasattr(block, 'kind'):
                        block_kind = str(block.kind).lower()
                        if 'table' in block_kind:
                            stats["table_count"] += 1
                        elif 'image' in block_kind or 'picture' in block_kind:
                            stats["image_count"] += 1
                        elif 'figure' in block_kind:
                            stats["figure_count"] += 1

            # Estimate tokens (rough calculation: ~4 chars per token)
            markdown_content = doc.export_to_markdown()
            stats["total_tokens"] = len(markdown_content) // 4
        except Exception as e:
            logger.warning(f"Could not extract all statistics: {e}")

        return stats

    def process_batch(self, file_paths: List[str]) -> List[Dict[str, Any]]:
        """Process multiple files"""
        results = []
        for file_path in file_paths:
            results.append(self.process_file(file_path))
        return results


def show():
    # Try to import docling
    try:
        from docling.document_converter import DocumentConverter
        DOCLING_AVAILABLE = True
    except ImportError:
        DOCLING_AVAILABLE = False
        st.error("❌ Docling not installed. Run: pip install docling")

    st.title("⚡ Docling Document Processing Pipeline")
    st.markdown("Transform unorganized files into AI-readable data")

    if not DOCLING_AVAILABLE:
        st.stop()

    # Initialize session state
    if "processed_results" not in st.session_state:
        st.session_state.processed_results = []

    # Main layout
    col1, col2 = st.columns([3, 1])

    with col1:
        st.subheader("📤 Upload & Process Documents")

        uploaded_files = st.file_uploader(
            "Choose files to process",
            type=["pdf", "docx", "pptx", "xlsx", "html", "png", "jpg", "jpeg", "tiff"],
            accept_multiple_files=True
        )

        if uploaded_files:
            # Show file summary
            st.info(f"📋 Selected {len(uploaded_files)} file(s)")
            for f in uploaded_files:
                st.caption(f"• {f.name} ({f.size / 1024:.1f} KB)")

            if st.button("🚀 Process Documents", type="primary", use_container_width=True):
                if uploaded_files:
                    with st.spinner("⏳ Processing documents... This may take a moment"):
                        converter = DocumentConverter()
                        results = []

                        progress_bar = st.progress(0)

                        for idx, uploaded_file in enumerate(uploaded_files):
                            try:
                                # Save file temporarily
                                with tempfile.NamedTemporaryFile(
                                    delete=False,
                                    suffix=Path(uploaded_file.name).suffix,
                                    dir=tempfile.gettempdir()
                                ) as tmp_file:
                                    tmp_file.write(uploaded_file.getbuffer())
                                    tmp_path = tmp_file.name

                                # Process file
                                start_time = time.time()
                                result = converter.convert(tmp_path)
                                processing_time = time.time() - start_time

                                # Extract content
                                doc = result.document
                                markdown_content = doc.export_to_markdown()
                                json_content = doc.export_to_dict()

                                # Calculate statistics
                                page_count = len(doc.pages)
                                table_count = 0
                                image_count = 0

                                for page in doc.pages:
                                    for block in page.blocks:
                                        block_kind = str(block.kind).lower() if hasattr(block, 'kind') else ""
                                        if 'table' in block_kind:
                                            table_count += 1
                                        elif 'image' in block_kind or 'picture' in block_kind:
                                            image_count += 1

                                # Estimate tokens
                                token_count = len(markdown_content) // 4

                                results.append({
                                    "file_name": uploaded_file.name,
                                    "status": "success",
                                    "markdown": markdown_content,
                                    "json": json_content,
                                    "processing_time": processing_time,
                                    "stats": {
                                        "pages": page_count,
                                        "tables": table_count,
                                        "images": image_count,
                                        "tokens": token_count
                                    }
                                })

                                # Cleanup
                                try:
                                    os.unlink(tmp_path)
                                except:
                                    pass

                            except Exception as e:
                                results.append({
                                    "file_name": uploaded_file.name,
                                    "status": "error",
                                    "error": str(e)
                                })

                            progress_bar.progress((idx + 1) / len(uploaded_files))

                        st.session_state.processed_results = results

                    st.success("✅ Processing complete!")

    with col2:
        st.subheader("ℹ️ Info")
        st.markdown("""
        **Supported Formats:**
        - 📄 PDF
        - 📊 DOCX, PPTX
        - 📈 XLSX
        - 🌐 HTML
        - 🖼️ Images

        **Output:**
        - 📝 Markdown
        - 📋 JSON
        """)

    # Display results
    if st.session_state.processed_results:
        st.divider()
        st.subheader("📊 Results")

        successful = sum(1 for r in st.session_state.processed_results if r["status"] == "success")
        failed = len(st.session_state.processed_results) - successful

        col1, col2 = st.columns(2)
        with col1:
            st.metric("✅ Processed", successful)
        with col2:
            st.metric("❌ Failed", failed)

        st.divider()

        # Results for each file
        for idx, result in enumerate(st.session_state.processed_results):
            if result["status"] == "error":
                with st.expander(f"❌ {result['file_name']}"):
                    st.error(f"Error: {result['error']}")
            else:
                with st.expander(f"✅ {result['file_name']}", expanded=(idx == 0)):
                    # Statistics
                    col1, col2, col3, col4 = st.columns(4)
                    stats = result["stats"]

                    with col1:
                        st.metric("Pages", stats["pages"])
                    with col2:
                        st.metric("Tables", stats["tables"])
                    with col3:
                        st.metric("Images", stats["images"])
                    with col4:
                        st.metric("Tokens", f"{stats['tokens']:,}")

                    st.caption(f"⏱️ Processing time: {result['processing_time']:.2f}s")

                    st.divider()

                    # Tabs for output
                    tab1, tab2 = st.tabs(["📝 Markdown", "📋 JSON"])

                    with tab1:
                        st.text_area(
                            "Markdown Output",
                            result["markdown"],
                            height=300,
                            disabled=True,
                            key=f"md_{idx}"
                        )
                        col1, col2 = st.columns(2)
                        with col1:
                            st.download_button(
                                "⬇️ Download Markdown",
                                result["markdown"],
                                file_name=f"{Path(result['file_name']).stem}.md",
                                mime="text/markdown",
                                key=f"dl_md_{idx}"
                            )
                        with col2:
                            if st.button("📋 Copy", key=f"copy_md_{idx}"):
                                st.toast("Copied to clipboard!")

                    with tab2:
                        json_str = json.dumps(result["json"], indent=2)
                        st.text_area(
                            "JSON Output",
                            json_str,
                            height=300,
                            disabled=True,
                            key=f"json_{idx}"
                        )
                        col1, col2 = st.columns(2)
                        with col1:
                            st.download_button(
                                "⬇️ Download JSON",
                                json_str,
                                file_name=f"{Path(result['file_name']).stem}.json",
                                mime="application/json",
                                key=f"dl_json_{idx}"
                            )
                        with col2:
                            if st.button("📋 Copy", key=f"copy_json_{idx}"):
                                st.toast("Copied to clipboard!")

        st.divider()
        if st.button("🔄 Process More Files", use_container_width=True):
            st.session_state.processed_results = []
            st.rerun()
    else:
        st.info("👆 Upload documents above to get started")