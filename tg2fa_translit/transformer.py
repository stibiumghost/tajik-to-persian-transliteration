from os import path

import math
from torch import (Tensor, load, from_numpy,
                   exp, arange, zeros, sin, cos)
import torch.nn as nn

import warnings
warnings.filterwarnings('ignore', category=UserWarning)


class PositionalEncoding(nn.Module):
    def __init__(self,
                 emb_size: int,
                 dropout: float,
                 maxlen: int = 5000):
        super(PositionalEncoding, self).__init__()
        den = exp(- arange(0, emb_size, 2) * math.log(10000) / emb_size)
        pos = arange(0, maxlen).reshape(maxlen, 1)
        pos_embedding = zeros((maxlen, emb_size))
        pos_embedding[:, 0::2] = sin(pos * den)
        pos_embedding[:, 1::2] = cos(pos * den)
        pos_embedding = pos_embedding.unsqueeze(-2)

        self.dropout = nn.Dropout(dropout)
        self.register_buffer('pos_embedding', pos_embedding)

    def forward(self, token_embedding: Tensor):
        return self.dropout(token_embedding + self.pos_embedding[:token_embedding.size(0), :])


class TokenEmbedding(nn.Module):
    def __init__(self, vocab_size: int, emb_size):
        super(TokenEmbedding, self).__init__()
        self.embedding = nn.Embedding(vocab_size, emb_size)
        self.emb_size = emb_size

    def forward(self, tokens: Tensor):
        return self.embedding(tokens.long()) * math.sqrt(self.emb_size)


class Seq2SeqTransformer(nn.Module):
    def __init__(self,
                 num_encoder_layers: int,
                 num_decoder_layers: int,
                 emb_size: int,
                 nhead: int,
                 src_vocab_size: int,
                 tgt_vocab_size: int,
                 dim_feedforward: int = 256,
                 dropout: float = 0.01):
        super(Seq2SeqTransformer, self).__init__()
        self.transformer = nn.Transformer(d_model=emb_size,
                                       nhead=nhead,
                                       num_encoder_layers=num_encoder_layers,
                                       num_decoder_layers=num_decoder_layers,
                                       dim_feedforward=dim_feedforward,
                                       dropout=dropout)
        self.generator = nn.Linear(emb_size, tgt_vocab_size)
        self.src_tok_emb = TokenEmbedding(src_vocab_size, emb_size)
        self.tgt_tok_emb = TokenEmbedding(tgt_vocab_size, emb_size)
        self.positional_encoding = PositionalEncoding(
            emb_size, dropout=dropout)

    def forward(self,
                src: Tensor,
                trg: Tensor,
                src_mask: Tensor,
                tgt_mask: Tensor,
                src_padding_mask: Tensor,
                tgt_padding_mask: Tensor,
                memory_key_padding_mask: Tensor):

        src_emb = self.positional_encoding(self.src_tok_emb(src))
        tgt_emb = self.positional_encoding(self.tgt_tok_emb(trg))
        outs = self.transformer(src_emb, tgt_emb, src_mask, tgt_mask, None,
                                src_padding_mask, tgt_padding_mask, memory_key_padding_mask)
        return self.generator(outs)


    def encode(self, src, src_mask):
        src = from_numpy(src)
        src_mask = from_numpy(src_mask)
        return self.transformer.encoder(self.positional_encoding(
                            self.src_tok_emb(src)), src_mask)
        

    def decode(self, tgt, memory: Tensor, tgt_mask):
        tgt = from_numpy(tgt)
        tgt_mask = from_numpy(tgt_mask)
        return self.transformer.decoder(self.positional_encoding(
                          self.tgt_tok_emb(tgt)), memory,
                          tgt_mask).transpose(0, 1)


filename = path.abspath(path.join(path.dirname(__file__), 'model_2.9.zip'))

# NUM_ENCODER_LAYERS, NUM_DECODER_LAYERS, EMB_SIZE,
# NHEAD, SRC_VOCAB_SIZE, TGT_VOCAB_SIZE, FFN_HID_DIM
transformer = Seq2SeqTransformer(3, 3, 64, 8, 43, 45, 64)
checkpoint = load(filename, map_location='cpu')
transformer.load_state_dict(checkpoint['model_state_dict'])
transformer = transformer.to('cpu')
transformer.eval()
