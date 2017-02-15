from setuptools import setup, find_packages

setup(
    name='recapi',
    version='0.0.1',
    description='implicit feedback recommender API',
    author='Christoph Schock',
    author_email='chschock@gmail.com',
    license='MIT',

    packages=find_packages(),
    install_requires=[
        'requests',
    ],
)
