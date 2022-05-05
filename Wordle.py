# -*- coding: utf-8 -*-
"""
Created on Wed May  4 01:10:12 2022

@author: Jose Luis
"""

import re
import random
import itertools 
import numpy as np

def insertWord(text):
    
    word = input ("Insert a word: ").lower()
    
    while (len(word) != 5 or len(re.findall(r''+word, text))==0):
        
        if (len(word) != 5):
            print("Error, word must contain 5 words")
            
        else:
            print ("Error, word does not exist")
            
        word = input ("Insert a word: ")
        
    return word
        
def evaluateWord(word, conditions, posLetters, posCorrect, boolValues):
    
    print ("For the following letters insert: \n\n\t1.'No' if letter is not in the word.")
    print("\t2.'Is' if letter is in word but not in the yes position.")
    print("\t3.'Yes' if letter is in word and in the yes position.\n")
    
    for i in range(len(word)):
        
        if (not boolValues[i]):
            result = input ("Indicate the result of "+word[i]+": ").lower()
        else:
            result = "yes"
        
        while (result not in ("no", "is", "yes")):
            print("Not an option. Choose between 'no', 'is', or 'yes'.")
            result = input ("Indicate the result of "+word[i]+": ").lower()
            
        if (result == "no"):
            for j in range(5):
                conditions[j] = "".join(re.findall(r'[^'+word[i]+']', conditions[j]))
        
        elif (result == "is"):
            posLetters.append((word[i], i))
            conditions[i] = "".join(re.findall(r'[^'+word[i]+']', conditions[i]))
        
        else:
            posCorrect.append((word[i], i))
            conditions[i] = word[i]
            boolValues[i] = True
            
    return conditions, posLetters, posCorrect, boolValues

def sortRandom(auxList):
    
    for i in range(len(auxList)):
        index = random.randint(0, len(auxList) - i - 1)

        aux = auxList[i]
        auxList[i] = auxList[index]
        auxList[index] = aux

    return auxList
    

##Main
idioma = input("Choose a language (fr, es, en): ").lower()
while (idioma not in ("fr", "es", "en")):
    print("Error. Not existing language")
    idioma = input("Choose a language (fr, es, en): ").lower()

if (idioma == "es"):
    idioma = "palabras"
elif (idioma == "en"):
    idioma = "words"
else:
    idioma = "mots"
lee = open(idioma+".txt")
text = lee.read()
lee.close()
abc = "abcdefghijklmnopqrstuvwxyz"
conditions = [abc, abc, abc, abc, abc]
words = text.split("\n")
contin = True 
boolValues = [False for i in range(5)]


while (contin):
    
    words = []
    posLetters = []
    posCorrect = []
    
    word = insertWord(text)
    
    conditions, posLetters, posCorrect, boolValues = evaluateWord(word, conditions, posLetters, posCorrect, boolValues)
    
    wordsInPosLetters = ("".join([j[0] for j in posLetters])+"#####")[:5]
    wordsInPosLetters = [i for i in wordsInPosLetters]   
    combinations = np.unique(["".join(i) for i in list(itertools.permutations(wordsInPosLetters))])

    for j in posLetters:
        combinations = [i for i in combinations if i[j[1]] != j[0]]
    
    for k in range(len(combinations)):
        for l in posCorrect:
            combinations[k] = combinations[k][:l[1]]+l[0]+combinations[k][l[1]+1:]
    
    for j in posLetters:
        combinations = [i for i in combinations if j[0] in i]
    
    combinations = np.unique(combinations)
    
    for i in combinations:
        conditionsParc = ["" for i in range(5)]

        for j in range(len(i)):
            
            if i[j] == "#":
                conditionsParc[j] = conditions[j]
                
            else:
                conditionsParc[j] = i[j]
                
        words += re.findall(r'['+conditionsParc[0]+']['+conditionsParc[1]+
                                ']['+conditionsParc[2]+']['+conditionsParc[3]+
                                ']['+conditionsParc[4]+']', text)
    words = list(np.unique(words))
    
    if (len(words)>1): 
        words = sortRandom(words)
        
        print ("\nYou still have "+str(len(words))+" options: \n")
        for i in range(min(5, len(words))):
            print("\t"+str(i+1)+". "+words[i]+"\n")
    
        
        if (len(words)>5):
            showMore = input ("Do you want to see more options (Insert 'y' or 'n'): \n").lower() == "y"
            
            times = 1
            
            while (showMore and len(words)>(times*5)):
                
                for i in range(5*times, min(5*(times+1), len(words))):
                    print("\t"+str(i+1)+". "+words[i]+"\n")
                    
                times += 1
                
                if (len(words)>(times*5)):
                    showMore = input ("Do you want to see more options (Insert 'y' or 'n'): \n").lower() == "y"
            
        text = "\n".join(words)
    
    if (len(words)<=1):
        contin = False
 
if (len(words) == 0):
    print("\nAnswer not found")
else:        
    print("\nThe answer is: "+words[0])
    