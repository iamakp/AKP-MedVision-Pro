import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras import layers, models
import os

# 1. Paths set karein
base_path = 'data/pneumonia_data'
train_dir = os.path.join(base_path, 'train')
test_dir = os.path.join(base_path, 'test')

# 2. Image Preprocessing (Synopsis Section 5.2)
# Images ko resize aur normalize (0-1 range) karna
train_datagen = ImageDataGenerator(
    rescale=1./255,
    shear_range=0.2,
    zoom_range=0.2,
    horizontal_flip=True
)

test_datagen = ImageDataGenerator(rescale=1./255)

# 3. Data Loaders
print("Loading Images...")
train_generator = train_datagen.flow_from_directory(
    train_dir,
    target_size=(224, 224),
    batch_size=32,
    class_mode='binary'
)

test_generator = test_datagen.flow_from_directory(
    test_dir,
    target_size=(224, 224),
    batch_size=32,
    class_mode='binary'
)

# 4. CNN Model Architecture (Synopsis Section 7)
model = models.Sequential([
    layers.Conv2D(32, (3, 3), activation='relu', input_shape=(224, 224, 3)),
    layers.MaxPooling2D((2, 2)),
    layers.Conv2D(64, (3, 3), activation='relu'),
    layers.MaxPooling2D((2, 2)),
    layers.Flatten(),
    layers.Dense(128, activation='relu'),
    layers.Dropout(0.5),
    layers.Dense(1, activation='sigmoid') # Binary Output: Normal ya Pneumonia
])

# 5. Compile & Train
model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

print("Training shuru ho rahi hai... Isme thoda samay lag sakta hai.")
history = model.fit(
    train_generator,
    epochs=10, # 10 baar poore dataset se seekhega
    validation_data=test_generator
)

# 6. Model ko save karein
model.save('pneumonia_trained_model.h5')
print("Mubarak ho! Model train ho gaya aur 'pneumonia_trained_model.h5' naam se save ho gaya.")