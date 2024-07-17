import string
import re
from tqdm import tqdm
from Levenshtein import ratio


# Magic strings
tg = 'tg'
fa = 'fa'
fa_placeholder = '؟'
tg_placeholder = '?'

# Normalization-related variables
alphabets = {
    tg:'абвгғдеёжзиӣйкқлмнопрстуӯфхҳчҷшъэюяь' + '-~ ',
    fa:'ابپتثجچحخدذرزژسشصضطظعغفقکگلمنوهی' + 'هٔئّْآ' + '-ي\u200c ',
    'lower': 'абвгғдеёжзиӣйкқлмнопрстуӯфхҳчҷшъэюяь' + 'ابپتثجچحخدذرزژسشصضطظعغفقکگلمنوهی' + 'هٔئّْآ'
    }

digits = {tg : '~', fa : 'ي'}
digits_dicts = {
    tg: str.maketrans(string.digits, digits[tg] * 10),
    fa: str.maketrans(string.digits, digits[fa] * 10),
    }

norm_tg = str.maketrans({'Ѓ':'Ғ', 'Ї':'Ӣ', 'Ќ':'Қ', 'Ў':'Ӯ', 'Њ':'Ҳ', 'Љ':'Ҷ',
                         'ѓ':'ғ', 'ї':'ӣ', 'ќ':'қ', 'ў':'ӯ', 'њ':'ҳ', 'љ':'ҷ'})

dash = '-‐−◌̱¯–—ー一_'
slash = '/|\\'
punctuation = '.,:;!?()…“”«»؟،؛' + string.punctuation
punct_trans = str.maketrans('', '', punctuation.replace('-', '') + '\u200e\u200f')
punct_trans.update(str.maketrans(dash, '-' * len(dash)))
punct_trans.update(str.maketrans(slash, ' ' * len(slash)))

tg_cons = 'бгдззззклмнпрсссттфхчжшғқч' + string.digits + string.ascii_letters
fa_cons = 'بگدظضذزکلمنپرثصستطفخچژشغقج' + string.digits + string.ascii_letters
fa_tg = dict(zip(fa_cons, tg_cons))


#####    Main     #####


