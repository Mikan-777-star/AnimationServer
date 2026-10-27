import sys
from PIL import Image, ImageSequence

def get_ansi_block(top_rgb, bot_rgb):
    # 透明ピクセルの判定 (alpha < 128)
    top_trans = top_rgb[3] < 128
    bot_trans = bot_rgb[3] < 128

    if top_trans and bot_trans:
        return " "
    elif top_trans and not bot_trans:
        # 上が透明、下が色あり -> 下半分文字 (▄)
        r, g, b = bot_rgb[:3]
        return f"\033[38;2;{r};{g};{b}m▄\033[0m"
    elif not top_trans and bot_trans:
        # 上が色あり、下が透明 -> 上半分文字 (▀)
        r, g, b = top_rgb[:3]
        return f"\033[38;2;{r};{g};{b}m▀\033[0m"
    else:
        # 両方色あり -> 前景色=上、背景色=下で ▀ を描画
        tr, tg, tb = top_rgb[:3]
        br, bg, bb = bot_rgb[:3]
        return f"\033[38;2;{tr};{tg};{tb};48;2;{br};{bg};{bb}m▀\033[0m"

def convert(gif_path, output_path, target_width=60):
    with Image.open(gif_path) as im:
        aspect = im.height / im.width
        # ハーフブロックを使う場合、縦は1文字=2pxなので、実質ピクセル高さを (幅 * aspect) にできる
        target_height = int(target_width * aspect)
        # 偶数行に揃える
        if target_height % 2 != 0:
            target_height += 1

        frames = []
        for frame in ImageSequence.Iterator(im):
            img = frame.convert("RGBA").resize((target_width, target_height), Image.Resampling.NEAREST)
            pixels = img.load()

            lines = []
            # 2ピクセルずつ縦に進む
            for y in range(0, target_height, 2):
                line = "".join(get_ansi_block(pixels[x, y], pixels[x, y+1]) for x in range(target_width))
                lines.append(line)
            frames.append("\n".join(lines))

        with open(output_path, "w", encoding="utf-8") as f:
            f.write("\n===FRAME===\n".join(frames))

    print(f"変換完了: 横{target_width}文字、縦{target_height//2}行で出力したわ。")

if __name__ == "__main__":
    convert(sys.argv[1], "frames.txt", int(sys.argv[2]) if len(sys.argv) > 2 else 60)
