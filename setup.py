"""
Setup script para instalar el juego como paquete
"""
from setuptools import setup, find_packages

setup(
    name="mage-arena-3d",
    version="0.1.0",
    description="Juego de combate mágico con control por voz y raycasting",
    author="Tu Nombre",
    author_email="tu@email.com",
    packages=find_packages(),
    install_requires=[
        "pygame>=2.5.0",
        "SpeechRecognition>=3.10.0",
        "pyaudio>=0.2.13",
    ],
    python_requires=">=3.11",
    entry_points={
        "console_scripts": [
            "mage-arena=src.main:main",
        ],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Games/Entertainment",
        "Programming Language :: Python :: 3.11",
    ],
)