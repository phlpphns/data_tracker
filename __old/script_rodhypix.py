# https://archive.researchdata.leeds.ac.uk/1010/6/Readme.txt
# https://archive.researchdata.leeds.ac.uk/1010/



"""
Rodhypix (.rodhypix) are binary versions of the Sapphire image files exported from Rigaku's CrysAlis Pro software.
The header is 5121 elements long and the data shape is 775 x 800.
These can be read in Matlab with the following script:

%% Read Sapphire File (single frame)

% Make path to file name
measurement_file_fullpath='C:\Example_File_Path\Example_File_Name.rodhypix';

fileID = fopen(measurement_file_fullpath,'r'); % Open Sapphire file

A = fread(fileID); % Read binary data
fclose(fileID); % Close file

B = A(5121:end); % Remove header

fileID = fopen('temp.bin','w'); % Open temp file
fwrite(fileID, B); % Write image data to temp file
fclose(fileID); % Close file

fileID = fopen('temp.bin'); % Open temp file
C = fread(fileID, [775 800], 'long'); % Read data as long format into matrix
fclose(fileID); % Close file

diffpattern = rot90(C);  % rotate image matrix 90 deg
"""

"""
# import fabio

# obj = fabio.open(file_)
# obj.data.shape
# print(dddd)


header_size = 5121
header_size = 5121 - 69
file_ = "./exp_92_1_7.rodhypix"


import matplotlib.pyplot as plt
import numpy as np
f = open(file_, "rb")  # only opens the file for reading
img_arr = np.fromfile(f, dtype=np.uint8)
# [print(ele) for ele in img_arr[:header_size]]
# plt.plot(img_arr)
# plt.show()
len_arr = len(img_arr) - header_size
print(338 * 338)
print(len_arr)
print(np.sqrt(len_arr))
print(len_arr / 385)
# plt.imshow(img_arr[header_size:].reshape(338,338))

plt.imshow(img_arr[header_size:].reshape(-1, 338//2))
plt.show()
# Dim_size=np.array((512,512,459),dtype=np.int) #Or read that from your mhd info File
# img_arr=img_arr.reshape(Dim_size[0],Dim_size[1],Dim_size[2])
# print(512*512)
f.close()
"""

"""
import numpy as np
import matplotlib.pyplot as plt

file_ = "./exp_92_1_7.rodhypix"
file_ = "microfluidics_calciumcarbonate_BG_31_2t_1_150.rodhypix"

# Open file in binary mode
with open(file_, "r") as f:
    data = np.fromfile(f, dtype=np.int8)  # Read all data as int32

# The first 5121 elements are the header, skip them
image_data = data[5121:].reshape((775, 800))  # Reshape to (775, 800)

# Rotate the image 90 degrees
image_data = np.rot90(image_data)

# Plot the image
plt.imshow(image_data, cmap="gray")
plt.colorbar(label="Intensity")
plt.title("Rigaku Rodhypix Image")
plt.show()
"""


"""
import numpy as np
import matplotlib.pyplot as plt

file_ = "./exp_92_1_7.rodhypix"
# file_ = "microfluidics_calciumcarbonate_BG_31_2t_1_150.rodhypix"

# Step 1: Read the file as raw bytes.
with open(file_, "rb") as f:
    raw_data = f.read()

# Step 2: Convert the file bytes to a NumPy array of type uint8.
all_bytes = np.frombuffer(raw_data, dtype=np.uint8)

header = 5120
header = 6576
# Remove the header (first 5121 bytes)
# data_bytes = all_bytes[header:]
data_bytes = all_bytes[header:]

# Step 3: Ensure the remaining data length is a multiple of 4 (size of a 32-bit integer).
num_ints = len(data_bytes) // 4
data_bytes = data_bytes[:num_ints * 4]

# Now interpret the bytes as 32-bit integers.
img_int = np.frombuffer(data_bytes.tobytes(), dtype=np.int32)
len_ = len(img_int)
print(len_)
print(np.sqrt(len_))
print(len_/775)
# Step 4: Reshape the data into the expected dimensions (775 x 800).
# MATLAB fills matrices in column-major order, so we use order='F'.
print(775*800)
img_reshaped = img_int.reshape((775, 800), order='F')

# Step 5: Rotate the image 90 degrees to match MATLAB's rot90.
img_rotated = np.rot90(img_reshaped)

# Plot the resulting image.
plt.imshow(img_rotated, cmap="gray")
plt.colorbar(label="Intensity")
plt.title("Rigaku Rodhypix Image")
plt.show()
"""



import struct
import numpy as np

import struct
import numpy as np

