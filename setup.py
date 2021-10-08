from setuptools import setup, find_packages

setup(
    name='declarativeTask3',
    version='2021.10',
    description='a declarative memory task',
    # long_description="""""",
    url='https://github.com/labdoyon/declarativeTask3',
    author='Thibault Vlieghe (current), Arnaud Boré (original)',
    # author_email='author@example.com',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Scientists',
        'Topic :: declarative memory :: Sleep :: memory reactivation :: memory manipulation during sleep',
        'License :: MIT License',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
    keywords='memory, declarative, sleep, reactivation',
    package_dir={'': 'src'},
    packages=find_packages(where='src'),
    python_requires='>=3.6, <4',
    # install_requires=[],
    # entry_points={  # Optional
    #     'console_scripts': [
    #         'sample=sample:main',
    #     ],
    # },
    # project_urls={  # Optional
    #     'Bug Reports': 'https://github.com/pypa/sampleproject/issues',
    #     'Funding': 'https://donate.pypi.org',
    #     'Say Thanks!': 'http://saythanks.io/to/example',
    #     'Source': 'https://github.com/pypa/sampleproject/',
    # },
)
