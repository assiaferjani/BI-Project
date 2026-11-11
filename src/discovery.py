"""Agrégats exploratoires : une unité = un identifiant d'article unique."""
from collections import Counter
import re

import pandas as pd

STOP_WORDS = set('the and for with from that this into using based via towards toward through over under between their its our are has have been new approach study analysis method methods model models data'.split())


def monthly_counts(frame, start, end):
    dates = pd.to_datetime(frame['submitted_at'])
    counts = frame.assign(month=dates.dt.month).groupby(['year', 'month'])['id'].nunique()
    index = pd.MultiIndex.from_product([range(start, end + 1), range(1, 13)], names=['year', 'month'])
    return counts.reindex(index, fill_value=0).unstack('month')


def category_trajectories(frame, start, end):
    expanded = frame[['id', 'year', 'selected_categories']].explode('selected_categories')
    table = expanded.groupby(['year', 'selected_categories'])['id'].nunique().unstack(fill_value=0)
    return table.reindex(range(start, end + 1), fill_value=0).rename_axis('year')


def category_overlap(frame, *, normalized=False):
    codes = sorted({c for values in frame['selected_categories'] for c in values})
    members = {code: set(frame.loc[frame['selected_categories'].map(lambda v: code in v), 'id']) for code in codes}
    table = pd.DataFrame(index=codes, columns=codes, dtype=float)
    for a in codes:
        for b in codes:
            intersection = len(members[a] & members[b])
            union = len(members[a] | members[b])
            table.loc[a, b] = 100 * intersection / union if normalized and union else intersection
    return table


def category_combinations(frame):
    unique = frame.drop_duplicates('id')
    labels = unique['selected_categories'].map(lambda v: ' + '.join(sorted(set(v))))
    return labels.value_counts().rename_axis('combination').reset_index(name='articles')


def title_vocabulary(frame, limit=15, excluded=''):
    stop = STOP_WORDS | set(re.findall(r'[a-z]{4,}', excluded.lower()))
    counts = Counter()
    for title in frame.drop_duplicates('id')['title']:
        # Présence dans un titre, et non nombre de répétitions d'un mot.
        words = set(re.findall(r'[a-z]{4,}', title.lower())) - stop
        counts.update(words)
    return pd.DataFrame(counts.most_common(limit), columns=['term', 'articles'])


def term_trajectory(frame, term, start, end, *, normalized=False):
    unique = frame.drop_duplicates('id')
    dates = range(start, end + 1)
    denominator = unique.groupby('year')['id'].nunique().reindex(dates, fill_value=0)
    matched = unique[unique['title'].str.contains(term.strip(), regex=False, case=False)] if term.strip() else unique.iloc[:0]
    counts = matched.groupby('year')['id'].nunique().reindex(dates, fill_value=0)
    return counts / denominator.where(denominator.ne(0)) * 1000 if normalized else counts
