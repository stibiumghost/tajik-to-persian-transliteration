import pickle
import numpy as np

from keras.models import load_model


with open('variables_12.txt', 'rb') as f:
    vars = pickle.load(file=f)

input_decoding = vars[0]
input_encoding = vars[1]
output_decoding = vars[2]
output_encoding = vars[3]

INPUT_LENGTH = vars[4]
OUTPUT_LENGTH = vars[5]

input_dict_size = vars[6]
output_dict_size = vars[7]

loaded_model = load_model('./model_12-6.h5')


def transform(encoding, data, vector_size=20):
    """
    :param encoding: encoding dict built by build_characters_encoding()
    :param data: list of strings
    :param vector_size: size of each encoded vector
    """
    transformed_data = np.zeros(shape=(len(data), vector_size))
    for i in range(len(data)):
        for j in range(min(len(data[i]), vector_size)):
            transformed_data[i][j] = encoding[data[i][j]]
    return transformed_data


def generate(text):
    encoder_input = transform(input_encoding, [text.lower()], INPUT_LENGTH)
    decoder_input = np.zeros(shape=(len(encoder_input), OUTPUT_LENGTH))
    decoder_input[:,0] = 1
    for i in range(1, OUTPUT_LENGTH):
        output = loaded_model.predict([encoder_input, decoder_input]).argmax(axis=2)
        decoder_input[:,i] = output[:,i]
    return decoder_input [:,1:]

def decode(sequence):
    text = ''
    for i in sequence:
        if i == 0:
            break
        text += output_decoding[i]
    return text

def to_persian(text):
    decoder_output = generate(text)
    return decode(decoder_output[0])
