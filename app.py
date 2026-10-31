import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# إعداد الصفحة الأساسي بعنوان عام
st.set_page_config(page_title="لوحة تحليلات البيانات الذكية - General Data Dashboard", layout="wide")

# شريط جانبي لاختيار اللغات والإعدادات
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

# عنوان عام للوحة التحكم
st.title("📊 لوحة تحليلات البيانات الذكية الشاملة" if is_arabic else "📊 General Data Analytics Dashboard")
st.markdown("---")

# رفع الملفات
st.sidebar.header("📁 رفع البيانات / Upload Data")
uploaded_file = st.sidebar.file_uploader(
    "ارفع ملف الإكسيل بأي صيغة" if is_arabic else "Upload your Excel file", 
    type=["xlsx", "xls"]
)

if uploaded_file is not None:
    try:
        xls = pd.ExcelFile(uploaded_file)
        sheet_names = xls.sheet_names
        
        selected_sheet = st.sidebar.selectbox(
            "اختر الورقة (Sheet) المطلوبة" if is_arabic else "Select Sheet", 
            sheet_names
        )
        
        df = pd.read_excel(uploaded_file, sheet_name=selected_sheet)
        
        st.success("تم رفع الملف بنجاح! جاري تحليل البيانات..." if is_arabic else "File successfully uploaded!")
        
        with st.expander("🔍 استعراض عينة من البيانات الخام" if is_arabic else "Preview Raw Data"):
            st.dataframe(df.head(10))
            
        cols = df.columns.tolist()
        
        st.sidebar.markdown("---")
        st.sidebar.subheader("🔗 ربط الأعمدة الذكي" if is_arabic else "Smart Column Mapping")
        
        cat_col = st.sidebar.selectbox("عمود التصنيف / الفئة (Category/Product)", cols, index=0 if len(cols)>0 else 0)
        date_col = st.sidebar.selectbox("عمود التاريخ (Date)", cols, index=1 if len(cols)>1 else 0)
        val_col = st.sidebar.selectbox("عمود القيمة أو العدد (Value/Sales)", cols, index=2 if len(cols)>2 else 0)
        
        # معالجة آمنة للتواريخ والقيم لمنع أي أخطاء
        df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
        df[val_col] = pd.to_numeric(df[val_col], errors='coerce')
        
        df = df.dropna(subset=[val_col])
        
        st.sidebar.markdown("---")
        st.sidebar.subheader("🔍 فلاتر البحث / Filters")
        
        if not df[date_col].isna().all():
            min_date = df[date_col].min().date()
            max_date = df[date_col].max().date()
            
            date_range = st.sidebar.date_input(
                "نطاق التواريخ / Date Range",
                [min_date, max_date]
            )
            
            if len(date_range) == 2:
                start_date, end_date = date_range
                mask = (df[date_col].dt.date >= start_date) & (df[date_col].dt.date <= end_date)
                df_filtered = df.loc[mask]
            else:
                df_filtered = df
        else:
            df_filtered = df
            
        st.subheader("📌 مؤشرات الأداء الرئيسية (KPIs)" if is_arabic else "Key Performance Indicators")
        
        total_val = df_filtered[val_col].sum()
        total_rows = len(df_filtered)
        avg_val = df_filtered[val_col].mean() if total_rows > 0 else 0
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("إجمالي القيمة / المجموع" if is_arabic else "Total Value", f"{total_val:,.2f}")
        with col2:
            st.metric("إجمالي عدد السطور/العمليات" if is_arabic else "Total Records", f"{total_rows:,}")
        with col3:
            st.metric("المتوسط" if is_arabic else "Average Value", f"{avg_val:,.2f}")
            
        st.markdown("---")
        
        st.subheader("📈 التحليل البصري والرسوم البيانية" if is_arabic else "Visualizations & Charts")
        
        col_a, col_b = st.columns(2)
        
        with col_a:
            if not df[date_col].isna().all():
                trend_data = df_filtered.groupby(df_filtered[date_col].dt.date)[val_col].sum().reset_index()
                fig_line = px.line(
                    trend_data, x=date_col, y=val_col, 
                    title="الخط الزمني للأداء" if is_arabic else "Timeline Trend",
                    template="plotly_white"
                )
                st.plotly_chart(fig_line, use_container_width=True)
            else:
                st.info("عمود التاريخ غير متوفر أو غير صالح للرسم الزمني.")
            
        with col_b:
            top_cats = df_filtered.groupby(cat_col)[val_col].sum().reset_index().nlargest(10, val_col)
            fig_bar = px.bar(
                top_cats, x=cat_col, y=val_col,
                title="أعلى التصنيفات / المنتجات" if is_arabic else "Top Categories",
                template="plotly_white"
            )
            st.plotly_chart(fig_bar, use_container_width=True)
            
        st.markdown("---")
        st.subheader("💡 الرؤى والتحليلات الذكية (AI Insights)" if is_arabic else "Smart Analytics & Insights")
        
        top_name = top_cats.iloc[0][cat_col] if not top_cats.empty else "N/A"
        top_val = top_cats.iloc[0][val_col] if not top_cats.empty else 0
        
        if is_arabic:
            st.info(f"""
            * **العنصر الأبرز:** العنصر **{top_name}** يحقق أعلى قيمة إجمالية بـ **{top_val:,.2f}**.
            * **توجيه عام:** يُنصح بالتركيز على العناصر الأعلى تأثيرًا لتحسين العوائد العامة وتقليل الهدر في العناصر الضعيفة.
            """)
        else:
            st.info(f"Top item is **{top_name}** with a value of **{top_val:,.2f}**.")
            
        st.markdown("---")
        st.subheader("📥 تصدير التقرير" if is_arabic else "Export Report")
        
        @st.cache_data
        def convert_df(df_to_export):
            return df_to_export.to_csv(index=False).encode('utf-8-sig')
        
        csv_data = convert_df(df_filtered)
        st.download_button(
            label="تحميل البيانات المفلترة (CSV)" if is_arabic else "Download Filtered Data",
            data=csv_data,
            file_name="general_analyzed_report.csv",
            mime="text/csv"
        )
        
    except Exception as e:
        st.error(f"حدث خطأ أثناء معالجة الملف: {e}" if is_arabic else f"Error processing file: {e}")
else:
    if is_arabic:
        st.warning("الرجاء رفع ملف إكسيل من القائمة الجانبية لعرض لوحة التحليلات والرسوم البيانية.")
    else:
        st.warning("Please upload an Excel file from the sidebar to start.")
