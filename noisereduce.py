# this is for noise reduction by using space modeling 

import numpy as np
from PIL import Image
import config
import cv2

import numpy as np
from sklearn.linear_model import OrthogonalMatchingPursuit
import matplotlib.pyplot as plt

import numpy as np
from spmimage.decomposition import KSVD
from sklearn.preprocessing import StandardScaler
from spmimage.feature_extraction.image import extract_simple_patches_2d, reconstruct_from_simple_patches_2d
        
#画像の行列を読み込んで行列データをベクトルに直す
def imageselect(imagepath):
    #1
    #画像ファイルを読み込む
    noiseimage = Image.open(imagepath).convert('L')

    # 画像をNumPy配列に変換する
    image_array = np.asarray(noiseimage)

    yp=image_array.shape[1]
    xp=image_array.shape[0]

   

    return image_array, xp, yp

        

    
def process(img,patch_size, n_components,transform_n_nonzero_coefs,max_iter):
    # パッチに切り出す
    patches = extract_simple_patches_2d(img, patch_size)
    print("shape:", patches.shape, "dtype:", patches.dtype)

    patches = patches.reshape(-1, np.prod(patch_size)).astype(np.float64)
    print("shape:", patches.shape, "dtype:", patches.dtype)

    scl = StandardScaler()
    Y = scl.fit_transform(patches)

    # 辞書を作成する
    ksvd = KSVD(n_components=n_components, transform_n_nonzero_coefs=transform_n_nonzero_coefs, max_iter=max_iter)
    #スパース行列
    X = ksvd.fit_transform(Y)
    #辞書
    D = ksvd.components_
    reconstructed_patches = np.dot(X, D)
    reconstructed_patches = scl.inverse_transform(reconstructed_patches)
    reconstructed_patches = reconstructed_patches.reshape(-1, patch_size[0], patch_size[1])
    reconstructed_img = reconstruct_from_simple_patches_2d(reconstructed_patches, img.shape)
    reconstructed_img[reconstructed_img < 0] = 0
    reconstructed_img[reconstructed_img > 255] = 255
    reconstructed_img = reconstructed_img.astype(np.uint8)

    print ("reconstructed_img.shape",reconstructed_img.shape)
    
    #行列が高さじゃなくて普通の画素になてっる
    dsp_originalimg = np.array([img.shape[0], img.shape[1],3])
    dsp_denoisedimg = np.array([reconstructed_img .shape[0], reconstructed_img.shape[1],3])
    DIcolor = np.zeros((256, 1, 3), dtype=np.uint8)
    
    for i in range(0, 256):

            if (i < 158):
                DIcolor[i, 0, 2] = i / 157 * 255
            elif (i >= 158):
                DIcolor[i, 0, 2] = 255

            DIcolor[i, 0, 1] = i

            if (i < 176):
                DIcolor[i, 0, 0] = 0
            elif (i >= 176):
                DIcolor[i, 0, 0] = 67 + 188 * (i - 176) / 79
    
    dsp_denoisedimg= cv2.applyColorMap(reconstructed_img, DIcolor)
    dsp_originalimg= cv2.applyColorMap(img, DIcolor)
    #save image with uging cv2
    cv2.imwrite("/Volumes/UnionSine/amiloid/original_color.png",dsp_originalimg)
    cv2.imwrite("/Volumes/UnionSine/amiloid/denoise_patch"+str(patch_size)+"_color.png",dsp_denoisedimg)


imgpath="/Volumes/UnionSine/amiloid/0.jpg"

img=imageselect(imgpath)[0]
#print (img)

patch_x=imageselect(imgpath)[1]
patch_y=imageselect(imgpath)[2]
#print (x,y)

divisorsx = [i for i in range(1, patch_x + 1) if patch_x % i == 0]
divisorsy = [i for i in range(1, patch_y + 1) if patch_y % i == 0]

print (divisorsx)
print (divisorsy)

patch_size=(divisorsx[3],divisorsy[3])


n_components=50
transform_n_nonzero_coefs=5
max_iter=10

process(img,patch_size,n_components,transform_n_nonzero_coefs,max_iter)

