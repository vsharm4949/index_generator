from typing import cast
import PyPDF2
import nltk
from keybert import KeyBERT
import string
import re
from itertools import chain

def findWholeWord(w):
    return re.compile(r'\b({0})\b'.format(w), flags=re.IGNORECASE).search

def pdf_to_txt() -> None:
    text = ""
    with open("./data/global_rapture_manuscript.pdf", "rb") as fp:
        pdfReader = PyPDF2.PdfFileReader(fp)

        # exclude front matter, back matter and tweet tables
        for pg in chain(range(12, 291), range(294, 344)): 
            pg_obj = pdfReader.getPage(pg)
            text += pg_obj.extract_text().replace(" -\n", "") + "\n"

    with open("./data/global_rapture.txt", "w", encoding="utf-8") as fp:
        fp.write(text)


def lemmatize_txt() -> None:
    nltk.download('omw-1.4')
    nltk.download('wordnet')

    print("Creating wortnet lemmatizer...")
    wnl = nltk.stem.WordNetLemmatizer()

    text_list = []
    print("Opening global_rapture.txt")
    with open("./data/global_rapture.txt", "r", encoding="utf-8") as fp:
        text = fp.read()
        print("Cleaning text...")
        text_clean = text
        text_clean  = re.sub(r'\d+', '', text_clean)
        text_clean  = re.sub(r'^#\w+', '',  text_clean)
        translate_table = dict((ord(char), None)
                               for char in string.punctuation 
                               if char != "-")
        translate_table[ord("¼")] = None
        translate_table[ord("¾")] = None
        translate_table[ord("¿")] = None
        translate_table[ord("©")] = None
        translate_table[ord("¿")] = None
        translate_table[ord("‘")] = None
        translate_table[ord("“")] = None
        translate_table[ord("”")] = None
        translate_table[ord("≠")] = None
        translate_table[ord("∵")] = None
        translate_table[ord("’")] = None
        translate_table[ord("…")] = None

        text_clean = text_clean.translate(translate_table)
        text_list = text_clean.split()
        text_list = list(filter(lambda w: len(w) < 30, text_list))
        
        del(text_clean)
        del(text)
        print("Lemmaizing text...")
        for i in range(len(text_list)):
            text_list[i] = wnl.lemmatize(text_list[i].strip()) 

    with open("./data/global_rapture_lemmatized.txt", "w",
              encoding="utf-8") as fp:
       fp.write(" ".join(text_list)) 


def get_keywords() -> None:
    print("Getting keywords...")
    kw_model = KeyBERT()

    with open("./data/global_rapture_lemmatized.txt", "r",
              encoding="utf-8") as fp:
        text = fp.read()
        keywords1 = kw_model.extract_keywords(
                    text,
                    keyphrase_ngram_range=(1, 1),
                    top_n=150,
                    diversity=1
                   )

        keywords2 = kw_model.extract_keywords(
                    text,
                    keyphrase_ngram_range=(2, 2),
                    top_n=50,
                    diversity=1
                   )

    words1, scores1 = zip(*keywords1)
    words2, scores2 = zip(*keywords2)

    words = words1 + words2
    words = cast(tuple[str], words)

    words = "\n".join(words)

    with open("./data/keywords.txt", "w", encoding="utf-8") as fp:
        fp.write(words)


def get_page_numbers() -> None:
    keywords_to_pages = {}

    with open("./data/keywords.txt", "r", encoding="utf-8") as fp:
        keywords_to_pages = {keyword: [] for keyword
                in fp.read().split('\n')}

    with open("./data/global_rapture_manuscript_2.pdf", "rb") as fp:
        pdfReader = PyPDF2.PdfFileReader(fp)

        # exclude front matter, back matter and tweet tables
        for pg in chain(range(11, 291), range(293, 344)): 
            pg_obj = pdfReader.getPage(pg)
            # text = pg_obj.extract_text().replace(" -\n", "").lower()
            text = pg_obj.extract_text().replace(" -\n", "")
            for keyword in keywords_to_pages.keys():
                if findWholeWord(keyword)(text) is not None:
                    keywords_to_pages[keyword].append(pg - 11)
            
    # Process page numbers
    for keyword, nums in keywords_to_pages.items():
        new_nums = []
        on_run = False
        for i in range(len(nums)):
            if i + 1 == len(nums):
                if on_run:
                    new_nums[-1] = str(new_nums[-1]) + "-" + str(nums[i])
                else:
                    new_nums.append(nums[i])

            elif nums[i+1] != nums[i] + 1:
                if not on_run:
                    new_nums.append(nums[i])
                else:
                    new_nums[-1] = str(new_nums[-1]) + "-" + str(nums[i])
                    on_run = False
            else:
                if not on_run:
                    new_nums.append(nums[i])
                    on_run = True

        keywords_to_pages[keyword] = new_nums


    # I don't think you have to do this. Just put the for loop inside the 
    # with ... as opening the file in write mode.
    with open("./data/keywords_to_pages.txt", "w", encoding="utf-8") as fp:
        fp.write("")

    with open("./data/keywords_to_pages.txt", "a", encoding="utf-8") as fp:
        for keyword, pages in sorted(keywords_to_pages.items(), key=lambda x: x[0].lower()):
            pages_str = ", ".join(str(page) for page in pages)
            fp.write(f"{keyword}  {pages_str}\n")


if __name__ == "__main__":
    # pdf_to_txt()
    # lemmatize_txt()
    # get_keywords()
    get_page_numbers()
