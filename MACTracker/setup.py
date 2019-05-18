import io

from setuptools import find_packages, setup

with io.open('README.rst', 'rt', encoding='utf8') as f:
    readme = f.read()

setup(
    name='MACTracker',
    version='1.0.0',
    url='http://www.google.com',
    license='BSD',
    maintainer='David Bedoya',
    maintainer_email='bedoyad1@southernct.edu',
    description='MACTracker Webmanagement',
    long_description=readme,
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'flask',
    ],
    extras_require={
        'test': [
            'pytest',
            'coverage',
        ],
    },
)