class ParallelText(dict):
    def __init__(self,
                 sorted_data=None,
                 names=(tg, fa, tg+'_comp', fa+'_comp'),
                 show=('ratio',)):
        self.names = names
        self.show = show
        if isinstance(sorted_data, list) or isinstance(sorted_data, tuple):
            data = {}
            for name, n in zip(self.names, range(len(self.names))):
                data[name] = list(i[n] for i in sorted_data)
            if 'ratio' not in self.names:
                try:
                    data['ratio'] = list(ratio(t, f) for t, f in
                                         zip(data[tg+'_comp'], data[fa+'_comp']))
                    self.names += ('ratio',)
                except KeyError:
                    print("Cannot generate 'ratio'")
            self.data = data

        elif isinstance(sorted_data, dict):
            self.data = sorted_data
            self.names = [*sorted_data]

        elif isinstance(sorted_data, ParallelText):
            self.data = sorted_data.data
            self.names = sorted_data.names

        elif isinstance(sorted_data, type(None)):
            data = {}
            self.names += ('ratio',)
            for name in self.names:
                data[name] = []
            self.data = data

        else:
            raise TypeError('Cannot create new ParallelText object')
        
        for name in self.names:
            if not isinstance(self.data[name], list):
                if isinstance(self.data[name], tuple):
                    self.data[name] = list(self.data[name])
                else:
                    self.data[name] = [self.data[name]]


    def __len__(self):
        return len(self.data[self.names[0]])


    def __repr__(self):
        #print(self)
        if all(i in self.names for i in (tg, fa)):
            to_show = []
            lens = [len(max((t, f), key=len)) + 2 for t, f
                    in zip(self.data[tg], self.data[fa])]
            format_list = '|\u200e'.join(['{:^' + str(n) + '}' for n in lens])
            to_show.append(format_list.format(*self.data[tg]))
            to_show.append(format_list.format(*self.data[fa]))

            for name in self.show:
                if name in self.names:
                    if name == 'ratio':
                        ratio = tuple(str(i)[:3] for i in self.data['ratio'])
                        to_show.append(format_list.format(*ratio))
                    else:
                        to_show.append(format_list.format(*self.data[name]))

            g_line = '-' * (sum(lens) + len(lens))
            to_show.insert(0, g_line)
            to_show.append(g_line)
            return '\n'.join(to_show)
        else:
            return str(self.data)
    

    def __getitem__(self, sliced):
        part = {}
        for name in self.names:
            part[name] = self.data[name][sliced]
        return ParallelText(part, self.names, self.show)
    

    def __add__(self, other):
        all_items = {}
        for name in self.names:
            all_items[name] = self.data[name] + other.data[name]
        return ParallelText(all_items, self.names, self.show)


    def __iter__(self):
        for name in self.names:
            data = [i for i in self.data[name] if i not in (fa_placeholder, tg_placeholder, ' ')]
            if name == 'ratio' and self.data[name]:
                yield sum(data)/len(data)
            elif 'comp' in name:
                yield ''.join(data)
            else:
                try:
                    yield ' '.join(data)
                except TypeError:
                    yield data


    def pop(self, ind):
        poped = {}
        for name in self.names:
            poped[name] = [self.data[name].pop(ind)]
        return ParallelText(poped, self.names, self.show)
    

    def split_by_ind(self, inds):
        '''
        Get a list of new ParallelTexts
        based on :inds: of split points:
        (2, 4) -> ([:2], [2:4], [4:])
        '''
        inds = sorted(list(set(i for i in inds if i > 0 and i < len(self)) | {0, len(self)}))
        slices = (slice(i, inds[ind+1]) for ind, i in enumerate(inds[:-1]))
        new_data = []
        for s in slices:
            new_data.append(self[s])
        return new_data


    def split_by_size(self, size:int):
        '''
        Get a list of new ParallelTexts
        based on :size:
        '''
        if size < 1:
            return self
        old_data = self
        new_data = []
        while len(old_data) > 0:
            new_data.append(old_data[:size])
            old_data = old_data[size:]
        return new_data


    def find(self, name, item):
        return tuple(ind for ind, i in enumerate(self.data[name])
                     if i == item)
    

    def ratio(self):
        try:
            self.data['ratio'] = list(ratio(t, f) for t, f in
                                      zip(self.data[tg+'_comp'], self.data[fa+'_comp']))
        except KeyError:
            print("Cannot generate 'ratio'")
        return sum(self.data['ratio'])/len(self.data['ratio'])


#####    Basic transcription    #####


def transcribe(line:str, lang:str) -> str:
    '''
    Simple transcription of consonants
    (cyrillic script)
    '''
    if lang == tg:
        line = line.lower().replace('ҷ', 'ч')
        return ''.join(tg_l for tg_l in line if tg_l in tg_cons)
    
    return ''.join(fa_tg[fa_l] for fa_l in line.replace('\u200c', '') if fa_l in fa_cons)


def trans_words(line, lang:str) -> tuple:
    '''
    Word-for-word transcription approximation
    (cyrillic script)
    '''
    line = (i.strip(' \u200c') for i in line.split())
    return tuple(conditions(word.lower(), lang) for word in line)


def conditions(word:str, lang:str) -> str:
    '''
    Helper conditions for transcription approximation
    (used in trans_words(...))
    '''
    # Placeholder for punctuation
    if word in punctuation:
        return '_'
    
    result = transcribe(word, lang)

    # Placeholder for empty strings
    if not result:
        return 'ф'
    
    if result == 'р' and len(word) > 2 and word[-2:] == 'ро':
        return 'фр'

    if any(word.endswith(i) for i
           in list('уӯвюو') + ['ӯй', 'ои', 'ой', 'ای']):
        result += 'ф'
    
    if ((word.startswith('в') or word.startswith('و'))
        and result != 'ф'):
        result = 'ф' + result
    
    return result


#####    Comparison and filtration    #####


