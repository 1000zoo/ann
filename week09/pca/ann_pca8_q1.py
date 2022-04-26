from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras import models, layers, optimizers
import matplotlib.pyplot as plt

# set image generators
# # 윈도우 경로
# train_dir='C:/Users/cjswl/python__/ann-data/dogs-vs-cats/for_learning/train'
# test_dir='C:/Users/cjswl/python__/ann-data/dogs-vs-cats/for_learning/test'
# validation_dir='C:/Users/cjswl/python__/ann-data/dogs-vs-cats/for_learning/validation'

# Mac 경로
train_dir = "/Users/1000zoo/Documents/prog/ANN/data_files/dogs_and_cats/train"
test_dir = "/Users/1000zoo/Documents/prog/ANN/data_files/dogs_and_cats/test"
validation_dir = "/Users/1000zoo/Documents/prog/ANN/data_files/dogs_and_cats/validation"

train_datagen = ImageDataGenerator(rescale=1./255)
validation_datagen = ImageDataGenerator(rescale=1./255)
test_datagen = ImageDataGenerator(rescale=1./255)

train_generator = train_datagen.flow_from_directory(
        train_dir,
        target_size=(150, 150),
        batch_size=20,
        class_mode='binary')
test_generator = test_datagen.flow_from_directory(
        test_dir,
        target_size=(150, 150),
        batch_size=20,
        class_mode='binary')
validation_generator = validation_datagen.flow_from_directory(
        validation_dir,
        target_size=(150, 150),
        batch_size=20,
        class_mode='binary')

# model definition
input_shape = [150, 150, 3] # as a shape of image
def build_model():
    model=models.Sequential()
    model.add(layers.Conv2D(32, (3, 3), activation='relu',
                            input_shape=input_shape))
    model.add(layers.MaxPooling2D((2, 2)))
    model.add(layers.Conv2D(64, (3, 3), activation='relu'))
    model.add(layers.MaxPooling2D((2, 2)))
    model.add(layers.Conv2D(128, (3, 3), activation='relu'))
    model.add(layers.MaxPooling2D((2, 2)))
    model.add(layers.Conv2D(128, (3, 3), activation='relu'))
    model.add(layers.MaxPooling2D((2, 2)))
    model.add(layers.Flatten())
    model.add(layers.Dense(512, activation='relu'))
    model.add(layers.Dense(1, activation='sigmoid'))
    # compile
    model.compile(optimizer=optimizers.RMSprop(lr=1e-4),
                  loss='binary_crossentropy', metrics=['accuracy'])
    return model

# main loop without cross-validation
import time
starttime=time.time()
num_epochs = 60
model = build_model()
history = model.fit_generator(train_generator,
                    epochs=num_epochs, steps_per_epoch=100,
                    validation_data=validation_generator, validation_steps=50)

# saving the model
model.save('cats_and_dogs_small_1.h5')

# evaluation
train_loss, train_acc = model.evaluate_generator(train_generator)
test_loss, test_acc = model.evaluate_generator(test_generator)
print('train_acc:', train_acc)
print('test_acc:', test_acc)
print("elapsed time (in sec): ", time.time()-starttime)

# visualization
def plot_acc(h, title="accuracy"):
    plt.plot(h.history['accuracy'])
    plt.plot(h.history ['val_accuracy'])
    plt.title(title)
    plt.ylabel('Accuracy')
    plt.xlabel('Epoch')
    plt.legend(['Training', 'Validation'], loc=0)

def plot_loss(h, title="loss"):
    plt.plot(h.history['loss'])
    plt.plot(h.history['val_loss'])
    plt.title(title)
    plt.ylabel('Loss')
    plt.xlabel('Epoch')
    plt.legend(['Training', 'Validation'], loc=0)

import os
file_name = os.path.basename(__file__)
ch = ".py"

for c in ch:
    file_name = file_name.replace(c, "")
wlist = file_name.split("_")
qnum = wlist[-1]
plot_loss(history)

plt.savefig('result/' + qnum + 'loss.png')
plt.clf()
plot_acc(history)
plt.savefig('result/' + qnum + 'accuracy.png')
