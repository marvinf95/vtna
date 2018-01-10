import setuptools


def readme():
    with open('README.rst') as f:
        return f.read()


setuptools.setup(
    name='vtna',
    version='0.1.1',
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
        'pandas>=0.21.0',
        'networkx>=2.0',
        'scipy',
        'sklearn'
    ],
    test_suite='nose.collector',
    tests_require=['nose', 'coverage'],
    setup_requires=['nose', 'coverage']
)
