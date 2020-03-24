import matplotlib

matplotlib.use('Agg')
from keras import models, layers

ACTIVATION = layers.Activation("tanh")


def generator_model():
    # Prepare noise input
    input_z = layers.Input((100,))
    dense_z_1 = layers.Dense(1024)(input_z)
    act_z_1 = ACTIVATION(dense_z_1)
    dense_z_2 = layers.Dense(128 * 8 * 8)(act_z_1)
    bn_z_1 = layers.BatchNormalization()(dense_z_2)
    reshape_z = layers.Reshape((8, 8, 128), input_shape=(128 * 8 * 8,))(bn_z_1)

    # Prepare Conditional (label) input
    input_c = layers.Input((100,))
    dense_c_1 = layers.Dense(1024)(input_c)
    act_c_1 = ACTIVATION(dense_c_1)
    dense_c_2 = layers.Dense(128 * 8 * 8)(act_c_1)
    bn_c_1 = layers.BatchNormalization()(dense_c_2)
    reshape_c = layers.Reshape((8, 8, 128), input_shape=(128 * 8 * 8,))(bn_c_1)

    # Combine input source
    concat_z_c = layers.Concatenate()([reshape_z, reshape_c])

    # Image generation with the concatenated inputs
    up_1 = layers.UpSampling2D(size=(2, 2))(concat_z_c)
    conv_1 = layers.Conv2D(64, (5, 5), padding='same')(up_1)
    act_1 = ACTIVATION(conv_1)
    up_2 = layers.UpSampling2D(size=(2, 2))(act_1)
    conv_2 = layers.Conv2D(32, (5, 5), padding='same')(up_2)
    act_2 = ACTIVATION(conv_2)
    up_3 = layers.UpSampling2D(size=(2, 2))(act_2)
    conv_3 = layers.Conv2D(16, (5, 5), padding='same')(up_3)
    act_3 = ACTIVATION(conv_3)
    conv_4 = layers.Conv2D(8, (5, 5), padding='same')(act_3)
    act_4 = ACTIVATION(conv_4)
    conv_5 = layers.Conv2D(3, (5, 5), padding='same')(act_4)
    act_5 = layers.Activation("tanh")(conv_5)
    model = models.Model(inputs=[input_z, input_c], outputs=act_5)

    return model


def discriminator_model():
    input_gen_image = layers.Input((64, 64, 3))
    conv_1_image = layers.Conv2D(32, (5, 5), padding='same')(input_gen_image)
    act_1_image = ACTIVATION(conv_1_image)
    pool_1_image = layers.MaxPooling2D(pool_size=(2, 2))(act_1_image)
    conv_2_image = layers.Conv2D(64, (5, 5))(pool_1_image)
    act_2_image = ACTIVATION(conv_2_image)
    pool_2_image = layers.MaxPooling2D(pool_size=(2, 2))(act_2_image)
    conv_3_image = layers.Conv2D(128, (5, 5))(pool_2_image)
    act_3_image = ACTIVATION(conv_3_image)
    pool_3_image = layers.MaxPooling2D(pool_size=(2, 2))(act_3_image)

    input_c = layers.Input((100,))
    dense_1_c = layers.Dense(1024)(input_c)
    act_1_c = ACTIVATION(dense_1_c)
    dense_2_c = layers.Dense(5 * 5 * 128)(act_1_c)
    bn_c = layers.BatchNormalization()(dense_2_c)
    reshaped_c = layers.Reshape((5, 5, 128))(bn_c)

    concat = layers.Concatenate()([pool_3_image, reshaped_c])

    flat = layers.Flatten()(concat)
    dense_1 = layers.Dense(1024)(flat)
    act_1 = ACTIVATION(dense_1)
    dense_2 = layers.Dense(1)(act_1)
    act_2 = layers.Activation('sigmoid')(dense_2)
    model = models.Model(inputs=[input_gen_image, input_c], outputs=act_2)
    return model


def generator_containing_discriminator(g, d):
    input_z = layers.Input((100,))
    input_c = layers.Input((100,))
    gen_image = g([input_z, input_c])
    d.trainable = False
    is_real = d([gen_image, input_c])
    model = models.Model(inputs=[input_z, input_c], outputs=is_real)
    return model
