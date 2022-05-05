## import
from tensorflow.keras import models, layers, optimizers
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras.applications import VGG16
import matplotlib.pyplot as plt
import time

## common

TRAIN_DIR = "C:/Users/cjswl/python__/ann-data/chest_xray/chest_xray/train"
VAL_DIR = "C:/Users/cjswl/python__/ann-data/chest_xray/chest_xray/val"
TEST_DIR = "C:/Users/cjswl/python__/ann-data/chest_xray/chest_xray/test"


def run(Q):
    ## Q1
    if Q == 1:
        input_shape = (128, 128, 3)
        batch_size = 20
        epochs1 = 100
        epochs2 = 50
    ## Q2
    elif Q == 2:
        input_shape = (128, 128, 3)
        batch_size = 20
        epochs1 = 100
        epochs2 = 100
    ## Q3 - 256
    elif Q == 3:
        input_shape = (256, 256, 3)
        batch_size = 10
        epochs1 = 100
        epochs2 = 100
    ## Q3 - 512
    elif Q == 4:
        input_shape = (512, 512, 3)
        batch_size = 10
        epochs1 = 100
        epochs2 = 100
    ## QE1
    elif Q == 5:
        input_shape = (None, None, 3)
        batch_size = 20
        epochs1 = 100
        epochs2 = 100
    else:
        print("ERROR")
        exit()
    
    starttime = time.time()
    train, val, test = generator(input_shape[:2], batch_size)
    model = get_model(Q, input_shape)
    history_before = model.fit_generator(
        train, epochs = epochs1,
        validation_data = val
    )
    model.save("new_models/chest_x_ray_Q" + str(Q) + ".h5")

    train_loss = history_before.history["loss"][-1]
    train_acc = history_before.history["accuracy"][-1]
    test_loss, test_acc = model.evaluate_generator(test)
    plot_result(history_before, Q, "accuracy")
    plot_result(history_before, Q, "loss")
    text_name = "Q" + Q + "before.txt"
    with open(text_name, 'w') as f:
        f.write("train_loss : " + str(train_loss) + "\n")
        f.write("train_acc : " + str(train_acc) + "\n")
        f.write("test_loss : " + str(test_loss) + "\n")
        f.write("test_acc : " + str(test_acc) + "\n")
        f.write("time : " + str(time.time() - starttime) + "\n")
    
    conv_base = model.layers[0]

    for layer in conv_base.layers:
        if layer.name.startswith('block5'):
            layer.trainable = True
    model.compile(
        optimizer = optimizers.RMSprop(learning_rate=1e-5),
        loss = "binary_crossentropy", metrics = ["accuracy"]
    )
    history_before = model.fit_generator(
        train, epochs = epochs2,
        validation_data = val
    )

    model.save("new_models/chest_x_ray_Q" + str(Q) + "_after.h5")

    train_loss = history_before.history["loss"][-1]
    train_acc = history_before.history["accuracy"][-1]
    test_loss, test_acc = model.evaluate_generator(test)
    plot_result(history_before, Q, "accuracy")
    plot_result(history_before, Q, "loss")
    text_name = "Q" + Q + "after.txt"
    with open(text_name, 'w') as f:
        f.write("train_loss : " + str(train_loss) + "\n")
        f.write("train_acc : " + str(train_acc) + "\n")
        f.write("test_loss : " + str(test_loss) + "\n")
        f.write("test_acc : " + str(test_acc) + "\n")
        f.write("time : " + str(time.time() - starttime) + "\n")


def get_model(Q, input_shape):
    model = models.Sequential()
    conv_base = VGG16(
        weights = 'imagenet',
        include_top = False,
        input_shape = input_shape
    )
    conv_base.trainable = False
    model.add(conv_base)
    if Q == 1:
        model.add(layers.GlobalAveragePooling2D())
        model.add(layers.Dense(512, activation='relu'))
        model.add(layers.BatchNormalization())
        model.add(layers.Activation('relu'))
        model.add(layers.Dense(128, activation='relu'))
    else:
        model.add(layers.GlobalAveragePooling2D())
        model.add(layers.Dropout(0.25))
        model.add(layers.Dense(512, activation='relu'))
        model.add(layers.BatchNormalization())
        model.add(layers.Activation('relu'))
        model.add(layers.Dropout(0.25))
        model.add(layers.Dense(128, activation='relu'))
        model.add(layers.Dropout(0.25))
    model.add(layers.Dense(1, activation='sigmoid'))
    model.compile(
        optimizer=optimizers.RMSprop(learning_rate=1e-4),
        loss='binary_crossentropy', metrics=['accuracy']
    )
    return model

def data_generator(dir, input_shape, batch_size, data):
    data_gen = data.flow_from_directory(
        dir,
        target_size = input_shape,
        batch_size = batch_size,
        class_mode = 'binary'
    )
    return data_gen

def generator(input_shape, batch_size):
    train_data = ImageDataGenerator(rescale=1./255)
    val_data = ImageDataGenerator(rescale=1./255)
    test_data = ImageDataGenerator(rescale=1./255)
    train_generator = data_generator(TRAIN_DIR, input_shape, batch_size, train_data)
    val_generator = data_generator(VAL_DIR, input_shape, batch_size, val_data)
    test_generator = data_generator(TEST_DIR, input_shape, batch_size, test_data)
    return train_generator, val_generator, test_generator

def plot_result(h, Q, title):
    if title == "accuracy":
        plt.plot(h.history['accuracy'])
        plt.plot(h.history['val_accuracy'])
    elif title == "loss":
        plt.plot(h.history['loss'])
        plt.plot(h.history['val_loss'])
    plt.title(title)
    plt.ylabel('Accuracy')
    plt.xlabel('Epoch')
    plt.legend(['Training', 'Validation'], loc=0)
    plt.savefig('Q' + str(Q) + title + '.png')
    plt.clf()

import datetime

if __name__ == "__main__":
    print(datetime.datetime.now())
    for q in range(1,6):
        run(q)
    print(datetime.datetime.now())