#!/usr/bin/env python3
"""
generate_qrcode.py

Generate a QR code on the commandline.
"""

import argparse
import PIL as pil
import qrcode as qr
import sys
import traceback
from qrcode.image.base import BaseImage
from qrcode.image.pure import PymagingImage
from qrcode.image.svg import SvgImage, SvgFillImage, SvgPathFillImage
from qrcode.image.pil import PilImage
from typing import Optional


def prompt_for_data() -> str:
    """Ask the user for the string to generate a QR code for."""
    pass


def generate_qrcode(
    data: str,
    error_correction: int = qr.constants.ERROR_CORRECT_Q,
    box_size: int = 10,
    border: int = 5,
) -> qr.QRCode:
    """
    Given a data string, generate a qrcode.QRCode.
    Uses the QRCode class for better control granularity.

    Arguments:
        * data             -- Data to QRify, as a str.
        * error_correction -- Error correction enum. See get_error_correction_constant() for info.
        * box_size         -- specify the pixels per 'box'. Default: 10
        * border           -- Specigy the box-width of the border. Default: 5, Min: 4

    Returns:
        * qrcode.QRCode object
    """
    if border < 4:
        raise ValueError(f"Argument to QRCode `border` has minimum value 4: specified {border}")
    qrcode = qr.QRCode(
        version=None,  # 'None' sets the size automatically
        error_correction=qr.constants.ERROR_CORRECT_Q,  # Correct up to 25% errors
        box_size=box_size,  # Pixels per 'box'
        border=border,  # Box-width of border (minimum: 4)
    )
    qrcode.add_data(data)
    qrcode.make(fit=True)  # The fit argument is required to work with version=None
    return qrcode


def get_error_correction_constant(desired_error_p: int) -> int:
    """
    Given a desired error correction value (percentage of total errors that can be handled),
    choose the qrcode.constants enum which has the closest value.

    Arguments:
        * desired_error_p  -- desired error correction percentage as an integer (0 - 100 inclusive)
                              Values over 30% will be set to the max, ERROR_CORRECT_H.

    Returns:
        * qrcode.constants.ERROR_CORRECT_L (0-7%],
          qrcode.constants.ERROR_CORRECT_M (7-15%],
          qrcode.constants.ERROR_CORRECT_Q (15-25%], or
          qrcode.constants.ERROR_CORRECT_H (25-100%]
    """
    if desired_error_p < 0 or desired_error_p > 100:
        raise ValueError(f"Argument desired_error_p ({desired_error_p}) must be in range 0-100")
    if desired_error_p <= 7:
        return qr.constants.ERROR_CORRECT_L
    elif desired_error_p <= 15:
        return qr.constants.ERROR_CORRECT_M
    elif desired_error_p <= 25:
        return qr.constants.ERROR_CORRECT_Q
    else:
        if desired_error_p > 30:
            print(
                f"WARNING: Specified error correction value ({desired_error_p}) is above the "
                + f"max supported value (30). Using max value instead.",
                file=sys.stderr,
            )
        return qr.constants.ERROR_CORRECT_H


def get_image_factory(factory_type: str) -> Optional[BaseImage]:
    """
    Choose an image factory, using a user-input string.

    Arguments:
        * factory_type  -- String specifying the factory type.

    Returns:
        * BaseImage subclass: SvgImage, SvgPathFillImage, SvgFillImage, or PymagingImage.
    """
    return {
        "svg": SvgImage,
        "svgpath": SvgPathFillImage,
        "svgfill": SvgFillImage,
        "png": PymagingImage,
        "pymaging": PymagingImage,
        # 'default': None
    }.get(factory_type)


def get_image(
    qrcode: qr.QRCode,
    factory_type: Optional[str] = None,
    fill_color: Optional[str] = None,
    back_color: Optional[str] = None,
) -> PilImage:
    """ """
    # TODO: Fix the documentation comments.
    # TODO: Fix whatever is going on with PymagingImage
    if factory_type:
        image_factory = get_image_factory(factory_type)
        if image_factory:
            print(
                f'WARNING: Ignoring specified colors (fill "{fill_color}" back "{back_color}") '
                + f"with image factory type {factory_type}: "
                + f"specifying both the factory type and setting the fill or back "
                + f"color is currently unsupported.",
                file=sys.stderr,
            )
            return qrcode.make_image(image_factory=image_factory)
        else:
            print(
                f"WARNING: Unknown image factory type: {image_factory}. Using default.",
                file=sys.stderr,
            )
    return qrcode.make_image(fill_color=fill_color, back_color=back_color)


def post_process_image(img: PilImage) -> PilImage:
    """ """
    pass


def write_image(img: PilImage, filename: str) -> None:
    """
    Given an image and a filename, write the image to file.
    """
    try:
        img.save(filename)
        print(f"Successfully wrote QR code to file: {filename}")
    except (AttributeError, ValueError):
        print(
            f"ERROR: Could not write out file {filename} due to error in generating the image.",
            file=sys.stderr,
        )
        traceback.print_exc()
    except IOError as ex:
        print(
            f"ERROR: Could not write out file {filename} due to IOError {ex.message}.",
            file=sys.stderr,
        )


def main() -> None:
    """ """
    parser = argparse.ArgumentParser(description="Generate a QR code from the commandline")
    parser.add_argument(
        "-e",
        "--error-correction",
        dest="error_correction",
        type=int,
        default=25,
        help="Target error correction percentage (default: 25)",
    )
    parser.add_argument(
        "-b",
        "--border-size",
        dest="border_size",
        type=int,
        default=5,
        help="Size of the border in boxes (default: 5, min: 4)",
    )
    parser.add_argument(
        "-p",
        "--box-size",
        dest="box_size",
        type=int,
        default=10,
        help="Pixels per box (default: 10)",
    )
    parser.add_argument(
        "-fc",
        "--fill-color",
        dest="fill_color",
        type=str,
        default="black",
        help="Foreground/fill color, as HTML name or hex (default: black)",
    )
    parser.add_argument(
        "-bc",
        "--back-color",
        dest="back_color",
        type=str,
        default="white",
        help="Background color, as HTML name or hex (default: white)",
    )
    parser.add_argument(
        "-f",
        "--factory",
        dest="factory_type",
        type=str,
        help="Image factory type (and output file type) (default: png)",
    )
    parser.add_argument(
        "-o", "--output-file", dest="output_file", type=str, required=True, help="Output filename"
    )
    parser.add_argument("data", type=str, nargs="+", help="The data/string to QRify")
    args = parser.parse_args()
    error_correction = get_error_correction_constant(args.error_correction)
    qrcode = generate_qrcode(args.data, error_correction, args.box_size, args.border_size)
    img = get_image(qrcode, args.factory_type, args.fill_color, args.back_color)
    write_image(img, args.output_file)


if __name__ == "__main__":
    main()
