import numpy as np


UNK_IDX, PAD_IDX, BOS_IDX, EOS_IDX = 0, 1, 2, 3
special_symbols = ['<unk>', '<pad>', '<bos>', '<eos>']

tg_keys = special_symbols + [' ', '-', '~', 'а', 'б', 'в', 'г', 'д', 'е', 'ж',
                             'з', 'и', 'й', 'к', 'л', 'м', 'н', 'о', 'п', 'р',
                             'с', 'т', 'у', 'ф', 'х', 'ч', 'ш', 'ъ', 'ь', 'э',
                             'ю', 'я', 'ё', 'ғ', 'қ', 'ҳ', 'ҷ', 'ӣ', 'ӯ']
tg_values = range(43)
tg_voc = dict(zip(tg_keys, tg_values))

fa_values = special_symbols + ['ه', ' ', '-', 'آ', 'ئ', 'ا', 'ب', 'ت', 'ث', 'ج',
                               'ح', 'خ', 'د', 'ذ', 'ر', 'ز', 'س', 'ش', 'ص', 'ض',
                               'ط', 'ظ', 'ع', 'غ', 'ف', 'ق', 'ل', 'م', 'ن', 'و',
                               'ي', 'ّ', 'ْ', 'ٔ', 'پ', 'چ', 'ژ', 'ک', 'گ', 'ی', '\u200c']
fa_keys = range(45)
fa_voc = dict(zip(fa_keys, fa_values))


def decode(model, src_sentence: str):
    src = np.array([2] + [tg_voc[i] for i in src_sentence] + [3]).reshape(-1, 1)
    num_tokens = src.shape[0]
    src_mask = np.zeros((num_tokens, num_tokens), bool)
    tgt_tokens = greedy(
        model, src, src_mask, max_len=num_tokens + 10).flatten()
    return ''.join(fa_voc[i] for i in tgt_tokens[1:-1])


def greedy(model, src, src_mask, max_len):
    memory = model.encode(src, src_mask)
    ys = np.array([[BOS_IDX]])

    for i in range(max_len-1):
        tgt_mask = (np.triu(np.ones((ys.shape[0], ys.shape[0]))) == 0).transpose(1, 0)
        out = model.decode(ys, memory, tgt_mask)
        prob = model.generator(out[:, -1,])
        next_word = np.argmax(prob.detach().numpy(), axis=1)[0]
        ys = np.concatenate([ys, np.array([[next_word]])])
        if next_word == EOS_IDX:
            break
    return ys
