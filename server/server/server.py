import argparse
import os

from flask import Flask
from flask import request, jsonify, abort, make_response
from flask_cors import CORS
import nltk
from nltk import tokenize
from typing import List
from summarizer import Summarizer, TransformerSummarizer


HOST = os.environ.get("HOST", "0.0.0.0")
PORT = os.environ.get("PORT", "5000")

app = Flask(__name__)
CORS(app)


def get_summarizer():
    model = "bert-base-uncased"
    transformer_type = None
    transformer_key = None
    greediness = 0.45
    reduce_ = "mean"
    hidden = -2

    if transformer_type is not None:
        print(f"Using Model: {transformer_type}")
        assert transformer_key is not None, 'Transformer Key cannot be none with the transformer type'

        return TransformerSummarizer(
            transformer_type=transformer_type,
            transformer_model_key=transformer_key,
            hidden=hidden,
            reduce_option=reduce_
        )

    else:
        print(f"Using Model: {model}")

        return Summarizer(
            model=model,
            hidden=hidden,
            reduce_option=reduce_
        )

summarizer = get_summarizer()



class Parser(object):

    def __init__(self, raw_text: bytes):
        self.all_data = str(raw_text, 'utf-8').split('\n')

    def __isint(self, v) -> bool:
        try:
            int(v)
            return True
        except:
            return False

    def __should_skip(self, v) -> bool:
        return self.__isint(v) or v == '\n' or '-->' in v

    def __process_sentences(self, v) -> List[str]:
        sentence = tokenize.sent_tokenize(v)
        return sentence

    def save_data(self, save_path, sentences) -> None:
        with open(save_path, 'w') as f:
            for sentence in sentences:
                f.write("%s\n" % sentence)

    def run(self) -> List[str]:
        total: str = ''
        for data in self.all_data:
            if not self.__should_skip(data):
                cleaned = data.replace('&gt;', '').replace('\n', '').strip()
                if cleaned:
                    total += ' ' + cleaned
        sentences = self.__process_sentences(total)
        return sentences

    def convert_to_paragraphs(self) -> str:
        sentences: List[str] = self.run()
        return ' '.join([sentence.strip() for sentence in sentences]).strip()


@app.route('/summarize', methods=['POST'])
def convert_raw_text():
    print("Converting text.")
    ratio = float(request.args.get('ratio', 0.2))
    min_length = int(request.args.get('min_length', 25))
    max_length = int(request.args.get('max_length', 500))

    data = request.data
    if not data:
        abort(make_response(jsonify(message="Request must have raw text"), 400))

    parsed = Parser(data).convert_to_paragraphs()
    summary = summarizer(parsed, ratio=ratio, min_length=min_length, max_length=max_length)

    return jsonify({
        'summary': summary
    })


@app.route('/healthy', methods=['GET'])
def healthy():
    print("Service is healthy.")

    return jsonify({
        'status': "healthy"
    })


if __name__ == "__main__":
    app.run(host=HOST, port=PORT, debug=True)