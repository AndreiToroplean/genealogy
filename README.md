# genealogy
A set of tools to encode family trees and draw them using ASCII art.

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
genealogy sample_data.yml
```

Output:
```
      ╔════════ James Smith
John Smith
    ╘═╣
      ╚════════ Emily Smith ne.e Johnson
                    ╘═╗
                      ╠════════ Robert Johnson
                      ╠════════ Helen Johnson ne.e Brown
                Michael Johnson
                    ╘═╣
                Sarah Johnson
                    ╘═╝
```
Meaning: 
- John Smith's parents are James and Emily.
- Emily's parents are Robert and Helen.
- Emily has two siblings: Michael and Sarah (since we can see that they all share the same parents).

N.B.:
- Only single-line indicators (╘═) are actually pointing to the names.
- Double-line ones (║) are to be understood as connected together, ignoring the names that appear "in front" of them.
