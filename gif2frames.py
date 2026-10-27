import sys
from PIL import Image, ImageSequence

# 輝度に応じたアスキー文字テーブル（暗い順）
ASCII_CHARS = " .:-=+*#%@"

def pixel_to_ansi(r, g, b, a=255):
    # 透明ピクセルは空白として出力
    if a < 128:
        return " "
    
    # 輝度計算（グレースケール変換標準式）
    luminance = int(0.299 * r + 0.587 * g + 0.114 * b)
    char_idx = int((luminance / 255) * (len(ASCII_CHARS) - 1))
    char = ASCII_CHARS[char_idx]
    
    # ANSI TrueColor (24-bit) 形式で色をつけて文字を出力
    return f"\033[38;2;{r};{g};{b}m{char}\033[0m"

def convert_gif_to_frames(gif_path, output_path, target_width=45):
    with Image.open(gif_path) as im:
        aspect_ratio = im.height / im.width
        # ターミナル文字の縦長補正（約0.5倍）
        target_height = int(target_width * aspect_ratio * 0.5)

        frames_output = []

        for frame in ImageSequence.Iterator(im):
            # RGBA に正規化してリサイズ
            img = frame.convert("RGBA").resize((target_width, target_height), Image.Resampling.LANCZOS)
            pixels = img.load()

            frame_lines = []
            for y in range(target_height):
                line = "".join(pixel_to_ansi(*pixels[x, y]) for x in range(target_width))
                frame_lines.append(line)
            
            frames_output.append("\n".join(frame_lines))

        # frames.txt 形式で書き出し
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("\n===FRAME===\n".join(frames_output))

    print(f"変換完了: {len(frames_output)} フレームを {output_path} に出力しました。")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python gif2frames.py <input.gif> [target_width]")
        sys.exit(1)

    input_gif = sys.argv[1]
    width = int(sys.argv[2]) if len(sys.argv) > 2 else 45
    convert_gif_to_frames(input_gif, "frames.txt", width)
