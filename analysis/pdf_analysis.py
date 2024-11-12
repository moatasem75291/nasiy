from collections import Counter
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import pandas as pd
from arabic_reshaper import reshape
from bidi.algorithm import get_display
from analysis.preprocessing_analysis import preprocess
import os
import dotenv

dotenv.load_dotenv()
ARABIC_FONT_PATH = os.getenv("ARABIC_FONT_PATH")
font_path = os.getcwd() + ARABIC_FONT_PATH


def reverse_words(text):
    return " ".join([word[::-1] for word in text.split()])


def generate_wordcloud(text):
    reversed_text = reverse_words(text)
    reshaped_text = reshape(reversed_text)
    data = get_display(reshaped_text)
    wordcloud_instance = WordCloud(
    font_path='arial', background_color='white',
    mode='RGB', width=800, height=400
    ).generate(data)
    
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.imshow(wordcloud_instance, interpolation='bilinear')
    ax.axis('off')
    plt.show()


def analyze_text_statistics(all_text):
    word_counts = Counter(all_text.split())
    most_common_words = word_counts.most_common(5)
    return pd.DataFrame(most_common_words, columns=["Word", "Frequency"])


def perform_analysis(all_text):
    all_text = preprocess(all_text)
    wordcloud = generate_wordcloud(all_text)
    statistics = analyze_text_statistics(all_text)

    return wordcloud, statistics
