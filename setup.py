# pylint: disable=no-name-in-module,import-error
import os
from distutils.core import setup

from setuptools import find_packages

DESCRIPTION = "pyosmo - a model-based testing tool"
OWNER_NAMES = 'Olli-Pekka Puolitaival'
OWNER_EMAILS = 'oopee1@gmail.com'


# Utility function to cat in a file (used for the README)
def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


setup(name='pyosmo',
      version='0.0.1',
      description=DESCRIPTION,
      long_description=read('README.md'),
      author=OWNER_NAMES,
      author_email=OWNER_EMAILS,
      maintainer=OWNER_NAMES,
      maintainer_email=OWNER_EMAILS,
      packages=find_packages(include=["pyosmo", "pyosmo.*"]),
      include_package_data=True,
      license="MIT",
      install_requires=[]
      )
