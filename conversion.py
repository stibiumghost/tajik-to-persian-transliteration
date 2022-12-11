import initiation


norm_tg = {'Ѓ':'Ғ', 'Ї':'Ӣ', 'Ќ':'Қ', 'Ў':'Ӯ', 'Њ':'Ҳ', 'Љ':'Ҷ', 'ѓ':'ғ', 'ї':'ӣ', 'ќ':'қ', 'ў':'ӯ', 'њ':'ҳ', 'љ':'ҷ'}
dash = '-‐−◌̱¯'
long_dash = '–—ー一_'

norm_tg = str.maketrans(norm_tg)
norm_tg.update(str.maketrans(dash, '-' * len(dash)))
norm_tg.update(str.maketrans(long_dash, '—' * len(long_dash)))

alphabet = '-—абвгғдеёжзиӣйкқлмнопрстуӯфхҳчҷшъэюяь'

def prep_prose(text:str):

    '''Preps tg prose for transliteration'''

    text = ''.join([' ' + letter + ' ' if not letter.isalnum() and letter != '-' else letter for letter in text])
    text = text.replace('\n', '\n***paragraph ends here***\n')

    text_new = []
    for line in text.splitlines():
        if '***paragraph ends here***' not in line:
            text_new.append(' '.join(
                ['\n***not tg word***' + word + '\n' if any(i not in alphabet for i in word.lower()) else word.lower() for word in line.split()]))
        else:
            text_new.append(line)
    text_new = '\n'.join(text_new).replace('\n\n', '\n').splitlines()

    return '\n'.join(['\n'.join(smaller(line)) if len(line) > 54 else line.strip() for line in text_new if line]).splitlines()


def smaller(line, length=54):

    '''Split long lines in smaller chunks based on the length'''

    piece = round(len(line.split()) / round((len(line) / length) + 0.5) + 0.5)
    line_new = []
    start = 0
    while len(line.split()) > len(line_new) * piece:
        line_new.append(' '.join(line.split()[start:piece + start]).strip())
        start += piece
    return line_new

def replace_all(text):
    to_replace = {' ***paragraph ends here*** ':'\n', '***not tg word***':'', ' .':'.', ' !':'!', ' ?':'؟', ' ,':'،', ' ;':'؛'}
    for i, j in zip(to_replace.keys(), to_replace.values()):
        text = text.replace(i, j)
    return text


def convert(text:str):

    '''Turn tg in fa'''

    text = text.translate(norm_tg)
    text = prep_prose(text)
    text = ' '.join([line if line.startswith('***') else initiation.to_persian(line.strip()) for line in text])
    
    return replace_all(text)
