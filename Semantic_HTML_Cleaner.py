import streamlit as st
from bs4 import BeautifulSoup

# ------------------ Semantic Mapping ------------------
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

def convert_html_content(html_content: str) -> str:
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

    return soup.prettify()

# ------------------ Streamlit UI ------------------
st.set_page_config(page_title="Semantic HTML Cleaner", layout="centered")

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
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="title">🧹 Semantic HTML Cleaner</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Upload your HTML file to remove <code>&lt;div&gt;</code> and <code>&lt;span&gt;</code> and convert to semantic tags.</div>', unsafe_allow_html=True)

st.markdown('<div class="upload-box">📤 Upload your HTML file below</div>', unsafe_allow_html=True)

uploaded_file = st.file_uploader("Choose an HTML file", type=["html", "htm"], label_visibility="collapsed")

if uploaded_file:
    html_content = uploaded_file.read().decode("utf-8", errors="ignore")

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("📄 Original HTML (Preview)")
        st.code(html_content[:2000], language="html")

    with col2:
        st.subheader("⚙️ Actions")
        if st.button("✨ Convert to Semantic HTML", use_container_width=True):
            cleaned_html = convert_html_content(html_content)

            st.success("Conversion complete! 🎉")

            st.download_button(
                label="⬇️ Download Cleaned HTML",
                data=cleaned_html,
                file_name="semantic_output.html",
                mime="text/html",
                use_container_width=True
            )

            st.subheader("✅ Cleaned Output (Preview)")
            st.code(cleaned_html[:2000], language="html")

else:
    st.info("👆 Upload an HTML file to get started.")
