import sys
import re
import string
import os
import numpy as np
import codecs

# From scikit learn that got words from:
# http://ir.dcs.gla.ac.uk/resources/linguistic_utils/stop_words
ENGLISH_STOP_WORDS = frozenset([
    "a", "about", "above", "across", "after", "afterwards", "again", "against",
    "all", "almost", "alone", "along", "already", "also", "although", "always",
    "am", "among", "amongst", "amoungst", "amount", "an", "and", "another",
    "any", "anyhow", "anyone", "anything", "anyway", "anywhere", "are",
    "around", "as", "at", "back", "be", "became", "because", "become",
    "becomes", "becoming", "been", "before", "beforehand", "behind", "being",
    "below", "beside", "besides", "between", "beyond", "bill", "both",
    "bottom", "but", "by", "call", "can", "cannot", "cant", "co", "con",
    "could", "couldnt", "cry", "de", "describe", "detail", "do", "done",
    "down", "due", "during", "each", "eg", "eight", "either", "eleven", "else",
    "elsewhere", "empty", "enough", "etc", "even", "ever", "every", "everyone",
    "everything", "everywhere", "except", "few", "fifteen", "fifty", "fill",
    "find", "fire", "first", "five", "for", "former", "formerly", "forty",
    "found", "four", "from", "front", "full", "further", "get", "give", "go",
    "had", "has", "hasnt", "have", "he", "hence", "her", "here", "hereafter",
    "hereby", "herein", "hereupon", "hers", "herself", "him", "himself", "his",
    "how", "however", "hundred", "i", "ie", "if", "in", "inc", "indeed",
    "interest", "into", "is", "it", "its", "itself", "keep", "last", "latter",
    "latterly", "least", "less", "ltd", "made", "many", "may", "me",
    "meanwhile", "might", "mill", "mine", "more", "moreover", "most", "mostly",
    "move", "much", "must", "my", "myself", "name", "namely", "neither",
    "never", "nevertheless", "next", "nine", "no", "nobody", "none", "noone",
    "nor", "not", "nothing", "now", "nowhere", "of", "off", "often", "on",
    "once", "one", "only", "onto", "or", "other", "others", "otherwise", "our",
    "ours", "ourselves", "out", "over", "own", "part", "per", "perhaps",
    "please", "put", "rather", "re", "same", "see", "seem", "seemed",
    "seeming", "seems", "serious", "several", "she", "should", "show", "side",
    "since", "sincere", "six", "sixty", "so", "some", "somehow", "someone",
    "something", "sometime", "sometimes", "somewhere", "still", "such",
    "system", "take", "ten", "than", "that", "the", "their", "them",
    "themselves", "then", "thence", "there", "thereafter", "thereby",
    "therefore", "therein", "thereupon", "these", "they", "thick", "thin",
    "third", "this", "those", "though", "three", "through", "throughout",
    "thru", "thus", "to", "together", "too", "top", "toward", "towards",
    "twelve", "twenty", "two", "un", "under", "until", "up", "upon", "us",
    "very", "via", "was", "we", "well", "were", "what", "whatever", "when",
    "whence", "whenever", "where", "whereafter", "whereas", "whereby",
    "wherein", "whereupon", "wherever", "whether", "which", "while", "whither",
    "who", "whoever", "whole", "whom", "whose", "why", "will", "with",
    "within", "without", "would", "yet", "you", "your", "yours", "yourself",
    "yourselves"])


def load_glove(filename):
    """
    Read all lines from the indicated file and return a dictionary
    mapping word:vector where vectors are of numpy `array` type.
    GloVe file lines are of the form:

    the 0.418 0.24968 -0.41242 0.1217 ...

    So split each line on spaces into a list; the first element is the word
    and the remaining elements represent factor components. The length of the vector
    should not matter; read vectors of any length.
    """
    word_list = {}
    with open(filename) as f:
        content = f.readlines()
    #content = [line.split(' ') for line in content]
    for line in content:
        # word_list[line[0]] = np.array([float(number) for number in line[1:]])
        cols = line.split(' ')
        word_list[cols[0]] = np.array(cols[1:]).astype(float)
    return word_list

