from setuptools import setup, find_packages

setup(
    name="isobrain",
    version="0.2.0",
    author="Harriss",
    description="Ultra-lightweight Local AI Agent for OS & Office Automation",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "rich>=13.0.0",
        "prompt_toolkit>=3.0.0",
        "typer>=0.9.0",
        "rapidfuzz>=3.0.0",
        "python-docx>=1.0.0",
        "openpyxl>=3.1.0",
        "docx2pdf>=0.1.8",  # Thêm thư viện chuyển Word -> PDF
    ],
    entry_points={
        "console_scripts": [
            "isobrain = isobrain.cli:main",
        ],
    },
    python_requires=">=3.8",
)