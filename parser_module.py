from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from document import Document
from nltk.stem import WordNetLemmatizer,PorterStemmer
from nltk import pos_tag
import re
from numerize import numerize as nume
import math
import ast



class Parse:
    def __init__(self):
        self.stop_words = stopwords.words('english')
        self.dictionary= {}
    def parse_text(self, text):
        """
        This function tokenize, remove stop words and apply lower case for every word within the text
        :param text:
        :return:
        """
        text= "1000 https://walla.com/hen-debi/evning.php THE DOLLAR’s computer’s People… @go Hen’s #footballStadium... in New-York COVID-19 https://walla.com with  percent Alex Cohen-Levi in Tel Aviv"
        #text = text.replace("…", " ")


        array_text_space = text.split(" ")
        string_ans =""
        array_size = range(len(array_text_space))
        string_ans_index=0
        for word,idx in zip(array_text_space,array_size):
            if not self.is_ascii(word) or word=="":
                continue
            if "www" in word or "https" in word or "http" in word:
                ans = self.add_to_dictionary(self.parse_url(word),string_ans_index)
                string_ans+=ans+" "
                string_ans_index += len(word)+1
                continue
            else:
                if word[0] != '#' and len(word)>1:
                    word = self.remove_panctuation(word)
                elif word[0]=='#' and len(word)==1:
                    continue
            if word[0] == '#' and len(word)>1:
                ans = self.add_to_dictionary(self.parse_hashtag(word),string_ans_index)
                string_ans+=ans+" "
                string_ans_index += len(word)+1
            elif word[0] == '#' and len(word)==1:
                ans = self.add_to_dictionary(self.remove_panctuation(word),string_ans_index)
                string_ans+=ans+" "
                string_ans_index += len(word)+1
            elif word[0] == '@' and len(word)>1:
                string_ans+=self.add_to_dictionary(word,string_ans_index)+" "
                string_ans_index += len(word)+1
            elif "percent" == word or "Percent" == word or "Percentage" ==word or "percentage" ==word:
                if(idx>0 and self.isfloat(array_text_space[idx-1])):
                    ans=self.add_to_dictionary(self.parse_percentage(array_text_space[idx-1]+" "+word),string_ans_index)
                    string_ans+= ans +" "
                    string_ans_index += len(word)+1
            elif word.isdecimal() or self.isfloat(word) or self.isFraction(word):
                ans =self.add_to_dictionary(self.convert_str_to_number(array_text_space,idx), string_ans_index)
                string_ans += ans + " "
                string_ans_index += len(word)+1
            else:
                string_ans+=self.add_to_dictionary(word,string_ans_index)+" "
                string_ans_index += len(word)+1
        ##remove stopwords
        #
        #
        #
        #
        # text = self.remove_panctuation(text)
        # # index_of_words={}
        # # for word,idx in enumerate(text.split(" ")):
        # #     index_of_words[word]=idx
        # names_and_entities = self.get_name_and_entities(text)
        # text=self.parse_percentage(text)
        # text= self.convert_str_to_number(text)
        # # take care of phrases
        # array_text_ = text
        # text_without_stopwords = []
        # index = 0
        # for word in array_text_:
        #     check_stop_word = word[0].lower() + word[1:]
        #     if word not in self.stop_words and check_stop_word not in self.stop_words:
        #         text_without_stopwords.append(word)
        #     else:
        #         continue
        #     if "www" in word or "https" in word or "http" in word:
        #         url_str = self.parse_url(word)
        #         for word_www in url_str:
        #             if word_www not in self.stop_words:
        #                 text_without_stopwords.append(word_www)
        #         text_without_stopwords.remove(word)
        #         continue
        #     # if "-" in word:
        #     #     splited_array = self.split_makaf(word)
        #     #     for word_ in splited_array:
        #     #         if word_ not in text_without_stopwords:
        #     #             text_without_stopwords.append(word_)
        #     if word[0] == '#' and len(word)>1:
        #         hashtag_str = self.parse_hashtag(word)
        #         for word_hash_tag in hashtag_str:
        #             text_without_stopwords.append(word_hash_tag)
        #         text_without_stopwords.remove(word)
        # , self.get_name_and_entities(string_ans)
        return string_ans
    def add_to_dictionary(self,word,index):
        array_of_words = word.split()
        ans=""
        for word in array_of_words:
            if word in self.stop_words:
                continue
            else:
                self.dictionary[word]=index
                ans+= word+" "
        return ans
    def split_makaf(self,word):
        if word[0].isnumeric() or word[len(word)-1].isnumeric():
            array=[]
            array.append(word)
            return array
        else:
            return word.split("-")

    def parse_hashtag(self, phrase):
        """"
        parser hash tag and lower the letters
        return array of string
        #stayAtHome -> ['@stayathome',stay,at,home]
        """
        original_phrase = phrase
        pattern = re.compile(r"[A-Z][a-z]+|\d+|[A-Z]+(?![a-z])")
        # temp_phrase = list(phrase)
        if phrase[1].islower():
            phrase = phrase[:1] + phrase[1].upper() + phrase[2:]
        # phrase = "".join(temp_phrase)
        temp = pattern.findall(phrase)
        temp = [str_to_lower.lower() for str_to_lower in temp]
        temp.insert(0, original_phrase[0:len(original_phrase)].lower().replace('_', ''))
        return " ".join(temp)

    def parse_url(self, string):
        """
        parsing url path
        return an array of the components
        """
        if "www" in string and ("https" in string or "http" in string):
            index = 2
        elif "http" in string and "www" not in string:
            index = 1
        elif "www" in string and "http" not in string and "https" not in string:
            index = 1
        url_str =re.split(r"[/:\.?=&…]+",string)
        temp_website_name = url_str[index]+"." + url_str[index+1]
        # url_str[index] = temp_website_name
        ans = temp_website_name+" "
        # del url_str[index+1:index+2]
        index_while=index+2
        while index_while < len(url_str):
            if "-" in url_str[index_while]:
                temp=re.split("-",url_str[index_while])
                range_temp = range(len(temp))
                for term_temp,idx_within in zip(temp,range_temp):
                    # url_str.insert(index_while, term_temp)
                    ans += temp[idx_within] + " "
                index_while+=1
            else:
                ans += url_str[index_while] + " "
                index_while+=1
        return ans

    def isfloat(self, value):
        """
            check if value is a float number
        :return: boolean
        """
        try:
            float(value)
            return True
        except ValueError:
            return False

    def isFraction(self, token):
        values = token.split('/')
        return len(values) == 2 and all(i.isdigit() for i in values)

    def convert_str_to_number(self,text_demo, idx):
        id_help = idx
        text_return = []
        range_textdemo = range(len(text_demo))
        text_demo[idx]=text_demo[idx].replace(",","")
        if not math.isnan(float(text_demo[id_help])):
            number = float(text_demo[id_help])
            number_numerize = nume.numerize(number, 3)
            if id_help + 1 < len(text_demo):
                token_next = text_demo[id_help + 1].lower()
                number_to_input = str(nume.numerize(number, 3))
                if self.isFraction(token_next):
                    text_return.append(number_to_input)
                    number_to_input = number_to_input + " " + token_next
                    text_return.append(number_to_input)
                    return text_return
                elif token_next.__eq__("billion"):
                    if 'K' in number_numerize or 'M' in number_numerize:
                        number_to_input = (number_to_input.translate({ord('K'): None}))
                        number_to_input = (number_to_input.translate({ord('M'): None}))
                        text_return.append(text_demo[id_help])
                    else:
                        text_return.append(str(number_numerize + 'B'))
                elif token_next.__eq__("million"):
                    if 'K' in number_numerize:
                        number_to_input = (number_to_input.translate({ord('K'): None}))
                        text_return.append(number_to_input + 'B')
                    else:
                        number_to_input = str(number_numerize)
                        text_return.append(number_to_input + 'M')
                elif token_next.__eq__("thousand"):
                    if 'K' in number_numerize:
                        number_to_input = (number_to_input.translate({ord('K'): None}))
                        text_return.append(number_to_input + 'M')
                    elif 'M' in number_numerize:
                        number_to_input = (number_to_input.translate({ord('M'): None}))
                        text_return.append(number_to_input + 'B')
                    else:
                        text_return.append(number_to_input + 'K')
                elif 1000 > number > -1000:
                    text_return.append(number_numerize)
                else:
                    text_return.append(number_numerize)
            else:
                text_return.append(number_numerize)
        return ' '.join(text_return)

    def is_ascii(self,s):
        return all(ord(c) < 128 for c in s)

    def get_long_url(self, url):
        """

        :param url: 2 two url . short and long
        :return:  long
        """
        c = '"'
        array=  ([pos for pos, char in enumerate(url) if char == c])
        start = array[0]
        stop = array[1]+1
        # Remove charactes from index 5 to 10
        if len(url) > stop:
            url = url[0: start:] + url[stop + 1::]
        url = url[:-2:]
        url = url[2::]
        return url

    def parse_percentage(self, string):
        """
        change word to percent
        100 percent -> 100%
        :param string: string to check if there is a percent within
        :return: array of converted strings
        """
        return string.split(" ")[0] + '%'

    def remove_panctuation(self, word):
        """
                remove pancuations from word (like . or , or : )
                :param word
                :return: word without panctuation
                """
        chars = set('.,:;!()[]{}=+…')
        if ("www" in word or "http" in word or "https" in word) or ('@' in word and word[0] != '@' and '.' in word):
            return word
        if "gmail" in word or "hotmail" in word or "yahoo" in word: return word
        if word[-2:] == "'s" or word[-2:] == "’s" or word[-2:] == "`s": word = word.replace(word[-2:], "")
        if "'s" in word: word = word.replace("'s", "")
        if "’s" in word: word = word.replace("’s", "")
        if "`s" in word: word = word.replace("`s", "")
        if "#" == word:
            return word.replace("#", "")
        if '#' in word and word[0] != '#': word = word.replace("#", "")
        if '@' in word and word[0] != '@': word = word.replace("@", "")
        for char in word:
            if any((c in chars) for c in char):
                word = word.replace(str(char), "")
        return word

    def get_name_and_entities(self,text):
        array_text = text.split()
        array_names_and_entities = {}
        idx = 0
        len_array_text = len(array_text)
        while idx < len_array_text:
            current_word = array_text[idx]
            if current_word[0].isupper():
                entity =array_text[idx]
                first_index=idx
                check_stop_word =array_text[idx][0].lower() + array_text[idx][1:]
                if check_stop_word in self.stop_words and idx+1 <len(array_text) and not array_text[idx+1][0].isupper():
                    idx+=1
                    continue
                first_char_array = array_text[idx+1][0].isupper()
                while idx+1 < len_array_text and first_char_array:
                    entity +=" "+array_text[idx+1]
                    idx+=1
                if entity in array_names_and_entities.keys():
                    array_names_and_entities[entity] = array_names_and_entities[entity]
                else:
                    array_names_and_entities[entity]=first_index
                idx += 1
            else:
                idx+=1
        # for word in array_names_and_entities.keys():
        #     temp=word[-2:]
        #     if word[:-2] == "'s" or word[:-2] == "’s" :
        #         word_tem = word[:-2]
        #         array_names_and_entities[word_tem] = array_names_and_entities[word]
        #         del array_names_and_entities[word]
        return array_names_and_entities

    def switch_long_url_in_short(self,text,url):
        text=text.replace("\n"," ")
        list_null = [m.start() for m in re.finditer("null", url)]
        quote = 0 #when add quote before and after null, we add 2 more chars and change the index of the next null
        len_list = range(len(list_null))
        for i in len_list:
            if str(url)[list_null[i] + quote - 1] == ':':
                url = url[:list_null[i] + quote] + '"' + url[list_null[i] + quote:list_null[i] + quote + 4] + '"' + url[list_null[i] + quote + 4:]
                quote += 2
        #index_null= url.find("null")
        #if index_null!=-1 and str(url)[index_null-1] == ':':
        #    url = url[:index_null] + '"' + url[index_null:index_null+4]+'"'+url[index_null+4:]
        dic_url = ast.literal_eval(url)
        array = text.split(" ")
        idx=0
        idx_value=0
        values = list(dic_url.values())
        keys = list(dic_url.keys())
        for word in array:
            if "www" in word or "https" in word or "http" in word:
                current_value = values[idx_value]
                current_key = keys[idx_value]
                if current_value == "null":
                    array[idx]= current_key
                    idx += 1
                    idx_value+=1
                    continue
                if word == current_key:
                    array[idx]=current_value
                    idx_value +=1
                    if idx_value+1>=len(values):
                        break
                #idx_value += 1
            idx+=1
        return " ".join(array)



    def parse_doc(self, doc_as_list):
        """
        This function takes a tweet document as list and break it into different fields
        :param doc_as_list: list re-preseting the tweet.
        :return: Document object with corresponding fields.
        """
        tweet_id = doc_as_list[0]
        tweet_date = doc_as_list[1]
        full_text = doc_as_list[2]
        url = doc_as_list[3]
        indices = doc_as_list[4]
        retweet_text = doc_as_list[5]
        retweet_url = doc_as_list[6]
        retweet_indices = doc_as_list[7]
        quote_text = doc_as_list[8]
        quote_url = doc_as_list[9]
        quote_indices = doc_as_list[10]
        term_dict = {}
        doc_length = len(full_text.split(" "))

        #and tweet_id=="1280919843924070402"
        if str(url)!="{}" and ( "www" in full_text or "https" in full_text or "http" in full_text):
            full_text= self.switch_long_url_in_short(full_text,url)
        #parse text
        tokenized_text = self.parse_text(full_text)

        doc_length = len(tokenized_text)  # after text operations.
        for term in tokenized_text:
            if term not in term_dict.keys():
                term_dict[term] = 1
            else:
                term_dict[term] += 1
        # for term in names_and_entities:
        #     if term not in term_dict.keys():
        #         term_dict[term] = 1

        document = Document(tweet_id, tweet_date, full_text, url, retweet_text, retweet_url, quote_text,
                            quote_url, term_dict, doc_length)
        return document
