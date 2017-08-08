"""Setup for data-structures."""
from setuptools import setup

DEPENDENCIES = ['beautifulsoup4', 'requests', 'html5lib']
MODULES = ['get_doc']
EXTRA_PACKAGES = {
    'testing': ['ipython', 'pytest']
}
CONSOLE_SCRIPTS = {
    'console_scripts': [
        'get_doc = get_doc:main',
    ]
}
setup(
    name="",
    description="""Python modules for postprisonedu project with PuPPy.""",
    version='0.1',
    author='Joe Sirott, Ophelia Yin',
    author_email='',
    license='MIT',
    package_dir={'': 'src'},
    # insert the names of pymodule into array
    py_modules=MODULES,
    install_requires=DEPENDENCIES,
    extras_require=EXTRA_PACKAGES,
    # console scripts allow for custom commands
    entry_points=CONSOLE_SCRIPTS
)
