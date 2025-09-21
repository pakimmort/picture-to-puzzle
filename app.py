import streamlit as st
from PIL import Image, ImageDraw, ImageFilter
import numpy as np
import io
import math
import random

# Set page configuration
st.set_page_config(
    page_title="Jigsaw Puzzle Creator",
    page_icon="🧩",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Add custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #4a6fa5;
        text-align: center;
        margin-bottom: 2rem;
    }
    .stButton>button {
        width: 100%;
        border-radius: 50px;
        padding: 15px;
        font-weight: bold;
    }
    .style-btn {
        width: 100%;
        margin-bottom: 10px;
    }
</style>
""", unsafe_allow_html=True)

# Language support
translations = {
    "en": {
        "create_custom_puzzle": "Create Your Custom Puzzle",
        "upload_photo": "Upload Your Photo",
        "choose_style": "Choose Style",
        "original_style": "Original Style",
        "cartoon_style": "Cartoon Style",
        "3d_style": "3D Style",
        "piece_count": "Number of Pieces",
        "tab_size": "Tab Size",
        "preview": "Preview",
        "generate_puzzle": "Generate Puzzle",
        "download_puzzle": "Download Puzzle",
        "select_style": "Select a style for your puzzle",
        "customize_puzzle": "Customize your puzzle",
        "drag_drop": "Drag and drop your image here or click to browse",
        "original_desc": "Keep your photo's original appearance",
        "cartoon_desc": "Transform your photo into a cartoon illustration",
        "3d_desc": "Give your photo a three-dimensional effect"
    },
    "ar": {
        "create_custom_puzzle": "اصنع puzzle مخصصة",
        "upload_photo": "حمّل صورتك",
        "choose_style": "اختر النمط",
        "original_style": "النمط الأصلي",
        "cartoon_style": "نمط الكارتون",
        "3d_style": "نمط ثلاثي الأبعاد",
        "piece_count": "عدد القطع",
        "tab_size": "حجم الألسنة",
        "preview": "معاينة",
        "generate_puzzle": "إنشاء Puzzle",
        "download_puzzle": "تحميل Puzzle",
        "select_style": "اختر نمطًا لـ puzzle الخاصة بك",
        "customize_puzzle": "تخصيص puzzle الخاصة بك",
        "drag_drop": "اسحب وأفلت صورتك هنا أو انقر للاستعراض",
        "original_desc": "احتفظ بالمظهر الأصلي لصورتك",
        "cartoon_desc": "حول صورتك إلى رسم كاريكاتوري",
        "3d_desc": "امنح صورتك تأثيرًا ثلاثي الأبعاد"
    },
    "es": {
        "create_custom_puzzle": "Crea Tu Rompecabezas Personalizado",
        "upload_photo": "Sube Tu Foto",
        "choose_style": "Elige Estilo",
        "original_style": "Estilo Original",
        "cartoon_style": "Estilo Cartoon",
        "3d_style": "Estilo 3D",
        "piece_count": "Número de Piezas",
        "tab_size": "Tamaño de Lengüeta",
        "preview": "Vista Previa",
        "generate_puzzle": "Generar Rompecabezas",
        "download_puzzle": "Descargar Rompecabezas",
        "select_style": "Selecciona un estilo para tu rompecabezas",
        "customize_puzzle": "Personaliza tu rompecabezas",
        "drag_drop": "Arrastra y suelta tu imagen aquí o haz clic para examinar",
        "original_desc": "Mantén la apariencia original de tu foto",
        "cartoon_desc": "Transforma tu foto en una ilustración cartoon",
        "3d_desc": "Da a tu foto un efecto tridimensional"
    }
}

# Initialize session state
if 'lang' not in st.session_state:
    st.session_state.lang = "en"
if 'selected_style' not in st.session_state:
    st.session_state.selected_style = "original"
if 'uploaded_image' not in st.session_state:
    st.session_state.uploaded_image = None
if 'puzzle_img' not in st.session_state:
    st.session_state.puzzle_img = None

# Language selector in sidebar
with st.sidebar:
    st.header("Settings")
    lang_option = st.radio("Language", ["English", "Arabic", "Spanish"], 
                          index=0)
    
    # Map to language codes
    lang_map = {"English": "en", "Arabic": "ar", "Spanish": "es"}
    st.session_state.lang = lang_map[lang_option]

# Get translation
def t(key):
    return translations[st.session_state.lang].get(key, key)

# Main header
st.markdown(f'<h1 class="main-header">{t("create_custom_puzzle")}</h1>', unsafe_allow_html=True)

# Upload section
st.subheader(t("upload_photo"))
uploaded_file = st.file_uploader(t("drag_drop"), type=['png', 'jpg', 'jpeg'])

if uploaded_file is not None:
    st.session_state.uploaded_image = Image.open(uploaded_file).convert('RGB')
    st.image(st.session_state.uploaded_image, caption=t("upload_photo"), use_column_width=True)

# Style selection
st.subheader(t("choose_style"))
col1, col2, col3 = st.columns(3)

with col1:
    if st.button(t("original_style"), use_container_width=True, key="btn_original"):
        st.session_state.selected_style = "original"
    st.caption(t("original_desc"))

with col2:
    if st.button(t("cartoon_style"), use_container_width=True, key="btn_cartoon"):
        st.session_state.selected_style = "cartoon"
    st.caption(t("cartoon_desc"))

with col3:
    if st.button(t("3d_style"), use_container_width=True, key="btn_3d"):
        st.session_state.selected_style = "3d"
    st.caption(t("3d_desc"))

# Show selected style
st.info(f"Selected style: {st.session_state.selected_style}")

# Customization
st.subheader(t("customize_puzzle"))
pieces = st.slider(t("piece_count"), 20, 100, 60)
tab_size = st.slider(t("tab_size"), 15, 40, 25)

# PROPER Jigsaw generation functions
def create_jigsaw_cuts(image, rows, cols, tab_size):
    """Create actual jigsaw puzzle cuts on the image"""
    width, height = image.size
    result = image.copy()
    draw = ImageDraw.Draw(result)
    
    cell_width = width / cols
    cell_height = height / rows
    
    # Draw horizontal puzzle cuts
    for row in range(1, rows):
        y = row * cell_height
        points = []
        
        for col in range(cols):
            x_start = col * cell_width
            x_end = x_start + cell_width
            
            # Create wave pattern for each cell
            for x in np.linspace(x_start, x_end, 50):
                # Normalized position in cell (0 to 1)
                norm_pos = (x - x_start) / cell_width
                
                # Create jigsaw wave pattern
                if 0.3 <= norm_pos <= 0.7:
                    # Curved tab shape
                    wave = tab_size * math.sin((norm_pos - 0.3) * math.pi / 0.4)
                else:
                    wave = 0
                
                points.append((x, y + wave))
        
        # Draw the horizontal cut line
        if len(points) > 1:
            draw.line(points, fill=(0, 0, 0), width=4)
    
    # Draw vertical puzzle cuts
    for col in range(1, cols):
        x = col * cell_width
        points = []
        
        for row in range(rows):
            y_start = row * cell_height
            y_end = y_start + cell_height
            
            # Create wave pattern for each cell
            for y in np.linspace(y_start, y_end, 50):
                # Normalized position in cell (0 to 1)
                norm_pos = (y - y_start) / cell_height
                
                # Create jigsaw wave pattern
                if 0.3 <= norm_pos <= 0.7:
                    # Curved tab shape
                    wave = tab_size * math.sin((norm_pos - 0.3) * math.pi / 0.4)
                else:
                    wave = 0
                
                points.append((x + wave, y))
        
        # Draw the vertical cut line
        if len(points) > 1:
            draw.line(points, fill=(0, 0, 0), width=4)
    
    return result

def create_puzzle_mask(width, height, rows, cols, tab_size):
    """Create a puzzle piece mask for more advanced effect"""
    # Create a white mask
    mask = Image.new('L', (width, height), 255)
    draw = ImageDraw.Draw(mask)
    
    cell_width = width / cols
    cell_height = height / rows
    
    # Draw puzzle cuts as black lines
    for row in range(1, rows):
        y = row * cell_height
        points = []
        
        for x in range(0, width, 2):  # Step by 2px for performance
            cell_x = (x % cell_width) / cell_width
            if 0.3 <= cell_x <= 0.7:
                wave = tab_size * math.sin((cell_x - 0.3) * math.pi / 0.4)
            else:
                wave = 0
            points.append((x, y + wave))
        
        if points:
            draw.line(points, fill=0, width=3)
    
    for col in range(1, cols):
        x = col * cell_width
        points = []
        
        for y in range(0, height, 2):
            cell_y = (y % cell_height) / cell_height
            if 0.3 <= cell_y <= 0.7:
                wave = tab_size * math.sin((cell_y - 0.3) * math.pi / 0.4)
            else:
                wave = 0
            points.append((x + wave, y))
        
        if points:
            draw.line(points, fill=0, width=3)
    
    return mask

def apply_style_filter(image, style):
    """Apply style filter to image"""
    if style == "original":
        return image
    elif style == "cartoon":
        # Simple cartoon effect
        return image.filter(ImageFilter.SMOOTH_MORE).filter(ImageFilter.EDGE_ENHANCE)
    elif style == "3d":
        # Simple 3D effect
        return image.filter(ImageFilter.EMBOSS)
    return image

# Generate puzzle button
if st.button(t("generate_puzzle"), type="primary", key="generate_btn"):
    if st.session_state.uploaded_image is not None:
        with st.spinner("Creating your puzzle..."):
            # Calculate rows and columns
            grid_size = int(math.sqrt(pieces))
            rows = cols = grid_size
            
            # Apply selected style
            styled_image = apply_style_filter(st.session_state.uploaded_image, st.session_state.selected_style)
            
            # Create the jigsaw puzzle with proper cuts
            st.session_state.puzzle_img = create_jigsaw_cuts(styled_image, rows, cols, tab_size)
            
        st.success("Puzzle created successfully!")
    else:
        st.error("Please upload an image first.")

# Display and download
if st.session_state.puzzle_img is not None:
    st.subheader(t("preview"))
    st.image(st.session_state.puzzle_img, use_column_width=True)
    
    # Download button
    buf = io.BytesIO()
    st.session_state.puzzle_img.save(buf, format="JPEG", quality=95)
    byte_im = buf.getvalue()
    
    st.download_button(
        label=t("download_puzzle"),
        data=byte_im,
        file_name="custom_puzzle.jpg",
        mime="image/jpeg",
        key="download_btn"
    )

# Add some explanation
with st.expander("How to use"):
    st.write("""
    1. Upload your image using the file uploader
    2. Choose a style for your puzzle (Original, Cartoon, or 3D)
    3. Adjust the number of pieces and tab size using the sliders
    4. Click 'Generate Puzzle' to create your custom jigsaw
    5. Download your puzzle using the download button
    """)

# Add footer
st.markdown("---")
st.caption("Jigsaw Puzzle Creator - Create custom puzzles from your photos")
