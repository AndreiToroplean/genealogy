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
    ╘═╦════════ Emily Smith ne.e Johnson
      ║             ╘═╗
      ╚════════ James Smith
                Sarah Johnson
                    ╘═╣
                Michael Johnson
                    ╘═╬════════ Helen Johnson ne.e Brown
                      ╚════════ Robert Johnson
```
Meaning: 
- John Smith's parents are Emily and James.
- Emily's parents are Helen and Robert.
- Emily has two siblings: Sarah and Michael (since we can see that they all share the same parents).

N.B.:
- Only single-line indicators (╘═) are actually pointing to the names.
- Double-line ones (║) are to be understood as connected together, ignoring the names that appear "in front" of them.
