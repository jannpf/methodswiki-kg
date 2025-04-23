import re
import os
import glob
import collections

import pandas as pd
import numpy as np

from decorana import decorana


def words_from_text(content: str) -> list[str]:
    # all lowercase
    content = content.lower()

    # consecutive whitespaces
    content = re.sub(r'\s+', ' ', content)

    # only words and whitespaces
    content = re.sub(r'[^a-z ]', '', content)

    # line breaks
    content = content.replace('- ', '')

    # leading and trailing whitespaces
    content = content.strip()

    return content.split()


def import_articles(dir: str, article_types: tuple = (), exclude_files: tuple = (), n: int = None):
    filepaths = glob.glob(f"{dir.rstrip('/')}/*.txt")
    if len(filepaths) == 0:
        return {}

    if n is not None:
        filepaths = filepaths[:n]

    file_words = dict()

    for fp in filepaths:
        # filter by article type, assume that the type is within the first 4 chars of the filename
        if article_types and not any([x in fp[:4] for x in article_types]):
            continue

        # exclude specifically mentioned files
        if fp in exclude_files:
            continue

        # count the word occurrences
        filename = os.path.basename(fp)
        with open(filename, 'rt') as f:
            text = ' '.join(f.readlines())

        file_words[filename] = words_from_text(text)

    return file_words


def remove_outliers(file_words: dict, words_min=None, words_max=None):
    if not file_words:
        return {}
    lengths = [len(v) for v in file_words.values()]
    q1, q3 = np.percentile(lengths, [25, 75])
    iqr = q3 - q1
    if words_min is None:
        words_min = q1 - 1.5 * iqr
    if words_max is None:
        words_max = q3 + 1.5 * iqr

    return {f: c for f, c in file_words.items() if words_min <= len(c) <= words_max}


def abundance_dataframe(file_words: dict) -> pd.DataFrame:
    abundances = dict()

    for filename, words in file_words.items():
        abundances[filename] = collections.Counter(words)

    # convert row counts to dataframe
    df = (
        pd.DataFrame
        .from_dict(abundances)
        .fillna(0)
        .astype(int)
    )

    # normalize by column, add factor 1e3
    df = df.div(df.sum() / 1000)

    return df


def select_top_quantile(df: pd.DataFrame, quantile: float = 0.85, mode: str = "sum"):
    """
    Select top species based on abundance.

    Parameters:
        abundance_table (pd.DataFrame): Rows are species, columns are samples.
        quantile (float): Top quantile to select (e.g., 0.15 for top 15%).
        mode (str): One of 'sum', 'mean', or 'both'.

    Returns:
        pd.DataFrame: Filtered abundance table with top species.
    """
    if mode == "sum":
        metric = df.sum(axis=1)
    elif mode == "mean":
        metric = df.mean(axis=1)
    elif mode == "both":
        # min-max scaling for both mean and sum
        sums = df.sum(axis=1)
        sum_norm = (sums - sums.min()) / (sums.max() - sums.min())
        means = df.mean(axis=1)
        mean_norm = (means - means.min()) / (means.max() - means.min())

        # weight sum and means 50:50
        metric = (sum_norm + mean_norm) / 2
    else:
        raise ValueError("mode must be one of: 'sum', 'mean', 'both'")

    threshold = metric.quantile(1 - quantile)
    top_species = metric[metric >= threshold].index
    return df.loc[top_species]


def words_dca(word_df: pd.DataFrame, logscaling: bool = True, iweigh: int = 0, ira: int = 0, iresc: int = 4, mk: int = 28, short: int = 0):
    df = word_df.copy()

    if logscaling:
        df = np.log(df + 1)

    sample_scores, species_scores = decorana(
        df,
        iweigh=iweigh,
        ira=ira,
        iresc=iresc,
        mk=mk,
        short=short
    )

    return sample_scores, species_scores
