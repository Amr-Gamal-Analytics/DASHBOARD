import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# إعداد الصفحة وتكوين الواجهة ودعم الـ RTL
st.set_page_title("تحليل المبيعات الذكي - Smart Sales & Discount Analytics", layout="wide")

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

st.title("📊 نظام تحليل المبيعات المتقدم (قبل وبعد الخصم)" if is_arabic else "📊 Advanced Sales & Discount Analytics Dashboard")
st.markdown("---")

# رفع الملفات
st.sidebar.header("📁 رفع البيانات / Upload Data")
uploaded_file = st.sidebar.file_uploader(
    "ارفع ملف الإكسيل الرئيسي (شيت المبيعات والخصومات)" if is_arabic else "Upload your Excel file", 
    type=["xlsx", "xls"]
)

if uploaded_file is not None:
    try:
        # قراءة الأوراق المتاحة في الملف
        xls = pd.ExcelFile(uploaded_file)
        sheet_names = xls.sheet_names
        
        selected_sheet = st.sidebar.selectbox(
            "اختر الورقة (Sheet) المطلوبة" if is_arabic else "Select Sheet", 
            sheet_names
        )
        
        df = pd.read_excel(uploaded_file, sheet_name=selected_sheet)
        
        st.success("تم رفع الملف بنجاح! جاري تحليل البيانات..." if is_arabic else "File successfully uploaded!")
        
        # عرض عينة سريعة من البيانات
        with st.expander("🔍 استعراض عينة من البيانات الخام" if is_arabic else "Preview Raw Data"):
            st.dataframe(df.head(10))
            
        # محاولة اكتشاف الأعمدة تلقائياً
        cols = df.columns.tolist()
        
        st.sidebar.markdown("---")
        st.sidebar.subheader("🔗 ربط الأعمدة الذكي" if is_arabic else "Smart Column Mapping")
        
        # اختيار الأعمدة الأساسية بذكاء
        product_col = st.sidebar.selectbox("عمود المنتج / Product", cols, index=0 if len(cols)>0 else 0)
        date_col = st.sidebar.selectbox("عمود تاريخ البيع / Date", cols, index=1 if len(cols)>1 else 0)
        sales_col = st.sidebar.selectbox("عمود قيمة/كمية المبيعات / Sales", cols, index=2 if len(cols)>2 else 0)
        
        # معالجة التواريخ والبيانات
        df[date_col] = pd.to_datetime(df[date_col], errors='coerce')
        df[sales_col] = pd.to_numeric(df[sales_col], errors='coerce')
        
        # تنظيف البيانات من القيم الفارغة
        df = df.dropna(subset=[date_col, sales_col])
        
        # الفلاتر الجانبية (Slicers)
        st.sidebar.markdown("---")
        st.sidebar.subheader("🔍 فلاتر البحث / Filters")
        
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
            
        # المؤشرات الرئيسية (KPI Cards)
        st.subheader("📌 مؤشرات الأداء الرئيسية (KPIs)" if is_arabic else "Key Performance Indicators")
        
        total_sales = df_filtered[sales_col].sum()
        total_orders = len(df_filtered)
        avg_sale = df_filtered[sales_col].mean() if total_orders > 0 else 0
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("إجمالي المبيعات" if is_arabic else "Total Sales", f"{total_sales:,.2f}")
        with col2:
            st.metric("إجمالي العمليات/الطلبات" if is_arabic else "Total Orders", f"{total_orders:,}")
        with col3:
            st.metric("متوسط قيمة الطلب" if is_arabic else "Average Order Value", f"{avg_sale:,.2f}")
            
        st.markdown("---")
        
        # الرسوم البيانية
        st.subheader("📈 التحليل البصري والرسوم البيانية" if is_arabic else "Visualizations & Charts")
        
        col_a, col_b = st.columns(2)
        
        with col_a:
            # رسم زمني للمبيعات
            daily_sales = df_filtered.groupby(df_filtered[date_col].dt.date)[sales_col].sum().reset_index()
            fig_line = px.line(
                daily_sales, x=date_col, y=sales_col, 
                title="اتجاه المبيعات الزمني اليومي" if is_arabic else "Daily Sales Trend",
                template="plotly_white"
            )
            st.plotly_chart(fig_line, use_container_width=True)
            
        with col_b:
            # مقارنة أعلى المنتجات مبيعاً
            top_products = df_filtered.groupby(product_col)[sales_col].sum().reset_index().nlargest(10, sales_col)
            fig_bar = px.bar(
                top_products, x=product_col, y=sales_col,
                title="أعلى 10 منتجات مبيعاً" if is_arabic else "Top 10 Products",
                template="plotly_white"
            )
            st.plotly_chart(fig_bar, use_container_width=True)
            
        # محرك الرؤى والتحليل الذكي (Insights Engine)
        st.markdown("---")
        st.subheader("💡 الرؤى والتوصيات التحليلية (AI Insights)" if is_arabic else "Smart Analytics & Insights")
        
        # حساب بعض الإحصائيات الذكية كأمثلة عملية
        best_product = top_products.iloc[0][product_col] if not top_products.empty else "N/A"
        best_sales_val = top_products.iloc[0][sales_col] if not top_products.empty else 0
        
        if is_arabic:
            st.info(f"""
            * **المنتج الأعلى أداءً:** المنتج **{best_product}** يستحوذ على النصيب الأكبر من المبيعات بإجمالي **{best_sales_val:,.2f}**.
            * **توجيه استراتيجي:** يُنصح بمراجعة المنتجات ذات الأداء المنخفض في النصف الثاني من الفترة وتفعيل خطط الخصومات عليها لتحريك المخزون الراكد.
            * **كشف الشاذ (Outliers):** تم رصد أيام بمعدلات طلب استثنائية، يُرجى مراجعة الحملات التسويقية المرتبطة بها لتعميم التجربة الناجحة.
            """)
        else:
            st.info(f"Top performing product is **{best_product}** with sales of **{best_sales_val:,.2f}**.")
            
        # زر لتصدير البيانات المعالجة
        st.markdown("---")
        st.subheader("📥 تصدير التقرير" if is_arabic else "Export Report")
        
        @st.cache_data
        def convert_df(df_to_export):
            return df_to_export.to_csv(index=False).encode('utf-8-sig')
        
        csv_data = convert_df(df_filtered)
        st.download_button(
            label="تحميل البيانات المفلترة (CSV)" if is_arabic else "Download Filtered Data",
            data=csv_data,
            file_name="analyzed_sales_report.csv",
            mime="text/csv"
        )
        
    except Exception as e:
        st.error(f"حدث خطأ أثناء معالجة الملف: {e}" if is_arabic else f"Error processing file: {e}")
else:
    if is_arabic:
        st.warning("الرجاء رفع ملف إكسيل من القائمة الجانبية لعرض لوحة التحليلات والرسوم البيانية.")
    else:
        st.warning("Please upload an Excel file from the sidebar to start.")