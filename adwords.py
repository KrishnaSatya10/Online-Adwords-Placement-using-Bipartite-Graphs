#!/usr/bin/env python
# coding: utf-8


import math
import random
import pandas as pd
import numpy as np
import sys


def calculate_MSVV(x):
    exp_val = math.exp((x['Spent']/x['Total Budget'])-1)
    return x['Bid Value'] * (1 - exp_val)


def msvv(queries, budgets, dataset):

    budgets_spent = original_budgets.copy()
    budgets_spent['Spent'] = 0
    budgets_spent['Total Budget'] = budgets_spent['Budget']

    # MSVV
    total_revenue = 0
    for query in queries:
        #         print(query)
        query_bidders = dataset[dataset['Keyword']
                                == query][['Advertiser', 'Bid Value']]

        # If there are valid bidders for this query (with valid budget)
        if (query_bidders.shape[0]):
            highest_bidder = None
            max_bid_value = -np.inf

            # Consider only those bidders who have minimum budget for the bid.
            query_bidders_budgets_spent = query_bidders.merge(
                budgets_spent, on='Advertiser')
            valid_bidders_only = query_bidders_budgets_spent[query_bidders_budgets_spent[
                'Bid Value'] <= query_bidders_budgets_spent['Budget']]

            if len(valid_bidders_only):
                valid_bidders_only['MSVV Bids'] = valid_bidders_only.apply(
                    lambda x: calculate_MSVV(x), axis=1)

                max_msvv_value = valid_bidders_only['MSVV Bids'].max()

                # Corresponding highest bidder
                highest_bidder = min(
                    valid_bidders_only[valid_bidders_only['MSVV Bids'] == max_msvv_value]['Advertiser'])

                # Corresponding bid value
                max_bid_value = min(
                    valid_bidders_only[valid_bidders_only['Advertiser'] == highest_bidder]['Bid Value'])

                # Reduce highest bidder's total budget
                budgets_spent.loc[budgets_spent['Advertiser']
                                  == highest_bidder, 'Budget'] -= max_bid_value

                # Increase the spent budget.
                budgets_spent.loc[budgets_spent['Advertiser']
                                  == highest_bidder, 'Spent'] += max_bid_value

                # Book keeping
                total_revenue += max_bid_value

    return round(total_revenue, 2)

# msvv(queries, original_budgets, dataset)

# Balance


def balance(queries, budgets, dataset):

    total_revenue = 0
    for query in queries:
        #         print(query)
        query_bidders = dataset[dataset['Keyword']
                                == query][['Advertiser', 'Bid Value']]

        # If there are valid bidders for this query (with valid budget)
        if (query_bidders.shape[0]):
            highest_bidder = None
            max_bid_value = -np.inf

            # Consider only those bidders who have minimum budget for the bid.
            query_bidders_budgets = query_bidders.merge(
                budgets, on='Advertiser')
            valid_bidders_only = query_bidders_budgets[query_bidders_budgets['Bid Value']
                                                       <= query_bidders_budgets['Budget']]

            if len(valid_bidders_only):
                # Get the bidder with highest unspent revenue and corresponding bid revenue
                highest_unspent = valid_bidders_only['Budget'].max()

                # Corresponding highest bidder
                highest_bidder = min(
                    valid_bidders_only[valid_bidders_only['Budget'] == highest_unspent]['Advertiser'])

                # Corresponding bid value
                max_bid_value = min(
                    valid_bidders_only[valid_bidders_only['Advertiser'] == highest_bidder]['Bid Value'])

                # Reduce highest bidder's unspent budget
                budgets.loc[budgets['Advertiser'] ==
                            highest_bidder, 'Budget'] -= max_bid_value

                # Book keeping
                total_revenue += max_bid_value

    return round(total_revenue, 2)

# balance(queries, original_budgets, dataset)

# Greedy


def greedy(queries, budgets, dataset):
    total_revenue = 0
    for query in queries:
        #         print(query)
        query_bidders = dataset[dataset['Keyword']
                                == query][['Advertiser', 'Bid Value']]

        # If there are valid bidders for this query (with valid budget)
        if (query_bidders.shape[0]):
            highest_bidder = None
            max_bid_value = -np.inf

            # Consider only those bidders who have minimum budget for the bid.
            query_bidders_budgets = query_bidders.merge(
                budgets, on='Advertiser')
            valid_bidders_only = query_bidders_budgets[query_bidders_budgets['Bid Value']
                                                       <= query_bidders_budgets['Budget']]

            if len(valid_bidders_only):
                # Get the highest bidder and corresponding bid revenue
                # First check if there are multiple people tying for the same query. Choose the one with smallest ID then
                max_bid_value = valid_bidders_only['Bid Value'].max()

                # Corresponding highest bidder
                highest_bidder = min(
                    valid_bidders_only[valid_bidders_only['Bid Value'] == max_bid_value]['Advertiser'])

                # Reduce highest bidder's total budget
                budgets.loc[budgets['Advertiser'] ==
                            highest_bidder, 'Budget'] -= max_bid_value

                # Book keeping
                total_revenue += max_bid_value
    return round(total_revenue, 2)

# greedy(queries, original_budgets, dataset)


random.seed(0)


def main():
    dataset = pd.read_csv("bidder_dataset.csv")
    with open('queries.txt') as f:
        queries = f.readlines()
    queries = [query.strip() for query in queries]

    random.shuffle(queries)

    original_budgets = dataset.groupby(['Advertiser']).first().drop(
        ['Keyword', 'Bid Value'], axis=1).reset_index()
#     dataset['Budget'] = dataset.groupby(['Advertiser'])['Budget'].transform('first')
    dataset.drop(['Budget'], axis=1, inplace=True)

    # For total revenue
    budgets = original_budgets.copy()
    total_revenue = 0

    # For competitive ratio
    opt = sum(original_budgets['Budget'])

    # Store the algorithm selected by user in algorithm
    algorithm = sys.argv[1]

    if algorithm == "greedy":
        # Get one iteration total revenue
        total_revenue = greedy(queries, budgets, dataset)
        print("Total revenue is ", total_revenue)

        alg = 0
        # Get competitive ratio
        for i in range(100):
            random.shuffle(queries)
            revenue = greedy(queries, budgets, dataset)
            alg += revenue

        alg /= 100

    elif algorithm == "msvv":
        # Get one iteration total revenue
        total_revenue = msvv(queries, budgets, dataset)

        alg = 0
        # Get competitive ratio
        for i in range(100):
            random.shuffle(queries)
            revenue = msvv(queries, budgets, dataset)
            alg += revenue

        alg /= 100

    elif algorithm == "balance":
        # Get one iteration total revenue
        total_revenue = balance(queries, budgets, dataset)

        alg = 0
        # Get competitive ratio
        for i in range(100):
            random.shuffle(queries)
            revenue = balance(queries, budgets, dataset)
            alg += revenue

        alg /= 100

    else:
        print("Please select one amongst greedy, msvv and balance")
        return

    print("Revenue for ", algorithm, "algorithm is ", total_revenue)
    print("Competitive for ", algorithm, "algorithm is ", round(alg/opt, 2))


if __name__ == "__main__":
    main()
