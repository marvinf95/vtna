import setuptools


def readme():
    with open('README.rst') as f:
        return f.read()


setuptools.setup(
    name='vtna',
    version='0.0',
    description='Visualizing temporal networks with attributes',
    long_description=readme(),
    url='https://gitlab.uni-koblenz.de/marvinforster/vtna',
    author='Alex Baier, Marvin Forster, Philipp Töws',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 3.6'
    ],
    author_email='',
    license='',
    packages=['vtna'],
    zip_safe=False,
    install_requires=[
        'numpy',
        'pandas',
        'networkx'
    ],
    test_suite='nose.collector',
    tests_require=['nose'],
)
