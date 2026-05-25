import math
import zlib
import numpy as np
from PIL import Image
from bitarray import bitarray

def flip_bits(data: bytes) -> bytes:
    return bytes(b ^ 0xFF for b in data)

def rotate_bytes(data: bytes, shift: int = 3) -> bytes:
    shift %= len(data) if data else 1
    return data[shift:] + data[:shift]

def unrotate_bytes(data: bytes, shift: int = 3) -> bytes:
    shift %= len(data) if data else 1
    return data[-shift:] + data[:-shift]

def avg_kth_msb(original_img: Image.Image, k: int) -> float:
    img_copy = original_img.copy()
    pixel_matrix = np.array(img_copy)
    divisor = 2 ** (8 - k)
    overall_msb = pixel_matrix // divisor
    avg = int(np.mean(overall_msb))

    return avg

def compress_file(data: bytes) -> bitarray:
    data = flip_bits(data)
    data = rotate_bytes(data)
    packed = zlib.compress(data, level=9)
    final_bits = bitarray()
    final_bits.frombytes(packed)
    return final_bits

def decompress_bits(encoded_bits: bitarray) -> str:
    packed = encoded_bits.tobytes()
    data = zlib.decompress(packed)
    data = unrotate_bytes(data)
    data = flip_bits(data)
    return data.decode("utf-8")

