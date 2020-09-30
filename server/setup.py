import setuptools
import os

setuptools.setup(
    name="bert-server",
    version=os.environ.get("TAG", "0.0.0"),
    packages=setuptools.find_packages(),
    install_requires=[
        "flask", "gunicorn"
    ],
    include_package_data=True,
    entry_points={
        "console_scripts": [
            "bert-server-download=server.download_files:download",
        ]
    },
)
