import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from skimage import color
from PIL import Image, ImageDraw

def main():
    # === Streamlit UI ===
    st.title("HEXtoLAB")
    st.header("L\*a\*b\* 色空間の3D可視化とCSV出力")

    if 'hex_colors' not in st.session_state: 
        st.session_state.hex_colors = []

    button = st.sidebar.button('Clear')
    if button:
        st.session_state.hex_colors = []
    button = st.sidebar.button('Undo')
    if st.session_state.hex_colors:
        if button:
            st.session_state.hex_colors.pop()
    button = st.sidebar.button('Plot')

    # === HEXカラーリスト設定 ===
    # hex_colors = hex_colors()
    hex_color = input_rgb()

    if button:
        st.session_state.hex_colors.append(hex_color)

    fig = go.Figure()
    if st.session_state.hex_colors:
        # === HEX → L*a*b* 変換 ===
        lab_colors = hex_to_lab(st.session_state.hex_colors)

        # === CSV出力 ===
        write_csv(lab_colors, st.session_state.hex_colors, 'hex_to_lab_colors.csv')

        # === 3Dグラフで可視化 ===
        for i, (l, a, b) in zip(st.session_state.hex_colors, lab_colors):
            fig = plot_graph(fig, i, l, a, b)

    # === Streamlitで3Dグラフ表示 ===
    fig = layout_graph(fig)
    st.subheader("L\*a\*b\* 色空間 3D可視化")
    st.plotly_chart(fig)
    return


# === RGBカラーを入力する関数 ===
def input_rgb():
    hex_color = '#808080'
    sel = st.sidebar.radio('', ('RGB input', 'Color picker'))
    if sel == 'RGB input':
       r = st.sidebar.slider('Red',   0, 255, 128,)
       g = st.sidebar.slider('Green', 0, 255, 128,)
       b = st.sidebar.slider('Blue',  0, 255, 128,)
       hex_color = '#{:02x}'.format(r) + '{:02x}'.format(g) + '{:02x}'.format(b)
       st.sidebar.write(f'RGB:　({r}, {g}, {b})')
       st.sidebar.write(f'HEX:　{hex_color}')
       img = Image.new('RGB', (300, 100), (240, 242, 246))
       draw = ImageDraw.Draw(img)
       draw.rectangle([(100, 0), (200, 100)], fill=(r, g, b), outline=None)
       st.sidebar.image(img, caption='Palette', use_container_width=True)
    else:
       # === カラーピッカーを用いたRGB入力 ===
       hex_color = st.sidebar.color_picker("Pick a color", "#00f900")
       st.sidebar.write("The current color is", hex_color)
    return hex_color


# === HEXカラーをL*a*b*に変換する関数 ===
def hex_to_lab(hex_list):
    
     # 複数のHEXカラーをL*a*b*に一括変換
    lab_list = []
    for hex_color in hex_list:
        hex_color = hex_color.lstrip('#')
        r = int(hex_color[0:2], 16)
        g = int(hex_color[2:4], 16)
        b = int(hex_color[4:6], 16)
        rgb_normalized = np.array([r, g, b]) / 255.0
        lab = color.rgb2lab(rgb_normalized.reshape((1, 1, 3))).reshape(3)
        lab_list.append(lab)
    return np.array(lab_list)


# === 各色を3Dプロット ===
def plot_graph(fig, hex_color, l, a, b):
    fig.add_trace(go.Scatter3d(
        x=[a], y=[b], z=[l],
        mode='markers+text',
        marker=dict(size=6, color=hex_color, opacity=1.0),
        text=[hex_color],
        hovertemplate=(
            f'HEX: {hex_color}<br>'
            f'L*: {l:6.2f}<br>'
            f'a*: {a:6.2f}<br>'
            f'b*: {b:6.2f}'
        )
        #textposition="top center"
    ))
    return fig


# === グラフレイアウト設定 ===
def layout_graph(fig):
        fig.add_trace(go.Scatter3d())
        fig.update_layout(
        title=dict(
            text='WinterPalette',
            y=0.95,           # タイトルを上部へ移動，デフォルト0.9
            x=0.5,            # 中央揃え
            xanchor='center', # 中央揃え
            yanchor='top'     # 上揃え  
        ),
        scene=dict(
            xaxis_title='a* 軸',
            yaxis_title='b* 軸',
            zaxis_title='L* 軸',
            xaxis=dict(range=[-100, 100]),
            yaxis=dict(range=[-100, 100]),
            zaxis=dict(range=[0, 100]),
            aspectmode='manual',
            aspectratio=dict(x=1, y=1, z=1)  # L*:a*:b* = 2:1:1 に設定
        ),
        margin=dict(l=10, r=10, b=10, t=10)
    )
    return fig


# === カラー初期値の設定 ===
def init_colors():
    hex_colors = [
        # "#ffffff", "#000000", "#d3d3d3", "#b5b5b5", "#9096a4",
        # "#4c4c4c", "#272564", "#2234c7", "#2413b9", "#f3190f",
        # "#b90b0d", "#a61415", "#10a251", "#068d62", "#084523",
        # "#25a479", "#4dbce9", "#2772e5", "#da38c2", "#a900b5",
        # "#6c019d", "#ff80b3", "#fc4477", "#f4f673", "#d4fcfb",
        # "#fcd4fe", "#f8f9b0", "#feddf6", "#dae4fe", "#eafde7"
    ]
    return hex_colors


# === CSVファイル保存 ===
def write_csv(lab_colors, hex_colors, csv_filename):

# === データフレーム作成（CSV保存用） ===
    df = pd.DataFrame(lab_colors, columns=['L*', 'a*', 'b*'])
    df.insert(0, 'HEX', hex_colors)
    # df.to_csv(csv_filename, index=False)

# === CSVダウンロードボタン ===
    st.write("### HEXカラーとL\*a\*b\*座標のCSV出力")
    st.download_button(
        label = "CSVをダウンロード",
        data = df.to_csv(index=False).encode('utf-8'),
        file_name = csv_filename,
        mime = 'text/csv'
    )
    return


if __name__ == "__main__":
    main()