def match_texts(tg_texts, fa_texts, min_ratio=0.7) -> list:
    '''
    Find best matches in :texts_tg: and :texts_fa:
    based on :min_ratio:
    '''
    match = []
    
    tg_texts = [line for line in tg_texts if line]
    fa_texts = [line for line in fa_texts if line]
    comp_tg = [''.join(trans_words(line, tg)).replace('_', '') for line in tg_texts]
    comp_fa = [''.join(trans_words(line, fa)).replace('_', '') for line in fa_texts]

    if len(tg_texts) > len(fa_texts):
        for fa_line in tqdm(range(len(fa_texts)), desc='Finding matches...'):
        #for fa_line in range(len(fa_texts)):
            similar_ind = find_similar(comp_fa[fa_line], comp_tg, min_ratio)
            if similar_ind > -1:
                match.append((tg_texts[similar_ind], fa_texts[fa_line]))
    else:
        for tg_line in tqdm(range(len(tg_texts)), desc='Finding matches...'):
        #for tg_line in range(len(tg_texts)):
            similar_ind = find_similar(comp_tg[tg_line], comp_fa, min_ratio)
            if similar_ind > -1:
                match.append((tg_texts[tg_line], fa_texts[similar_ind]))
    
    return match


def match_words(tg_line:str, fa_line:str, window=3, seq_len=3) -> list:
    '''
    Word-by-word comparison of a sentence.
    Return [('tg', 'fa', 'transcript (tg)', 'transcript (fa)')...]
    '''
    tg_list = tg_line.split()
    tg_comp = trans_words(tg_line, tg)

    fa_list = fa_line.split()
    fa_comp = trans_words(fa_line, fa)

    tg_result = []
    tg_result_comp = []
    fa_result = []
    fa_result_comp = []

    while tg_list and fa_list:
        # Each Tajik chain of strings is compared
        # against each Persian chain of strings;
        # (values from the start of the string are prioritized:
        # since max() retrives first best option,
        # they are put first)
        tg_comp_chunks = make_variants(tg_comp[:window+seq_len-1], 1, seq_len)
        fa_comp_chunks = make_variants(fa_comp[:window+seq_len-1], 1, seq_len)

        fa_comp_chunks_sorted = []
        fa_comp_part = []
        for i in fa_comp_chunks:
            if len(i) == 1 and fa_comp_part:
                fa_comp_chunks_sorted.append(fa_comp_part)
                fa_comp_part = []
            fa_comp_part.append(i)
        fa_comp_chunks_sorted.append(fa_comp_part)

        best_matches = []
        for f in fa_comp_chunks_sorted:
            for t in tg_comp_chunks:
                if len(t) == 1:
                    fa_variants = (''.join(v) for v in f)
                else:
                    fa_variants = (''.join(v) if len(v) == 1
                                else '' for v in f)
                fa_ind = find_similar(''.join(t), fa_variants, -1)
                best_matches.append((t, f[fa_ind]))
        ratios = [ratio(''.join(p[0]), ''.join(p[1])) for p in best_matches]
        best = best_matches[ratios.index(max(ratios))]
        
        # Retrive best chains of strings
        if len(best[0]) == 1:
            tg_start = tg_comp.index(best[0][0])
        else:
            tg1 = ' '.join(tg_comp).find(' '.join(best[0]))
            tg_start = len(' '.join(tg_comp)[:tg1].split())
        tg_end = len(best[0]) + tg_start
        tg_left = ' '.join(tg_list[:tg_start])
        tg_chunk = ' '.join(tg_list[tg_start:tg_end])
        tg_list, tg_comp = tg_list[tg_end:], tg_comp[tg_end:]

        if len(best[1]) == 1:
            fa_start = fa_comp.index(best[1][0])
        else:
            fa1 = ' '.join(fa_comp).find(' '.join(best[1]))
            fa_start = len(' '.join(fa_comp)[:fa1].split())
        fa_end = len(best[1]) + fa_start
        fa_left = ' '.join(fa_list[:fa_start])
        fa_chunk = ' '.join(fa_list[fa_start:fa_end])
        fa_list, fa_comp = fa_list[max(fa_end, 0):], fa_comp[max(fa_end, 0):]

        # Retrive not-so-good chains of strings
        # (if they exist)
        if any((tg_left, fa_left)):
            if tg_left:
                tg_result.append(tg_left.strip(' -\u200c'))
                tg_result_comp.append(''.join(trans_words(tg_left, tg)))
            else:
                tg_result.append(tg_placeholder)
                tg_result_comp.append(tg_placeholder)
            
            if fa_left:
                fa_result.append(fa_left.strip(' -\u200c'))
                fa_result_comp.append(''.join(trans_words(fa_left, fa)))
            else:
                fa_result.append(fa_placeholder)
                fa_result_comp.append(fa_placeholder)

        tg_result.append(tg_chunk.strip(' -\u200c'))
        tg_result_comp.append(''.join(best[0]))
        fa_result.append(fa_chunk.strip(' -\u200c'))
        fa_result_comp.append(''.join(best[1]))
    
    # Retrive "tails"
    if tg_list:
        tg_left = ' '.join(tg_list)
        tg_result.append(tg_left)
        tg_result_comp.append(''.join(trans_words(tg_left, tg)))
        fa_result.append(fa_placeholder)
        fa_result_comp.append(fa_placeholder)
    elif fa_list:
        fa_left = ' '.join(fa_list)
        fa_result.append(fa_left)
        fa_result_comp.append(''.join(trans_words(fa_left, fa)))
        tg_result.append(tg_placeholder)
        tg_result_comp.append(tg_placeholder)

    return [(tg_result[ind], fa_result[ind],
              tg_result_comp[ind], fa_result_comp[ind])
              for ind in range(len(tg_result))]


