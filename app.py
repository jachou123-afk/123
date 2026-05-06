import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io

st.set_page_config(page_title="商品圖合成工具", layout="centered")
st.title("📦 商品四宮格合成工具 (雙圖輸出版)")

# 1. 圖片上傳區 (開放到 4 張圖)
uploaded_files = st.file_uploader("請一次框選或拖曳 2~4 張圖片到這裡", type=['png', 'jpg', 'jpeg'], accept_multiple_files=True)

# 2. 文案輸入區
st.header("2. 貼上原始廣告文案")
raw_description = st.text_area("直接貼上整段文案，系統會自動無視連結", height=200)

# 3. 圖片微調與即時預覽區
if uploaded_files and len(uploaded_files) >= 2:
    st.divider()
    st.header("🛠️ 調整圖片位置")

    # 動態產生對應數量的微調拉桿 (最多 4 組)
    num_imgs = min(len(uploaded_files), 4)
    cols = st.columns(num_imgs)
    adjustments = []
    for i in range(num_imgs):
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
            line = line.replace("免運", "").strip()
            if line:
                cleaned_lines.append(line)

    cell_size = 500

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
        # 處理所有上傳的圖片
        processed_imgs = []
        for i in range(num_imgs):
            processed_imgs.append(process_img(uploaded_files[i], *adjustments[i]))

        # ==========================================
        # 🎨 第一張圖：原始文字排版版 (Text Version)
        # ==========================================
        canvas1 = Image.new('RGB', (cell_size * 2, cell_size * 2), 'white')
        canvas1.paste(processed_imgs[0], (0, 0)) # 左上
        canvas1.paste(processed_imgs[1], (cell_size, 0)) # 右上
        if len(processed_imgs) >= 3:
            canvas1.paste(processed_imgs[2], (cell_size, cell_size)) # 右下

        draw1 = ImageDraw.Draw(canvas1)
        try:
            font_title = ImageFont.truetype("cute.ttf", 46) 
            font_body = ImageFont.truetype("cute.ttf", 34)    
        except IOError:
            font_title = font_body = ImageFont.load_default()

        # 畫主邊框
        draw1.rectangle([10, cell_size + 10, cell_size - 10, cell_size * 2 - 10], outline="#00BFA5", width=8)

        # 寫入文字 (左下角)
        if cleaned_lines:
            text_x_start = 30
            y_offset = cell_size + 40
            for i, line in enumerate(cleaned_lines):
                if i == 0:
                    draw1.text((text_x_start, y_offset), line, font=font_title, fill="black")
                    y_offset += 65 
                else:
                    draw1.text((text_x_start, y_offset), line, font=font_body, fill="black")
                    y_offset += 50 

        # ==========================================
        # 🖼️ 第二張圖：純圖片四宮格版 (Pure Images)
        # ==========================================
        canvas2 = Image.new('RGB', (cell_size * 2, cell_size * 2), 'white')
        canvas2.paste(processed_imgs[0], (0, 0)) # 左上
        canvas2.paste(processed_imgs[1], (cell_size, 0)) # 右上
        if len(processed_imgs) >= 3:
            canvas2.paste(processed_imgs[2], (0, cell_size)) # 左下
        if len(processed_imgs) >= 4:
            canvas2.paste(processed_imgs[3], (cell_size, cell_size)) # 右下

        # ==========================================
        # 顯示預覽與下載按鈕
        # ==========================================
        st.divider()
        
        # 建立兩個區塊並排顯示預覽圖
        col_preview1, col_preview2 = st.columns(2)
        with col_preview1:
            st.image(canvas1, caption="✨ 圖卡 1：文字說明版", use_container_width=True)
        with col_preview2:
            st.image(canvas2, caption="✨ 圖卡 2：純商品圖版", use_container_width=True)

        # 準備下載檔案
        file_name_prefix = cleaned_lines[0].split(' ')[0] if cleaned_lines else "商品"
        
        buf1 = io.BytesIO()
        canvas1.save(buf1, format="JPEG", quality=95)
        byte_im1 = buf1.getvalue()

        buf2 = io.BytesIO()
        canvas2.save(buf2, format="JPEG", quality=95)
        byte_im2 = buf2.getvalue()

        # 並排顯示下載按鈕
        st.markdown("### 📥 下載區")
        col_dl1, col_dl2 = st.columns(2)
        with col_dl1:
            st.download_button(
                label="📥 下載【圖卡 1：文字說明版】",
                data=byte_im1,
                file_name=f"{file_name_prefix}_文字圖.jpg",
                mime="image/jpeg",
                use_container_width=True
            )
        with col_dl2:
            st.download_button(
                label="📥 下載【圖卡 2：純商品圖版】",
                data=byte_im2,
                file_name=f"{file_name_prefix}_純圖版.jpg",
                mime="image/jpeg",
                use_container_width=True
            )

    except Exception as e:
        st.error(f"合成時發生錯誤: {e}")
