import re
from distutils.core import setup

# Get version this way, so that we don't load any modules.
with open('./myob/__init__.py') as f:
    exec(re.search(r'VERSION = .*', f.read(), re.DOTALL).group())

try:
    setup(
        name='pymyob',
        packages=['myob'],
        version=__version__,
        description="A Python API around MYOB's AccountRight API.",
        license='BSD',
        author='Jarek Głowacki',
        author_email='jarekwg@gmail.com',
        url='https://github.com/ABASystems/pymyob',
        keywords=['myob'],
        classifiers=[
            'Development Status :: 2 - Pre-Alpha',
            'Environment :: Web Environment',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: BSD License',
            'Operating System :: OS Independent',
            'Programming Language :: Python',
            'Programming Language :: Python :: 3.5',
            'Topic :: Office/Business',
        ],
        install_requires=[
            'requests>=2.10.0',
            'requests-oauthlib>=0.6.0',
        ],
    )
except NameError:
    raise RuntimeError("Unable to determine version.")
