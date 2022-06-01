#! /home/joseluistl/anaconda3/bin/python

import string
import numpy as np
import pandas as pd
import time
import re
import os


class Wordle:

    def __init__(self, data_path, language, coefficients):
        """
        Here we will initialize the game, we want to find the best way
        to choose the next guess so the game can be solved in the least
        number of tries.

        :param data_path: the path to the data source.
        """
        self.coefficients = coefficients
        self.language = language
        self.data_path = data_path
        self.words = None
        self.best_opener = None
        self.mean_tries = None
        self.freq_texts = None
        self.freq_tot = None
        self.pos_tot = None
        self.unique = None
        self.opener_mean_tries = None

    def get_words(self):
        """
        Here we read the file with the words
        and create the list of words as a Pandas Series
        that is ordered alphabetically.
        """
        if self.language == "es":
            name = "palabras"
        elif self.language == "en":
            name = "words"
        else:
            name = "mots"

        with open(os.path.join(self.data_path, "data", name + ".txt")) as f:
            self.words = pd.Series(f.read().split('\n')).sort_values(ignore_index=True)

    def initialize(self):
        """
        In this function we initialize the attributes of the game.
        """
        self.get_words()
        self.freq_tot = pd.Series(self.get_freq(self.words.values), index=self.words.values)
        self.pos_tot = pd.Series(self.get_pos(self.words.values), index=self.words.values)
        self.unique = pd.Series(map(lambda x: int(len(x) == len(np.unique(list(x)))), self.words.values),
                                index=self.words.values)
        self.get_freq_texts()
        self.best_opener = self.get_next(self.words)
        self.mean_tries = self.get_mean_tries(self.best_opener)
        print("Best opener:", self.best_opener)
        print("Mean tries:", self.mean_tries)

    def get_mean_tries(self, word):
        """
        For each word we will get the average tries as if that
        word was the opener.
        :param word: word to analyze.
        """
        return pd.Series(map(lambda x: self.wordle(word, x), self.words.values)).mean()

    def wordle(self, word, first_trie):
        """
        This method is the way calculates the number of
        guesses that the wordle game would take with the solver.
        :param word: The word that we will guess.
        :param first_trie: The opener word that will be the first guess.
        :return: The number of guesses that the solver delayed.
        """
        rem_words = self.words.values

        last = False
        tries = 0
        cond = np.array([string.ascii_lowercase for _ in range(5)])
        trie = first_trie
        while len(rem_words) > 1:
            letters = []
            for i, letter in enumerate(trie):
                if letter not in word:
                    cond = np.array(list(map(lambda x: re.sub(f'[{letter}]', "", x), cond)))
                elif word[i] == letter:
                    cond[i] = letter
                else:
                    cond[i] = re.sub(f'[{letter}]', "", cond[i])
                    letters.append(letter)

            rem_words = pd.Series(
                re.findall(f'[{cond[0]}][{cond[1]}][{cond[2]}][{cond[3]}][{cond[4]}]', " ".join(rem_words)))

            letters = np.unique(letters)
            for letter in letters:
                rem_words = pd.DataFrame(rem_words.values, columns=["words"]).query(
                    'words.str.contains(@letter)', engine='python')["words"]
                rem_words.index = [i for i in range(len(rem_words))]

            if len(rem_words) == 1:
                last = True

            tries += 1
            trie = self.get_next(rem_words)

        if last:
            tries += 1

        return tries

    def get_next(self, word_list):
        """
        Return the word that has the higher value in a list of pondered words.
        :param word_list: The list of words that will evaluate.
        :return: The word that has the highest value.
        """
        freq_loc = self.get_freq(word_list)
        pos_loc = self.get_pos(word_list)
        freq_tot_loc = np.array(list(map(lambda x: self.freq_tot[x], word_list)))
        pos_tot_loc = np.array(list(map(lambda x: self.pos_tot[x], word_list)))
        freq_texts_loc = np.array(list(map(lambda x: self.freq_texts[x], word_list)))
        unique = np.array(list(map(lambda x: self.unique[x], word_list)))
        return word_list[pd.Series(self.coefficients[0] * freq_tot_loc +
                                   self.coefficients[1] * freq_loc +
                                   self.coefficients[2] * pos_tot_loc +
                                   self.coefficients[3] * pos_loc +
                                   self.coefficients[4] * freq_texts_loc +
                                   self.coefficients[5] * unique
                                   ).idxmax()]

    @staticmethod
    def get_freq(word_list):
        """
        This method generates an array with the values of frequency of the
        words in the list that receives as a parameter.
        :param word_list: List of words from which will generate the list
                          of frequencies.
        :return: A list with the frequency values of word_list.
        """
        freq = pd.DataFrame().assign(Letter=list("".join(word_list))).groupby(["Letter"])["Letter"].count()
        freq = freq / freq.sum()
        return np.array([np.mean([freq[i] for i in x]) for x in word_list])

    @staticmethod
    def get_pos(word_list):
        """
        This method generates an array with the values of frequency in
        each position of the words that receives from the list.
        :param word_list: List of words from which will generate the list
                          of frequencies.
        :return: A list with the frequency values of word_list.
        """
        pos = pd.DataFrame(np.array([(pd.DataFrame(list(map(lambda x: x[i], word_list)) + list(string.ascii_lowercase),
                                                   columns=[i]).groupby([i])[i].count() - 1).values for i in
                                     range(5)]).transpose(),
                           index=list(string.ascii_lowercase))
        pos = pos / [pos[i].sum() for i in pos.columns]
        word_list = np.array([np.mean([pos[i][letter] for i, letter in enumerate(x)]) for x in word_list])
        return word_list

    def get_freq_texts(self):
        """
        Creates a Series with the words as an index and the frequency
        of the word in the texts as a value.
        """
        with open(os.path.join(self.data_path, "env", "results", self.language + ".txt")) as f:
            freq = pd.DataFrame(f.read().split('\n'), columns=["word"])
        freq = freq.groupby(["word"])["word"].count()
        freq = freq / freq.sum()
        self.freq_texts = pd.Series(map(lambda x: freq[x] if (x in freq.index) else 0, self.words.values),
                                    index=self.words.values)
        self.freq_texts = (pd.Series(np.log(self.freq_texts + 0.007) * 0.15) + 1).sort_index()


if __name__ == '__main__':
    coef = [0.1, 0.2, 0.1, 0.2, 0.35, 0.05]
    wd = Wordle(os.path.join("."), "es", coef)
    start = time.time()
    wd.initialize()
    fin = time.time()
    print(fin - start)
