import os
import platform
import sys


def erg_file():
    if sys.platform == "linux":
        ergFile = "erg-2024-daily-ubuntu-perplexity.dat"

    elif sys.platform == "darwin":
        # Mac returns darwin for both M1 and Intel silicon, need to dig deeper
        unameResult = platform.uname()

        if "ARM" in unameResult.version:
            # M1 silicon
            ergFile = "erg-2023-osx-m1-perplexity.dat"

        else:
            # Intel silicon
            ergFile = "erg-2024-daily-osx-perplexity.dat"

    else:
        ergFile = "erg-2024-daily-ubuntu-perplexity.dat"

    return os.path.join(os.path.dirname(os.path.realpath(__file__)), ergFile)