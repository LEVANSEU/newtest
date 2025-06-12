import streamlit as st
import pandas as pd
import io
from openpyxl import Workbook
import re

st.set_page_config(layout="wide")
st.title("📑 ანგარიშფაქტურების ანალიზი")

report_file = st.file_uploader("ატვირთე ანგარიშფაქტურების ფაილი (report.xlsx)", type=["xlsx"])
statement_files = st.file_uploader("ატვირთე საბანკო ამონაწერის ფაილები (statement.xlsx)", type=["xlsx"], accept_multiple_files=True)

if report_file and statement_files:
    # Show action buttons
    col1, col2 = st.columns([1, 1])
    with col1:
        show_invoices = st.button("📄 ანგარიშფაქტურები")
    with col2:
        show_transactions = st.button("💵 ჩარიცხვები")

    purchases_df = pd.read_excel(report_file, sheet_name='Grid')
    purchases_df['დასახელება'] = purchases_df['გამყიდველი'].astype(str).apply(lambda x: re.sub(r'^\(\d+\)\s*', '', x).strip())
    purchases_df['საიდენტიფიკაციო კოდი'] = purchases_df['გამყიდველი'].apply(lambda x: ''.join(re.findall(r'\d', str(x)))[:11])

    bank_dfs = []
    for file in statement_files:
        df = pd.read_excel(file)
        df['P'] = df.iloc[:, 15].astype(str).str.strip()
        df['Amount'] = pd.to_numeric(df.iloc[:, 3], errors='coerce').fillna(0)
        bank_dfs.append(df)

    bank_df = pd.concat(bank_dfs, ignore_index=True)

    wb = Workbook()
    wb.remove(wb.active)

    ws1 = wb.create_sheet(title="ანგარიშფაქტურები კომპანიით")
    ws1.append(['დასახელება', 'საიდენტიფიკაციო კოდი', 'ანგარიშფაქტურების ჯამი', 'ჩარიცხული თანხა', 'სხვაობა'])

    company_summaries = []

    for company_id, group in purchases_df.groupby('საიდენტიფიკაციო კოდი'):
        company_name = group['დასახელება'].iloc[0]
        unique_invoices = group.groupby('სერია №')['ღირებულება დღგ და აქციზის ჩათვლით'].sum().reset_index()
        company_invoice_sum = unique_invoices['ღირებულება დღგ და აქციზის ჩათვლით'].sum()
        paid_sum = bank_df[bank_df["P"] == str(company_id)]["Amount"].sum()
        difference = company_invoice_sum - paid_sum

        ws1.append([company_name, company_id, company_invoice_sum, paid_sum, difference])
        company_summaries.append((company_name, company_id, company_invoice_sum, paid_sum, difference))

    output = io.BytesIO()
    wb.save(output)
    output.seek(0)

    if show_invoices:
        st.subheader("📋 კომპანიების ჩამონათვალი")

        search_code = st.text_input("🔎 ჩაწერე საიდენტიფიკაციო კოდი:", "")
        sort_column = st.selectbox("📊 დალაგების ველი", ["ინვოისების ჯამი", "ჩარიცხვა", "სხვაობა"])
        sort_order = st.radio("⬆️⬇️ დალაგების ტიპი", ["ზრდადობით", "კლებადობით"], horizontal=True)

        sort_index = {"ინვოისების ჯამი": 2, "ჩარიცხვა": 3, "სხვაობა": 4}[sort_column]
        reverse = sort_order == "კლებადობით"

        filtered_summaries = company_summaries
        if search_code.strip():
            filtered_summaries = [item for item in company_summaries if item[1] == search_code.strip()]

        filtered_summaries = sorted(filtered_summaries, key=lambda x: x[sort_index], reverse=reverse)

        st.markdown("""
        <div class='summary-header'>
            <div style='display: flex; font-weight: bold; background-color: #f0f0f0; padding: 10px;'>
                <div style='flex: 2;'>დასახელება</div>
                <div style='flex: 2;'>საიდენტიფიკაციო კოდი</div>
                <div style='flex: 1.5;'>ინვოისების ჯამი</div>
                <div style='flex: 1.5;'>ჩარიცხვა</div>
                <div style='flex: 1.5;'>სხვაობა</div>
            </div>
        """, unsafe_allow_html=True)

        for name, company_id, invoice_sum, paid_sum, difference in filtered_summaries:
            col1, col2, col3, col4, col5 = st.columns([2, 2, 1.5, 1.5, 1.5])
            with col1:
                st.markdown(name)
            with col2:
                st.markdown(f"{company_id}")
            with col3:
                st.markdown(f"<div class='number-cell'>{invoice_sum:,.2f}</div>", unsafe_allow_html=True)
            with col4:
                st.markdown(f"<div class='number-cell'>{paid_sum:,.2f}</div>", unsafe_allow_html=True)
            with col5:
                st.markdown(f"<div class='number-cell'>{difference:,.2f}</div>", unsafe_allow_html=True)

        st.download_button(
            label="⬇️ ჩამოტვირთე Excel ფაილი",
            data=output,
            file_name="ანგარიშფაქტურები.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
