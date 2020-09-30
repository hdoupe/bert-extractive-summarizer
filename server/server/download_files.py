import nltk
from .server import get_summarizer

def download():
    nltk.download('punkt')
    get_summarizer()


if __name__ == "__main__":
    download()