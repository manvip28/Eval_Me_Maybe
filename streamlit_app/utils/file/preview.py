"""File preview utilities for PDF and DOCX files"""
import streamlit as st

def preview_pdf_content(uploaded_file):
    """Preview PDF content"""
    try:
        import PyPDF2
        import io
        
        # Get file data and ensure it's bytes
        file_data = uploaded_file.getbuffer()
        
        # Convert memoryview to bytes if necessary
        if hasattr(file_data, 'tobytes'):
            file_data = file_data.tobytes()
        elif not isinstance(file_data, bytes):
            file_data = bytes(file_data)
        
        # Read PDF content
        pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_data))
        
        # Extract text from first few pages
        preview_text = ""
        max_pages = min(3, len(pdf_reader.pages))  # Show first 3 pages
        
        for page_num in range(max_pages):
            page = pdf_reader.pages[page_num]
            text = page.extract_text()
            preview_text += f"\n--- Page {page_num + 1} ---\n{text}\n"
        
        # Display preview
        st.markdown("### 📖 PDF Content Preview")
        st.markdown(f"**Total Pages:** {len(pdf_reader.pages)}")
        st.markdown(f"**Preview (First {max_pages} pages):**")
        
        with st.expander("📄 View PDF Content", expanded=True):
            st.text(preview_text[:2000] + "..." if len(preview_text) > 2000 else preview_text)
            
    except ImportError:
        st.warning("⚠️ PyPDF2 not available for PDF preview. Install with: pip install PyPDF2")
    except Exception as e:
        st.error(f"❌ Error reading PDF: {str(e)}")

def preview_docx_content(uploaded_file):
    """Preview DOCX content"""
    try:
        from docx import Document
        import io
        
        # Read DOCX content
        doc = Document(io.BytesIO(uploaded_file.getbuffer()))
        
        # Extract text content
        paragraphs = []
        for para in doc.paragraphs:
            if para.text.strip():
                paragraphs.append(para.text.strip())
        
        # Extract images info
        images = []
        for rel in doc.part.rels.values():
            if "image" in rel.target_ref:
                images.append(rel.target_ref)
        
        # Display preview
        st.markdown("### 📖 DOCX Content Preview")
        st.markdown(f"**Total Paragraphs:** {len(paragraphs)}")
        st.markdown(f"**Images Found:** {len(images)}")
        
        with st.expander("📄 View DOCX Content", expanded=True):
            # Show first few paragraphs
            preview_text = "\n\n".join(paragraphs[:10])  # First 10 paragraphs
            if len(paragraphs) > 10:
                preview_text += f"\n\n... and {len(paragraphs) - 10} more paragraphs"
            
            st.text(preview_text[:2000] + "..." if len(preview_text) > 2000 else preview_text)
            
            # Show images info
            if images:
                st.markdown("**🖼️ Images in document:**")
                for i, img in enumerate(images[:5]):  # Show first 5 images
                    st.markdown(f"- {img}")
                if len(images) > 5:
                    st.markdown(f"- ... and {len(images) - 5} more images")
                    
    except ImportError:
        st.warning("⚠️ python-docx not available for DOCX preview. Install with: pip install python-docx")
    except Exception as e:
        st.error(f"❌ Error reading DOCX: {str(e)}")