circular_set = set()
def circle_cells(h, w, dis, offset_x=0, offset_y=0):
    max_radius = min(h // 2, w // 2)
    if dis >= max_radius or h <= 0 or w <= 0:
        return
    cx = h // 2
    cy = w // 2
    r = max_radius - dis
    if r <= 0:
        return
    samples = max(360, int(2 * math.pi * r * 8))
    for i in range(samples):
        theta = 2 * math.pi * i / samples
        x = round(cx + r * math.cos(theta)) + offset_x
        y = round(cy + r * math.sin(theta)) + offset_y
        circular_set.add((x, y))
    left_w = w // 2
    right_w = w - left_w
    top_h = h // 2
    bottom_h = h - top_h
    circle_cells(top_h, left_w, dis, offset_x, offset_y)
    circle_cells(top_h, right_w, dis, offset_x, offset_y + left_w)
    circle_cells(bottom_h, left_w, dis, offset_x + top_h, offset_y)
    circle_cells(bottom_h, right_w, dis, offset_x + top_h, offset_y + left_w)

def calculate_max_capacity(h, w, reserved_pixels):
    total_bits = 0
    for x in range(h):
        for y in range(w):
            if x == h-1 and y >= (w - reserved_pixels):
                continue
            if (x,y) in circular_set:
                total_bits += 3 * 2
            else:
                total_bits += 3 * 1
    return total_bits
def genBinImage(w,h):
    img = Image.new("1", (w, h), 0)
    for x, y in circular_set:
        if 0 <= x < h and 0 <= y < w:
            img.putpixel((y, x), 1)
    img.save("circles.png")
def encode_image(image_path, text):
    img = Image.open(image_path).convert("RGB")
    arr = np.array(img, dtype=np.uint8)
    h, w, _ = arr.shape
    circular_distance = avg_kth_msb(img,4) + 1 
    circular_set.clear()
    print(circular_distance)
    circular_set.clear()
    circle_cells(h, w, circular_distance)
    genBinImage(h,w)
    bits = compress_file(text)
    payload = bits.to01()
    total_len = len(payload)
    is_large = (h >= 1024 or w >= 1024)
    reserved_pixels = 2 if is_large else 1
    
    max_capacity = calculate_max_capacity(h, w,reserved_pixels)
    if total_len > max_capacity:
        raise ValueError(
            f"\n[ERROR] Payload size exceeds image capacity!\n"
            f"Required Payload: {total_len} bits\n"
            f"Image Max Capacity: {max_capacity} bits\n"
            f"Shortfall: {total_len - max_capacity} bits. Use a larger image or less text."
        )
    
    stream = payload
    bit_idx = 0
    
    for x in range(h):
        for y in range(w):
            if x == h - 1 and y >= (w - reserved_pixels):
                continue  
            for c in range(3):
                if bit_idx >= total_len:
                    break
                value = int(arr[x, y, c])
                if (x,y) in circular_set:
                    if bit_idx + 2 <= total_len:
                        bits_chunk = stream[bit_idx:bit_idx + 2]
                        arr[x, y, c] = (value & 0b11111100) | int(bits_chunk, 2)
                        bit_idx += 2
                    else:
                        bits_chunk = stream[bit_idx]
                        arr[x, y, c] = (value & 0b11111110) | int(bits_chunk)
                        bit_idx += 1
                else:
                    bits_chunk = stream[bit_idx]
                    arr[x, y, c] = (value & 0b11111110) | int(bits_chunk)
                    bit_idx += 1
            if bit_idx >= total_len:
                break
        if bit_idx >= total_len:
            break
            
    if not is_large:
        length24bit = total_len & 0xFFFFFF
        arr[h-1, w-1, 0] = (length24bit >> 16) & 0xFF
        arr[h-1, w-1, 1] = (length24bit >> 8) & 0xFF
        arr[h-1, w-1, 2] = length24bit & 0xFF
    else:
        length48bit = total_len & 0xFFFFFFFFFFFF
        arr[h-1, w-2, 0] = (length48bit >> 40) & 0xFF
        arr[h-1, w-2, 1] = (length48bit >> 32) & 0xFF
        arr[h-1, w-2, 2] = (length48bit >> 24) & 0xFF
        arr[h-1, w-1, 0] = (length48bit >> 16) & 0xFF
        arr[h-1, w-1, 1] = (length48bit >> 8) & 0xFF
        arr[h-1, w-1, 2] = length48bit & 0xFF 
    img = Image.fromarray(arr)
    return img
    # img.save(output_path, format="PNG", compress_level=0)
    # print(f"Success! Embedded {total_len} bits safely. Capacity utilized: {(total_len / max_capacity) * 100:.2f}%")

def decode_image(image_path):
    img = Image.open(image_path).convert("RGB")
    arr = np.array(img, dtype=np.uint8)
    h, w, _ = arr.shape
    circular_distance = avg_kth_msb(img,4) + 1
    circular_set.clear()
    circle_cells(h, w, circular_distance)
    is_large = (h >= 1024 or w >= 1024)
    reserved_pixels = 2 if is_large else 1
    
    if not is_large:
        r = int(arr[h - 1, w - 1, 0])
        g = int(arr[h - 1, w - 1, 1])
        b = int(arr[h - 1, w - 1, 2])
        total_size = (r << 16) | (g << 8) | b
    else:
        p1_r = int(arr[h - 1, w - 2, 0])
        p1_g = int(arr[h - 1, w - 2, 1])
        p1_b = int(arr[h - 1, w - 2, 2])
        p2_r = int(arr[h - 1, w - 1, 0])
        p2_g = int(arr[h - 1, w - 1, 1])
        p2_b = int(arr[h - 1, w - 1, 2])
        total_size = (p1_r << 40) | (p1_g << 32) | (p1_b << 24) | (p2_r << 16) | (p2_g << 8) | p2_b
        
    extracted_list = []
    current_bits_count = 0
    for x in range(h):
        for y in range(w):
            if x == h - 1 and y >= (w - reserved_pixels):
                continue
            for c in range(3):
                if current_bits_count >= total_size:
                    break
                value = int(arr[x, y, c])
                remaining_bits = total_size - current_bits_count
                if (x,y) in circular_set:
                    if remaining_bits == 1:
                        bits_str = format(value & 0b1, "01b")
                        current_bits_count += 1
                    else:
                        bits_str = format(value & 0b11, "02b")
                        current_bits_count += 2
                else:
                    bits_str = format(value & 0b1, "01b")
                    current_bits_count += 1
                extracted_list.append(bits_str)
            if current_bits_count >= total_size:
                break
        if current_bits_count >= total_size:
            break
            
    extracted = "".join(extracted_list)[:total_size]
    bits = bitarray(extracted)
    return decompress_bits(bits)

if __name__ == "__main__":
    try:
        encode_image("images//abstract512.png", "input.txt", "encoded.png")
        recovered = decode_image("encoded.png")
        print("Decoded Output:")
        print(recovered)
    except ValueError as e:
        print(e)
