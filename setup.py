# pylint: disable=no-name-in-module,import-error
from distutils.core import setup
from os import path

from setuptools import find_packages

DESCRIPTION = "pyosmo - a model-based testing tool"
OWNER_NAMES = 'Olli-Pekka Puolitaival'
OWNER_EMAILS = 'oopee1@gmail.com'


# Utility function to cat in a file (used for the README)
def read(fname):
    this_directory = path.abspath(path.dirname(__file__))
    with open(path.join(this_directory, fname), encoding='utf-8') as f:
        return f.read()


setup(name='pyosmo',
      version='0.1.2',
      python_requires='>=3.8',
      description=DESCRIPTION,
      long_description=read('README.md'),
      long_description_content_type='text/markdown',
      author=OWNER_NAMES,
      author_email=OWNER_EMAILS,
      maintainer=OWNER_NAMES,
      maintainer_email=OWNER_EMAILS,
      packages=find_packages(include=["pyosmo", "pyosmo.*"]),
      include_package_data=True,
      license="MIT",
      install_requires=['click'],
      entry_points={
          'console_scripts': ['pyosmo=pyosmo.main:pyosmo_cli'],
      })
