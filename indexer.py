from collections import OrderedDict
from global_method import GlobalMethod
import math
import os
import datetime
from ranker import Ranker


class Indexer:

    def __init__(self, config):
        '''

        :param config: configuration file
        '''
        self.set_of_upper_words = set()
        self.dic_for_later = {}
        self.postingDic = {}
        self.idx_posting_file_test = 0
        self.counter_test = 0
        self.number_of_documents = 0

        self.details_about_docs = {}
        self.postingDic_lower = {}
        self.postingDic_upper = {}
        self.inverted_index = {}

    def add_new_doc(self, document):
        self.number_of_documents += 1
        mechane_tf = (document.doc_length - document.size_of_entities)
        if mechane_tf == 0: document.doc_length = 0.00011111111
        document_dictionary = document.term_doc_dictionary
        max_tf = -1
        for term in document_dictionary.keys():
            if term == document.tweet_id: continue
            self.number_of_documents += 1
            tf = round(document_dictionary[term] / document.doc_length, 4)
            tf_in_doc = document_dictionary[term]
            tweet_id = document.tweet_id
            keys = self.postingDic.keys()
            if tf_in_doc > max_tf:
                max_tf = tf_in_doc
            if term[0].islower():
                if term in self.postingDic_lower:
                    text = str(tweet_id) + " " + str(tf_in_doc) + " " + str(tf)
                    self.postingDic_lower[term] += text + ","
                else:
                    text = str(tweet_id) + " " + str(tf_in_doc) + " " + str(tf)
                    self.postingDic_lower[term] = text + ","
            else:
                if 'A' <= term[0] <= 'Z':
                    term_upper = term.upper()
                else:
                    term_upper = term
                if term_upper in self.postingDic_upper:
                    text = str(tweet_id) + " " + str(tf_in_doc) + " " + str(tf)
                    self.postingDic_upper[term_upper] += text + ","
                else:
                    text = str(tweet_id) + " " + str(tf_in_doc) + " " + str(tf)
                    self.postingDic_upper[term_upper] = text + ","
        self.details_about_docs[document.tweet_id] = {}
        self.details_about_docs[document.tweet_id]['rt'] = str(document.rt)
        self.details_about_docs[document.tweet_id]['date'] = str(document.tweet_date)
        self.details_about_docs[document.tweet_id]['max_tf'] = str(max_tf)
        self.details_about_docs[document.tweet_id]['uni_w'] = str(len(document.term_doc_dictionary))

    def write_posting_to_txt_file_lower_upper(self, idx):
        # self.write_details_about_docs()
        self.postingDic_lower = self.sort_dictionary_by_key(self.postingDic_lower)
        path = os.path.dirname(os.path.abspath(__file__))
        if not os.path.exists(path + '\\Posting_Files'):
            os.mkdir(path + '\\Posting_Files')
        if not os.path.exists(path + '\\Posting_Files\\posting_file_lower'):
            os.mkdir(path + '\\Posting_Files\\posting_file_lower')
        path = os.path.dirname(os.path.abspath(__file__)) + '\\Posting_Files\\posting_file_lower\\'
        file = open(path + str(idx) + ".txt", "w")
        self.sort_dictionary_by_key(self.postingDic_lower)
        keys = self.postingDic_lower.keys()
        for term in keys:
            text = term + ":" + self.postingDic_lower[term] + "\n"
            try:
                file.write(text)
            except:
                print(text)
                continue
        file.close()
        self.postingDic_lower.clear()
        self.postingDic_lower = {}
        self.postingDic_upper = self.sort_dictionary_by_key(self.postingDic_upper)
        path = os.path.dirname(os.path.abspath(__file__))
        if not os.path.exists(path + '\\Posting_Files\\posting_file_upper'):
            os.mkdir(path + '\\Posting_Files\\posting_file_upper')
        path = os.path.dirname(os.path.abspath(__file__)) + '\\Posting_Files\\posting_file_upper\\'
        file = open(path + str(idx) + ".txt", "w")
        self.sort_dictionary_by_key(self.postingDic_upper)
        keys = self.postingDic_upper.keys()
        for term in keys:
            text = term + ":" + self.postingDic_upper[term] + "\n"
            try:
                file.write(text)
            except:
                print(text)
                continue

        file.close()
        self.postingDic_upper.clear()
        self.postingDic_upper = {}
        self.write_details_about_docs()

    def merge_posting_file_round2(self):
        path = os.path.dirname(os.path.abspath(__file__)) + '\\Posting_Files\\posting_file_lower'
        files = []
        has_files_to_merge = True
        counter = 0
        while has_files_to_merge:
            files_in_path = os.listdir(path)
            count = 0
            for i in files_in_path:
                files.append(int(i.split(".")[0]))
                counter += 1
            files.sort()
            max_size = int(max(files)) + 1
            even = True
            if len(files) % 2 == 1:
                even = False
            if len(files) > 1:
                is_merge = True
                for i in range(0, len(files), 2):
                    if i + 1 == len(files) and not even:
                        continue
                    self.merge_two_posting_file_txt_round2(files[i], files[i + 1], max_size, "posting_file_lower")
                    os.remove(path + "\\" + str(files[i]) + ".txt")
                    os.remove(path + "\\" + str(files[i + 1]) + ".txt")
                    max_size += 1
                files = []
            else:
                has_files_to_merge = False
        path = os.path.dirname(os.path.abspath(__file__)) + '\\Posting_Files\\posting_file_upper'
        files = []
        has_files_to_merge = True
        counter = 0
        while has_files_to_merge:
            files_in_path = os.listdir(path)
            count = 0
            for i in files_in_path:
                files.append(int(i.split(".")[0]))
                counter += 1
            files.sort()
            max_size = int(max(files)) + 1
            even = True
            if len(files) % 2 == 1:
                even = False
            if len(files) > 1:
                is_merge = True
                for i in range(0, len(files), 2):
                    if i + 1 == len(files) and not even:
                        continue
                    self.merge_two_posting_file_txt_round2(files[i], files[i + 1], max_size, "posting_file_upper")
                    os.remove(path + "\\" + str(files[i]) + ".txt")
                    os.remove(path + "\\" + str(files[i + 1]) + ".txt")
                    max_size += 1
                files = []
            else:
                has_files_to_merge = False

    def merge_two_posting_file_txt_round2(self, idx1, idx2, idx3, case):
        path = os.path.dirname(os.path.abspath(__file__)) + '\\Posting_Files\\' + case + '\\'
        dic_1 = path + str(idx1) + ".txt"
        size_1 = os.path.getsize(dic_1)
        dic_2 = path + str(idx2) + ".txt"
        size_2 = os.path.getsize(dic_2)
        path = os.path.dirname(os.path.abspath(__file__)) + '\\Posting_Files\\' + case + '\\'
        file = open(path + str(idx3) + ".txt", "w")
        with open(dic_1) as dic_1_fp, open(dic_2) as dic_2_fp:
            dic_1_line = dic_1_fp.readline()
            dic_2_line = dic_2_fp.readline()
            while dic_1_line and dic_2_line:
                dic_1_line_term, dic_1_line_details = self.get_line_details(dic_1_line)
                if dic_1_line_term == "" or dic_1_line_details == "":
                    dic_1_line = dic_1_fp.readline()
                    continue
                dic_2_line_term, dic_2_line_details = self.get_line_details(dic_2_line)
                if dic_2_line_term == "" or dic_2_line_details == "":
                    dic_2_line = dic_2_fp.readline()
                    continue
                if dic_1_line_term == dic_2_line_term:
                    detailes_merge = dic_1_line_details + dic_2_line_details
                    file.write(dic_2_line_term + ":" + detailes_merge + '\n')
                    dic_1_line = dic_1_fp.readline()
                    dic_2_line = dic_2_fp.readline()
                elif dic_2_line_term.lower() <= dic_1_line_term.lower():
                    file.write(dic_2_line_term + ":" + dic_2_line_details + '\n')
                    dic_2_line = dic_2_fp.readline()
                elif dic_2_line_term.lower() > dic_1_line_term.lower():
                    file.write(dic_1_line_term + ":" + dic_1_line_details + '\n')
                    dic_1_line = dic_1_fp.readline()
                else:
                    print("error with :", dic_1_line_term, dic_2_line_term)
            while dic_1_line:
                file.write(dic_1_line_term + ":" + dic_1_line_details + "\n")
                dic_1_line = dic_1_fp.readline()
                if dic_1_line:
                    dic_1_line_term, dic_1_line_details = self.get_line_details(dic_1_line)
            while dic_2_line:
                file.write(dic_2_line_term + ":" + dic_2_line_details + "\n")
                dic_2_line = dic_2_fp.readline()
                if dic_2_line:
                    dic_2_line_term, dic_2_line_details = self.get_line_details(dic_2_line)
            file.close()
            dic_1_fp.close()
            dic_2_fp.close()

    def get_line_details(self, line):
        line = line.rstrip()
        splited_line = line.split(":")
        term = ""
        list_list_details = ""
        try:
            term = splited_line[0]
            list_list_details = ""
            list_details = splited_line[1]
        except:
            term = ""
            list_list_details = ""
        return term, list_details

    def merge_two_last_posting_file(self):
        path = os.path.dirname(os.path.abspath(__file__)) + '\\Posting_Files\\posting_file_lower\\'
        files_in_path = os.listdir(path)
        dic_1 = path + files_in_path[0]
        path = os.path.dirname(os.path.abspath(__file__)) + '\\Posting_Files\\posting_file_upper\\'
        files_in_path = os.listdir(path)
        dic_2 = path + files_in_path[0]
        path = os.path.dirname(os.path.abspath(__file__)) + '\\Posting_Files\\'
        file = open(path + "merge_posting_file.txt", "w")
        with open(dic_1) as dic_1_fp, open(dic_2) as dic_2_fp:
            dic_1_line = dic_1_fp.readline()
            dic_2_line = dic_2_fp.readline()
            while dic_2_line and dic_1_line:
                dic_1_line_term, dic_1_line_details = self.get_line_details(dic_1_line)
                if dic_1_line_term == "" or dic_1_line_details == "":
                    dic_1_line = dic_1_fp.readline()
                    continue
                dic_2_line_term, dic_2_line_details = self.get_line_details(dic_2_line)
                if dic_2_line_term == "" or dic_2_line_details == "":
                    dic_2_line = dic_2_fp.readline()
                    continue
                if dic_2_line_term.lower() == dic_1_line_term:
                    detailes_merge = dic_1_line_details + dic_2_line_details
                    file.write(dic_1_line_term + ":" + detailes_merge + '\n')
                    dic_1_line = dic_1_fp.readline()
                    dic_2_line = dic_2_fp.readline()
                elif dic_2_line_term.lower() < dic_1_line_term:
                    file.write(dic_2_line_term + ":" + dic_2_line_details + '\n')
                    dic_2_line = dic_2_fp.readline()
                elif dic_2_line_term.lower() > dic_1_line_term:
                    file.write(dic_1_line_term + ":" + dic_1_line_details + '\n')
                    dic_1_line = dic_1_fp.readline()
                else:
                    print("error with :", dic_1_line_term, dic_2_line_term)
            while dic_1_line:
                file.write(dic_1_line_term + ":" + dic_1_line_details + "\n")
                dic_1_line = dic_1_fp.readline()
                if dic_1_line:
                    dic_1_line_term, dic_1_line_details = self.get_line_details(dic_1_line)
            while dic_2_line:
                file.write(dic_2_line_term + ":" + dic_2_line_details + "\n")
                dic_2_line = dic_2_fp.readline()
                if dic_2_line:
                    dic_2_line_term, dic_2_line_details = self.get_line_details(dic_2_line)
            file.close()
            dic_1_fp.close()
            dic_2_fp.close()

    def split_posting_file_and_create_inverted_index(self):
        self.number_of_documents = 100000 * 3
        main_posting_file = os.path.dirname(os.path.abspath(__file__)) + '\\Posting_Files\\'
        merge_file = main_posting_file + "merge_posting_file.txt"
        array = ["A", "B", "C", "D", "E", "F", "G", "H", "I", "J", "K", "L", "M", "N", "O", "P", "Q", "R", "S", "T",
                 "U", "V", "W", "X", "Y", "Z"]
        counter_falta = 0
        for i in array:
            open(main_posting_file + str(i) + ".txt", "w")
        open(main_posting_file + "nums.txt", "w")
        with open(merge_file) as main_posting_file_fp:
            line_main_posting_file = main_posting_file_fp.readline()
            while line_main_posting_file and line_main_posting_file != "":
                letter = line_main_posting_file[0]
                letter_upper = line_main_posting_file[0].upper()
                letter_lower = line_main_posting_file[0].lower()
                if 'A' <= letter_upper <= 'Z':
                    path_posting_sub_file = os.path.dirname(os.path.abspath(__file__)) + '\\Posting_Files\\' + str(
                        letter_upper) + ".txt"
                    with open(path_posting_sub_file, 'a') as sub_posting_file_fp:
                        while line_main_posting_file != "" and (
                                line_main_posting_file[0] == letter_upper or line_main_posting_file[0] == letter_lower):
                            sub_posting_file_fp.write(line_main_posting_file)
                            term, frequency, pointer = self.get_details_from_posting_file_by_line(
                                line=line_main_posting_file)
                            if term is None or frequency is None or pointer is None:
                                line_main_posting_file = main_posting_file_fp.readline()
                                continue
                            # if 0 == int(frequency):
                            #     line_main_posting_file = main_posting_file_fp.readline()
                            #     continue
                            if 0 == int(frequency) or int(frequency) < 5:
                                line_main_posting_file = main_posting_file_fp.readline()
                                continue
                            self.inverted_index[term] = {}
                            self.inverted_index[term]['tf'] = frequency
                            self.inverted_index[term]['idf'] = math.log10(self.number_of_documents / int(frequency))
                            self.inverted_index[term]['pt'] = pointer
                            line_main_posting_file = main_posting_file_fp.readline()
                        sub_posting_file_fp.close()
                        continue

                else:
                    path_posting_sub_file = os.path.dirname(
                        os.path.abspath(__file__)) + '\\Posting_Files\\' + "nums.txt"
                    with open(path_posting_sub_file, 'a') as sub_posting_file_fp:
                        while line_main_posting_file != "" and line_main_posting_file[0] not in array:
                            sub_posting_file_fp.write(line_main_posting_file)
                            term, frequency, pointer = self.get_details_from_posting_file_by_line(
                                line=line_main_posting_file, pt="nums")
                            if term is None or frequency is None or pointer is None:
                                counter_falta += 1
                                print(counter_falta)
                                line_main_posting_file = main_posting_file_fp.readline()
                                continue
                            if 0 == int(frequency) or int(frequency) < 5:
                                line_main_posting_file = main_posting_file_fp.readline()
                                continue
                            self.inverted_index[term] = {}
                            self.inverted_index[term]['tf'] = frequency
                            self.inverted_index[term]['idf'] = math.log10(self.number_of_documents / float(frequency))
                            self.inverted_index[term]['pt'] = pointer
                            line_main_posting_file = main_posting_file_fp.readline()
                        sub_posting_file_fp.close()
                        continue

    def write_inverted_index_to_txt_file(self):
        path = os.path.dirname(os.path.abspath(__file__))
        if not os.path.exists(path + '\\inverted_index'):
            os.mkdir(path + '\\inverted_index')
        path = os.path.dirname(os.path.abspath(__file__)) + "\\inverted_index\\"
        file = open(path + "inverted_index_dic.txt", "w")
        keys = self.inverted_index.keys()
        for key in keys:
            frequency = self.inverted_index[key]['tf']
            idf = self.inverted_index[key]['idf']
            pointer = self.inverted_index[key]['pt']
            text = key + ":" + str(frequency) + " " + str(idf) + " " + str(pointer) + "\n"
            file.write(text)
        file.close()

    def load_inverted_index_to_dictionary_online(self):
        path = os.path.dirname(os.path.abspath(__file__)) + "\\inverted_index\\"
        file = open(path + "inverted_index_dic.txt", "r")
        inverted_index = {}
        line = file.readline()
        while line:
            splited_line = line.split(":")
            term = splited_line[0]
            inverted_index[term] = {}
            values = splited_line[1].split(" ")
            inverted_index[term]["tf"] = values[0]
            inverted_index[term]["idf"] = values[1]
            inverted_index[term]["pt"] = values[2].rstrip()
            line = file.readline()
        file.close()
        self.inverted_index = inverted_index
        return inverted_index

    @staticmethod
    def load_inverted_index_to_dictionary_offline():
        path = os.path.dirname(os.path.abspath(__file__))
        file = open(path + "\\inverted_index\\inverted_index_dic.txt", "r")
        inverted_index = {}
        line = file.readline()
        while line:
            splited_line = line.split(":")
            term = splited_line[0]
            inverted_index[term] = {}
            values = splited_line[1].split(" ")
            inverted_index[term]["fr"] = values[0]
            inverted_index[term]["idf"] = values[1]
            inverted_index[term]["pt"] = values[2].rstrip()
            line = file.readline()
        file.close()
        return inverted_index

    def create_matrix_global_method(self):
        g = GlobalMethod(self.inverted_index)

    # def add_new_doc(self, document):
    #     self.number_of_documents +=1
    #     mechane_tf = (document.doc_length - document.size_of_entities)
    #     if mechane_tf == 0: document.doc_length = 0.00011111111
    #     document_dictionary = document.term_doc_dictionary
    #     max_tf=-1
    #     for term in document_dictionary.keys():
    #         tf = round(document_dictionary[term] / document.doc_length, 4)
    #         tf_in_doc = document_dictionary[term]
    #         tweet_id = document.tweet_id
    #         keys = self.postingDic.keys()
    #         if tf_in_doc > max_tf:
    #             max_tf = tf_in_doc
    #         if term[0].isupper():
    #             term_upper = term.upper()
    #             term_lower = term_upper.lower()
    #             if term_upper not in self.set_of_upper_words:
    #                 self.set_of_upper_words.add(term_upper)
    #             if term_upper in keys and term_lower not in keys:
    #                 text =str(tweet_id) + " " + str(tf_in_doc) + " " + str(tf)
    #                 self.postingDic[term_upper] +=  text+","
    #             elif term_lower in keys:
    #                 self.set_of_upper_words.remove(term_upper)
    #                 text = str(tweet_id) + " " + str(tf_in_doc) + " " + str(tf)
    #                 self.postingDic[term_lower] =self.postingDic[term_lower]+text+","
    #                 if term_upper in keys:
    #                     del self.postingDic[term_upper]
    #             else:
    #                 text =  str(tweet_id) + " " + str(tf_in_doc) + " " + str(tf)
    #                 self.postingDic[term_upper] = text + ","
    #         elif term[0].islower():
    #             term_upper = term.upper()
    #             if term_upper in self.set_of_upper_words:
    #                 self.set_of_upper_words.remove(term_upper)
    #                 if term_upper not in keys and term in keys:
    #                     text = str(tweet_id) + " " + str(tf_in_doc) + " " + str(tf)
    #                     self.postingDic[term]= self.postingDic[term] + text+","
    #                 elif term_upper in keys and term not in keys:
    #                     text = str(tweet_id) + " " + str(tf_in_doc) + " " + str(tf)
    #                     self.postingDic[term] = self.postingDic[term_upper] + text + ","
    #                     del self.postingDic[term_upper]
    #                 else:
    #                     text =str(tweet_id) + " " + str(tf_in_doc) + " " + str(tf)
    #                     self.postingDic[term] = text+","
    #             else:
    #                 if term not in keys:
    #                     text =str(tweet_id) + " " + str(tf_in_doc) + " " + str(tf)
    #                     self.postingDic[term]= text+","
    #                 else:
    #                     text =str(tweet_id) + " " + str(tf_in_doc) + " " + str(tf)
    #                     self.postingDic[term]+= text+","
    #         else:
    #             if term not in keys:
    #                 text = str(tweet_id) + " " + str(tf_in_doc) + " " + str(tf)
    #                 self.postingDic[term] = text+ ","
    #             else:
    #                 text = str(tweet_id) + " " + str(tf_in_doc) + " " + str(tf)
    #
    #                 self.postingDic[term] += text + ","
    #     # self.details_about_docs[document.tweet_id]={}
    #     # self.details_about_docs[document.tweet_id]['rt']= str(document.rt)
    #     # self.details_about_docs[document.tweet_id]['date']= str(document.tweet_date)
    #     # self.details_about_docs[document.tweet_id]['max_tf']= str(max_tf)
    #     # self.details_about_docs[document.tweet_id]['uni_w']= str(len(document.term_doc_dictionary))
    def sort_dictionary_by_key(self, dictionary):
        '''
        sort dictionary by key
        :param dictionary: dictionary to sort
        :return: sorted dictionary
        '''
        self.postingDic = OrderedDict(sorted(dictionary.items(), key=lambda t: t[0]))
        return self.postingDic

    def write_details_about_docs(self):
        path = os.path.dirname(os.path.abspath(__file__))
        if not os.path.exists(path + '\\Details_about_docs'):
            os.mkdir(path + '\\Details_about_docs')
        path_to_file = os.path.dirname(os.path.abspath(__file__)) + '\\Details_about_docs\\details_about_docs.txt'
        if os.path.isfile(path_to_file):
            file = open(path_to_file, "a")
        else:
            file = open(path_to_file, "w")
        keys = self.details_about_docs.keys()
        for key in keys:
            file.write(
                key + ":" + self.details_about_docs[key]['date'] + " " + self.details_about_docs[key]['rt'] + " " +
                self.details_about_docs[key]['uni_w'] + " " + self.details_about_docs[key]['max_tf'] + "\n")
        file.close()
        self.details_about_docs.clear()
        self.details_about_docs = {}

    def write_posting_file_to_txt_file(self, idx):
        self.write_details_about_docs()
        self.sort_dictionary_by_key(self.postingDic)
        path = os.path.dirname(os.path.abspath(__file__))
        if not os.path.exists(path + '\\Posting_Files'):
            os.mkdir(path + '\\Posting_Files')
        path = os.path.dirname(os.path.abspath(__file__)) + '\\Posting_Files\\'
        file = open(path + str(idx) + ".txt", "w")
        self.sort_dictionary_by_key(self.postingDic)
        keys = self.postingDic.keys()
        for term in keys:
            text = term + ":" + self.postingDic[term] + "\n"
            # text=self.get_shorter_line(text)
            try:
                file.write(text)
            except:
                print(text)
                continue
        print("FINISH to write 200K docs to disk...")
        print(datetime.datetime.now())
        file.close()
        self.postingDic.clear()
        self.postingDic = {}
        print("START to write 200K docs to DETAILS ABOUT DOCS...")
        print(datetime.datetime.now())
        # self.write_details_about_docs()
        print("FINISH to write 200K docs to DETAILS ABOUT DOCS...")
        print(datetime.datetime.now())

    def merge_posting_files(self):
        path = os.path.dirname(os.path.abspath(__file__)) + '\\Posting_Files\\'
        files = []
        has_files_to_merge = True
        is_merge = False
        counter = 0
        while has_files_to_merge:
            files_in_path = os.listdir(path)
            count = 0
            for i in files_in_path:
                files.append(int(i.split(".")[0]))
                counter += 1
            files.sort()
            max_size = int(max(files)) + 1
            even = True
            if len(files) % 2 == 1:
                even = False
            if len(files) > 1:
                is_merge = True
                for i in range(0, len(files), 2):
                    if i + 1 == len(files) and not even:
                        continue
                    self.merge_two_posting_file_txt(files[i], files[i + 1], max_size)
                    os.remove(path + "\\" + str(files[i]) + ".txt")
                    os.remove(path + "\\" + str(files[i + 1]) + ".txt")
                    max_size += 1
                files = []
            else:
                has_files_to_merge = False

    def get_shorter_line(self, line):
        first_split = line.split(":")
        splited_line = first_split[1].split(",")
        if len(splited_line) == 2:
            return line
        array = []
        for i in splited_line:
            if i == "\n": continue
            splited_revach = i.split(" ")
            array.append(splited_revach[0])
        array = sorted(array, key=int, reverse=True)
        first = array[0]
        last_ans = []
        index = 0
        for word in splited_line:
            if word == "\n": continue
            splited_revach = word.split(" ")
            max = array[0]
            temp = word[0]
            calc = int(max) - int(word.split(" ")[0])
            if calc == 0:
                text = str(max) + " " + word[1] + " " + word[2]
            text = str(calc) + " " + splited_line[1] + " " + splited_line[2]
            last_ans.append(text)
            index += 1
        return str(first_split[0]) + ":" + ",".join(last_ans) + "\n"

    def compare_two_posting_file(self, idx1, idx2):
        path = os.path.dirname(os.path.abspath(__file__)) + '\\Posting_Files\\'
        dic_1 = path + str(idx1) + ".txt"
        dic_2 = path + str(idx2) + ".txt"
        file_1 = open(path + str(idx1) + ".txt", "w")
        file_2 = open(path + str(idx2) + ".txt", "w")
        with open(dic_1) as fp_small, open(dic_2) as fp_big:
            line_small = fp_small.readline()
            line_big = fp_big.readline()
            while line_small and line_big:
                term_and_values_small = line_small.split(":")
                term_small = term_and_values_small[0]
                term_and_values_big = line_big.split(":")
                term_big = term_and_values_big[0]

    def merge_two_posting_file_txt(self, idx1, idx2, idx3):
        text_to_print = ""
        path = os.path.dirname(os.path.abspath(__file__)) + '\\Posting_Files\\'
        dic_1 = path + str(idx1) + ".txt"
        size_1 = os.path.getsize(dic_1)
        dic_2 = path + str(idx2) + ".txt"
        size_2 = os.path.getsize(dic_2)
        if size_1 >= size_2:
            big = dic_1
            small = dic_2
        else:
            small = dic_1
            big = dic_2
        path = os.path.dirname(os.path.abspath(__file__)) + '\\Posting_Files\\'
        file = open(path + str(idx3) + ".txt", "w")
        with open(small) as fp_small, open(big) as fp_big:
            line_small = fp_small.readline()
            line_big = fp_big.readline()
            while line_small and line_big:
                term_and_values_small = line_small.split(":")
                term_small = term_and_values_small[0]
                term_and_values_big = line_big.split(":")
                term_big = term_and_values_big[0]
                try:
                    is_term_small_in_dic_for_later = term_small in self.dic_for_later
                    is_term_big_in_dic_for_later = term_big in self.dic_for_later
                    is_term_small_in_set_of_words = term_small in self.set_of_upper_words
                    if is_term_small_in_dic_for_later:
                        term_and_values_small[1] += self.dic_for_later[term_small]
                        line_small = str(line_small.rstrip()) + str(str(self.dic_for_later[term_small]).rstrip()) + "\n"
                        del self.dic_for_later[term_small]

                    if is_term_big_in_dic_for_later:
                        term_and_values_big[1] += self.dic_for_later[term_big]
                        line_big = str(line_big.rstrip()) + str(str(self.dic_for_later[term_big]).rstrip()) + "\n"
                        del self.dic_for_later[term_big]

                    if not term_small[0].isdigit() and term_small.isupper() and not is_term_small_in_set_of_words:
                        term_small = term_small.lower()
                        if term_small in self.dic_for_later:
                            self.dic_for_later[term_small] += term_and_values_small[1]
                        else:
                            self.dic_for_later[term_small] = term_and_values_small[1]
                        line_small = fp_small.readline()
                        continue

                    elif not term_small[
                        0].isdigit() and term_small.islower() and term_small.upper() in self.set_of_upper_words:
                        self.set_of_upper_words.remove(term_small.upper())
                        # pick up form later dictionary
                        if is_term_small_in_dic_for_later:
                            term_and_values_small[1] += self.dic_for_later[term_small]
                            del self.dic_for_later[term_small]
                except:
                    line_small = fp_small.readline()
                    continue
                try:
                    is_term_big_in_set_of_words = term_big in self.set_of_upper_words
                    if is_term_big_in_dic_for_later:
                        term_and_values_big[1] += self.dic_for_later[term_big]
                        line_big = str(line_big.rstrip()) + str(str(self.dic_for_later[term_big]).rstrip()) + "\n"
                        del self.dic_for_later[term_big]
                    elif not term_big[0].isdigit() and term_big.isupper() and not is_term_big_in_set_of_words:
                        term_big = term_big.lower()
                        if term_big in self.dic_for_later:
                            self.dic_for_later[term_big] += term_and_values_big[1]
                            line_big = fp_big.readline()
                            continue
                        else:
                            self.dic_for_later[term_big] = term_and_values_big[1]
                            line_big = fp_big.readline()
                            continue
                    elif not term_big[
                        0].isdigit() and term_big.islower() and term_big.upper() in self.set_of_upper_words:
                        self.set_of_upper_words.remove(term_big.upper())
                        # pick up form later dictionary
                        if is_term_big_in_dic_for_later:
                            term_and_values_small[1] += self.dic_for_later[term_big]
                            del self.dic_for_later[term_big]
                except:
                    line_big = fp_big.readline()
                    continue
                if term_big < term_small:
                    text = line_big
                    line_big = fp_big.readline()
                elif term_big > term_small:
                    text = line_small
                    line_small = fp_small.readline()
                else:
                    tweet_id_fr_small = term_and_values_small[1].split(",")
                    tweet_id_fr_big = term_and_values_big[1].split(",")
                    tweet_id_fr_big.extend(tweet_id_fr_small)
                    values = list()
                    for item in tweet_id_fr_big:
                        if item == "\n":
                            continue
                        else:
                            if item not in values:
                                values.append(item)
                    text = term_big + ":" + ",".join(values) + ",\n"
                    text = self.get_shorter_line(text)
                    text_to_print += text
                    line_small = fp_small.readline()
                    line_big = fp_big.readline()
                    continue
                file.write(text)
            while line_big:
                file.write(line_big)
                line_big = fp_big.readline()
            while line_small:
                file.write(line_small)
                line_small = fp_small.readline()
        fp_small.close()
        fp_big.close()
        file.close()

    # def split_posting_file_and_create_inverted_index(self):
    #     path_posting_file = os.path.dirname(os.path.abspath(__file__)) + '\\Posting_Files\\'
    #     files_in_path = os.listdir(path_posting_file)
    #     main_posting_file = path_posting_file+"\\"+files_in_path[0]
    #     array = ["A","B","C","D","E","F","G","H","I","J","K","L","M","N","O","P","Q","R","S","T","U","V","W","X","Y","Z","a","b","c","d","e","f","g","h","i","j","k","l","m","n","o","p","q","r","s","t","u","v","w","x","y","z"]
    #     counter_falta=0
    #     for i in array:
    #         open(path_posting_file + str(i) + ".txt", "w")
    #     num_lines = sum(1 for line in open(main_posting_file))
    #     open(path_posting_file  + "nums.txt", "w")
    #     with open(main_posting_file) as main_posting_file_fp:
    #         line_main_posting_file = main_posting_file_fp.readline()
    #         while line_main_posting_file and line_main_posting_file!="":
    #             letter= line_main_posting_file[0]
    #             if letter  in array:
    #                 path_posting_sub_file=os.path.dirname(os.path.abspath(__file__)) + '\\Posting_Files\\'+str(letter)+".txt"
    #                 with open(path_posting_sub_file,'a') as sub_posting_file_fp:
    #                 #inverted index
    #                     while line_main_posting_file!="" and line_main_posting_file[0] == letter:
    #                         sub_posting_file_fp.write(line_main_posting_file)
    #                         term,frequency,pointer=self.get_details_from_posting_file_by_line(line=line_main_posting_file)
    #                         if term is None or frequency is None or pointer is None:
    #                             counter_falta+=1
    #                             print(counter_falta)
    #                             line_main_posting_file = main_posting_file_fp.readline()
    #                             continue
    #                         if 0==int(frequency):
    #                             print(term)
    #                             line_main_posting_file = main_posting_file_fp.readline()
    #                             continue
    #                         self.inverted_idx[term]={}
    #                         self.inverted_idx[term]['fr'] = frequency
    #                         self.inverted_idx[term]['idf'] = math.log10(self.number_of_documents/int(frequency))
    #                         self.inverted_idx[term]['pt'] = pointer
    #                         line_main_posting_file = main_posting_file_fp.readline()
    #                     sub_posting_file_fp.close()
    #                     continue
    #
    #             else:
    #                 path_posting_sub_file=os.path.dirname(os.path.abspath(__file__)) + '\\Posting_Files\\'+"nums.txt"
    #                 with open(path_posting_sub_file,'a') as sub_posting_file_fp:
    #                     while line_main_posting_file!="" and line_main_posting_file[0] not in array :
    #                         sub_posting_file_fp.write(line_main_posting_file)
    #                         term,frequency,pointer=self.get_details_from_posting_file_by_line(line=line_main_posting_file,pt="nums")
    #                         if term is None or frequency is None or pointer is None:
    #                             counter_falta+=1
    #                             print(counter_falta)
    #                             line_main_posting_file = main_posting_file_fp.readline()
    #                             continue
    #                         if 0 == int(frequency):
    #                             print(term)
    #                             line_main_posting_file = main_posting_file_fp.readline()
    #                             continue
    #                         self.inverted_idx[term]={}
    #                         self.inverted_idx[term]['fr'] = frequency
    #
    #                         self.inverted_idx[term]['idf'] = math.log10(self.number_of_documents/float(frequency))
    #                         self.inverted_idx[term]['pt'] = pointer
    #                         line_main_posting_file = main_posting_file_fp.readline()
    #                     sub_posting_file_fp.close()
    #                     continue
    def get_details_from_posting_file_by_line(self, line, pt=""):
        split_double_dots = line.split(":")
        term = split_double_dots[0]
        try:
            tweets_ = split_double_dots[1].split(",")
        except:
            return None, None, None

        number_of_tweets = str(len(tweets_) - 1)
        if pt == "":
            pointer = line[0]
        elif pt == "nums":
            pointer = "nums"
        return term, number_of_tweets, pointer

    @staticmethod
    def get_values_in_posting_file_of_dictionary_term(term, pointer):
        path = os.path.dirname(os.path.abspath(__file__)) + '\\Posting_Files\\'
        file = open(path + str(pointer) + ".txt", "r")
        dic_tweet = {}
        with file as fp_small:
            line_small = fp_small.readline()
            while line_small:
                splited_line = line_small.split(":")
                term_ = splited_line[0]
                if term_ == term:
                    dic_tweet = Indexer.get_details_about_term_in_posting_file(splited_line[1])
                    break
                line_small = fp_small.readline()
        file.close()
        return dic_tweet

    @staticmethod
    def get_details_about_term_in_posting_file(line):
        details_dic = {}
        splited_line = line.split(",")
        for i in splited_line:
            details_array = i.split(" ")
            if i != "\n":
                tweet_id = details_array[0]
                details_dic[tweet_id] = {}
                details_dic[tweet_id]['tf'] = details_array[1]
                details_dic[tweet_id]['tfl'] = details_array[2]
        return details_dic

    def get_details_about_term_in_inverted_index(self, term):
        dic = None
        if term in self.inverted_index.keys():
            dic = {}
            dic["tf"] = self.inverted_index[term]["tf"]
            dic["idf"] = self.inverted_index[term]["idf"]
            dic["pt"] = self.inverted_index[term]["pt"]
            return dic
        return dic

    # def new_sub_dict(self):
    #     self.inverted_idx={}
    #     self.posting_file=PostingFile()
    #     self.sub_dic_posting_file_idx+=1
    # def add_new_doc_round2(self,document):
    #     write=False
    #     for term in document.term_doc_dictionary.keys():
    #         tf = round(document.term_doc_dictionary[term]/document.doc_length,4)
    #         tf_in_term = document.term_doc_dictionary[term]
    #         #tf_in_term = document.document_dictionary[term]
    #
    #         self.posting_file.add_term_to_posting_file_round2(document.tweet_id,tf,tf_in_term,term)
    #     self.counter_round2+=1
    #     if self.counter_round2 == 20:
    #         self.posting_file.write_to_disk_after_X_of_documents()
    #         self.counter_round2 = 0

    # def add_new_doc(self, document,clear_tresh=10000):
    #     """
    #     This function perform indexing process for a document object.
    #     Saved information is captures via two dictionaries ('inverted index' and 'posting')
    #     :param document: a document need to be indexed.
    #     :return: -
    #     """
    #     self.number_of_documents+=1
    #
    #     document_dictionary = document.term_doc_dictionary
    #     max_tf=0
    #     # Go over each term in the doc
    #     for term in document_dictionary.keys():
    #         tf = round(document_dictionary[term]/document.doc_length,4)
    #         tf_in_term = document_dictionary[term]
    #         if tf_in_term > max_tf:
    #             max_tf = tf
    #         keys = self.inverted_idx.keys()
    #         try:
    #             if term[0].isupper():
    #                 term_upper = term.upper()
    #                 term_lower = term_upper.lower()
    #                 # in case of new term in the dictionary - capital or lower it doesnt matter
    #                 if term_upper not in keys and term_lower not in keys:
    #                     self.inverted_idx[term_upper] = {}
    #                     self.inverted_idx[term_upper]['frequency_show_term'] = 1
    #                     new_pointer = self.posting_file.add_term_to_posting_file(tweet_id=document.tweet_id, tf=tf,
    #                                                                              freq_in_tweet=document_dictionary[
    #                                                                                  term],term=term_upper)
    #                     self.inverted_idx[term_upper]['posting_pointer'] = new_pointer
    #                     continue
    #                 # in case of capital letter already exists in the dictionary
    #                 elif term_upper in keys and term_lower not in keys:
    #                     self.inverted_idx[term_upper]['frequency_show_term'] += 1
    #                     self.posting_file.add_term_to_posting_file(tweet_id=document.tweet_id, tf=tf,
    #                                                                freq_in_tweet=document_dictionary[term],term=term_upper,
    #                                                                posting_id=self.inverted_idx[term_upper][
    #                                                                    'posting_pointer'])
    #                     # in case of word with capital letter fit to word with lower case
    #                 elif term_lower in keys:
    #                     self.inverted_idx[term_lower]['frequency_show_term'] += 1
    #                     self.posting_file.add_term_to_posting_file(tweet_id=document.tweet_id, tf=tf,
    #                                                                freq_in_tweet=document_dictionary[term],term=term_lower,
    #                                                                posting_id=self.inverted_idx[term_lower][
    #                                                                    'posting_pointer'])
    #             else:
    #                 term_upper= term.upper()
    #                 # in case of word that already exists in dictionary
    #                 if term_upper  in keys and not term_upper.isnumeric() :
    #                     temp_freq = self.inverted_idx[term_upper]['frequency_show_term']
    #                     temp_pointer = self.inverted_idx[term_upper]['posting_pointer']
    #                     self.inverted_idx[term] = {}
    #                     self.inverted_idx[term]['frequency_show_term'] = temp_freq + 1
    #                     new_pointer = self.posting_file.add_term_to_posting_file(document.tweet_id, tf,
    #                                                                              document_dictionary[term],term,
    #                                                                              temp_pointer)
    #                     self.inverted_idx[term]['posting_pointer'] = new_pointer
    #                     del self.inverted_idx[term_upper]  ## consume a lot of resource - check it
    #                 # in case of new term in dictionary
    #                 elif term not in keys:
    #                     self.inverted_idx[term] = {}
    #                     self.inverted_idx[term]['frequency_show_term'] = 1
    #                     new_pointer = self.posting_file.add_term_to_posting_file(document.tweet_id, tf,
    #                                                                              document_dictionary[term],term)
    #                     self.inverted_idx[term]['posting_pointer'] = new_pointer
    #                     continue
    #                 # in case of new term that join to exist term in dictionary
    #                 elif term in keys:
    #                     self.inverted_idx[term]['frequency_show_term'] += 1
    #                     self.posting_file.add_term_to_posting_file(document.tweet_id, tf,document_dictionary[term],term,
    #                                                                self.inverted_idx[term]['posting_pointer'])
    #
    #         except:
    #             print('problem with the following key {}'.format(term[0]))
    #     # if self.number_of_documents == int(round(clear_tresh/2)):
    #     if self.number_of_documents == 250000:
    #         self.write_new_dictionary_to_disk()
    #         self.idx_inverted_dic += 1
    #         self.posting_file.clear_memory()
    #         self.number_of_documents=0
    #     # self.dic_max_tf_and_uniqueness[str(document.tweet_id)] = {}
    #     # self.dic_max_tf_and_uniqueness[str(document.tweet_id)]['max_tf'] = max_tf
    #     # self.dic_max_tf_and_uniqueness[str(document.tweet_id)]['uniqueness_words'] = len(document_dictionary)
    #     # self.dic_max_tf_and_uniqueness[str(document.tweet_id)]['rt'] = str(document.rt)
    # def add_idf_to_dictionary(self,number_of_document,idx):
    #     keys = self.inverted_idx.keys()
    #     for key in keys:
    #         self.inverted_idx[key]['idf'] = math.log10(number_of_document/self.inverted_idx[key]['frequency_show_term'])
    #     os.remove(os.path.dirname(os.path.abspath(__file__)) + "\\inverted_dic_file_" + str(idx) + ".json")
    #     self.write_inverted_index_to_disk(idx,self.inverted_idx)
    #
    # def write_to_disk_dic_max_tf_and_uniqueness(self):
    #     '''
    #     write dictionary max tf and number of uniqueness word in document
    #     :return:
    #     '''
    #     j = json.dumps(self.dic_max_tf_and_uniqueness)
    #     with open('dic_max_tf_and_uniqueness.json','w') as f:
    #         f.write(j)
    #         f.close()
    # def open_dic_max_tf_and_uniqueness(self):
    #     '''
    #     get max_tf and uniqueness dictionary from json to dictionary
    #     :return:
    #     '''
    #     with open('dic_max_tf_and_uniqueness.json') as json_file:
    #         data = json.load(json_file)
    #         return data
    # def write_new_dictionary_to_disk(self):
    #     self.sort_dictionary_by_key(self.inverted_idx)
    #     self.write_inverted_index_to_disk(idx=self.idx_inverted_dic,inverted_index=self.inverted_idx)
    # def divide_dictionary(self, documents_list_after_parse,idx=None):
    #     '''
    #     divide the dictionary to multiple smaller dictionaries
    #     :param documents_list_after_parse: dictionary
    #     :param idx:
    #     :return:
    #     '''
    #     if idx is None:
    #         idx = len(documents_list_after_parse)
    #     dic_index = 0
    #     sub_dic_idx = 0
    #     index = 0
    #     limit = int(idx / 10)
    #     limit_extra = idx - limit * 10
    #     len_parsed_documents = len(documents_list_after_parse)
    #     while dic_index < 10:
    #         while sub_dic_idx < limit and index < len_parsed_documents:
    #             self.add_new_doc(documents_list_after_parse[index])
    #             sub_dic_idx += 1
    #             index += 1
    #             if dic_index == 9:
    #                 limit = limit + limit_extra
    #         self.sort_dictionary_by_key(self.inverted_idx)
    #         self.posting_file.sort_posting_file()
    #         self.write_to_disk(self.sub_dic_posting_file_idx)
    #         self.new_sub_dict()
    #         dic_index += 1
    #         sub_dic_idx = 0
    #     self.write_to_disk_dic_max_tf_and_uniqueness()
    #     # ans = self.open_dic_max_tf_and_uniqueness()
    #
    # def write_to_disk(self,idx, posting_file=None,inverted_idx=None):
    #     '''
    #     write posting file and inverted index to disk
    #     :param idx: offset of the dictionary
    #     :param posting_file:
    #     :param inverted_idx:
    #     '''
    #     if inverted_idx is not None:
    #         j=json.dumps(inverted_idx)
    #     else:
    #         j =json.dumps(self.inverted_idx)
    #     with open('inverted_dic_file_'+str(idx)+'.json','w') as f:
    #         f.write(j)
    #         f.close()
    #     # j =json.dumps(self.posting_file.posting_file_to_json())
    #     if posting_file is not None:
    #         j = json.dumps(posting_file.posting_file_to_json())
    #     else:
    #         j = json.dumps(self.posting_file.posting_file_to_json())
    #
    #     with open('posting_file_' + str(idx) + '.json', 'w') as f:
    #         f.write(j)
    #         f.close()
    # def write_posting_file_to_disk(self, idx):
    #     '''
    #     write posting file to disk
    #     :param idx: offset of the posting file
    #     '''
    #     j = json.dumps(self.posting_file.posting_file_to_json())
    #     with open('posting_file_' + str(idx) + '.json', 'w') as f:
    #         f.write(j)
    #         f.close()
    # def write_inverted_index_to_disk(self,idx,inverted_index):
    #     path = os.path.dirname(os.path.abspath(__file__))
    #     if not os.path.exists(path+'\\inverted_index'):
    #         os.mkdir(path+'\\inverted_index')
    #     path = os.path.dirname(os.path.abspath(__file__))+'\\inverted_index\\'
    #     j =json.dumps(inverted_index)
    #     with open(path+'\\inverted_dic_file_'+str(idx)+'.json','w') as f:
    #         f.write(j)
    #         f.close()
    #     self.inverted_idx.clear()
    #     self.inverted_idx={}
    #
    # def open_sub_dic_inverted_index(self, idx):
    #     '''
    #     open sub dictionary of inverted dictionary
    #     :param idx: offset of the sub dictionary
    #     :return:
    #     '''
    #     with open('inverted_dic_file_' + str(idx) + '.json') as json_file:
    #         data = json.load(json_file)
    #         return data
    # '''

    #
    #
    # def merge_sub_dic_inverted_index(self, idx_origin, idx_aim):
    #
    #     merge sub dic inverted index and posting file
    #     :param idx_origin: offset of origin dictionary
    #     :param idx_aim: offset of aim dictionary
    #     :return:
    #     dic_idx_origin = self.open_sub_dic_inverted_index(idx_origin)
    #     posting_file_origin = self.posting_file.open_posting_file(idx_origin)
    #     dic_idx_aim = self.open_sub_dic_inverted_index(idx_aim)
    #     posting_file_aim = self.posting_file.open_posting_file(idx_aim)
    #     items_origin = dic_idx_origin.items()
    #     keys_aim = dic_idx_aim.keys()
    #     for key, value in items_origin:
    #         if key in keys_aim:
    #             if key=="19":
    #                 print("")
    #             dic_idx_aim[key]['frequency_show_term'] += dic_idx_origin[key]['frequency_show_term']
    #             pointer = dic_idx_aim[key]['posting_pointer']
    #             temp = dic_idx_origin[key]['posting_pointer']
    #             posting_file_aim[pointer].extend(posting_file_origin[dic_idx_origin[key]['posting_pointer']])
    #         else:
    #             dic_idx_aim[key] = {}
    #             dic_idx_aim[key]['frequency_show_term'] = dic_idx_origin[key]['frequency_show_term']
    #             dic_idx_aim[key]['posting_pointer'] = dic_idx_origin[key]['posting_pointer']
    #             pointer = dic_idx_origin[key]['posting_pointer']
    #             temp_1 = posting_file_origin[pointer]
    #             posting_file_aim[pointer] = posting_file_origin[pointer]
    #             temp_1 = posting_file_aim[pointer]
    #
    #     dic_idx_aim = self.sort_dictionary_by_key(dic_idx_aim)
    #     self.posting_file.posting_file_dictionary = posting_file_aim
    #     posting_file_aim = self.posting_file.sort_posting_file()
    #     self.inverted_idx = dic_idx_aim
    #     self.posting_file.posting_file_dictionary = posting_file_aim
    #     return PostingFile(posting_file_aim), dic_idx_aim
    # '''
    # def sort_posting_file_by_abc(self):
    #     '''
    #     split the posting file to a'b'c
    #     '''
    #     items_inverted_idx = self.inverted_idx.items()
    #     sorted_posting_file_hashtag = {}
    #     a_k = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k']
    #     l_z = ['l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'w', 'x', 'y', 'z']
    #     sorted_posting_file_a_k = {}
    #     sorted_posting_file_l_z = {}
    #     for key, value in items_inverted_idx:
    #         posting_id = self.inverted_idx[key]['posting_pointer']
    #         first_letter = key[0].lower()
    #         if first_letter in a_k:
    #             sorted_posting_file_a_k[posting_id] = self.posting_file.posting_file_dictionary[posting_id]
    #         elif first_letter in l_z:
    #             sorted_posting_file_l_z[posting_id] = self.posting_file.posting_file_dictionary[posting_id]
    #         else:
    #             sorted_posting_file_hashtag[posting_id] = self.posting_file.posting_file_dictionary[posting_id]
    #     self.posting_file.posting_file_dictionary = sorted_posting_file_hashtag
    #     self.write_posting_file_to_disk("hash")
    #     self.posting_file.posting_file_dictionary = sorted_posting_file_a_k
    #     self.write_posting_file_to_disk("a_k")
    #     self.posting_file.posting_file_dictionary = sorted_posting_file_l_z
    #     self.write_posting_file_to_disk("l_z")
    # def merge_all_posting_and_inverted_idx(self):
    #     '''
    #     build the posting file and the inverted index step by step like a tournament
    #     '''
    #     path =  "C:\\Users\\HEN\\PycharmProjects\\Search_Engine_Project"
    #     files = []
    #     has_files_to_merge = True
    #     is_merge = False
    #     counter=0
    #     while has_files_to_merge:
    #         files_in_path =os.listdir(path)
    #         count=0
    #         for i in files_in_path:
    #             if re.match('posting_file_',i):
    #                 file = re.findall("\d+", i)[0]
    #                 files.append(file)
    #                 counter+=1
    #         max_size = int(max(files))+1
    #         even =True
    #         if len(files) %2==1:
    #             even=False
    #         if len(files) >1:
    #             is_merge = True
    #             for i in range(0,len(files),2):
    #                 if i+1 == len(files) and not even:
    #                     continue
    #                 posting_file_aim,dic_idx_aim = self.merge_sub_dic_inverted_index(files[i],files[i+1])
    #                 os.remove(path+"\\posting_file_"+files[i]+".json")
    #                 os.remove(path+"\\inverted_dic_file_"+files[i]+".json")
    #                 os.remove(path+"\\posting_file_"+files[i+1]+".json")
    #                 os.remove(path+"\\inverted_dic_file_"+files[i+1]+".json")
    #                 self.write_to_disk(max_size,posting_file=posting_file_aim,inverted_idx=dic_idx_aim)
    #                 max_size+=1
    #             files = []
    #         else:
    #             has_files_to_merge=False
    #     if is_merge:
    #         self.inverted_idx=dic_idx_aim
    #         return dic_idx_aim,max_size-1
    #     return self.inverted_idx,max_size-1
