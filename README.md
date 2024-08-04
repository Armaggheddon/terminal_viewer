# terminal_viewer 
terminal_viwer is a simple command line application that allows to display media files in the terminal. Uses OpenCV as a backend to open the media files and therefore all media files supported by OpenCv can be opened and displayed.

## Installation
1. Clone the repository: 
    ``` bash
    git clone https://github.com/Armaggheddon/terminal_viewer.git
    cd terminal_viewer
    ```
1. Build the python wheel:
    ``` bash
    python .\setup.py sdist bdist_wheel
    ```
1. Depending on your os:
    ``` bash
    # for windows
    pip install .\dist\terminal_viewer-0.1-py3-none-any.whl

    # for MacOS/Linux
    pip install .\dist\terminal_viewer-0.1.tar.gz
    ```
    [!NOTE]
    If the tool is already installed run the above command with `--force-reinstall` option.
1. Launch the application with:
    ```bash
    terminal_viewer --help
    ```

## Usage
The application supports the following arguments:
- `-s`, `--source`: specifies a single media file to be opened. Multiple files can be specified using a space as a separator between paths.
- `-f`, `--folder`: specifies a single folder that can contain 1 or more media files to be displayed. Multiple folders can be specified using a space as a separator between paths.
- `-g`, `--grayscale`: display the media files in grayscale. By default all the media files are shown in RGB 256. 
- `-h`, `--help`: show the available commands with a brief description.
