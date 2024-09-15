from PIL import Image
import os

# Convert text to binary
def message_to_binary(message):
    return ''.join(format(ord(char), '08b') for char in message)

# Convert binary to text
def binary_to_message(binary_data):
    binary_chars = [binary_data[i:i+8] for i in range(0, len(binary_data), 8)]
    message = ''.join(chr(int(binary_char, 2)) for binary_char in binary_chars)
    return message

# Function to convert any image to PNG format
def ensure_png(image_path):
    img = Image.open(image_path)
    if img.format != 'PNG':
        png_image_path = os.path.splitext(image_path)[0] + '.png'
        img.save(png_image_path)
        return png_image_path
    return image_path

# Function to encode data into image
def encode_image(image_path, data, output_path):
    # Ensure the image is in PNG format
    image_path = ensure_png(image_path)

    img = Image.open(image_path)
    binary_data = message_to_binary(data) + '00000000'  # Add null character
    img_data = list(img.getdata())

    if len(binary_data) > len(img_data) * 3:
        raise ValueError("Data is too large to encode in the given image.")

    data_index = 0
    new_pixels = []

    for pixel in img_data:
        pixel = list(pixel)
        for i in range(3):
            if data_index < len(binary_data):
                pixel[i] = pixel[i] & ~1 | int(binary_data[data_index])
                data_index += 1
        new_pixels.append(tuple(pixel))

    encoded_img = Image.new(img.mode, img.size)
    encoded_img.putdata(new_pixels)
    encoded_img.save(output_path)

# Function to encode a file into an image
def encode_file(image_path, file_path, output_path):
    # Ensure the image is in PNG format
    image_path = ensure_png(image_path)

    with open(file_path, 'rb') as file:
        file_data = file.read()
    binary_data = ''.join(format(byte, '08b') for byte in file_data) + '00000000'

    img = Image.open(image_path)
    img_data = list(img.getdata())

    if len(binary_data) > len(img_data) * 3:
        raise ValueError("File is too large to encode in the given image.")

    data_index = 0
    new_pixels = []

    for pixel in img_data:
        pixel = list(pixel)
        for i in range(3):
            if data_index < len(binary_data):
                pixel[i] = pixel[i] & ~1 | int(binary_data[data_index])
                data_index += 1
        new_pixels.append(tuple(pixel))

    encoded_img = Image.new(img.mode, img.size)
    encoded_img.putdata(new_pixels)
    encoded_img.save(output_path)

# Function to decode data from image
def decode_image(image_path):
    # Ensure the image is in PNG format
    image_path = ensure_png(image_path)

    img = Image.open(image_path)
    img_data = list(img.getdata())

    binary_data = ''

    for pixel in img_data:
        for i in range(3):
            binary_data += str(pixel[i] & 1)

    null_terminator_index = binary_data.find('00000000')
    if null_terminator_index != -1:
        binary_data = binary_data[:null_terminator_index]
    else:
        return None

    message = binary_to_message(binary_data)
    return message

# Function to decode file from image
def decode_file(image_path, output_path):
    # Ensure the image is in PNG format
    image_path = ensure_png(image_path)

    img = Image.open(image_path)
    img_data = list(img.getdata())

    binary_data = ''

    for pixel in img_data:
        for i in range(3):
            binary_data += str(pixel[i] & 1)

    null_terminator_index = binary_data.find('00000000')
    if null_terminator_index != -1:
        binary_data = binary_data[:null_terminator_index]
    else:
        return None

    file_bytes = bytearray()
    for i in range(0, len(binary_data), 8):
        byte = binary_data[i:i+8]
        file_bytes.append(int(byte, 2))

    with open(output_path, 'wb') as output_file:
        output_file.write(file_bytes)
    return output_path
