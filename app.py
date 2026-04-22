import streamlit as st
from PIL import Image, ImageDraw, ImageFont, ImageOps
import io

st.set_page_config(page_title="商品圖合成工具", layout="centered")
st.title("📦 商品四宮格合成工具 (滿格美化版)")

uploaded_files = st.file_uploader("請一次框選或拖曳 2~3 張圖片到這裡", type=['png', 'jpg', 'jpeg'], accept_multiple_files=True)

default_text = """K187 舔狗發聲吊飾
尺寸：約5.5x6.5cm 4款混出

48個 起批 $21元/個
96個起批 $20元/個

◎超商最多一箱 96個

#小娃娃吊飾類 #迷你機"""

description = st.text_area("請直接將整段文案貼在這裡 (第一行會自動放大當作標題)", default_text, height=250)

if st.button("🚀 生成合成圖", use_container_width=True):
    if len(uploaded_files) < 2:
        st.warning("⚠️ 請至少上傳 2 張圖片喔！")
    else:
        try:
            cell_size = 500
            canvas = Image.new('RGB', (cell_size * 2, cell_size * 2), 'white')

            # ✅ 升級功能：換成智能剪裁 (ImageOps.fit)！塞滿格子，不留白邊！
            def resize_and_crop(img_file):
                img = Image.open(img_file).convert("RGB")
                # ImageOps.fit 會自動將圖片等比縮放並剪裁到指定尺寸，保證填滿格子且中央對齊
                return ImageOps.fit(img, (cell_size, cell_size), method=Image.Resampling.LANCZOS)

            img1 = resize_and_crop(uploaded_files[0])
            img2 = resize_and_crop(uploaded_files[1])
            canvas.paste(img1, (0, 0))              
            canvas.paste(img2, (cell_size, 0))      
            
            if len(uploaded_files) >= 3:
                img3 = resize_and_crop(uploaded_files[2])
                canvas.paste(img3, (cell_size, cell_size)) 

            draw = ImageDraw.Draw(canvas)
            
            try:
                # 這裡假設你的字體檔是全小寫，如果 GitHub 上是大寫，請改成大寫
                font_title = ImageFont.truetype("msjhbd.ttc", 40) 
                font_body = ImageFont.truetype("msjh.ttc", 32)    
            except IOError:
                font_title = font_body = ImageFont.load_default()
                st.warning("找不到中文字體，請檢查 GitHub 上的字體檔名大小寫。")

            draw.rectangle(
                [10, cell_size + 10, cell_size - 10, cell_size * 2 - 10], 
                outline="#00BFA5", width=8
            )

            lines = description.split('\n')
            text_x_start = 30
            y_offset = cell_size + 40
            
            for i, line in enumerate(lines):
                if i == 0:
                    draw.text((text_x_start, y_offset), line, font=font_title, fill="black")
                    y_offset += 65
                else:
                    draw.text((text_x_start, y_offset), line, font=font_body, fill="black")
                    y_offset += 45

            st.success("合成成功！")
            st.image(canvas, caption="生成的商品圖", use_container_width=True)

            buf = io.BytesIO()
            # ✅ 提升儲存圖片的畫質參數 (quality=95)
            canvas.save(buf, format="JPEG", quality=95)
            byte_im = buf.getvalue()
            
            file_name_prefix = lines[0].split(' ')[0] if lines else "商品"
            st.download_button(
                label="📥 下載圖片",
                data=byte_im,
                file_name=f"{file_name_prefix}_圖.jpg",
                mime="image/jpeg",
                use_container_width=True
            )

        except Exception as e:
            st.error(f"發生錯誤: {e}")
