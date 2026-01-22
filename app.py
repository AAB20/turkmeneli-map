import streamlit as st
import folium
from folium import plugins
from streamlit_folium import st_folium

# --------------------------------------------------------
# 1. إعدادات الصفحة (يجب أن يكون في أول سطر)
# --------------------------------------------------------
st.set_page_config(
    page_title="Turkmeneli Maps",
    page_icon="📍",
    layout="wide",
    initial_sidebar_state="collapsed" # القائمة مغلقة لزيادة مساحة الخريطة
)

# --------------------------------------------------------
# 2. حقن CSS لجعل التصميم يشبه Google Maps (ملء الشاشة)
# --------------------------------------------------------
st.markdown("""
<style>
    /* إزالة الهوامش الافتراضية لـ Streamlit */
    .block-container {
        padding-top: 0rem;
        padding-bottom: 0rem;
        padding-left: 0rem;
        padding-right: 0rem;
        max-width: 100%;
    }
    
    /* تنسيق القائمة الجانبية */
    [data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #ddd;
        width: 320px !important;
    }
    
    /* تحسين شكل الأزرار */
    .stButton button {
        background-color: #1a73e8; /* لون أزرق جوجل */
        color: white;
        border-radius: 20px;
        width: 100%;
    }
    
    /* صندوق المعلومات العائم في الأسفل */
    .info-box {
        background-color: white; 
        padding: 15px; 
        border-radius: 8px; 
        box-shadow: 0 2px 6px rgba(0,0,0,0.3);
        text-align: center;
        margin: 10px;
    }
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------------
# 3. القائمة الجانبية (لوحة التحكم والبحث)
# --------------------------------------------------------
with st.sidebar:
    st.title("🗺️ خرائط المنطقة")
    
    # محاكاة "الاتجاهات" (Directions)
    with st.expander("🚙 الاتجاهات والمسار", expanded=True):
        start = st.text_input("نقطة الانطلاق", value="موقعي الحالي")
        end = st.selectbox("الوجهة", ["كركوك - المركز", "تلعفر - القلعة", "طوز خورماتو", "آلتون كوبري"])
        
        if st.button("بحث عن المسار"):
            st.success(f"تم رسم المسار المقترح إلى {end}")
            st.caption("ℹ️ المسافة: 45 كم | الوقت المتوقع: 40 دقيقة (حركة مرور خفيفة)")

    st.markdown("---")
    
    # خيارات الطبقات (Layers)
    st.write("**نوع الخريطة:**")
    map_style = st.radio(
        "اختر المظهر:",
        ["خرائط (افتراضي)", "أقمار صناعية (Satellite)", "تضاريس (Terrain)"],
        label_visibility="collapsed"
    )

    st.markdown("---")
    
    # خيارات إضافية
    show_traffic = st.checkbox("عرض حركة المرور (تجريبي)", value=True)
    show_borders = st.checkbox("إظهار حدود منطقة تركمن إيلي", value=True)
    
    st.info("نظام MVP تم تطويره باستخدام Python Streamlit")

# --------------------------------------------------------
# 4. منطق بناء الخريطة (Map Logic)
# --------------------------------------------------------
def create_map():
    # تحديد نوع البلاطات (Tiles)
    if map_style == "أقمار صناعية (Satellite)":
        tiles = "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
        attr = "Esri WorldImagery"
    elif map_style == "تضاريس (Terrain)":
        tiles = "https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png"
        attr = "OpenTopoMap"
    else:
        # CartoDB Voyager هو الأقرب لتصميم Google Maps النظيف
        tiles = "CartoDB voyager"
        attr = "CartoDB"

    # إنشاء الخريطة (مركزة على كركوك)
    m = folium.Map(
        location=[35.47, 44.39], 
        zoom_start=9, 
        tiles=tiles, 
        attr=attr,
        control_scale=True,
        zoom_control=False # سنضيف أزرار تحكم مخصصة لاحقاً أو نعتمد على الماوس
    )

    # 1. شريط البحث (Google Search Bar)
    plugins.Geocoder(
        collapsed=False,
        position='topleft',
        add_marker=True,
        placeholder="ابحث هنا (مثل: كركوك، بغداد...)"
    ).add_to(m)

    # 2. زر تحديد الموقع (GPS)
    plugins.LocateControl(
        auto_start=False,
        position='bottomright',
        strings={"title": "أين أنا؟"}
    ).add_to(m)

    # 3. زر ملء الشاشة
    plugins.Fullscreen(position='topright').add_to(m)

    # 4. رسم حدود المنطقة (Polygon)
    if show_borders:
        region_coords = [
            (36.37, 42.45), (36.34, 43.13), (35.95, 43.60), 
            (35.47, 44.39), (34.89, 44.70), (34.33, 45.10), 
            (33.75, 45.55), (33.60, 45.40), (34.50, 44.20), 
            (35.20, 43.80), (36.00, 42.80)
        ]
        folium.Polygon(
            locations=region_coords,
            color="#4285F4", # أزرق جوجل
            weight=2,
            fill=True,
            fill_opacity=0.1,
            popup="منطقة تركمن إيلي"
        ).add_to(m)

    # 5. محاكاة حركة المرور (AntPath Animation)
    if show_traffic:
        # مسار تجريبي بين كركوك وأربيل
        route = [
            [35.47, 44.39], [35.50, 44.38], [35.60, 44.30], 
            [35.80, 44.10], [36.19, 44.01]
        ]
        plugins.AntPath(
            locations=route,
            color="#1a73e8", # المسار الأزرق
            weight=6,
            delay=800,
            opacity=0.7,
            pulse_color="white"
        ).add_to(m)

    # 6. إضافة معالم (Markers) بأيقونات مميزة
    landmarks = [
        {"name": "قلعة كركوك", "loc": [35.47, 44.39], "icon": "star", "color": "orange"},
        {"name": "قلعة تلعفر", "loc": [36.376, 42.45], "icon": "flag", "color": "red"},
        {"name": "مرقد الإمام زين العابدين", "loc": [34.45, 44.38], "icon": "bookmark", "color": "green"},
    ]

    for mark in landmarks:
        folium.Marker(
            location=mark["loc"],
            popup=mark["name"],
            tooltip=mark["name"],
            icon=folium.Icon(color=mark["color"], icon=mark["icon"], prefix='fa')
        ).add_to(m)

    # إضافة خاصية النقر لاستخراج الإحداثيات
    m.add_child(folium.LatLngPopup())

    return m

# --------------------------------------------------------
# 5. عرض الخريطة
# --------------------------------------------------------

# استدعاء دالة الخريطة
map_obj = create_map()

# عرض الخريطة على كامل ارتفاع الشاشة تقريباً (85vh)
st_data = st_folium(
    map_obj, 
    width=None, # يأخذ العرض الكامل تلقائياً
    height=750, # ارتفاع ثابت لمحاكاة الشاشة الكاملة
    use_container_width=True
)

# --------------------------------------------------------
# 6. التفاعل السفلي (Bottom Sheet)
# --------------------------------------------------------
# إذا قام المستخدم بالنقر على الخريطة، نعرض الإحداثيات ورابط جوجل مابس
if st_data['last_clicked']:
    lat = st_data['last_clicked']['lat']
    lng = st_data['last_clicked']['lng']
    
    st.markdown(f"""
        <div class="info-box">
            <h4 style="margin:0; color:#333;">📍 تم تحديد موقع</h4>
            <p style="margin:5px 0;">الإحداثيات: {lat:.5f}, {lng:.5f}</p>
            <a href="https://www.google.com/maps/search/?api=1&query={lat},{lng}" target="_blank" 
               style="background-color:#4285F4; color:white; padding:8px 15px; text-decoration:none; border-radius:5px; font-size:14px;">
               فتح في خرائط Google الأصلية ↗
            </a>
        </div>
    """, unsafe_allow_html=True)
