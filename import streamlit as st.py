import streamlit as st

st.set_page_config(layout="wide")
st.title("კომპანიების ანალიზი - ფაილების ატვირთვა და არჩევანი")

# File uploaders
report_file = st.file_uploader("ატვირთე ანგარიშფაქტურების ფაილი (report.xlsx)", type=["xlsx"])
statement_files = st.file_uploader("ატვირთე საბანკო ამონაწერის ფაილები (statement.xlsx)", type=["xlsx"], accept_multiple_files=True)

# Show buttons after file upload
if report_file and statement_files:
    st.success("ფაილები წარმატებით აიტვირთა. აირჩიე მოქმედება:")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📄 ანგარიშფაქტურები"):
            st.session_state['action'] = 'invoice'
    with col2:
        if st.button("💰 ჩარიცხვები"):
            st.session_state['action'] = 'deposit'

    if 'action' in st.session_state:
        st.write(f"✅ არჩეულია: {st.session_state['action']}")
