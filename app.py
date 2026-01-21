import streamlit as st
import folium
from folium import plugins
from streamlit_folium import st_folium
import pandas as pd
import plotly.express as px

# --------------------------------------------------------
# 1. إعدادات الصفحة (يجب أن يكون هذا أول سطر في الكود)
# --------------------------------------------------------
st.set_page_config(
    page_title="مرصد تركمن إيلي الجغرافي",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# تخصيص CSS لدعم اللغة العربية (RTL) وتحسين المظهر
st.markdown("""
<style>
    .stApp { direction: rtl; }
    div[data-testid="column"] { text-align: right; }
    h1, h2, h3, h4, p, div { font-family: 'Segoe UI', Tahoma, sans-serif; }
    .stMetric { 
        background-color: #f8f9fa; 
        padding: 15px; 
        border-radius: 10px; 
        border-right: 5px solid #00a8cc;
        box-shadow: 2px 2px 5px rgba(0,0,0,0.1);
    }
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------------
# 2. تجهيز البيانات (Data Layer)
# --------------------------------------------------------
data = {
    "المدينة": ["كركوك", "تلعفر", "طوز خورماتو", "مندلي", "كفري", "آلتون كوبري", "خانقين", "داقوق"],
    "المحافظة": ["كركوك", "نينوى", "صلاح الدين", "ديالى", "ديالى", "كركوك", "ديالى", "كركوك"],
    "التعداد التقديري": [1250000, 500000, 220000, 55000, 45000, 60000, 180000, 70000],
    "خط العرض": [35.47, 36.37, 34.89, 33.75, 34.33, 35.75, 34.35, 35.13],
    "خط الطول": [44.39, 42.45, 44.70, 45.55, 45.10, 44.14, 45.38, 44.40],
    "النوع": ["مركز محافظة", "قضاء", "قضاء", "ناحية", "قضاء", "ناحية", "قضاء", "قضاء"]
}
df = pd.DataFrame(data)

# --------------------------------------------------------
# 3. القائمة الجانبية (Sidebar)
# --------------------------------------------------------
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/8/87/Turkmeneli_flag.svg/320px-Turkmeneli_flag.svg.png", width=100)
    st.title("🎛️ لوحة التحكم")
    
    st.markdown("### 🔍 فلترة البيانات")
    # فلتر المحافظة
    all_govs = ["الكل"] + list(df["المحافظة"].unique())
    selected_gov = st.selectbox("اختر المحافظة:", all_govs)
    
    st.markdown("---")
    st.markdown("### 🎨 إعدادات الخريطة")
    # خيارات الخريطة
    map_style = st.radio("نمط العرض:", ["قياسي (Light)", "داكن (Dark Mode)", "أقمار صناعية"], index=0)
    show_boundary = st.toggle("إظهار حدود المنطقة", value=True)
    
    st.markdown("---")
    st.caption("تطبيق MVP تفاعلي - الإصدار 1.0")

# --------------------------------------------------------
# 4. معالجة البيانات بناءً على الفلتر
# --------------------------------------------------------
if selected_gov != "الكل":
    filtered_df = df[df["المحافظة"] == selected_gov]
    # تكبير الخريطة تلقائياً إذا تم اختيار محافظة محددة
    zoom_level = 9
    center_lat = filtered_df["خط العرض"].mean()
    center_lon = filtered_df["خط الطول"].mean()
else:
    filtered_df = df
    zoom_level = 7
    center_lat, center_lon = 35.00, 44.00

# --------------------------------------------------------
# 5. واجهة المؤشرات (KPIs)
# --------------------------------------------------------
st.title("📍 مرصد تركمن إيلي الجغرافي")
st.markdown("نظام تفاعلي لتحليل البيانات الجغرافية والسكانية.")

col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("عدد المدن", f"{len(filtered_df)}")
with col2:
    total_pop = filtered_df["التعداد التقديري"].sum()
    st.metric("إجمالي السكان (التقديري)", f"{total_pop:,.0f}")
with col3:
    max_city = filtered_df.loc[filtered_df["التعداد التقديري"].idxmax()]["المدينة"]
    st.metric("أكبر كثافة", max_city)
with col4:
    st.metric("المحافظات المغطاة", f"{filtered_df['المحافظة'].nunique()}")

st.divider()

# --------------------------------------------------------
# 6. بناء الخريطة (Map Logic)
# --------------------------------------------------------
def create_map():
    # تحديد الخلفية (Tiles)
    if map_style == "داكن (Dark Mode)":
        tiles = "CartoDB dark_matter"
        attr = "CartoDB"
    elif map_style == "أقمار صناعية":
        tiles = "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
        attr = "Esri WorldImagery"
    else:
        tiles = "OpenStreetMap"
        attr = "OpenStreetMap"
    
    m = folium.Map(location=[center_lat, center_lon], zoom_start=zoom_level, tiles=tiles, attr=attr)

    # رسم حدود المنطقة (Polygon)
    if show_boundary:
        region_coords = [
            (36.37, 42.45), (36.34, 43.13), (35.95, 43.60), 
            (35.47, 44.39), (34.89, 44.70), (34.33, 45.10), 
            (33.75, 45.55), (33.60, 45.40), (34.50, 44.20), 
            (35.20, 43.80), (36.00, 42.80)
        ]
        folium.Polygon(
            locations=region_coords,
            color="#00a8cc",
            weight=2,
            fill=True,
            fill_color="#00a8cc",
            fill_opacity=0.15,
            popup="النطاق الجغرافي التقريبي"
        ).add_to(m)

    # إضافة العلامات (Markers)
    marker_cluster = plugins.MarkerCluster().add_to(m) # تجميع النقاط عند التصغير
    
    for _, row in filtered_df.iterrows():
        folium.Marker(
            location=[row["خط العرض"], row["خط الطول"]],
            popup=folium.Popup(f"<b>{row['المدينة']}</b><br>السكان: {row['التعداد التقديري']:,}", max_width=300),
            tooltip=row['المدينة'],
            icon=folium.Icon(color="blue", icon="info-sign", prefix='fa')
        ).add_to(marker_cluster)

    # أدوات إضافية
    plugins.Fullscreen(position='topleft').add_to(m)
    plugins.LocateControl(position='bottomright').add_to(m)
    plugins.MiniMap(toggle_display=True, position='bottomleft').add_to(m)
    
    return m

# --------------------------------------------------------
# 7. التخطيط: الخريطة + الرسوم البيانية
# --------------------------------------------------------
row_map, row_charts = st.columns([2, 1])

with row_map:
    st.subheader("🗺️ الخريطة")
    map_obj = create_map()
    # عرض الخريطة
    st_folium(map_obj, height=550, use_container_width=True)

with row_charts:
    st.subheader("📊 الرسوم البيانية")
    
    # Chart 1: Bar Chart
    fig_bar = px.bar(
        filtered_df, 
        x='المدينة', 
        y='التعداد التقديري',
        color='النوع',
        title="توزيع السكان حسب المدينة",
        color_discrete_sequence=px.colors.qualitative.Safe
    )
    fig_bar.update_layout(xaxis_title=None, yaxis_title=None, showlegend=False)
    st.plotly_chart(fig_bar, use_container_width=True)
    
    # Chart 2: Pie Chart
    fig_pie = px.pie(
        filtered_df, 
        names='المحافظة', 
        values='التعداد التقديري', 
        title="نسب التوزيع السكاني حسب المحافظة",
        hole=0.4
    )
    st.plotly_chart(fig_pie, use_container_width=True)

# --------------------------------------------------------
# 8. جدول البيانات
# --------------------------------------------------------
with st.expander("📂 عرض سجل البيانات التفصيلي"):
    st.dataframe(
        filtered_df[["المدينة", "المحافظة", "النوع", "التعداد التقديري"]],
        use_container_width=True,
        hide_index=True
    )
