import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io

st.set_page_config(page_title="商品圖合成工具", layout="centered")
st.title("📦 商品四宮格合成工具 (升級版)")

# 區塊 1：批次上傳圖片
st.header("1. 上傳商品圖片 (可一次拉多張)")
# 加入 accept_multiple_files=True 就能一次選取或拖曳多張圖
uploaded_files = st.file_uploader("請一次框選或拖曳 2~3 張圖片到這裡", type=['png', 'jpg', 'jpeg'], accept_multiple_files=True)

# 區塊 2：統整文字框
st.header("2. 貼上完整商品敘述 (左下角)")
default_text = """K187 舔狗發聲吊飾
尺寸：約5.5x6.5cm 4款混出

48個 起批 $21元/個
96個起批 $20元/個

◎超商最多一箱 96個

#小娃娃吊飾類 #迷你機"""

# 改用 text_area 讓你可以一次貼上整段多行文字
description = st.text_area("請直接將整段文案貼在這裡 (第一行會自動放大當作標題)", default_text, height=250)

# 區塊 3：生成圖片
if st.button("🚀 生成合成圖", use_container_width=True):
    if len(uploaded_files) < 2:
        st.warning("⚠️ 請至少上傳 2 張圖片喔！")
    else:
        try:
            cell_size = 500
            canvas = Image.new('RGB', (cell_size * 2, cell_size * 2), 'white')

            # 處理圖片 (依序讀取上傳陣列裡的第1、2、3張圖)
            img1 = Image.open(uploaded_files[0]).convert("RGB").resize((cell_size, cell_size))
            img2 = Image.open(uploaded_files[1]).convert("RGB").resize((cell_size, cell_size))
            canvas.paste(img1, (0, 0))              # 左上
            canvas.paste(img2, (cell_size, 0))      # 右上
            
            # 如果有上傳第3張才貼到右下
            if len(uploaded_files) >= 3:
                img3 = Image.open(uploaded_files[2]).convert("RGB").resize((cell_size, cell_size))
                canvas.paste(img3, (cell_size, cell_size)) 

            # 處理左下角的文字區塊
            draw = ImageDraw.Draw(canvas)
            
            try:
                font_title = ImageFont.truetype("msjhbd.ttc", 40) # 粗體 (標題)
                font_body = ImageFont.truetype("msjh.ttc", 32)    # 一般 (內文)
            except IOError:
                font_title = font_body = ImageFont.load_default()
                st.warning("找不到中文字體，可能無法正常顯示中文。")

            # 畫綠色外框
            draw.rectangle(
                [10, cell_size + 10, cell_size - 10, cell_size * 2 - 10], 
                outline="#00BFA5", width=8
            )

            # 處理使用者貼上的多行文字
            lines = description.split('\n') # 將文字用換行符號切開
            text_x_start = 30
            y_offset = cell_size + 40 # 從左下角方塊頂部開始往下算
            
            for i, line in enumerate(lines):
                if i == 0:
                    # 第一行自動套用粗體大字
                    draw.text((text_x_start, y_offset), line, font=font_title, fill="black")
                    y_offset += 65
                else:
                    # 第二行開始套用一般字體，並根據行距往下排
                    draw.text((text_x_start, y_offset), line, font=font_body, fill="black")
                    y_offset += 45

            # 顯示與下載結果
            st.success("合成成功！")
            st.image(canvas, caption="生成的商品圖", use_container_width=True)

            buf = io.BytesIO()
            canvas.save(buf, format="JPEG")
            byte_im = buf.getvalue()
            
            # 自動抓取第一行文字當作下載檔名
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