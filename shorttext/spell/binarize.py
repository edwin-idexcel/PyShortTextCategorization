
import re
import string

import numpy as np
from shorttext.generators.charbase.char2vec import initSentenceToCharVecEncoder

default_alph = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz.,:;'*!?`$%&(){}[]-/\@_#"
# NB. # is <eos>, _ is <unk>, @ is number
default_specialsignals = {'eos': '#', 'unk': '_', 'number': '@'}
default_signaldenotions = {'<eos>': 'eos', '<unk>': 'unk'}


class SpellingToConcatCharVecEncoder:
    def __init__(self, alph):
        self.charevec_encoder = initSentenceToCharVecEncoder(alph)

    def encode_spelling(self, spelling):
        spmat = self.charevec_encoder.encode_sentence(spelling, len(spelling))
        return spmat.sum(axis=0)

    def __len__(self):
        return len(self.charevec_encoder)


def hasnum(word):
    return len(re.findall('\\d', word)) > 0


class SCRNNBinarizer:
    def __init__(self, alpha, signalchar_dict):
        self.signalchar_dict = signalchar_dict
        self.concatchar_encoder = SpellingToConcatCharVecEncoder(alpha)


    def noise_char(self, word, opt):
        bin_all = np.zeros((len(self.signalchar_dict), 1))
        w = word
        if word in default_signaldenotions.keys():
            bin_all[default_specialsignals[default_signaldenotions[word]]] += 1
        elif hasnum(word):
            bin_all[default_specialsignals['number']] += 1
        elif opt=='DELETE':
            idx = np.random.randint(0, len(word))
            w = word[:idx] + word[(idx+1):]
            bin_all = self.concatchar_encoder.encode_spelling(w)
        elif opt=='INSERT':
            ins_idx = np.random.randint(0, len(word)+1)
            ins_char = np.random.choice([c for c in string.ascii_lowercase])
            w = word[:ins_idx] + ins_char + word[ins_idx:]
            bin_all = self.concatchar_encoder.encode_spelling(w)
        elif opt=='REPLACE':
            rep_idx = np.random.randint(0, len(word))
            rep_char = np.random.choice([c for c in string.ascii_lowercase])
            w = word[:rep_idx] + rep_char + w[(rep_char+1):]
            bin_all = self.concatchar_encoder.encode_spelling(w)
        else:
            raise Exception('Unknown options: '+opt)
        return np.repeat(np.array([bin_all]), 3, axis=0).reshape((1, len(self.concatchar_encoder)))[0], w


    def jumble_char(self, word, opt):
        if opt=='WHOLE':
            return self.jumble_char_whole(word)
        elif opt=='BEG':
            return self.jumble_char_beg(word)
        elif opt=='END':
            return self.jumble_char_end(word)
        elif opt=='INT':
            return self.jumble_char_int(word)
        else:
            raise Exception('Unknown options: '+opt)


    def jumble_char_whole(self, word):
        bin_all = np.zeros((len(self.signalchar_dict), 1))
        w = word
        if word in default_signaldenotions.keys():
            bin_all[default_specialsignals[default_signaldenotions[word]]] += 1
        elif hasnum(word):
            bin_all[default_specialsignals['number']] += 1
        else:
            w = ''.join(np.random.choice([c for c in word], len(word), replace=False))
            bin_all = self.concatchar_encoder.encode_spelling(w)
        bin_filler = np.zeros((len(self.signalchar_dict)*2, 1))
        return np.append(bin_all, bin_filler), w


    def jumble_char_beg(self, word):
        bin_initial = np.zeros((len(self.signalchar_dict), 1))
        bin_end = np.zeros((len(self.signalchar_dict), 1))
        bin_filler = np.zeros((len(self.signalchar_dict), 1))
        w = word
        if word in default_signaldenotions.keys():
            bin_initial[default_specialsignals[default_signaldenotions[word]]] += 1
            bin_end[default_specialsignals[default_signaldenotions[word]]] += 1
        elif hasnum(word):
            bin_initial[default_specialsignals['number']] += 1
            bin_end[default_specialsignals['number']] += 1
        else:
            w_init = ''.join(np.random.choice([c for c in word[:-1]], len(word)-1)) if len(w)>3 else word[:-1]
            w = w_init + word[-1]
            bin_initial = self.concatchar_encoder.encode_spelling(w_init)
            bin_end = self.concatchar_encoder.encode_spelling(word[:-1])
        return reduce(np.append, [bin_initial, bin_end, bin_filler]), w


    def jumble_char_end(self, word):
        bin_initial = np.zeros((len(self.signalchar_dict), 1))
        bin_end = np.zeros((len(self.signalchar_dict), 1))
        bin_filler = np.zeros((len(self.signalchar_dict), 1))
        w = word
        if word in default_signaldenotions.keys():
            bin_initial[default_specialsignals[default_signaldenotions[word]]] += 1
            bin_end[default_specialsignals[default_signaldenotions[word]]] += 1
        elif hasnum(word):
            bin_initial[default_specialsignals['number']] += 1
            bin_end[default_specialsignals['number']] += 1
        else:
            w_end = ''.join(np.random.choice([c for c in word[1:]], len(word)-1)) if len(w)>3 else word[1:]
            w = word[0] + w_end
            bin_initial = self.concatchar_encoder.encode_spelling(word[0])
            bin_end = self.concatchar_encoder.encode_spelling(w_end)
        return reduce(np.append, [bin_initial, bin_end, bin_filler]), w


    def jumble_char_int(self, word):
        bin_initial = np.zeros((len(self.signalchar_dict), 1))
        bin_middle = np.zeros((len(self.signalchar_dict), 1))
        bin_end = np.zeros((len(self.signalchar_dict), 1))
        w = word
        if word in default_signaldenotions.keys():
            bin_initial[default_specialsignals[default_signaldenotions[word]]] += 1
            bin_middle[default_specialsignals[default_signaldenotions[word]]] += 1
            bin_end[default_specialsignals[default_signaldenotions[word]]] += 1
        elif hasnum(word):
            bin_initial[default_specialsignals['number']] += 1
            bin_middle[default_specialsignals['number']] += 1
            bin_end[default_specialsignals['number']] += 1
        else:
            w_mid = ''.join(np.random.choice([c for c in word[1:-1]], len(word)-2)) if len(w)>3 else w[1:-1]
            w = word[0] + w_mid + word[-1]
            bin_initial = self.concatchar_encoder.encode_spelling(word[0])
            bin_middle = self.concatchar_encoder.encode_spelling(w_mid)
            bin_end = self.concatchar_encoder.encode_spelling(word[-1])
        return reduce(np.append, [bin_initial, bin_middle, bin_end]), w
