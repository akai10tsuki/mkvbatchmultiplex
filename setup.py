"""Setup.py for mkvbatchmultiplex"""

from setuptools import setup, find_packages

def readme():
    with open('README.rst') as f:
        return f.read()


setup(
    name='mkvbatchmultiplex',  # Required

    version='0.5.3a1.dev2',  # Required

    description='A mkv media batch processor',  # Required

    long_description=readme(),  # Optional

    author='Efrain Vergara',  # Optional
    author_email='akai10tsuki@gmail.com',  # Optional

    classifiers=[  # Optional
        'Development Status :: 3 - Alpha',
        'Environment :: MacOS X',
        'Environment :: Win32 (MS Windows)',
        'Environment :: X11 Applications :: Qt',

        # Indicate who your project is intended for
        'Intended Audience :: End Users/Desktop',
        'Topic :: Multimedia :: Video',

        # Pick your license as you wish
        'License :: OSI Approved :: MIT License',

        # Operating Systems
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows :: Windows 10',
        'Operating System :: POSIX :: Linux',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],

    keywords='mkv multimedia video',  # Optional

    #packages=['mkvbatchmultiplex', 'mkvbatchmultiplex/library'],  # Required
    packages=find_packages(exclude=['docs', 'tests*']),  # Required

    install_requires=[
        'pymediainfo>=2.2.1',
        'PyQt5>=5.10.1'
    ],  # Optional

    python_requires='>=3.6, <4',

    include_package_data=True,

    entry_points={  # Optional
        'console_scripts': [
            'mkvbatchmultiplex=mkvbatchmultiplex.mkvbatchmultiplex:mainApp',
        ],
    },

    project_urls={  # Optional
        'Bug Reports': 'https://github.com/akai10tsuki/mkvbatchmultiplex/issues',
        'Source': 'https://github.com/akai10tsuki/mkvbatchmultiplex/',
    },
)
