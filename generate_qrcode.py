#!/usr/bin/env python3
"""
generate_qrcode.py

Generate a QR code on the commandline.
"""

import argparse
import sys
import traceback
from enum import IntEnum

import qrcode as qr  # type: ignore
from qrcode.image.base import BaseImage  # type: ignore
from qrcode.image.pil import PilImage  # type: ignore
from qrcode.image.pure import PymagingImage  # type: ignore
from qrcode.image.svg import SvgFillImage, SvgImage, SvgPathFillImage  # type: ignore

BORDER_PX_MINIMUM = 4
BORDER_PX_DEFAULT = 5
BOX_SIZE_PX_DEFAULT = 10
VERSION_MAXIMUM = 40


class ErrorCorrectionEnum(IntEnum):
    """
    Enum for storing legal error correction values.
    """

    ERROR_CORRECT_M = 0
    ERROR_CORRECT_L = 1
    ERROR_CORRECT_H = 2
    ERROR_CORRECT_Q = 3


QRVersionT = int | None
ErrorCorrectionT = int | ErrorCorrectionEnum


def generate_qrcode(  # noqa: D417, PLR0913
    data: str,
    error_correction: ErrorCorrectionT = ErrorCorrectionEnum.ERROR_CORRECT_Q,
    box_size: int = BOX_SIZE_PX_DEFAULT,
    border: int = BORDER_PX_DEFAULT,
    version: QRVersionT = None,
    debug: bool = False,
) -> qr.QRCode:
    """
    Given a data string, generate a qrcode.QRCode.
    Uses the QRCode class for better control granularity.

    Arguments:
    ---------
        * data             -- Data to QRify, as a str.
        * error_correction -- Error correction enum. See get_error_correction_constant() for info.
        * box_size         -- Specify the pixels per 'box'.
                              Default: 10
        * border           -- Specify the box-width of the border in pixels.
                              Default: 5, Minimum value: 4
        * version          -- Specify the QR version (int in range [1, 40] inclusive.
                              1 is the smallest at 21x21, 40 is the largest at
                              Default: None, which sets the size automatically
        * debug            -- Use debug logging
                              Default: False

    Returns:
    -------
        * qrcode.QRCode object
    """
    if border < BORDER_PX_MINIMUM:
        raise ValueError(
            "Argument 'border' to generate_qrcode() has "
            f"a minimum value {BORDER_PX_MINIMUM}px: "
            f"specified {border}px"
        )
    if version:
        version = int(version)
        try:
            assert version in {_ for _ in range(1, VERSION_MAXIMUM)}
        except AssertionError as err:
            raise ValueError(
                f"Invalid version {version} - must be in range 1 -> {VERSION_MAXIMUM}"
            ) from err
    if not isinstance(error_correction, ErrorCorrectionEnum):
        try:
            error_correction = ErrorCorrectionEnum(error_correction)
        except ValueError as err:
            raise ValueError(
                f"Invalid error correction value {error_correction} - "
                f"must be in range 0 -> {int(max(ErrorCorrectionEnum))}"
            ) from err
    if debug:
        print(
            f"Generating QRCode<version: {version}, error_correction: {error_correction}, "
            f"box_size={box_size}, border={border}>"
        )
    qrcode = qr.QRCode(
        version=version,
        error_correction=int(error_correction),
        box_size=box_size,  # Pixels per 'box'
        border=border,  # Box-width of border (minimum: 4)
    )
    make_kwargs = {"fit": True if version is None else False}
    if debug:
        print(f"Adding data: {data!s}")
        print(f"Using qrcode.make() kwargs: {make_kwargs}")
    qrcode.add_data(data)
    # The fit argument is required to work with version=None
    qrcode.make(**make_kwargs)
    return qrcode


