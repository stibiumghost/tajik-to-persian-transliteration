# Tajik-to-Persian transliteration

A Tajik-to-Persian transliteration model based on https://github.com/bashartalafha/Arabizi-Transliteration. The project includes the tg-fa parallel corpus, the trained model, and the framework for its implementation.

The presented model shows a Levenshtein ratio of 0.96.

## Dependency

- `numpy`
- `keras`

## Installation and Usage

```pip install tg2fa_translit```

```py
from tg2fa_translit.conversion import convert

text = 'То ғами фардо нахӯрем!'
print(convert(text))  # can be printed in reverse order; in this case copy-paste the output or write directly to a file
```