def filelist(root):
    """Return a fully-qualified list of filenames under root directory"""
    allfiles = []
    for path, subdirs, files in os.walk(root):
        for name in files:
            allfiles.append(os.path.join(path, name))
    return allfiles


def get_text(filename):
    """
    Load and return the text of a text file, assuming latin-1 encoding as that
    is what the BBC corpus uses.  Use codecs.open() function not open().
    """
    f = codecs.open(filename, encoding='latin-1', mode='r')
    s = f.read()
    f.close()
    return s


def words(text):
    """
    Given a string, return a list of words normalized as follows.
    Split the string to make words first by using regex compile() function
    and string.punctuation + '0-9\\r\\t\\n]' to replace all those
    char with a space character.
    Split on space to get word list.
    Ignore words < 3 char long.
    Lowercase all words
    Remove English stop words
    """
    regex = re.compile('[' + re.escape(string.punctuation) + '0-9\\r\\t\\n]')
    nopunct = regex.sub(" ", text)
    words = nopunct.split(" ")
    words = [w for w in words if len(w) > 2]
    words = [w.lower() for w in words]
    words = [w for w in words if w not in ENGLISH_STOP_WORDS]
    return words

def load_articles(articles_dirname, gloves):
    """
    Load all .txt files under articles_dirname and return a table (list of lists/tuples)
    where each record is a list of:

      [filename, title, article-text-minus-title, wordvec-centroid-for-article-text]

    We use gloves parameter to compute the word vectors and centroid.

    The filename is stripped of the prefix of the articles_dirname pulled in as
    script parameter sys.argv[2]. E.g., filename will be "business/223.txt"
    """


    filepaths = filelist(articles_dirname)
    noprefix = [os.path.relpath(filepath ,os.path.dirname(os.path.dirname(filepath))) for filepath in filepaths]

    record = []
    for i in range(len(filepaths)):
        content = get_text(filepaths[i])
        # record.append(tuple([noprefix[i], content[:content.find('\n\n')],
        #                     content[content.find('\n\n') + 2:].split('\n\n')]))
        # record.append(tuple([noprefix[i], content[:content.find('\n\n')], '<p>'+content[content.find('\n\n')+2:].replace('\n\n', '<\p><p>')]))
        record.append(tuple([noprefix[i], content[:content.find('\n\n')], content[content.find('\n\n') + 2:].split('\n\n'),
                       doc2vec(content[content.find('\n\n')+2:], gloves)]))
    return record



def doc2vec(text, gloves):
    """
    Return the word vector centroid for the text. Sum the word vectors
    for each word and then divide by the number of words. Ignore words
    not in gloves.
    """
    content = words(text)
    length = len(gloves.values()[0])
    sum = np.array([0]*length)
    for word in content:
        if word in gloves:
            sum = sum + gloves[word]

    return sum/len(content) #?


def distances(article, articles):
    """
    Compute the euclidean distance from article to every other article and return
    a list of (distance, a) tuples for all a in articles. The article is one
    of the elements (tuple) from the articles list.
    """
    result = []
    for element in articles:
        distance = np.linalg.norm(article[3] - element[3])
        result.append(tuple([distance, element[0]]))
    return result



def recommended(article, articles, n):
    """
    Return a list of the n articles (records with filename, title, etc...)
    closest to article's word vector centroid. The article is one of the elements
    (tuple) from the articles list.
    """
    result = distances(article, articles)
    result.sort(key=lambda x: x[0])
    result = result[1:n+1]
    filename = [i[1] for i in result] # return
    final_result = []
    for i in filename:
        for element in articles:
            if i == element[0]: #os.path.basename(element[0]):
                final_result.append(element)
                break
    return final_result
