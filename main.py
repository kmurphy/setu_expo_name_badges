import streamlit as st

from my_lib import *

from streamlit_pdf_viewer import pdf_viewer


# df_content = pd.read_csv("../df_student_content.csv")
# df_content[['Name','Number','Room']].to_csv("df_student_content.csv",index=False)

st.write("""
# Generate Name Tags
""")

st.write("### Step 1 - Specify the label size on the paper")

col1, col2 = st.columns(2)
with col1:
    st.write("**Label size**")
    width = st.number_input("Label width (in cm)", format="%.1f", step=0.1, min_value=0.0, max_value=10.0, value=7.5)
    height = st.number_input("Label height (in cm)", format="%.1f", step=0.1, min_value=0.0, max_value=10.0, value=4.0)
with col2:
    st.write("**Page margins**")
    left = st.number_input("Size of left margin (in cm)", format="%.1f", step=0.1, min_value=0.0, max_value=10.0, value=3.0)
    top = st.number_input("Size of top margin (in cm)", format="%.1f", step=0.1, min_value=0.0, max_value=10.0, value=3.0)
# with col3:
#     st.write("**Page layout**")
#     update_config(config, width, height, left, top)
#     df = clean_name_df(pd.read_excel("sample.xlsx"), drop_duplicates=False)
#     doc = generate_doc(df, config, first_page_only=True, debug=True)
#     doc.save("sample.pdf")
#     pdf_viewer("sample.pdf", width=300)

update_config(config, width, height, left, top)

st.write("### Step 1a - Tweak build settings")

config.draw_border = st.checkbox("Show border of name badges", value=False, 
    help="Draw border to help placement of items. You probably want to turn this off when you are ready to print the name tags. ")

config.draw_internal_borders = st.checkbox("Show border of name badge components", value=False, 
    help="Draw border to help placement of items. You CERTAINLY want to turn this off when you are ready to print the name tags. ")

# config.INNER_SEP = st.number_input("Size of inner margin on name badges (in pts)", step=1, min_value=0, max_value=20, value=10)

df = clean_name_df(pd.read_excel("data/sample.xlsx"), drop_duplicates=False)
doc = generate_doc(df, config, first_page_only=True, debug=False)
# doc.save("sample_4837592752.pdf")
# with open('sample_4837592752.pdf', 'rb') as f:
st.download_button("Download Sample PDF with empty labels", doc.tobytes(), file_name="sample.pdf", mime="application/pdf")

st.write("### Step 2 - Upload mailing list")

uploaded_file = st.file_uploader("Upload mailing list as an Excel or CSV file", 
    type=["xlsx", "csv"]) 

if uploaded_file is not None:

    if uploaded_file.name.endswith('.csv'):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    df = clean_name_df(df)

    st.write("The first few rows of the uploaded mailing list are:")
    st.dataframe(df.head())

    doc = generate_doc(df, config, debug=False)

    if doc is not None:
        doc.save("name_badges.pdf")    
    
        st.write("### Step 3 - Download the generated PDF of name badges")
        with open('name_badges.pdf', 'rb') as f:
            st.download_button("Download PDF", f, file_name="name_badges.pdf", type="primary", mime="application/pdf")
