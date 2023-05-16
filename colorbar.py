from PIL import Image
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap

# 画像を読み込む
img = Image.open("/Users/kanaokayuui/HSAFM_Python_Dlab_YK/image14413-3.png")
rgb_img = img.convert('RGB')

# 画像の一行目のRGB値を取得し、0から1の範囲に正規化する
rgb_values = np.array([rgb_img.getpixel((0, i)) for i in range(rgb_img.height)]) / 255.0

# RGB値の配列を整形する (256色に収まるように調整)
rgb_values = rgb_values[:256]
np.savetxt('rgb.csv', rgb_values, delimiter=',')
print (rgb_values)

# カラーマップを作成する
cmap = LinearSegmentedColormap.from_list("my_cmap", rgb_values)

# デモ用のヒートマップを作成
gradient = np.linspace(0, 1, 256)
gradient = np.vstack((gradient, gradient))

# カラーマップを表示
fig, ax = plt.subplots(figsize=(4, 2))
ax.imshow(gradient, aspect='auto', cmap=cmap)
plt.show()
