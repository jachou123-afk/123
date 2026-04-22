import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io

st.set_page_config(page_title="商品圖合成工具", layout="centered")
st.title("📦 商品四宮格合成工具 (排版美化版)")

# 1. 圖片上傳區
uploaded_files = st.file_uploader("請一次框選或拖曳 2~3 張圖片到這裡", type=['png', 'jpg', 'jpeg'], accept_multiple_files=True)

# 2. 文案輸入區
st.header("2. 貼上原始廣告文案")
raw_description = st.text_area("直接貼上整段文案，系統會自動淨化並美化排版", height=200)

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

    # --- 核心邏輯：自動過濾與美化文字 ---
    lines = [line.strip() for line in raw_description.split('\n') if line.strip()]
    cleaned_lines = []
    for line in lines:
        # 無視連結與雜項
        if "http" in line or "lin.ee" in line or "有問題請私小幫手" in line:
            continue
        # 移除「免運」字樣
        processed_line = line.replace("免運", "").strip()
        if processed_line:
            cleaned_lines.append(processed_line)
    # --------------------------

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
        try:
            font_title = ImageFont.truetype("msjhbd.ttc", 44) # 標題更大更粗
            font_body = ImageFont.truetype("msjh.ttc", 30)    # 內文精緻
        except IOError:
            font_title = font_body = ImageFont.load_default()

        # 畫主邊框
        draw.rectangle([10, cell_size + 10, cell_size - 10, cell_size * 2 - 10], outline="#00BFA5", width=8)

        # --- 繪製美化排版文字 ---
        if cleaned_lines:
            # 1. 標題繪製 (第一行，置中)
            title = cleaned_lines[0]
            # 取得標題寬度以利置中
            bbox = draw.textbbox((0, 0), title, font=font_title)
            title_w = bbox[2] - bbox[0]
            draw.text(((cell_size - title_w) // 2, cell_size + 40), title, font=font_title, fill="black")
            
            # 2. 裝飾線
            line_y = cell_size + 95
            draw.line([(50, line_y), (450, line_y)], fill="#00BFA5", width=2)

            # 3. 內文繪製 (第二行開始，自動補點)
            y_offset = line_y + 30
            for i in range(1, len(cleaned_lines)):
                bullet_text = f"• {cleaned_lines[i]}"
                draw.text((40, y_offset), bullet_text, font=font_body, fill="#333333")
                y_offset += 48 # 加大行距，看起來更清爽

        st.divider()
        st.image(canvas, caption="✨ 排版已自動升級：置中標題、分隔線、規格清單", use_container_width=True)

        buf = io.BytesIO()
        canvas.save(buf, format="JPEG", quality=95)
        byte_im = buf.getvalue()
        file_name_prefix = cleaned_lines[0].split(' ')[0] if cleaned_lines else "商品"
        
        st.download_button(
            label="📥 排版很漂亮，點此下載！",
            data=byte_im,
            file_name=f"{file_name_prefix}_圖.jpg",
            mime="image/jpeg",
            use_container_width=True
        )
    except Exception as e:
        st.error(f"合成時發生錯誤: {e}")