def decompress_ty6(file_path):
    """Decompresses TY6 compressed SAPPHIRE image data."""
    try:
        with open(file_path, 'rb') as f:
            data = f.read()

        # Placeholder offsets (adjust based on your file)
        width_offset = 18
        height_offset = 20
        compression_mode_offset = 352 # offset for *((__int16 *)a5 + 176)
        header_72_offset = 144
        header_73_offset = 140
        header_74_offset = 152
        header_75_offset = 156
        header_76_offset = 160
        buffer_size_offset = 4608 #offset to read the buffer size.

        width = struct.unpack('<H', data[width_offset:width_offset + 2])[0]
        height = struct.unpack('<H', data[height_offset:height_offset + 2])[0]
        compression_mode = struct.unpack('<h', data[compression_mode_offset:compression_mode_offset+2])[0]

        if compression_mode != 6:
            raise ValueError("File is not TY6 compressed.")

        header_72 = struct.unpack('<i', data[header_72_offset:header_72_offset+4])[0]
        header_73 = struct.unpack('<i', data[header_73_offset:header_73_offset+4])[0]
        header_74 = struct.unpack('<i', data[header_74_offset:header_74_offset+4])[0]
        header_75 = struct.unpack('<i', data[header_75_offset:header_75_offset+4])[0]
        header_76 = struct.unpack('<i', data[header_76_offset:header_76_offset+4])[0]

        buffer_size = struct.unpack('<i', data[buffer_size_offset:buffer_size_offset+4])[0]

        compressed_data_start = buffer_size_offset + 4 # compressed data starts after the buffer size.
        compressed_data = data[compressed_data_start:compressed_data_start + buffer_size]

        image_data = np.zeros(width * height, dtype=np.int32)
        compressed_data_index = 0
        image_data_index = 0

        v3 = compressed_data
        v4 = width * height
        v5 = 0 #image_data index.
        v20 = header_75
        v18 = header_76

        v6 = v3[compressed_data_index]
        compressed_data_index += 1

        if v6 == 0xFF:
            v8 = struct.unpack('<i', data[v18:v18+4])[0]
            v18 += 4
        elif v6 == 0xFE:
            v8 = struct.unpack('<h', data[v20:v20+2])[0]
            v20 += 2
        else:
            v8 = v6 - 127

        image_data[image_data_index] = v8
        image_data_index+=1

        v9 = compressed_data[compressed_data_index:]
        compressed_data_index+=1

        v10 = 0
        if header_72 > 0:
            v10 = 1
        if header_73 > 0:
            v10 += 2

        if v10 == 3:
            if v4 > 1:
                 v18_counter = v18
                 v20_counter = v20
                 for _ in range(v4-1):
                     v17 = v9[0]
                     if v17 == 0xFF:
                         image_data[image_data_index] = struct.unpack('<i', data[v18_counter:v18_counter+4])[0] + image_data[image_data_index-1]
                         v18_counter+=4
                     elif v17 == 0xFE:
                         image_data[image_data_index] = struct.unpack('<h', data[v20_counter:v20_counter+2])[0] + image_data[image_data_index-1]
                         v20_counter+=2
                     else:
                         image_data[image_data_index] = v17 + image_data[image_data_index-1] -127
                     image_data_index +=1
                     v9 = v9[1:]
        image_data = image_data.reshape((height,width))
        return image_data

    except FileNotFoundError:
        print(f"Error: File not found at {file_path}")
        return None
    except ValueError as e:
        print(f"ValueError: {e}")
        return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None


file_ = "./exp_92_1_7.rodhypix"
# file_ = "microfluidics_calciumcarbonate_BG_31_2t_1_150.rodhypix"
# decompress_ty6(file_)



import numpy as np

def decompress_sapphire_image(file_path, width, height, header_length=6576):
    """
    Simplified decompression function for TY6 (SAPPHIRE v4) compressed images.
    This function implements a basic delta-decoding scheme based on the pseudo-code.
    
    The algorithm:
      - Skips the header (header_length bytes).
      - Processes the remainder of the file as a stream of codes:
          * If a code is less than 0xFE, it is interpreted as a delta value:
              delta = code - 127
          * If a code equals 0xFE, the next two bytes are read as a 16-bit little-endian signed integer.
          * If a code equals 0xFF, the next four bytes are read as a 32-bit little-endian signed integer.
      - Each decompressed value is computed as: current_value = previous_value + delta.
      - The resulting pixel values are stored in a flat array and then reshaped into (height, width).
    
    Note: This is a simplified approximation.
    
    Args:
      file_path (str): Path to the compressed image file.
      width (int): Width of the final image.
      height (int): Height of the final image.
      header_length (int): Number of bytes to skip for the header (default: 6576).
    
    Returns:
      np.ndarray: Decompressed image as a 2D NumPy array (dtype=np.int64).
    """
    with open(file_path, "rb") as f:
        raw = f.read()
    
    # Skip the header
    data = raw[header_length:]
    
    num_pixels = width * height
    # Use int64 to avoid overflow during processing
    output = np.empty(num_pixels, dtype=np.int64)
    
    pos = 0  # Position in compressed data
    out_idx = 0  # Position in output array
    prev_val = 0  # Initial previous value for delta decoding

    while pos < len(data) and out_idx < num_pixels:
        code = data[pos]
        pos += 1
        
        if code < 0xFE:
            delta = code - 127
        elif code == 0xFE:
            if pos + 2 > len(data):
                break
            delta = int.from_bytes(data[pos:pos+2], byteorder="little", signed=True)
            pos += 2
        elif code == 0xFF:
            if pos + 4 > len(data):
                break
            delta = int.from_bytes(data[pos:pos+4], byteorder="little", signed=True)
            pos += 4
        else:
            # Should not happen; skip invalid code.
            continue
        
        cur_val = prev_val + delta
        output[out_idx] = cur_val
        prev_val = cur_val
        out_idx += 1

    if out_idx != num_pixels:
        raise ValueError(f"Decompressed pixel count ({out_idx}) does not match expected size ({num_pixels}).")
    
    # Optionally, if you expect the final image to be in 16-bit range,
    # you might clip the values and cast them.
    # For example, if valid pixel range is -32768 to 32767:
    final_image = np.clip(output, -32768, 32767).astype(np.int16)
    
    return final_image.reshape((height, width))

# Example usage:
# decompressed_image = decompress_sapphire_image("image.rodhypix", width=800, height=775)

print(775*385)
decompress_sapphire_image(file_, 775, 385)



