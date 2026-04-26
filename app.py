import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io
import re

st.set_page_config(page_title="商品圖合成工具", layout="centered")
st.title("📦 商品四宮格合成工具 (可愛圓體+星標版)")

uploaded_files = st.file_uploader("請一次框選或拖曳 2~3 張圖片到這裡", type=['png', 'jpg', 'jpeg'], accept_multiple_files=True)
st.header("2. 貼上原始廣告文案")
raw_description = st.text_area("直接貼上整段文案，系統會自動無視連結、雜訊並美化排版", height=200)

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

    # --- 基礎清理 ---
    raw_lines = [line.strip() for line in raw_description.split('\n') if line.strip()]
    cleaned_lines = []
    ignore_keywords = ["http", "lin.ee", "有問題請私小幫手"]
    for line in raw_lines:
        if not any(kw in line for kw in ignore_keywords):
            cleaned_lines.append(line)
    
    final_lines = [line.replace("免運", "").strip() for line in cleaned_lines if line.replace("免運", "").strip()]
    
    # 自動代碼高亮偵測
    product_code = ""
    title_text = ""
    if final_lines:
        first_line = final_lines[0]
        match_code = re.match(r'^([A-Z]*\d+[A-Z]*\s*)\s*(.*)', first_line)
        if match_code:
            product_code = match_code.group(1).strip()
            title_text = match_code.group(2).strip()
        else:
            title_text = first_line

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
        
        # ⚠️ 讀取你剛剛上傳的可愛字體 cute.ttf
        try:
            font_title = ImageFont.truetype("cute.ttf", 46) 
            font_body = ImageFont.truetype("cute.ttf", 34)    
            font_logistics = ImageFont.truetype("cute.ttf", 28) 
        except IOError:
            st.error("找不到 cute.ttf 字體檔！請確認你有把字體上傳到 GitHub，並且檔名全小寫。")
            font_title = font_body = font_logistics = ImageFont.load_default()

        # 畫主邊框 (改為圓體風格常用的黑色粗框，更像圖卡)
        draw.rectangle([10, cell_size + 10, cell_size - 10, cell_size * 2 - 10], outline="#222222", width=8)

        if final_lines:
            text_x_start = 30
            y_offset = cell_size + 40
            
            if product_code:
                # 代碼紅底白字
                code_bbox = draw.textbbox((0, 0), product_code, font=font_title)
                code_w = code_bbox[2] - code_bbox[0]
                code_h = code_bbox[3] - code_bbox[1] + 10 
                draw.rectangle([(text_x_start, y_offset), (text_x_start + code_w + 16, y_offset + code_h)], fill="#E53935", radius=8) # 圓角矩形
                draw.text((text_x_start + 8, y_offset + 5), product_code, font=font_title, fill="white")
                
                # 商品全稱
                full_title_bbox = draw.textbbox((0, 0), title_text, font=font_title)
                full_title_w = full_title_bbox[2] - full_title_bbox[0]
                draw.text(((cell_size - full_title_w) // 2 + (text_x_start + code_w + 16) // 2, y_offset + 5), title_text, font=font_title, fill="black")
            else:
                bbox = draw.textbbox((0, 0), title_text, font=font_title)
                title_w = bbox[2] - bbox[0]
                draw.text(((cell_size - title_w) // 2, y_offset), title_text, font=font_title, fill="black")
            
            line_y = cell_size + 105
            draw.line([(50, line_y), (450, line_y)], fill="#CCCCCC", width=2)

            y_offset = line_y + 30
            spec_x_start = 35
            logistics_lines = []
            
            for i in range(1, len(final_lines)):
                current_line = final_lines[i]
                if "◎" in current_line:
                    logistics_lines.append(current_line)
                else:
                    # 換成星星符號 ★
                    bullet_text = f"★ {current_line}"
                    
                    # 自動偵測是否為價格行，如果是就標成紅色
                    if "起批" in current_line or "元" in current_line or "$" in current_line:
                        text_color = "#D32F2F" # 紅色
                    else:
                        text_color = "#222222" # 黑色
                        
                    draw.text((spec_x_start, y_offset), bullet_text, font=font_body, fill=text_color)
                    y_offset += 52

            if logistics_lines:
                y_offset_logistics = cell_size * 2 - 40 
                for log in reversed(logistics_lines): 
                    draw.text((35, y_offset_logistics - 35), log, font=font_logistics, fill="#666666")
                    y_offset_logistics -= 35

        st.divider()
        st.image(canvas, caption="✨ 圓體星標紅字預覽版", use_container_width=True)

        buf = io.BytesIO()
        canvas.save(buf, format="JPEG", quality=95)
        byte_im = buf.getvalue()
        file_name_prefix = final_lines[0].split(' ')[0] if final_lines else "商品"
        
        st.download_button(
            label="📥 滿意的話，點此下載！",
            data=byte_im,
            file_name=f"{file_name_prefix}_圓體排版圖.jpg",
            mime="image/jpeg",
            use_container_width=True
        )
    except Exception as e:
        st.error(f"合成時發生錯誤: {e}")
