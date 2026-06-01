from pathlib import Path
import struct
import zlib
import unicodedata

FONT = {
"A":["01110","10001","10001","11111","10001","10001","10001"],
"B":["11110","10001","10001","11110","10001","10001","11110"],
"C":["01111","10000","10000","10000","10000","10000","01111"],
"D":["11110","10001","10001","10001","10001","10001","11110"],
"E":["11111","10000","10000","11110","10000","10000","11111"],
"F":["11111","10000","10000","11110","10000","10000","10000"],
"G":["01111","10000","10000","10111","10001","10001","01111"],
"H":["10001","10001","10001","11111","10001","10001","10001"],
"I":["11111","00100","00100","00100","00100","00100","11111"],
"J":["00111","00010","00010","00010","10010","10010","01100"],
"K":["10001","10010","10100","11000","10100","10010","10001"],
"L":["10000","10000","10000","10000","10000","10000","11111"],
"M":["10001","11011","10101","10101","10001","10001","10001"],
"N":["10001","11001","10101","10011","10001","10001","10001"],
"O":["01110","10001","10001","10001","10001","10001","01110"],
"P":["11110","10001","10001","11110","10000","10000","10000"],
"Q":["01110","10001","10001","10001","10101","10010","01101"],
"R":["11110","10001","10001","11110","10100","10010","10001"],
"S":["01111","10000","10000","01110","00001","00001","11110"],
"T":["11111","00100","00100","00100","00100","00100","00100"],
"U":["10001","10001","10001","10001","10001","10001","01110"],
"V":["10001","10001","10001","10001","10001","01010","00100"],
"W":["10001","10001","10001","10101","10101","10101","01010"],
"X":["10001","10001","01010","00100","01010","10001","10001"],
"Y":["10001","10001","01010","00100","00100","00100","00100"],
"Z":["11111","00001","00010","00100","01000","10000","11111"],
"0":["01110","10001","10011","10101","11001","10001","01110"],
"1":["00100","01100","00100","00100","00100","00100","01110"],
"2":["01110","10001","00001","00010","00100","01000","11111"],
"3":["11110","00001","00001","01110","00001","00001","11110"],
"4":["00010","00110","01010","10010","11111","00010","00010"],
"5":["11111","10000","10000","11110","00001","00001","11110"],
"6":["01110","10000","10000","11110","10001","10001","01110"],
"7":["11111","00001","00010","00100","01000","01000","01000"],
"8":["01110","10001","10001","01110","10001","10001","01110"],
"9":["01110","10001","10001","01111","00001","00001","01110"],
" ":["00000","00000","00000","00000","00000","00000","00000"],
"-":["00000","00000","00000","11111","00000","00000","00000"],
".":["00000","00000","00000","00000","00000","01100","01100"],
"!":["00100","00100","00100","00100","00100","00000","00100"],
}

def _chunk(tag, data):
    return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data) & 0xffffffff)

def write_rgb_png(path, width, height, pixels):
    raw = bytearray()
    stride = width * 3
    for y in range(height):
        raw.append(0)
        start = y * stride
        raw.extend(pixels[start:start + stride])
    data = b"".join([
        b"\x89PNG\r\n\x1a\n",
        _chunk(b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)),
        _chunk(b"IDAT", zlib.compress(bytes(raw), level=9)),
        _chunk(b"IEND", b""),
    ])
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Path(path).write_bytes(data)

def clean_text(text):
    text = unicodedata.normalize("NFKD", str(text))
    text = "".join(ch for ch in text if not unicodedata.combining(ch))
    out = []
    for ch in text.upper():
        out.append(ch if ch in FONT else " ")
    return "".join(out)

def new_canvas(width, height, color):
    r, g, b = color
    return bytearray([r, g, b] * width * height)

def rect(pixels, width, height, x, y, w, h, color):
    r, g, b = color
    x0 = max(0, int(x)); y0 = max(0, int(y))
    x1 = min(width, int(x + w)); y1 = min(height, int(y + h))
    for yy in range(y0, y1):
        row = yy * width * 3
        for xx in range(x0, x1):
            i = row + xx * 3
            pixels[i] = r; pixels[i+1] = g; pixels[i+2] = b

def text_size(text, scale):
    text = clean_text(text)
    return len(text) * 6 * scale, 7 * scale

def draw_text(pixels, width, height, text, x, y, scale, color):
    text = clean_text(text)
    cursor = int(x)
    for ch in text:
        glyph = FONT.get(ch, FONT[" "])
        for gy, row in enumerate(glyph):
            for gx, value in enumerate(row):
                if value == "1":
                    rect(pixels, width, height, cursor + gx * scale, y + gy * scale, scale, scale, color)
        cursor += 6 * scale

def centered_text(pixels, width, height, text, y, scale, color):
    tw, th = text_size(text, scale)
    x = (width - tw) // 2
    draw_text(pixels, width, height, text, x, y, scale, color)

def create_campaign_png(path, title, subtitle, cta):
    width = 1080
    height = 1080

    bg = (13, 36, 58)
    blue = (0, 132, 196)
    sand = (244, 196, 111)
    white = (245, 247, 250)
    green = (38, 166, 91)
    dark = (8, 24, 39)

    pixels = new_canvas(width, height, bg)

    rect(pixels, width, height, 0, 0, 1080, 1080, bg)
    rect(pixels, width, height, 0, 0, 1080, 210, blue)
    rect(pixels, width, height, 0, 850, 1080, 230, dark)
    rect(pixels, width, height, 70, 285, 940, 415, (18, 55, 83))
    rect(pixels, width, height, 70, 285, 940, 14, sand)
    rect(pixels, width, height, 70, 686, 940, 14, sand)

    centered_text(pixels, width, height, title, 88, 13, white)
    centered_text(pixels, width, height, subtitle, 375, 9, sand)
    centered_text(pixels, width, height, cta, 905, 8, white)

    rect(pixels, width, height, 180, 745, 720, 70, green)
    centered_text(pixels, width, height, "K-OS CAMPANHA ATIVA", 765, 5, white)

    write_rgb_png(path, width, height, pixels)
    return {
        "width": width,
        "height": height,
        "format": "png",
        "path": str(path),
    }
