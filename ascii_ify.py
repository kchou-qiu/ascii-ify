import argparse
import os
import sys
from PIL import Image, ImageDraw, ImageFont


def resize_image(image, resized_width):
    # resize original image to reduce pixel count + image complexity
    # given width determines # of ASCII characters in final image
    aspect_ratio = image.size[1] / image.size[0]
    resized_height = int(resized_width * aspect_ratio)
    return image.resize((resized_width, resized_height))


def image_to_ascii(image, density, font_size, colored=False):
    # set up blank image to draw ASCII characters on
    font = ImageFont.truetype(os.path.join(os.environ["WINDIR"], "Fonts", "consola.ttf"), size=font_size)
    b_left, b_top, b_right, b_bottom = font.getbbox("@")
    ascii_image = Image.new("RGB", (image.size[0] * b_right, image.size[1] * b_bottom), color=(255, 255, 255))
    draw = ImageDraw.Draw(ascii_image)

    # use grayscale pixel brightness to determine how "dense" ASCII char should be
    pixels = image.load()
    fill_color = (0, 0, 0)

    for x in range(image.size[0]):
        for y in range(image.size[1]):
            r, g, b = pixels[x, y]
            luminosity = int(r * 0.3 + g * 0.59 + b * 0.11)
            pixels[x, y] = (luminosity, luminosity, luminosity)
            ascii_char = density[int(luminosity * (len(density) - 1) / 255)]

            if colored:
                fill_color = (r, g, b)

            draw.text((x * b_right, y * b_bottom), ascii_char, font=font, fill=fill_color)

    return ascii_image


if __name__ == "__main__":
    output_directory = os.getcwd()
    density = "@%#*+=-:. "
    font_size = 12
    images = []

    # set up accepted commandline arguments
    parser = argparse.ArgumentParser(description="Asciify given image(s)")
    path_type = parser.add_mutually_exclusive_group(required=True)
    path_type.add_argument("-f", "-filepath", type=str, help="path to file to asciify")
    path_type.add_argument("-d", "-directory", type=str, help="path to directory of images to asciify")
    parser.add_argument("-o", "--outputDir", help="path to output directory")
    parser.add_argument("-s", "--size", type=int, help="font size of ASCII char for output image. Default: 12")
    parser.add_argument("-r", "--resize", type=int, help="resize width of image while retaining aspect ratio")
    parser.add_argument("-c", "--color", action="store_true", help="toggle color for output image")
    parser.add_argument("-v", "--video", action="store_true", help="toggle for video output instead of images")
    args = parser.parse_args()

    # process commandline arguments
    if args.f:
        # open a single image
        if not os.path.isfile(args.f):
            print(f"{args.f} doesn't exist")
            sys.exit(2)
        else:
            try:
                images.append(Image.open(args.f).convert("RGB"))
            except OSError as err:
                print(f"Unable to open file: {err}")
                sys.exit(1)
    else:
        # open all image files in directory
        if not os.path.isdir(args.d):
            print("Given filepath is not a directory.")
            sys.exit(2)
        else:
            for filename in os.listdir(args.d):
                if filename.endswith(".jpg") or filename.endswith(".jpeg") or filename.endswith(".png"):
                    try:
                        images.append(Image.open(os.path.join(args.d, filename)).convert("RGB"))
                    except OSError as err:
                        print(f"Unable to open file: {err}")
                        sys.exit(1)

            if len(images) < 1:
                print(f"No images were found in {args.d}.")
                sys.exit(0)

    # override output directory
    if args.outputDir:
        if not os.path.isdir(args.outputDir):
            print(f"{args.outputDir} is not a directory.")
            sys.exit(2)
        else:
            output_directory = args.outputDir

    # override font size
    if args.size:
        if args.size < 1:
            print("Font size cannot be negative")
            sys.exit(2)
        else:
            font_size = args.size

    # resize image(s)
    if args.resize:
        if args.resize < 1:
            print("Resized width cannot be negative.")
            sys.exit(2)
        else:
            print("Resizing images...")
            images = [resize_image(image, args.resize) for image in images]
            print(f"{len(images)} images resized!")

    # convert image to ASCII
    print("Converting images...")
    ascii_images = [image_to_ascii(image, density, font_size, args.color) for image in images]
    print(f"{len(ascii_images)} images converted!")

    # save image to output directory
    for i in range(len(ascii_images)):
        ascii_images[i].save(os.path.join(output_directory, f"image{i}.png"))
