from __future__ import division
import nltk
from nltk import sent_tokenize,pos_tag,word_tokenize
import os
import numpy as np
from tfidf import TFIDF_Model,Tokenizer
from nltk.corpus import stopwords
import script_manager as sm
from graph import Graph
from matplotlib import pyplot as plt

class Reader():
    #Many scripts have rogue characters names, like Mike(on the phone), etc.
    #This method removes contents in () from a line
    def proc_char(self,line):
        if '(' in line:
            line = line[:line.index('(')]
        if ')' in line:
            line = line[:line.index(')')]
        return line.strip().lower()

    #This method returns a set of the character names in the script
    #The character names are assumed to be written one per line, completely capitalized
    #As per the format in README.txt
    def extract_char(self,lines):
        return set(map(self.proc_char,[l for l in lines if (l.strip().isupper() & (l.strip() != sm.DESC_TAG))]))

    #Method to extract the dialogue and characters in each scene
    def extract_details(self,s):
        lines = s.splitlines()
        words = word_tokenize('\n'.join([l for l in lines if not l.strip().isupper()]))
        charlist = self.extract_char(lines)
        return (lines,charlist)

    #Returns a list of 2-tuples: (scene details, graph of every scene)
    #scene_details contains the dialogue and a list of characters per scene
    #The graph of a scene is the co-occurrence matrix of the characters
    def char_graph(self,script,char_list):
        scenes = '\n'.join(script).split(sm.DESC_TAG)
        scene_details = map(self.extract_details,scenes)
        self.merge_scenes(scene_details)
        g = Graph(self.occur_mat(char_list,scene_details),char_list)
        return (scene_details,g)

    #Merges frames of character interactions
    #Each frame is a set of lines between two consecutive description tags (see the blog post for details)
    #Two or more consecutive frames are merged if they contain the same set of characters
    def merge_scenes(self,scenes):
        scenes=list(scenes)
        i = 0
        while i < len(scenes)-1:
            while len(set(scenes[i+1][1])-set(scenes[i][1])) == 0:
                scenes[i][0].extend(scenes[i+1][0][1:])
                del scenes[i+1]
                if i >= len(scenes)-1:
                    break
            i = i+1

    #Returns the co-occurrence matrix based on character interaction in the whole script
    def occur_mat(self,char_list,scenes):
        char_mat = np.zeros((len(char_list),len(char_list)))
        for scene,charlist in scenes:
            for w in charlist:
                w_id = char_list.index(w)
                for c in charlist:
                    c_id = char_list.index(c)
                    char_mat[w_id][c_id] = char_mat[w_id][c_id]+1
                    if c_id != w_id:
                        char_mat[c_id][w_id] = char_mat[c_id][w_id]+1
        return char_mat

    #Extracts the main characters from the character interaction graph
    #Displays the graph with all the characters and the pruned graph with only the main ones
    def show_all_and_main_char(self,script,F,centrality_type):
        char_list = list(self.extract_char(script))
        if len(char_list) == 0:
            return None
        scenes,g = self.char_graph(script,char_list)
        g.show()
        cent_dict,m_cent,gmi = g.most_central(F,cent_type=centrality_type)
        gmi.show()

    #Plots the centrality-vs-time graphs of the main characters extracted with the mean cutoff
    def centrality_trace(self,script,F=1,centrality_type='betweenness'):
        all_chars = list(self.extract_char(script))
        if len(all_chars) == 0:
            return None
        cent_trace = dict([(c,[]) for c in all_chars])
        scene_details,g = self.char_graph(script,all_chars)
        centrality_measure = centrality_type
        main_char_dict,cent_thresh,main_g = g.most_central(F=1,cent_type=centrality_measure)
        scenelist = []
        charlist = set([])
        for scene_text,scene_char in scene_details:
            scenelist.append((scene_text,scene_char))
            charlist = charlist.union(scene_char)
            g = Graph(self.occur_mat(list(charlist),scenelist),list(charlist))
            cent_dict,thresh,gmi = g.most_central(F,cent_type=centrality_measure)
            for c in cent_dict:
                cent_trace[c].append(cent_dict[c])

        for char in cent_trace:
            t = cent_trace[char]
            if sum(t)/len(t) > cent_thresh:
                plt.title(char)
                plt.plot(cent_trace[char])
                plt.show()