import os
import sys
import glob
import argparse
from typing import List

from unstructured.partition.pdf import partition_pdf

import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords, words, wordnet
from nltk.stem import WordNetLemmatizer
from nltk import pos_tag

nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')
nltk.download('stopwords')
nltk.download('maxent_ne_chunker')
nltk.download('words')
nltk.download('words')
nltk.download('wordnet')
nltk.download('maxent_ne_chunker_tab')


def text_from_pdf(filepath: str, categories: tuple = ("NarrativeText")) -> List[str]:
    """
    Reads the pdf document at the given path, partitions it and returns the text for each paragraph.

    Inputs:
        filepath:   str:        Path to the PDF file
        categories: tuple:      Categories to parse from the file (Options: Title, NarrativeText, ListItem). Default: NarrativeText

    Output:
        paragraphs: List[str]:  The paragraphs found in the file, each as text.
    """
    elements = partition_pdf(
        filename=filepath,  # mandatory
        strategy="auto",    # mandatory to use ``hi_res`` strategy
        # extract_images_in_pdf=True,   # mandatory to set as ``True``
        # extract_image_block_types=["Image", "Table"],   # optional
        # infer_table_structure = True
        # model_name ="yolox"
    )

    paragraphs = [e.text for e in elements if e.category in categories]

    return paragraphs


def tokenize(text: str) -> List[str]:
    return word_tokenize(text)


def tag_tokens(tokens: str | list) -> List[tuple[str, str]]:
    input = tokens
    if isinstance(tokens, str):
        input = tokenize(tokens)

    return pos_tag(input)


def lemmatize_tokens(tokens: list[str]) -> list[str]:
    lemmatizer = WordNetLemmatizer()
    return [lemmatizer.lemmatize(w) for w in tokens]


def filter_tokens(tokens: list, additionalFilterTokens: tuple = ('et', 'al', 'etc', 'ie', 'ISSN', 'http', 'https'), validTags: tuple = ('NN', 'NNS', 'JJ'), validTokens: tuple = (), lemmatize: bool = False, removeStopwords: bool = True) -> list[str]:
    """
    Filters the given tokens. 
    Inputs:
        additionalFilterTokens: Tuple containing additional stopwords to remove.
        validTags:              Set of tags to include. Any token with a tag not in validTags will be ignored. If empty set is passed, all is included.
        validTokens:            Set of tokens to include. Any token not in validTokens will be ignored. If empty set is passed, all is included.
        lemmatize:              Whether or not to lemmatize the input before filtering.
        removeStopwords:        Whether or not to remove english stopwords.
    Outputs:
        List[str] contining filtered tokens
    """
    if len(tokens) == 0:
        return []

    if type(tokens[0]) == tuple:
        # if input tokens are already tagged
        taggedInput = tokens
    elif type(tokens[0]) == str:
        # if only tokens are passed -> tag
        taggedInput = tag_tokens(tokens)
    else:
        raise TypeError(
            f"Invalid type. Pass list[str] or list[tuple[str, str]]"
        )

    if lemmatize:
        taggedInput = [(lemmatize_tokens([t[0]])[0], t[1]) for t in taggedInput]

    filterWords = set()

    # filter stopwords
    if removeStopwords:
        filterWords.update(stopwords.words('english'))

    # filter named entities
    for chunk in nltk.ne_chunk(taggedInput):
        if hasattr(chunk, "label"):
            filterWords.update(c[0] for c in chunk)

    # user defined filter words
    filterWords.update(additionalFilterTokens)

    # all lower case
    filterWords = {w.lower() for w in filterWords}

    def filter_token(taggedToken: tuple[str, str]) -> bool:
        token, tag = taggedToken
        return (
            token.isalpha() and
            len(token) > 2 and
            (tag in validTags or not validTags) and
            (token in validTokens or not validTokens) and
            token.lower() not in filterWords
        )

    return [token for token, _ in list(filter(filter_token, taggedInput))]


def process_file(filepath: str, outputpath: str, additionalFilterTokens: tuple = ('et', 'al', 'etc', 'ie', 'ISSN', 'http', 'https'), validTags: tuple = ('NN', 'NNS', 'JJ'), validTokens: tuple = (), lemmatize: bool = False, removeStopwords: bool = True):
    """
    Process the PDF at filepath. Includes tokenization, tagging and filtering.
    """
    allTokens: list[str] = []
    paragraphs = text_from_pdf(filepath)
    for p in paragraphs:
        tokens = tokenize(p)
        tokensTagged = tag_tokens(tokens)
        tokensFiltered = filter_tokens(
            tokensTagged,
            additionalFilterTokens=additionalFilterTokens,
            validTags=validTags,
            validTokens=validTokens,
            lemmatize=lemmatize,
            removeStopwords=removeStopwords
        )
        print(f"{len(tokensFiltered)} filtered tokens")
        allTokens.extend(tokensFiltered)

    print(f"{len(allTokens)} tokens total")
    with open(outputpath, 'wt') as f:
        f.write(' '.join(allTokens))


def _parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("input_path")
    parser.add_argument('-o', '--output-path')
    parser.add_argument('-l', '--lemmatize', action='store_true')
    parser.add_argument(
        '-ft', '--filter-tokens',
        default="et,al,etc,ie,ISSN,http,https",
        type=lambda x: set(x.split(",") if x else set())
    )
    parser.add_argument(
        '-vto', '--valid-tokens',
        default="",
        type=lambda x: set(x.split(",") if x else set())
    )
    parser.add_argument(
        '-vta', '--valid-tags',
        default="NN,NNS,JJ",
        type=lambda x: set(x.split(",") if x else set())
    )

    return parser.parse_args()


if __name__ == "__main__":
    args = _parse_args()

    inputpath: str = args.input_path
    outputpath = args.output_path

    if os.path.isfile(inputpath):
        if not outputpath:
            outputpath = inputpath + '.txt'
        if os.path.isdir(outputpath):
            outputpath = outputpath + os.path.basename(inputpath) + '.txt'
        process_file(
            inputpath,
            outputpath,
            additionalFilterTokens=args.filter_tokens,
            validTags=args.valid_tags,
            validTokens=args.valid_tokens,
            lemmatize=args.lemmatize
        )
    elif os.path.isdir(inputpath):
        files = glob.glob(f"{inputpath.rstrip('/')}/*.pdf")
        if not outputpath:
            outputpath = inputpath
        for f in files:
            process_file(
                f,
                f"{outputpath}/{os.path.basename(f)}.txt",
                additionalFilterTokens=args.filter_tokens,
                validTags=args.valid_tags,
                validTokens=args.valid_tokens,
                lemmatize=args.lemmatize
            )
    else:
        print(f"File / Folder {inputpath} not found.")
