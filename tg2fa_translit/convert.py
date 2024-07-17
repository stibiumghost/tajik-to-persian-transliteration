import re
from decode import decode
from transformer import transformer


norm = str.maketrans({'Ѓ':'Ғ', 'Ї':'Ӣ', 'Ќ':'Қ', 'Ў':'Ӯ', 'Њ':'Ҳ', 'Љ':'Ҷ',
                         'ѓ':'ғ', 'ї':'ӣ', 'ќ':'қ', 'ў':'ӯ', 'њ':'ҳ', 'љ':'ҷ'})
norm.update(str.maketrans('-‐−◌̱¯–—', '-' * 8)) # type: ignore

upper = rf'{"абвгғдеёжзиӣйкқлмнопрстуӯфхҳчҷшъэюяь".upper()}'

part_middle = ('шуд', 'шуда', 'нашуда', 'ки', 'он',
               'ӯ', 'гуфт', 'чун', 'гар', 'чи', 'чӣ')
part_start = ('ба', 'бар', 'бо', 'то', 'ту', 'ҳар',
              'дар', 'аз', 'к-аз', 'зи', 'чу', 'ҳам',
              'ҳаме', 'ҳамон', 'бад-он', 'сар')
part_end = ('аст', 'асту', 'шудааст', 'нашудааст', 'ин',
            'буд', 'буданд', 'бувад', 'эй', 'ва')
parts = part_start + part_middle + part_end
parts = tuple('|'.join(i) for i in (part_start, part_middle, part_end))


def get_numbers(test_str:str):
    test_nums = [i[0] for i in re.finditer(r'(\d+\W*)+(?= |-|$)', test_str)]
    test_str = re.sub(r'(\d+\W*)+(?= |-|$)', r'~', test_str)
    return test_str, test_nums


def place_numbers(test:tuple):
    test_new = test[0]
    for i in test[1]:
        test_new = test_new.replace('ي', i, 1)
    return test_new


def split(test_str:str, max_len=50):
    test_str, test_nums = get_numbers(test_str)
    test_list = re.sub(rf'(\w*[^{upper + upper.lower()} ~-]\w*)+',
                       r'\n***\g<0>***\n', test_str
                       ).strip(' \n').replace('\n\n', '\n').splitlines()
    test_list = [i for i in test_list if i.strip()]

    new_list = []
    for i in test_list:
        if len(i) <= max_len or i[0] == '*':
            new_list.append(i.strip())
        else:
            i = re.sub(rf'(?<!\w)({parts})(?= |$)',
                    r'_\g<0>_', i).strip('_')
            i_list = re.sub(r'(_ _)|(_ )|( _)', '_', i).split()
            new_line = ''
            for j in i_list:
                if len(new_line) + len(j) < max_len:
                    new_line += f' {j}'
                else:
                    new_list.append(new_line.replace('_', ' ').strip())
                    new_line = j
            new_list.append(new_line.replace('_', ' ').strip())
            
    return new_list, test_nums


def fix_punct(test:str):
    test = re.sub(r'(«)([^«»]+)(»)', r'”\g<2>“', test)
    test = re.sub(r'(\")([^\"]+)(\")', r'”\g<2>“', test)
    test = re.sub(r'(\')([^\']+)(\')', r'’\g<2>‘', test)
    to_replace = {'” ':'”', ' “':'“', '’ ':'’', ' ‘':'‘',
                  '« ':'«', ' »':'»', ' )':')', '( ':'(',
                   ' .':'.', ' !':'!', ' ?':'؟', ' ,':'،',
                   ' ;':'؛', ' :':':'}
    for i, j in zip(to_replace.keys(), to_replace.values()):
        test = test.replace(i, j)
    
    return test


def feed_pipeline(test_str:str):
    # Remove dots in the middle of a sentence
    test_str = re.sub(rf'(?<=[A-Z{upper}])\.(?=([A-Za-z{upper}{upper.lower()}]| [A-Za-z{upper}{upper.lower()}]))',
                      '', test_str)
    test_str = re.sub(rf'(?<=[a-z{upper.lower()}])\.(?=( [a-z{upper.lower()}]))',
                      '', test_str)
    # Catch punctuation
    test_str = re.sub(rf'(?<=\w)(\W+)(?= |$)|(?<= )(\W+)(?=\w)|(?<=^)(\W+)(?=\w)',
                    r'\n***\g<0>***\n', test_str)
    
    # Catch non-Tajik words and split into smaller chunks
    test_list = [i for i in test_str.splitlines() if i]
    test_list = [split(part.strip()) if part[0] != '*'
                else ([part], [])
                for part in test_list]

    # Decode Tajik words and put back everything else
    new_list = []
    for line in test_list:
        line = (' '.join(decode(transformer, i.lower()) if i[0] != '*'
                      else i[3:-3].strip() for i in line[0]),
                line[1])
        new_list.append(place_numbers(line).replace('  ', ' '))

    return fix_punct(' '.join(new_list))


def convert(test_str:str):
    test_str = test_str.translate(norm)
    return '\n'.join(feed_pipeline(i) if i else '' for i in test_str.splitlines())

