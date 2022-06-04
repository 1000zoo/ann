from tensorflow.keras.applications.vgg16 import VGG16,\
     preprocess_input, decode_predictions
from tensorflow.keras import backend as K
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
import matplotlib.pyplot as plt
import numpy as np
import tensorflow as tf
tf.compat.v1.disable_eager_execution()

PATH = "/Users/1000zoo/Documents/prog/ANN/data_files/\
chest_xray/test/PNEUMONIA/person1641_virus_2840.jpeg"

image_path = PATH
img = image.load_img(image_path, target_size = (224,224))
img_tensor = image.img_to_array(img)
img_tensor = np.expand_dims(img_tensor, axis=0)
img_tensor = preprocess_input(img_tensor)

def gradCAM(model, x):
    preds = model.predict(x)
    print('Predicted:', decode_predictions(preds, top=3)[0])

    max_output = model.output[:, np.argmax(preds)]
    last_conv_layer = model.get_layer("block5_conv3")
    grads = K.gradients(max_output, last_conv_layer.output)[0]
    pooled_grads = K.mean(grads, axis=(0,1,2))

    iterate = K.function([model.input], [pooled_grads, last_conv_layer.output[0]])
    pooled_grads_value, conv_layer_output_value = iterate([x])

    for i in range(512):
        conv_layer_output_value[:,:,i] *= pooled_grads_value[i]
    heatmap = np.mean(conv_layer_output_value, axis=-1)
    heatmap = np.maximum(heatmap, 0)
    heatmap /= np.max(heatmap)
    return heatmap, conv_layer_output_value, pooled_grads_value

def deprocess_image(X):
    X -= X.mean()
    X /= (X.std() + 1e-5)
    X *= 0.1
    X += 0.5
    X = np.clip(X, 0, 1)
    X += 255
    X = np.clip(X, 0, 255).astype('uint8')
    return X

def draw_activation(activation, figure_name):
    images_per_row = 16
    n_features = activation.shape[-1]
    size = activation.shape[1]
    n_cols = n_features // images_per_row
    display_grid = np.zeros((size * n_cols, images_per_row * size))
    for col in range(n_cols):
        for row in range(images_per_row):
            channel_image = activation[0,:,:,col*images_per_row + row]
            channel_image = deprocess_image(channel_image)
            display_grid[col*size : (col+1)*size, row*size : (row+1)*size] = channel_image
    scale = 1./size
    plt.figure(figsize=(scale*display_grid.shape[1], scale*display_grid.shape[0]))
    plt.title(figure_name)
    plt.grid(False)
    plt.imshow(display_grid, aspect='auto', cmap='viridis')
    plt.show()

model = VGG16(weights="imagenet")
heatmap, conv_output, pooled_grads = gradCAM(model, img_tensor)

import cv2

img = cv2.imread(image_path)
heatmap = cv2.resize(heatmap, (img.shape[1], img.shape[0]))
heatmap = np.uint8(255*heatmap)
heatmap = cv2.applyColorMap(heatmap, cv2.COLORMAP_JET)
superimposed_img = heatmap*0.4 + img
cv2.imwrite('result/hw3_Q4_virus.jpg', superimposed_img)

draw_no = range(256, 256 + 32, 1)
conv_activation = np.expand_dims(conv_output[:,:,draw_no], axis=0)
draw_activation(conv_activation, 'last_conv')
plt.show()

plt.matshow(pooled_grads[draw_no].reshape(-1, 16), cmap='viridis')
plt.show()