def get_error_correction_constant(desired_error_p: int, debug: bool = False) -> ErrorCorrectionT:  # noqa: D417
    """
    Given a desired error correction value (percentage of total errors that can be handled),
    choose the qrcode.constants enum which has the closest value.

    Arguments:
    ---------
        * desired_error_p  -- desired error correction percentage as an integer (0 - 100 inclusive)
                              Values over 30% will be set to the max, ERROR_CORRECT_H.
        * debug            -- debug logging
                              Default: False

    Returns:
    -------
        * ErrorCorrectionEnum.ERROR_CORRECT_L (0-7%],
          ErrorCorrectionEnum.ERROR_CORRECT_M (7-15%],
          ErrorCorrectionEnum.ERROR_CORRECT_Q (15-25%], or
          ErrorCorrectionEnum.ERROR_CORRECT_H (25-100%]
    """
    if debug:
        print(f"desired_error_p: {desired_error_p}%")
    if desired_error_p < 0 or desired_error_p > 100:  # noqa: PLR2004
        raise ValueError(f"Argument desired_error_p ({desired_error_p}) must be in range 0-100")
    if desired_error_p <= 7:  # noqa: PLR2004
        if debug:
            print("desired_error_p {desired_error_p}% in range 0 - 7, using ERROR_CORRECT_L")
        return ErrorCorrectionEnum.ERROR_CORRECT_L
    elif desired_error_p <= 15:  # noqa: PLR2004
        if debug:
            print("desired_error_p {desired_error_p}% in range 8 - 15, using ERROR_CORRECT_M")
        return ErrorCorrectionEnum.ERROR_CORRECT_M
    elif desired_error_p <= 25:  # noqa: PLR2004
        if debug:
            print("desired_error_p {desired_error_p}% in range 16 - 25, using ERROR_CORRECT_Q")
        return ErrorCorrectionEnum.ERROR_CORRECT_Q
    else:
        if desired_error_p > 30:  # noqa: PLR2004
            print(
                f"WARNING: Specified error correction value ({desired_error_p}) is above the "
                + "max supported value (30). Using max value ERROR_CORRECT_H instead.",
                file=sys.stderr,
            )
        elif debug:
            print(f"desired_error_p {desired_error_p}% in range 26 - 30, using ERROR_CORRECT_H")
        return ErrorCorrectionEnum.ERROR_CORRECT_H


def get_image_factory(factory_type: str) -> BaseImage | None:  # noqa: D417
    """
    Choose an image factory, using a user-input string.

    Arguments:
    ---------
        * factory_type  -- String specifying the factory type.

    Returns:
    -------
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
    factory_type: str | None = None,
    fill_color: str | None = None,
    back_color: str | None = None,
    debug: bool = False,
) -> PilImage:
    """
    # TODO: Fix the documentation comments.
    # TODO: Fix whatever is going on with PymagingImage
    """
    if factory_type:
        if debug:
            print(f"Using factory: {factory_type}")
        image_factory = get_image_factory(factory_type)
        if image_factory:
            print(
                f'WARNING: Ignoring specified colors (fill "{fill_color}" back "{back_color}") '
                + f"with image factory type {factory_type}: "
                + "specifying both the factory type and setting the fill or back "
                + "color is currently unsupported.",
                file=sys.stderr,
            )
            return qrcode.make_image(image_factory=image_factory)
        else:
            print(
                f"WARNING: Unknown image factory type: {image_factory}. Using default.",
                file=sys.stderr,
            )
    if debug:
        print(f"Using default factory type with fill color {fill_color}, back color {back_color}")
    return qrcode.make_image(fill_color=fill_color, back_color=back_color)


def write_image(img: PilImage, filename: str) -> None:
    """
    Given an image and a filename, write the image to file.
    """
    try:
        img.save(filename)
        print(f"Successfully wrote QR code to file: {filename}")
    except (AttributeError, ValueError) as err:
        print(
            f"ERROR: Could not write out file {filename} due to error in generating the image.",
            file=sys.stderr,
        )
        traceback.print_exc()
        raise err
    except OSError as err:
        raise OSError(f"ERROR: Could not write out file {filename}") from err


def main() -> None:
    """
    Main function with the CLI argument parser.
    """
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
        "-v",
        "--version",
        dest="version",
        type=int,
        help="Specify a version (1-40). Default: dynamically fitted automatically",
    )
    parser.add_argument(
        "-d",
        "--debug",
        dest="debug",
        action="store_true",
        help="Turn on debug logging",
    )
    parser.add_argument(
        "-o", "--output-file", dest="output_file", type=str, required=True, help="Output filename"
    )
    parser.add_argument("data", type=str, nargs="+", help="The data/string to QRify")
    args = parser.parse_args()
    error_correction = get_error_correction_constant(args.error_correction, debug=args.debug)
    qrcode = generate_qrcode(
        args.data,
        error_correction=error_correction,
        box_size=args.box_size,
        border=args.border_size,
        version=args.version,
        debug=args.debug,
    )
    img = get_image(qrcode, args.factory_type, args.fill_color, args.back_color, debug=args.debug)
    write_image(img, args.output_file)


if __name__ == "__main__":
    main()
