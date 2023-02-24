import argparse
import os
import sys
from PIL import Image, ImageDraw, ImageFont


def resize_image(image, resized_width):
    """
    Resizes given image while the preserving aspect ratio of the original image.
    Resizing large images reduces image complexity and improves performance during ASCII
    conversion process.

    :param image: The image to be resized.
    :param resized_width: The desired width of the resized image.
    :return: A PIL.Image.Image object.
    """
    aspect_ratio = image.size[1] / image.size[0]
    resized_height = int(resized_width * aspect_ratio)
    return image.resize((resized_width, resized_height))


def image_to_ascii(image, density, font_size, colored=False):
    """
    Converts an image to it's ASCII equivalent.

    :param image: The image to be converted.
    :param density: A string of ASCII characters that maps to the brightness of each pixel. For example using the string
        "@%#*+=-:. " means pure black pixels are assigned the character "@" while pure white pixels are given the value
        " ". Anything else are assigned characters in between. More dense strings would give more gradual transitions
        between colors and lighting.
    :param font_size: The size of each individual ASCII character.
    :param colored: Toggle to allow color in the converted image.
    :return: A PIL.Image.Image object.
    """
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
            r, g, b, a = pixels[x, y]

            # transparent pixels have same RGB values as black (i.e. 0, 0, 0) with alpha = 0 instead of 255
            # need to check alpha channel, to differentiate between the two
            luminosity = 255 if a == 0 else int(r * 0.3 + g * 0.59 + b * 0.11)
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
    ascii_images = []
    video = None

    # set up accepted commandline arguments
    parser = argparse.ArgumentParser(description="Asciify given image(s)")
    path_type = parser.add_mutually_exclusive_group(required=True)
    path_type.add_argument("-f", "-filepath", type=str, help="path to file")
    path_type.add_argument("-d", "-directory", type=str, help="path to directory of images(.png, .jpg, .jpeg)")
    parser.add_argument("-o", "--outputDir", help="path to output directory")
    parser.add_argument("--fontSize", type=int, help="font size of ASCII char for output image. Default: 12")
    parser.add_argument("-r", "--resize", type=int, help="resize width of original image while retaining aspect ratio")
    parser.add_argument("--resizeFinal", type=int, help="resizes width of final image output while retaining"
                                                        " aspect ratio")
    parser.add_argument("-g", "--gif", type=int, help="toggle to output a gif with specified duration of each frame")
    parser.add_argument("-c", "--color", action="store_true", help="toggle color for output image")
    args = parser.parse_args()

    # process commandline arguments
    try:
        if args.f:
            images.append(Image.open(args.f).convert("RGBA"))
        else:
            for filename in os.listdir(args.d):
                if filename.endswith(".jpg") or filename.endswith(".jpeg") or filename.endswith(".png"):
                    images.append(Image.open(os.path.join(args.d, filename)).convert("RGBA"))

            if len(images) < 1:
                print(f"No images were found in {args.d}.")
                sys.exit(0)

    except (FileNotFoundError, OSError) as e:
        print(e)
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)

    if args.outputDir:
        if not os.path.isdir(args.outputDir):
            print(f"{args.outputDir} is not a valid output directory")
            sys.exit(2)
        else:
            output_directory = args.outputDir

    if args.fontSize:
        if args.size < 1:
            print("Font size cannot be negative")
            sys.exit(2)
        else:
            font_size = args.size

    if args.resize:
        if args.resize < 1:
            print("Resized width cannot be negative")
            sys.exit(2)

    if args.gif:
        if args.gif < 1:
            print("Duration of an individual frame cannot be negative")
            sys.exit(2)

    # convert image(s) to ASCII
    print("Converting images...")
    for i in range(len(images)):
        images[i] = resize_image(images[i], args.resize)
        ascii_image = image_to_ascii(images[i], density, font_size, args.color)

        if args.resizeFinal:
            ascii_image = resize_image(ascii_image, args.resizeFinal)

        if args.gif:
            ascii_images.append(ascii_image)
        else:
            ascii_image.save(os.path.join(output_directory, f"output{i}.png"))

        print(f"Processed image #{i}...")

    if args.gif:
        ascii_images[0].save("test.gif", save_all=True, append_images= ascii_images[1:], duration=args.gif, loop=0)
    print("Process completed.")
