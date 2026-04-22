import streamlit as st
from PIL import Image, ImageDraw, ImageFont
import io

st.set_page_config(page_title="商品圖合成工具", layout="centered")
st.title("📦 商品四宮格合成工具 (自訂微調版)")

# 1. 圖片上傳區
uploaded_files = st.file_uploader("請一次框選或拖曳 2~3 張圖片到這裡", type=['png', 'jpg', 'jpeg'], accept_multiple_files=True)

# 2. 文案輸入區
default_text = """K187 舔狗發聲吊飾
尺寸：約5.5x6.5cm 4款混出

48個 起批 $21元/個
96個起批 $20元/個

◎超商最多一箱 96個

#小娃娃吊飾類 #迷你機"""
description = st.text_area("請直接將整段文案貼在這裡", default_text, height=200)

# 3. 圖片微調與即時預覽區
if uploaded_files and len(uploaded_files) >= 2:
    st.divider()
    st.header("🛠️ 調整圖片位置 (即時預覽)")
    st.info("💡 提示：調整下方拉桿，圖片會即時更新！如果想看到圖片「全貌」不想被切到，請把「放大倍率」調小喔！")

    # 動態建立每一張圖的控制拉桿
    cols = st.columns(min(len(uploaded_files), 3))
    adjustments = []
    for i in range(min(len(uploaded_files), 3)):
        with cols[i]:
            st.markdown(f"**🖼️ 圖片 {i+1} 設定**")
            # 縮放：0.5 (縮小看全貌) ~ 3.0 (特寫)
            zoom = st.slider(f"🔍 放大倍率", 0.5, 3.0, 1.0, 0.1, key=f"z_{i}")
            # 位移：負數往左/上，正數往右/下
            dx = st.slider(f"↔️ 左右平移", -300, 300, 0, 10, key=f"x_{i}")
            dy = st.slider(f"↕️ 上下平移", -300, 300, 0, 10, key=f"y_{i}")
            adjustments.append((zoom, dx, dy))

    # 即時生成邏輯 (完全自動，不需要點擊按鈕)
    cell_size = 500
    canvas = Image.new('RGB', (cell_size * 2, cell_size * 2), 'white')

    def process_img(file, zoom, dx, dy):
        img = Image.open(file).convert("RGB")
        w, h = img.size
        
        # 基準比例：以短邊填滿 500 為準
        base_ratio = max(cell_size / w, cell_size / h)
        new_w = int(w * base_ratio * zoom)
        new_h = int(h * base_ratio * zoom)
        img_resized = img.resize((new_w, new_h), Image.Resampling.LANCZOS)

        # 建立 500x500 的純白底圖 (防止縮小或平移時出現難看的黑邊)
        bg = Image.new('RGB', (cell_size, cell_size), 'white')

        # 計算貼上位置：預設置中 + 使用者的平移量
        paste_x = (cell_size - new_w) // 2 + dx
        paste_y = (cell_size - new_h) // 2 + dy

        bg.paste(img_resized, (paste_x, paste_y))
        return bg

    try:
        # 處理並貼上圖片
        img1 = process_img(uploaded_files[0], *adjustments[0])
        img2 = process_img(uploaded_files[1], *adjustments[1])
        canvas.paste(img1, (0, 0))
        canvas.paste(img2, (cell_size, 0))

        if len(uploaded_files) >= 3:
            img3 = process_img(uploaded_files[2], *adjustments[2])
            canvas.paste(img3, (cell_size, cell_size))

        # 處理左下角文字
        draw = ImageDraw.Draw(canvas)
        try:
            font_title = ImageFont.truetype("msjhbd.ttc", 40)
            font_body = ImageFont.truetype("msjh.ttc", 32)
        except IOError:
            font_title = font_body = ImageFont.load_default()

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

        st.divider()
        
        # 顯示即時預覽圖
        st.image(canvas, caption="✨ 即時預覽：調整上方拉桿，畫面會自動更新！", use_container_width=True)

        # 下載按鈕
        buf = io.BytesIO()
        canvas.save(buf, format="JPEG", quality=95)
        byte_im = buf.getvalue()
        file_name_prefix = lines[0].split(' ')[0] if lines else "商品"
        
        st.download_button(
            label="📥 圖片確認無誤，點此下載！",
            data=byte_im,
            file_name=f"{file_name_prefix}_圖.jpg",
            mime="image/jpeg",
            use_container_width=True
        )
        
    except Exception as e:
        st.error(f"合成時發生錯誤: {e}")
        
elif uploaded_files and len(uploaded_files) < 2:
    st.warning("⚠️ 請至少上傳 2 張圖片喔！")
