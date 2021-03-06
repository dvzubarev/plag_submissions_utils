#!/usr/bin/env python
# coding: utf-8

import logging
import distance

from . import sents
from .source_doc import get_src_filename

class ModType(object):
    UNK  = 0
    CPY  = 1
    LPR  = 2
    HPR  = 3
    ORIG = 4
    DEL  = 5
    ADD  = 6
    CCT  = 7
    SSP  = 8
    #from v2
    SHF  = 9
    SEP  = 10
    SYN  = 11

    @classmethod
    def get_all_mod_types_v1(cls):
        return list(range(0,9))

    @classmethod
    def get_all_mod_types_v2(cls):
        return list(range(0,8)) + list(range(9,12))

    @classmethod
    def get_all_mod_types_v3(cls):
        return 0, 2, 4, 5, 6, 7, 9, 10

def mod_types_to_str(mod_types):
    return ",".join(mod_type_to_str(m) for m in mod_types)

MOD_TYPE_DICT = {
    0 : "UNK",
    1 : "CPY",
    2 : "LPR",
    3 : "HPR",
    4 : "ORIG",
    5 : "DEL",
    6 : "ADD",
    7 : "CCT",
    8 : "SSP",
    9 : "SHF",
    10 : "SEP",
    11 : "SYN"
}

def mod_type_to_str(mod_type):
    return MOD_TYPE_DICT.get(mod_type, "unk")

def _create_mod_types(mods_str):
    if not mods_str:
        return [ModType.ORIG]
    return [_create_mod_type(m) for m in mods_str.split(',') if m.strip()]

def _create_mod_type(mod_str):
    mls = mod_str.strip().lower()
    if not mls:
        return ModType.ORIG
    elif mls == "cpy":
        return ModType.CPY
    elif mls == "lpr":
        return ModType.LPR
    elif mls == "hpr":
        return ModType.HPR
    elif mls == "del":
        return ModType.DEL
    elif mls == "add":
        return ModType.ADD
    elif mls == "ssp":
        return ModType.SSP
    elif mls == "cct":
        return ModType.CCT
    elif mls == "shf":
        return ModType.SHF
    elif mls == "sep":
        return ModType.SEP
    elif mls == "syn":
        return ModType.SYN
    else:
        return ModType.UNK


class ChunkOpts(object):
    def __init__(self, normalize = False,
                 skip_stop_words = False):
        self.normalize = normalize
        self.skip_stop_words = skip_stop_words


class Chunk(object):
    def __init__(self, orig_text, mod_text,
                 mod_type_str, orig_doc, chunk_num,
                 opts = ChunkOpts()):
        self._chunk_num           = chunk_num

        logging.debug("input mode type string: %s", mod_type_str)
        self._mod_types           = _create_mod_types(mod_type_str)

        self._original_sents      = sents.SentsHolder(orig_text, opts,
                                                      segment = self.has_mod_type(ModType.CCT))
        self._modified_sents      = sents.SentsHolder(mod_text, opts)

        self._orig_doc            = orig_doc

    def get_id(self):
        return self.get_chunk_id()

    def get_chunk_id(self):
        return self._chunk_num

    def get_mod_type(self):
        """If chunk has only one modification type, this one will be returned.
        If there are many types (like in v2), UNK is returned.
        """
        if len(self._mod_types) == 1:
            return self._mod_types[0]
        return ModType.UNK

    def set_mod_types(self, mod_types):
        self._mod_types = mod_types

    def get_all_mod_types(self):
        return self._mod_types


    def has_mod_type(self, mod_type):
        return mod_type in self._mod_types

    def get_orig_doc(self):
        return self._orig_doc

    def get_orig_doc_filename(self):
        return get_src_filename(self._orig_doc)

    def get_avg_original_words_cnt(self):
        return self._original_sents.get_avg_words_cnt()

    def get_avg_mod_words_cnt(self):
        return self._modified_sents.get_avg_words_cnt()

    def measure_dist(self):
        return distance.nlevenshtein(self.get_orig_tokens(),
                                     self.get_mod_tokens())

    def lexical_dist(self):
        return distance.jaccard(self.get_orig_tokens(),
                                self.get_mod_tokens())

    def get_mod_sent_holder(self):
        return self._modified_sents

    def get_orig_sent_holder(self):
        return self._original_sents

    def get_orig_sents(self):
        return self._original_sents.get_sents()

    def get_mod_sents(self):
        return self._modified_sents.get_sents()

    def get_orig_tokens(self):
        return self._original_sents.get_all_tokens()

    def get_orig_tokens_list(self):
        return self._original_sents.get_tokens_list()

    def get_mod_tokens(self):
        """Tokens are lowercased.
        """
        return self._modified_sents.get_all_tokens()

    def get_orig_text(self):
        return self._original_sents.get_text()

    def get_mod_text(self):
        return self._modified_sents.get_text()

    def __str__(self):
        chunk_str = "%d (%s): %s, %s" %(
            self._chunk_num,
            mod_types_to_str(self._mod_types),
            " ".join(self.get_mod_sents()),
            "|".join(self.get_mod_tokens()))
        return chunk_str
