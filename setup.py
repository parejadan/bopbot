import setuptools


setuptools.setup(
    install_requires=[
        "asyncio==3.4.3",
        "pyppeteer==0.2.2",
        "user-agent==0.1.9",
        "psutil==5.7.0",
        "python-json-logger==0.1.11",
    ],
    include_package_data=True,
    packages=setuptools.find_packages(exclude=("*.tests.*",)),
    package_data={
        "bopbot": ["static/*"]
    }
)