def find_similar(comp_line:str, comp_list, set_ratio=0.8) -> int:
    '''
    Define the best match for :comp_line: in :comp_list:.
    Return -1 if the best ratio < :set_ratio:
    '''
    ratios = tuple(ratio(comp_line, item) for item in comp_list)
    if any(r >= set_ratio for r in ratios):
        return ratios.index(max(ratios))
    return -1


def make_variants(line, min_size:int, max_size:int) -> list:
    '''
    Make a sequence of lists from a given :line:
    from :min_size: up to :max_size:
    '''
    variants = [line[i:j]
                for i in range(len(line))
                for j in range(i + 1, len(line) + 1)]
    if len(line) > max_size:
        variants = variants[:sum(range(max_size, len(line) + 1))]
    variants = [i for i in variants if min_size <= len(i) <= max_size]
    return variants


#####    Basic text transformation    #####


def split_lines(text:str) -> list:
    text = re.sub(rf'([A-Z{alphabets[tg][:-3].upper()}])\.', r'\1LQCdUHBfgQDOT', text)
    text = text.replace('...', 'LQCdUHBfgQDOOOT').replace('…', 'LQCdUHBfgQDOOOT')
    text = re.sub(r'\[[^\[\]]+\]', '', text)
    text = re.sub(r'\([^\(\)]+\)', '', text)
    text = re.sub(r'([^ \n]+[\.!?؟]\W*) ', r'\1\n', text)
    text = text.replace('LQCdUHBfgQDOT', '.').replace('LQCdUHBfgQDOOOT', '...')
    text = re.sub(r' {2,}', ' ', text)
    text = re.sub(r' (?=[\.,!?؟:;»\)])', '', text)
    text = re.sub(r'(?<=[\(«]) ', '', text)
    text_split = [t.strip().strip('-_–*') for t in text.splitlines()]
    text_split = [t for t in text_split if len(t) > 4]
    return text_split


def replace_digits(line:str, lang:str) -> str:
    '''
    Replace digits with a placeholder
    '''
    line = re.sub(r'(?<=\d)[ :.](?=\d)', '', line)
    return re.sub(r'\d+', digits[lang], line)


def remove_punctuation(line:str) -> str:
    '''
    Fix dashes and remove punctuation (exept dashes)
    '''
    line = line.translate(punct_trans)
    line = re.sub(r' - ', ' ', line)
    line = re.sub(r'(?<=\S-) | (?=-\S)', '', line)
    return re.sub(r'\s+', ' ', line).strip(' -\u200c')
