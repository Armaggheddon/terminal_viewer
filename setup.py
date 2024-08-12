"""
Installation steps:
1. Build wheel with 
    python .\setup.py sdist bdist_wheel
2. Install wheel with
    pip install .\dist\terminal_viewer-0.1-py3-none-any.whl -> for windows
    pip install .\dist\terminal_viewer-0.1.tar.gz -> for linux-mac
2.1 Force install with option --force-reinstall
3. Run with the command
    terminal_viewer --source="/path/to/media.ext"
"""

from setuptools import setup, find_packages

setup(
   name='terminal_viewer',
   version='0.1',
   author='Armaggheddon',
   author_email='your@email.com',
   description='Terminal media viewer, can display images and videos on your terminal.',
   packages=find_packages(),
   requires=['numpy', 'opencv-python', 'av'],
   entry_points={
      'console_scripts': [
         'terminal_viewer=terminal_viewer.main:main',
      ],
   },
)