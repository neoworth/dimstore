
"""
"
" publish package to pypl index
" docu: https://realpython.com/pypi-publish-python-package/
" docu: https://packaging.python.org/tutorials/packaging-projects/
"
"""
from setuptools import setup, Command, find_packages
import os

with open("README.md", "r") as fh:
    long_description = fh.read()

"""
"
" clean up build files. e.g. python setup.py clean
" docu: https://stackoverflow.com/questions/3779915/why-does-python-setup-py-sdist-create-unwanted-project-egg-info-in-project-r
"
"""
class CleanCommand(Command):
    """Custom clean command to tidy up the project root."""
    user_options = []
    def initialize_options(self):
        pass
    def finalize_options(self):
        pass
    def run(self):
        os.system('rm -vrf ./build ./dist ./src/*.egg-info ./*.pyc ./*.tgz ./*.egg-info')

setup(
    name='DimStore',
    version='0.0.12',
    license='BSD 2-Clause License',
    author='Kai Niu',
    author_email='kai.niu@ibm.com',
    description='an implementation of feature store',
    long_description='###an implementation of feature store',
    long_description_content_type="text/markdown",
    url=" ",
    packages= find_packages(where='./src'),
    package_dir={
        '': 'src',
    },
    keywords=[
        'feature store', 'data science', 'pipeline'
    ],
    zip_safe=True,
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Topic :: Utilities' 
    ],
    python_requires='>=3.6',
    install_requires=[
        # eg: 'aspectlib==1.1.1', 'six>=1.7',
        'dill ~= 0.2.9',
        'pickleshare ~= 0.7.5',
        'botocore ~= 1.12.201', 
        'ibm-cos-sdk ~= 2.5.2',
        'ibm-cos-sdk-core ~= 2.5.2',
        'ibm-cos-sdk-s3transfer ~= 2.5.2',
        'pyspark ~= 2.4.0'
    ],
    extras_require={
        'dev' : [''],
        'test' : ['pytest', 'pytest-cov','mock']
    },
    cmdclass={
        'clean': CleanCommand,
    }
)


""""
To build package:
1. move to project root directory
2. python3 setup.py sdist bdist_wheel
3. check dist/ folder
4. python3 -m pip install --user --upgrade twine (optional)
5. python3 -m twine upload dist/*
6. python3 -m setup.py clean
"""