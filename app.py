import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# إعداد الصفحة
st.set_page_config(page_title="تحليل مبيعات الخصومات - Sales & Discount Dashboard", layout="wide")

st.sidebar.title("إعدادات التقرير / Settings")
lang = st.sidebar.selectbox("اختر اللغة / Language", ["العربية (Arabic)", "English"])
is_arabic = "العربية" in lang

if is_arabic:
    st.markdown("""
        <style>
            body, div, p, span, h1, h2, h3, h4, h5, h6 {
                direction: rtl;
                text-align: right;
            }
        </style>
    """, unsafe_allow_html=True)

st.title("📊 لوحة تحليلات المنتجات والخصومات ومبيعات ٢٠٢٦" if is_arabic else "📊 Discount & Sales Analytics Dashboard")
st.markdown("---")

# رفع الملفات
st.sidebar.header("📁 رفع البيانات / Upload Data")
uploaded_file = st.sidebar.file_uploader(
    "ارفع ملف الإكسيل الخاص بك" if is_arabic else "Upload your Excel file", 
    type=["xlsx", "xls"]
)

if uploaded_file is not None:
    try:
        xls = pd.ExcelFile(uploaded_file)
        sheet_names = xls.sheet_names
        
        selected_sheet = st.sidebar.selectbox(
            "اختر الورقة (Sheet)" if is_arabic else "Select Sheet", 
            sheet_names
        )
        
        df = pd.read_excel(uploaded_file, sheet_name=selected_sheet)
        st.success("تم رفع وتحليل الملف بنجاح!" if is_arabic else "File successfully uploaded!")
        
        with st.expander("🔍 استعراض عينة من البيانات" if is_arabic else "Preview Data"):
            st.dataframe(df.head(10))
            
        cols = df.columns.tolist()
        
        st.sidebar.markdown("---")
        st.sidebar.subheader("🔗 ربط الأعمدة" if is_arabic else "Column Mapping")
        
        # اختيار الأعمدة الافتراضية بناءً على شيتك
        default_prod = "المسمي" if "المسمي" in cols else cols[0]
        default_sales = "sales 26" if "sales 26" in cols else (cols[16] if len(cols)>16 else cols[0])
        default_price = "سعر شامل ض" if "سعر شامل ض" in cols else cols[0]
        
        product_col = st.sidebar.selectbox("عمود اسم المنتج / الصنف", cols, index=cols.index(default_prod) if default_prod in cols else 0)
        sales_col = st.sidebar.selectbox("عمود مبيعات سنة 2026 (sales 26)", cols, index=cols.index(default_sales) if default_sales in cols else 0)
        price_col = st.sidebar.selectbox("عمود السعر أو القيمة", cols, index=cols.index(default_price) if default_price in cols else 0)
        
        # تحويل القيم لأرقام لتجنب أي أخطاء
        df[sales_col] = pd.to_numeric(df[sales_col], errors='coerce').fillna(0)
        df[price_col] = pd.to_numeric(df[price_col], errors='coerce').fillna(0)
        
        # الفلاتر الجانبية
        st.sidebar.markdown("---")
        st.sidebar.subheader("🔍 فلاتر البحث" if is_arabic else "Filters")
        
        if "اسم المورد" in cols:
            suppliers = ["الكل / All"] + list(df["اسم المورد"].dropna().unique())
            selected_supplier = st.sidebar.selectbox("تصفية حسب المورد", suppliers)
            if selected_supplier != "الكل / All":
                df = df[df["اسم المورد"] == selected_supplier]
                
        # المؤشرات الرئيسية (KPIs)
        st.subheader("📌 مؤشرات الأداء الرئيسية (KPIs)" if is_arabic else "Key Performance Indicators")
        
        total_sales_26 = df[sales_col].sum()
        total_items = len(df)
        total_revenue_potential = (df[sales_col] * df[price_col]).sum()
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("إجمالي مبيعات 2026 (qtys/sales)", f"{total_sales_26:,.2f}")
        with col2:
            st.metric("إجمالي عدد أصناف الخصومات", f"{total_items:,}")
        with col3:
            st.metric("إجمالي القيمة المحتملة", f"{total_revenue_potential:,.2f}")
            
        st.markdown("---")
        
        # الرسوم البيانية
        st.subheader("📈 التحليل البصري والرسوم البيانية" if is_arabic else "Visualizations & Charts")
        
        col_a, col_b = st.columns(2)
        
        with col_a:
            if "اسم المورد" in cols:
                supplier_sales = df.groupby("اسم المورد")[sales_col].sum().reset_index().nlargest(10, sales_col)
                fig_bar = px.bar(
                    supplier_sales, x="اسم المورد", y=sales_col,
                    title="أعلى الموردين حسب المبيعات" if is_arabic else "Top Suppliers by Sales",
                    template="plotly_white"
                )
                st.plotly_chart(fig_bar, use_container_width=True)
            else:
                st.info("عمود اسم المورد غير متوفر.")
                
        with col_b:
            top_products = df.groupby(product_col)[sales_col].sum().reset_index().nlargest(10, sales_col)
            fig_top = px.bar(
                top_products, x=product_col, y=sales_col,
                title="أعلى المنتجات مبيعاً" if is_arabic else "Top Products",
                template="plotly_white"
            )
            st.plotly_chart(fig_top, use_container_width=True)
            
        st.markdown("---")
        st.subheader("💡 الرؤى والتوصيات الذكية" if is_arabic else "Smart Insights")
        
        st.info(f"""
        * **إجمالي وحدات المبيعات المسجلة لعام 2026:** {total_sales_26:,.2f} وحدة عبر {total_items} صنف خاضع للخصم.
        * **توجيه تحليل البيانات:** تم ربط الأعمدة الفعلية لشيتك بنجاح، مما يتيح لك تصفية النتائج بحرية عبر القائمة الجانبية ومراقبة تأثير الخصومات بدقة.
        """)
        
        # تصدير التقرير
        st.markdown("---")
        st.subheader("📥 تصدير البيانات" if is_arabic else "Export")
        
        @st.cache_data
        def convert_df(df_to_export):
            return df_to_export.to_csv(index=False).encode('utf-8-sig')
            
        csv_data = convert_df(df)
        st.download_button(
            label="تحميل التقرير كملف CSV" if is_arabic else "Download Report",
            data=csv_data,
            file_name="discount_analysis_report.csv",
            mime="text/csv"
        )
        
    except Exception as e:
        st.error(f"خطأ في قراءة ملف الإكسيل: {e}" if is_arabic else f"Error: {e}")
else:
    if is_arabic:
        st.warning("الرجاء رفع ملف الإكسيل (discount items sales.xlsx) من القائمة الجانبية لعرض التحليلات.")
    else:
        st.warning("Please upload your Excel file from the sidebar.")
