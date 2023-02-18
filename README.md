```python
import httpimport


with httpimport.github_repo('laquazi', 'chinpokomon_utils', 'chinpokomon_utils'):
    from chinpokomon_utils import mypprint as print
    from chinpokomon_utils import update_chromedriver, connect, get_onload, By
```
