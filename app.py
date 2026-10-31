import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# إعداد الصفحة وتوسيع العرض
st.set_page_config(page_title="لوحة تحليلات المبيعات والخصومات المتقدمة", layout="wide")

st.sidebar.title("⚙️ لوحة التحكم والإعدادات")
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

st.title("📊 لوحة تحليلات المبيعات والخصومات الاحترافية (Power BI Style)" if is_arabic else "📊 Professional Sales & Discount Analytics Dashboard")
st.markdown("---")

# رفع الملفات
st.sidebar.header("📁 بيانات الملف")
uploaded_file = st.sidebar.file_uploader(
    "ارفع شيت الإكسيل (discount items sales.xlsx)" if is_arabic else "Upload Excel file", 
    type=["xlsx", "xls"]
)

if uploaded_file is not None:
    try:
        xls = pd.ExcelFile(uploaded_file)
        sheet_names = xls.sheet_names
        selected_sheet = st.sidebar.selectbox("اختر الشيت (Sheet)", sheet_names)
        
        df = pd.read_excel(uploaded_file, sheet_name=selected_sheet)
        st.success("تم تحليل الشيت وعرض لوحة القيادة بنجاح!" if is_arabic else "Dashboard loaded successfully!")
        
        cols = df.columns.tolist()
        
        # الفلاتر الجانبية التفاعلية
        st.sidebar.markdown("---")
        st.sidebar.subheader("🔍 فلاتر التصفية الذكية")
        
        # تصفية حسب المورد
        if "اسم المورد" in cols:
            suppliers = ["الكل"] + list(df["اسم المورد"].dropna().unique())
            sel_sup = st.sidebar.selectbox("تصفية حسب المورد", suppliers)
            if sel_sup != "الكل":
                df = df[df["اسم المورد"] == sel_sup]
                
        # تصفية حسب نوع المورد
        if "نوع المورد" in cols:
            types = ["الكل"] + list(df["نوع المورد"].dropna().unique())
            sel_type = st.sidebar.selectbox("نوع المورد", types)
            if sel_type != "الكل":
                df = df[df["نوع المورد"] == sel_type]

        # تنظيف وتحويل الأعمدة الرقمية أساس المقارنة
        sales_26_col = "sales 26" if "sales 26" in cols else cols[0]
        sales_25_col = "sales 25" if "sales 25" in cols else cols[0]
        sales_24_col = "sales 24" if "sales 24" in cols else cols[0]
        discount_col = "الخصم الجديد" if "الخصم الجديد" in cols else cols[0]
        price_col = "سعر شامل ض" if "سعر شامل ض" in cols else cols[0]
        prod_col = "المسمي" if "المسمي" in cols else cols[0]

        df[sales_26_col] = pd.to_numeric(df[sales_26_col], errors='coerce').fillna(0)
        df[sales_25_col] = pd.to_numeric(df[sales_25_col], errors='coerce').fillna(0)
        df[sales_24_col] = pd.to_numeric(df[sales_24_col], errors='coerce').fillna(0)
        df[discount_col] = pd.to_numeric(df[discount_col], errors='coerce').fillna(0)
        df[price_col] = pd.to_numeric(df[price_col], errors='coerce').fillna(0)

        # بطاقات مؤشرات الأداء الرئيسية (KPIs)
        st.subheader("📌 مؤشرات الأداء الرئيسية (KPI Cards)")
        tot_s26 = df[sales_26_col].sum()
        tot_s25 = df[sales_25_col].sum()
        tot_s24 = df[sales_24_col].sum()
        total_items_count = len(df)
        avg_disc = df[discount_col].mean()

        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.metric("مبيعات 2026", f"{tot_s26:,.0f}", delta=f"{tot_s26 - tot_s25:,.0f} vs 2025")
        with c2:
            st.metric("مبيعات 2025", f"{tot_s25:,.0f}")
        with c3:
            st.metric("إجمالي عدد الأصناف", f"{total_items_count:,}")
        with c4:
            st.metric("متوسط نسبة الخصم الجديد", f"{avg_disc:.1f}%")

        st.markdown("---")

        # شبكة الرسوم البيانية المتنوعة والاحترافية (6 Charts)
        st.subheader("📈 التحليلات البصرية المتقدمة (Visualizations)")

        # الصف الأول من الرسوم
        col_r1_1, col_r1_2 = st.columns(2)
        
        with col_r1_1:
            # 1. مقارنة المبيعات عبر الأعوام (2024 vs 2025 vs 2026)
            yearly_data = pd.DataFrame({
                'السنة': ['2024', '2025', '2026'],
                'إجمالي المبيعات': [tot_s24, tot_s25, tot_s26]
            })
            fig_years = px.bar(
                yearly_data, x='السنة', y='إجمالي المبيعات', 
                title="مقارنة إجمالي المبيعات عبر الأعوام (2024 - 2026)",
                color='السنة', template="plotly_white"
            )
            st.plotly_chart(fig_years, use_container_width=True)

        with col_r1_2:
            # 2. توزيع قيم الخصومات الجديدة
            fig_disc = px.histogram(
                df, x=discount_col, 
                title="توزيع نسب الخصومات الجديدة على الأصناف",
                template="plotly_white", color_discrete_sequence=['indianred']
            )
            st.plotly_chart(fig_disc, use_container_width=True)

        # الصف الثاني من الرسوم
        col_r2_1, col_r2_2 = st.columns(2)

        with col_r2_1:
            # 3. أعلى 10 منتجات مبيعاً في 2026
            top_prods = df.nlargest(10, sales_26_col)
            fig_top = px.bar(
                top_prods, x=sales_26_col, y=prod_col, orientation='h',
                title="أعلى 10 منتجات مبيعاً لعام 2026",
                template="plotly_white", color=sales_26_col
            )
            fig_top.update_layout(yaxis={'categoryorder':'total ascending'})
            st.plotly_chart(fig_top, use_container_width=True)

        with col_r2_2:
            # 4. أداء الموردين (إجمالي مبيعات 2026 لكل مورد)
            if "اسم المورد" in cols:
                sup_perf = df.groupby("اسم المورد")[sales_26_col].sum().reset_index().nlargest(10, sales_26_col)
                fig_sup = px.bar(
                    sup_perf, x="اسم المورد", y=sales_26_col,
                    title="أداء الموردين (أعلى 10 موردين في مبيعات 2026)",
                    template="plotly_white", color=sales_26_col
                )
                st.plotly_chart(fig_sup, use_container_width=True)

        # الصف الثالث من الرسوم
        col_r3_1, col_r3_2 = st.columns(2)

        with col_r3_1:
            # 5. العلاقة بين السعر ومبيعات 2026 (Scatter Plot)
            fig_scatter = px.scatter(
                df, x=price_col, y=sales_26_col, color=discount_col,
                title="تحليل العلاقة بين السعر ومبيعات 2026 (مُموّن بنسبة الخصم)",
                template="plotly_white", hover_data=[prod_col]
            )
            st.plotly_chart(fig_scatter, use_container_width=True)

        with col_r3_2:
            # 6. نسبة أنواع الموردين (محلي vs خارجي)
            if "نوع المورد" in cols:
                type_counts = df["نوع المورد"].value_counts().reset_index()
                type_counts.columns = ['نوع المورد', 'العدد']
                fig_pie = px.pie(
                    type_counts, names='نوع المورد', values='العدد',
                    title="توزيع الأصناف حسب نوع المورد (محلي / خارجي)",
                    hole=0.4, template="plotly_white"
                )
                st.plotly_chart(fig_pie, use_container_width=True)

        st.markdown("---")
        
        # قسم الرؤى التحليلية العميقة (AI Insights)
        st.subheader("💡 محرك الرؤى والتوصيات التحليلية (Smart Insights Engine)")
        
        best_p = top_prods.iloc[0][prod_col] if not top_prods.empty else "N/A"
        best_p_sales = top_prods.iloc[0][sales_26_col] if not top_prods.empty else 0
        growth_rate = ((tot_s26 - tot_s25) / tot_s25 * 100) if tot_s25 > 0 else 0

        st.info(f"""
        * **معدل النمو العام:** إجمالي مبيعات 2026 يسجل نمواً مقارنة بعام 2025 بنسبة تقريبية **{growth_rate:.1f}%**.
        * **المنتج النجم (Top Performer):** المنتج الأكثر مبيعاً لعام 2026 هو **{best_p}** بإجمالي مبيعات بلغ **{best_p_sales:,.0f}**.
        * **توصية استراتيجية:** الأصناف التي تجاوزت نسبة خصمها 30% ولم تحقق معدلات مبيعات مرتفعة يجب مراجعة تسعيرها أو ترويجها في فروع أخرى لتحريك المخزون.
        """)

        # جدول عينة البيانات المفصلة
        with st.expander("📋 استعراض الجدول الكامل للبيانات المصفاة"):
            st.dataframe(df)

    except Exception as e:
        st.error(f"حدث خطأ أثناء معالجة الشيت: {e}")
else:
    st.warning("الرجاء رفع ملف الإكسيل من القائمة الجانبية (Sidebar) لعرض لوحة التحليلات المتقدمة.")
