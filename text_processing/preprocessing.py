import re
from nltk.corpus import stopwords

stop_words = stopwords.words("arabic")

arabic_diacritics = re.compile(
    """
                             ّ    | # Shadda
                            -    | # Tashdid
                             َ    | # Fatha
                             ً    | # Tanwin Fath
                             ُ    | # Damma
                             ٌ    | # Tanwin Damm
                             ِ    | # Kasra
                             ٍ    | # Tanwin Kasr
                             ْ    | # Sukun
                            ـ    | # Tatwil/Kashida
                         """,
    re.VERBOSE,
)
arabic_to_english_map = str.maketrans("٠١٢٣٤٥٦٧٨٩", "0123456789")


def preprocess(text):
    """
    text is an Arabic string input

    the preprocessed text is returned
    """

    text = re.sub(r"-\s+\d+\s+-", "", text)
    text = re.sub(r"\s+", " ", text)
    text = re.sub(arabic_diacritics, "", text)
    text = re.sub(
        r"[٠١٢٣٤٥٦٧٨٩]+",  # Match Arabic numbers
        lambda match: match.group(0)[::-1].translate(
            arabic_to_english_map
        ),  # Reverse and then translate
        text,
    )
    text = re.sub("[إأآا]", "ا", text)
    text = re.sub("ى", "ي", text)
    text = re.sub("ؤ", "ء", text)
    text = re.sub("ئ", "ء", text)
    text = re.sub("ة", "ه", text)
    text = re.sub("گ", "ك", text)

    # text = " ".join([word for word in text.split() if word not in stop_words])

    return text
