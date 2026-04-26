import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io
import re

st.set_page_config(page_title="商品圖合成工具", layout="centered")
st.title("📦 商品四宮格合成工具 (專業排版美化版)")

# 1. 圖片上傳區
uploaded_files = st.file_uploader("請一次框選或拖曳 2~3 張圖片到這裡", type=['png', 'jpg', 'jpeg'], accept_multiple_files=True)

# 2. 文案輸入區
st.header("2. 貼上原始廣告文案")
raw_description = st.text_area("直接貼上整段文案，系統會自動無視連結、雜訊並美化排版", height=200)

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

    # --- 核心邏輯：自動淨化與美化文字 ---
    # 1. 基礎清理
    raw_lines = [line.strip() for line in raw_description.split('\n') if line.strip()]
    cleaned_lines = []
    # 定義雜訊關鍵字
    ignore_keywords = ["http", "lin.ee", "有問題請私小幫手"]
    for line in raw_lines:
        # 自動無視連結與特定語句
        if not any(kw in line for kw in ignore_keywords):
            cleaned_lines.append(line)
    
    # 2. 文字細節處理：移除「免運」
    final_lines = [line.replace("免運", "").strip() for line in cleaned_lines if line.replace("免運", "").strip()]
    
    # 3. 自動代碼高亮偵測：偵測第一行是否含有代碼（例如 K322）
    product_code = ""
    title_text = ""
    if final_lines:
        first_line = final_lines[0]
        # 使用正則表達式嘗試拆分代碼 (例如：K322 合金坦克...)
        match_code = re.match(r'^([A-Z]*\d+[A-Z]*\s*)\s*(.*)', first_line)
        if match_code:
            product_code = match_code.group(1).strip()
            title_text = match_code.group(2).strip()
        else:
            # 沒偵測到代碼就用預設置中
            title_text = first_line
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
        # 繪製圖片格
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
            font_body = ImageFont.truetype("msjh.ttc", 30)    # 內文精緻深灰
            font_logistics = ImageFont.truetype("msjh.ttc", 26) # 物流灰色小字
        except IOError:
            font_title = font_body = font_logistics = ImageFont.load_default()

        # 墨綠色主框線 (#006655)
        teal_color = "#006655"
        draw.rectangle([10, cell_size + 10, cell_size - 10, cell_size * 2 - 10], outline=teal_color, width=8)

        # --- 繪製專業美化排版文字 ---
        if final_lines:
            # 1. 標題繪製 (含自動高亮代碼)
            text_x_start = 30
            y_offset = cell_size + 40
            
            if product_code:
                # 取得代碼寬度以繪製實心框
                code_bbox = draw.textbbox((0, 0), product_code, font=font_title)
                code_w = code_bbox[2] - code_bbox[0]
                code_h = code_bbox[3] - code_bbox[1] + 10 # 增加高度填滿感
                
                # 實心墨綠色框
                draw.rectangle([(text_x_start, y_offset), (text_x_start + code_w + 16, y_offset + code_h)], fill=teal_color)
                # 白色代碼
                draw.text((text_x_start + 8, y_offset + 5), product_code, font=font_title, fill="white")
                
                # 置中商品全稱（位於代碼框框右側）
                full_title_bbox = draw.textbbox((0, 0), title_text, font=font_title)
                full_title_w = full_title_bbox[2] - full_title_bbox[0]
                draw.text(((cell_size - full_title_w) // 2 + (text_x_start + code_w + 16) // 2, y_offset + 5), title_text, font=font_title, fill="black")

            else:
                # 沒代碼則全部置中
                bbox = draw.textbbox((0, 0), title_text, font=font_title)
                title_w = bbox[2] - bbox[0]
                draw.text(((cell_size - title_w) // 2, y_offset), title_text, font=font_title, fill="black")
            
            # 2. 優雅銀灰色分隔線線
            line_y = cell_size + 98
            draw.line([(50, line_y), (450, line_y)], fill="#C0C0C0", width=1)

            # 3. 內文繪製 (第二行開始，自動群組排版)
            y_offset = line_y + 35
            spec_x_start = 40
            logistics_lines = []
            
            for i in range(1, len(final_lines)):
                current_line = final_lines[i]
                
                # 自動識別「◎」開頭為物流備註
                if "◎" in current_line:
                    logistics_lines.append(current_line)
                else:
                    # 優雅清爽的點點
                    bullet_text = f"• {current_line}"
                    draw.text((spec_x_start, y_offset), bullet_text, font=font_body, fill="#333333")
                    y_offset += 48 # 加大行距，避免擁擠

            # 4. 物流灰色小字單獨呈現 (格子最底部)
            if logistics_lines:
                y_offset_logistics = cell_size * 2 - 40 # 底部留白
                for log in reversed(logistics_lines): # 從底部向上推
                    draw.text((40, y_offset_logistics - 35), log, font=font_logistics, fill="#888888")
                    y_offset_logistics -= 35

        st.divider()
        st.image(canvas, caption="✨ 排版已自動升級：代碼高亮、分隔線、清爽清單、灰色備註", use_container_width=True)

        buf = io.BytesIO()
        canvas.save(buf, format="JPEG", quality=95)
        byte_im = buf.getvalue()
        file_name_prefix = final_lines[0].split(' ')[0] if final_lines else "商品"
        
        st.download_button(
            label="📥 排版很漂亮，點此下載！",
            data=byte_im,
            file_name=f"{file_name_prefix}_專業排版圖.jpg",
            mime="image/jpeg",
            use_container_width=True
        )
    except Exception as e:
        st.error(f"合成時發生錯誤: {e}")
