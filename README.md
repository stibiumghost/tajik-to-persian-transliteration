
# Tajik-to-Persian transliteration

A Tajik-to-Persian transliteration project. It includes:

* Tajik-Persian parallel corpus;

* 2 (best) trained models;

* aligning algorithms;

* implementation of the best model.

## /data

Text data in the Tajik-Persian parallel corpus was matched algorithmically. It is NOT preprocessed. Both full and segmented texts are given. You can find the overview of the dataset in */data/data_overview.ipynb*.

There are:

* ~ 101 thousand pairs of bayts (couplets);

* ~ 24 thousand pairs of sentences;

* ~ 50 thousand pairs of single words.

## /tg2fa_match

The aligning algorithms can be found here (with examples).

```py
from tg2fa_match import ParallelText, match_words

>>>tg = 'Фориғ зи умеди раҳмату бими азоб'
>>>fa = 'فارغ ز امید رحمت و بیم عذاب'
>>>matched = ParallelText(match_words(tg, fa))
>>>matched
--------------------------------------------
Фориғ |‎ зи |‎ умеди |‎ раҳмату |‎ бими |‎ азоб                  
فارغ  |‎ ز  |‎ امید  |‎ رحمت و  |‎ بیم  |‎ عذاب  
 1.0  |‎1.0 |‎  1.0  |‎   1.0   |‎ 1.0  |‎ 1.0
--------------------------------------------
```

## /models

*Look here for the training .ipynb documents and trained models.*

While the LSTM-based model gives slightly better results, it is ~50 times slower than Transformer-based model. So the latter is implemented. It shows a Levenshtein ratio of 0.988.

## /tg2fa_translit

The implementation of the best Tajik-to-Persian transliteration model.

It can be downloaded with **pip**:

### Installation
```pip install tg2fa_translit```

### Dependency
- `numpy`
- `torch` (CPU is OK!)

### API

```py
from tg2fa_translit import convert

tg_text = 'То ғами фардо нахӯрем!'
fa_text = convert(text)
print(fa_text)
'تا غم فردا نخوریم!'
# Depending on your setup, the resulting string can be displayed incorrectly.
```
