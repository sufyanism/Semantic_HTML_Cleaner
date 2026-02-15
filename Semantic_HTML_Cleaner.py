import streamlit as st
from bs4 import BeautifulSoup
import zipfile
import io

# Semantic mapping
SEMANTIC_MAP = {
    "header": "header",
    "nav": "nav",
    "navbar": "nav",
    "menu": "nav",
    "main": "main",
    "content": "main",
    "section": "section",
    "article": "article",
    "post": "article",
    "footer": "footer",
    "sidebar": "aside",
    "aside": "aside"
}

def guess_semantic_tag(tag):
    class_id = " ".join(tag.get("class", [])) + " " + (tag.get("id") or "")
    class_id = class_id.lower()
    for key, semantic in SEMANTIC_MAP.items():
        if key in class_id:
            return semantic
    return None

def convert_html_content(html_content):
    soup = BeautifulSoup(html_content, "lxml")
    for tag in soup.find_all(["div", "span"]):
        semantic = guess_semantic_tag(tag)
        if semantic:
            new_tag = soup.new_tag(semantic)
            new_tag.attrs = tag.attrs
            new_tag.extend(tag.contents)
            tag.replace_with(new_tag)
        else:
            tag.unwrap()
    # Remove empty tags
    remove_empty_tags(soup)
    return soup.prettify()

def remove_empty_tags(soup):
    """
    Recursively remove tags with no content or only whitespace.
    """
    for tag in soup.find_all():
        if not tag.contents or all(
            (str(content).strip() == "" if isinstance(content, str) else False)
            for content in tag.contents
        ):
            tag.decompose()

def is_valid_epub(file_bytes):
    try:
        with zipfile.ZipFile(io.BytesIO(file_bytes)) as z:
            if 'mimetype' in z.namelist():
                mimetype_content = z.read('mimetype').decode('utf-8').strip()
                return mimetype_content == 'application/epub+zip'
            else:
                return False
    except zipfile.BadZipFile:
        return False

st.set_page_config(page_title="Semantic HTML Cleaner & EPUB Validator", layout="centered")

st.markdown("""
<style>
    .title {
        font-size: 2.2rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    .subtitle {
        color: #6c757d;
        margin-bottom: 1.5rem;
    }
    .upload-box {
        padding: 1.5rem;
        border: 2px dashed #dee2e6;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 1.5rem;
        background: #fafafa;
    }
    /* Style for scrollable preview */
    .scrollable-preview {
        max-height: 300px;
        overflow-y: auto;
        border: 1px solid #ccc;
        padding: 10px;
        background-color: #f8f9fa;
        border-radius: 5px;
        margin-top: 1rem;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="title">🧹 Semantic HTML Cleaner & EPUB Validator</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Upload your HTML or EPUB file for validation and cleaning.</div>', unsafe_allow_html=True)

st.markdown('<div class="upload-box">📤 Upload your HTML or EPUB file below</div>', unsafe_allow_html=True)

uploaded_file = st.file_uploader("Choose an HTML or EPUB file", type=["html", "epub"])

if uploaded_file:
    # Read the file bytes
    file_bytes = uploaded_file.read()
    filename = uploaded_file.name

    # Check if EPUB and validate
    if filename.lower().endswith('.epub'):
        is_epub_valid = is_valid_epub(file_bytes)
        if is_epub_valid:
            st.success("✅ Valid EPUB file detected!")
        else:
            st.error("❌ Invalid EPUB file or corrupted file.")
        uploaded_file.seek(0)

    # If HTML file, decode content
    if filename.lower().endswith('.html') or filename.lower().endswith('.htm'):
        html_content = file_bytes.decode("utf-8", errors="ignore")

        # Show convert button
        if st.button("✨ Convert to Semantic HTML"):
            cleaned_html = convert_html_content(html_content)
            filename_base = filename.replace('.html', '').replace('.htm', '')
            semantic_filename = filename_base + "_semantic.html"

            st.success("Conversion complete! 🎉")
            st.download_button(
                label="⬇️ Download Cleaned HTML",
                data=cleaned_html,
                file_name=semantic_filename,
                mime="text/html"
            )

            # Display scrollable preview of cleaned HTML
            st.subheader("📝 Cleaned HTML Preview")
            with st.container():
                st.markdown(
                    f'<div class="scrollable-preview"><pre>{cleaned_html}</pre></div>',
                    unsafe_allow_html=True
                )
    else:
        st.info("Please upload a valid HTML or EPUB file.")
else:
    st.info("👆 Upload an HTML or EPUB file to get started.")
