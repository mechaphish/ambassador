from setuptools import setup, find_packages

setup(
    name='ambassador',
    version='0.0.1',
    description=u"Officially delegated component to report info from/to CGC TI API",
    classifiers=[],
    keywords='',
    author=u"Francesco Disperati",
    author_email='francesco@cs.ucsb.edu',
    packages=find_packages(exclude=['tests']),
    include_package_data=True,
    install_requires=[
        'farnsworth',
        'python-dotenv>=0.3.0',
    ],
    extras_require={
        'test': [
            'nose>=1.3.7',
        ],
    },
    entry_points={
        'console_scripts': [
            "ambassador=ambassador.scripts.cli:main"
        ],
    }
)
