from datetime import date
import pandas as pd
import pytest
from src.discovery import (monthly_counts,category_trajectories,category_overlap,
    category_combinations,title_vocabulary,term_trajectory)


@pytest.fixture
def frame():
    result=pd.DataFrame({'id':['a','b','c'], 'year':[2020,2021,2021],
        'submitted_at':[date(2020,1,1),date(2021,2,1),date(2021,2,2)],
        'title':['Neural neural transformers','Diffusion for learning','Neural diffusion'],
        'selected_categories':[('cs.AI','cs.LG'),('cs.LG',),('cs.AI','cs.CL')]})
    return pd.concat([result,result.iloc[[0]]],ignore_index=True)


def test_monthly_counts_complete_calendar_without_duplicate_ids(frame):
    matrix=monthly_counts(frame,2020,2022)
    assert matrix.shape==(3,12)
    assert matrix.loc[2020,1]==1
    assert matrix.loc[2021,2]==2
    assert matrix.loc[2022].sum()==0
    assert matrix.to_numpy().sum()==3


def test_category_trajectories_count_memberships_but_not_duplicates(frame):
    table=category_trajectories(frame,2020,2022)
    assert table['cs.AI'].tolist()==[1,1,0]
    assert table['cs.LG'].tolist()==[1,1,0]
    assert table['cs.CL'].tolist()==[0,1,0]


def test_overlap_uses_intersection_over_union_not_sum(frame):
    counts=category_overlap(frame)
    assert counts.loc['cs.AI','cs.LG']==1
    assert counts.loc['cs.AI','cs.AI']==2
    normalized=category_overlap(frame,normalized=True)
    assert normalized.loc['cs.AI','cs.LG']==pytest.approx(100/3)
    assert normalized.loc['cs.AI','cs.AI']==100
    assert normalized.loc['cs.CL','cs.LG']==0


def test_combinations_are_exclusive_and_sum_to_unique_articles(frame):
    table=category_combinations(frame)
    assert table['articles'].sum()==3
    assert set(table['combination'])=={'cs.AI + cs.LG','cs.LG','cs.AI + cs.CL'}


def test_vocabulary_counts_title_presence_not_repeated_words(frame):
    words=title_vocabulary(frame).set_index('term')['articles']
    assert words['neural']==2
    assert words['diffusion']==2
    assert words['transformers']==1
    assert 'for' not in words.index
    assert 'neural' not in title_vocabulary(frame,excluded='NEURAL')['term'].tolist()


def test_terms_normalize_with_all_unique_titles_per_year(frame):
    rate=term_trajectory(frame,'NEURAL',2020,2022,normalized=True)
    assert rate.loc[2020]==1000
    assert rate.loc[2021]==500
    assert pd.isna(rate.loc[2022])
    assert term_trajectory(frame,'[.*',2020,2021).tolist()==[0,0]
    assert term_trajectory(frame,'',2020,2021).tolist()==[0,0]


def test_empty_frames_keep_valid_aggregates(frame):
    empty=frame.iloc[:0]
    assert monthly_counts(empty,2020,2021).to_numpy().sum()==0
    assert category_overlap(empty).empty
    assert category_combinations(empty).empty
    assert title_vocabulary(empty).empty
