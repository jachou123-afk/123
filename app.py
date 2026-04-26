import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io

st.set_page_config(page_title="商品圖合成工具", layout="centered")
st.title("📦 商品四宮格合成工具 (簡單排版+可愛字體)")

# 1. 圖片上傳區
uploaded_files = st.file_uploader("請一次框選或拖曳 2~3 張圖片到這裡", type=['png', 'jpg', 'jpeg'], accept_multiple_files=True)

# 2. 文案輸入區
st.header("2. 貼上原始廣告文案")
raw_description = st.text_area("直接貼上整段文案，系統會自動無視連結", height=200)

# 3. 圖片微調與即時預覽區
if uploaded_files and len(uploaded_files) >= 2:
    st.divider()
    st.header("🛠️ 調整圖片位置")

    cols = st.columns(min(len(uploaded_files), 3))
    adjustments = []
    for i in range(min(len(uploaded_files), 3)):
        with cols[i]:
            st.markdown(f"**🖼️ 圖片 {i+1}**")
            zoom = st.slider(f"🔍 放大", 0.5, 3.0, 1.0, 0.1, key=f"z_{i}")
            dx = st.slider(f"↔️ 左右", -300, 300, 0, 10, key=f"x_{i}")
            dy = st.slider(f"↕️ 上下", -300, 300, 0, 10, key=f"y_{i}")
            adjustments.append((zoom, dx, dy))

    # --- 基礎清理 (保留過濾功能) ---
    raw_lines = [line.strip() for line in raw_description.split('\n') if line.strip()]
    cleaned_lines = []
    ignore_keywords = ["http", "lin.ee", "有問題請私小幫手"]
    for line in raw_lines:
        if not any(kw in line for kw in ignore_keywords):
            # 自動清掉免運
            line = line.replace("免運", "").strip()
            if line:
                cleaned_lines.append(line)

    cell_size = 500
    canvas = Image.new('RGB', (cell_size * 2, cell_size * 2), 'white')

    def process_img(file, zoom, dx, dy):
        img = Image.open(file).convert("RGB")
        w, h = img.size
        base_ratio = max(cell_size / w, cell_size / h)
        new_w = int(w * base_ratio * zoom)
        new_h = int(h * base_ratio * zoom)
        img_resized = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
        bg = Image.new('RGB', (cell_size, cell_size), 'white')
        paste_x = (cell_size - new_w) // 2 + dx
        paste_y = (cell_size - new_h) // 2 + dy
        bg.paste(img_resized, (paste_x, paste_y))
        return bg

    try:
        img1 = process_img(uploaded_files[0], *adjustments[0])
        img2 = process_img(uploaded_files[1], *adjustments[1])
        canvas.paste(img1, (0, 0))
        canvas.paste(img2, (cell_size, 0))
        if len(uploaded_files) >= 3:
            img3 = process_img(uploaded_files[2], *adjustments[2])
            canvas.paste(img3, (cell_size, cell_size))

        draw = ImageDraw.Draw(canvas)
        
        # 讀取可愛字體
        try:
            font_title = ImageFont.truetype("cute.ttf", 46) 
            font_body = ImageFont.truetype("cute.ttf", 34)    
        except IOError:
            st.error("找不到 cute.ttf 字體檔！請確認你有把字體上傳到 GitHub。")
            font_title = font_body = ImageFont.load_default()

        # 畫主邊框 (恢復清爽的綠色)
        draw.rectangle([10, cell_size + 10, cell_size - 10, cell_size * 2 - 10], outline="#00BFA5", width=8)

        # --- 最原始單純的左對齊排版 ---
        if cleaned_lines:
            text_x_start = 30
            y_offset = cell_size + 40
            
            for i, line in enumerate(cleaned_lines):
                if i == 0:
                    draw.text((text_x_start, y_offset), line, font=font_title, fill="black")
                    y_offset += 65 # 標題與內文的距離
                else:
                    draw.text((text_x_start, y_offset), line, font=font_body, fill="black")
                    y_offset += 50 # 內文的行距

        st.divider()
        st.image(canvas, caption="✨ 簡單排版 + 可愛字體", use_container_width=True)

        buf = io.BytesIO()
        canvas.save(buf, format="JPEG", quality=95)
        byte_im = buf.getvalue()
        file_name_prefix = cleaned_lines[0].split(' ')[0] if cleaned_lines else "商品"
        
        st.download_button(
            label="📥 點此下載圖片！",
            data=byte_im,
            file_name=f"{file_name_prefix}_圖.jpg",
            mime="image/jpeg",
            use_container_width=True
        )
    except Exception as e:
        st.error(f"合成時發生錯誤: {e}")
