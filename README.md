# genealogy
A standard for encoding family trees and a script to draw them in ascii.

(Tested on Windows, using Powershell, and Python 3.13.)

## Installation
```
git clone https://github.com/AndreiToroplean/genealogy.git
cd genealogy
python -m venv venv
.\venv\Scripts\activate
pip install -e .
```

## Sample Usage
```
genealogy sample_data.txt
```

Output:
```
John Smith 
    ╘═╦════════ Emily Smith
      ╚════════ James Smith
```
Meaning: "John Smith's parents are Emily Smith and James Smith".
