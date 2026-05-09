import tensorflow as tf
from tensorflow.keras.preprocessing.image import ImageDataGenerator
from tensorflow.keras import layers, models
import os

# 1. Path set karein
base_path = 'data/brain_tumor_data'
train_dir = os.path.join(base_path, 'train')
test_dir = os.path.join(base_path, 'test')

# 2. Image Preprocessing (Synopsis Section 5.2)
train_datagen = ImageDataGenerator(rescale=1./255, validation_split=0.2)

train_generator = train_datagen.flow_from_directory(
    train_dir,
    target_size=(224, 224),
    batch_size=32,
    class_mode='categorical' # Kyunki 4 bimariyan hain
)

test_generator = train_datagen.flow_from_directory(
    test_dir,
    target_size=(224, 224),
    batch_size=32,
    class_mode='categorical'
)

# 3. Model Architecture (Multi-class Classification)
model = models.Sequential([
    layers.Conv2D(32, (3, 3), activation='relu', input_shape=(224, 224, 3)),
    layers.MaxPooling2D((2, 2)),
    layers.Conv2D(64, (3, 3), activation='relu'),
    layers.MaxPooling2D((2, 2)),
    layers.Flatten(),
    layers.Dense(256, activation='relu'),
    layers.Dense(4, activation='softmax') # 4 classes ke liye softmax zaruri hai
])

model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

# 4. Training
print("Brain Tumor Model Training shuru ho rahi hai...")
model.fit(train_generator, epochs=10, validation_data=test_generator)

# 5. Save
model.save('brain_tumor_model.h5')
print("Brain Tumor Model Saved!")