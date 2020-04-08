from setuptools import setup, find_packages

setup(
    name='solid-rock-hb',
    version='1.0.0',
    packages=find_packages(),
    description='Normalization, collation, and conversion tools developed for the preparation of the Solid Rock Greek Hebrew Bible',
    author='Joey McCollum',
    license='MIT',
    author_email='jjmccollum@vt.edu',
    url='https://github.com/jjmccollum/solid-rock-hb',
    python_requires='>=3.5',
    install_requires=[
        'lxml',
        'collatex',
        'python-Levenshtein'
    ],
	classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ]
)