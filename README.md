# qrcode-generator
Wrapper script for the Python qrcode package, allowing easy commandline generation of QR codes

```
usage: generate_qrcode.py [-h] [-e ERROR_CORRECTION] [-b BORDER_SIZE] [-p BOX_SIZE]
                          [-fc FILL_COLOR] [-bc BACK_COLOR] [-f FACTORY_TYPE] [-v VERSION]
                          [-d] -o OUTPUT_FILE
                          data [data ...]

Generate a QR code from the commandline

positional arguments:
  data                  The data/string to QRify

options:
  -h, --help            show this help message and exit
  -e ERROR_CORRECTION, --error-correction ERROR_CORRECTION
                        Target error correction percentage (default: 25)
  -b BORDER_SIZE, --border-size BORDER_SIZE
                        Size of the border in boxes (default: 5, min: 4)
  -p BOX_SIZE, --box-size BOX_SIZE
                        Pixels per box (default: 10)
  -fc FILL_COLOR, --fill-color FILL_COLOR
                        Foreground/fill color, as HTML name or hex (default: black)
  -bc BACK_COLOR, --back-color BACK_COLOR
                        Background color, as HTML name or hex (default: white)
  -f FACTORY_TYPE, --factory FACTORY_TYPE
                        Image factory type (and output file type) (default: png)
  -v VERSION, --version VERSION
                        Specify a version (1-40). Default: dynamically fitted automatically
  -d, --debug           Turn on debug logging
  -o OUTPUT_FILE, --output-file OUTPUT_FILE
                        Output filename
```
