import pandas as pd
import numpy as np

from sklearn.cluster import KMeans, DBSCAN
from sklearn.decomposition import PCA
from sklearn.manifold import TSNE
from sklearn import preprocessing

from statsmodels.tsa.stattools import coint

from scipy import stats
import statsmodels.api as sm
from hurst import compute_Hc  # Assuming you have a function to compute the Hurst exponent
from statsmodels.tools.tools import add_constant
from scipy.stats import skew, kurtosis


def get_pca_features(ret_df,N_PRIN_COMPONENTS =10):

    pca = PCA(n_components=N_PRIN_COMPONENTS)
    pca.fit(ret_df)

    # Extract factor loadings
    factor_loadings = pca.components_.T  # Transpose the components matrix

    # Create a DataFrame with the correct orientation
    factor_loadings_df = pd.DataFrame(factor_loadings, index=ret_df.columns, columns=[f'Factor {i+1}' for i in range(N_PRIN_COMPONENTS)])

    X = preprocessing.StandardScaler().fit_transform(pca.components_.T)

    return X



def create_clusters(X,index):
    clf = DBSCAN(eps=1, min_samples=3)

    print(clf)

    clf.fit(X)
    labels = clf.labels_
    n_clusters_ = len(set(labels)) - (1 if -1 in labels else 0)
    print("\nClusters discovered: %d" % n_clusters_)

    clustered = clf.labels_

    clustered_series = pd.Series(index=index, data=clustered.flatten())
    clustered_series = clustered_series[clustered_series != -1]

    return clustered_series



def find_cointegrated_pairs(data, significance=0.05):
    # This function is from https://www.quantopian.com/lectures/introduction-to-pairs-trading
    n = data.shape[1]
    score_matrix = np.zeros((n, n))
    pvalue_matrix = np.ones((n, n))
    keys = data.keys()
    pairs = []
    for i in range(n):
        for j in range(i+1, n):
            S1 = data[keys[i]]
            S2 = data[keys[j]]
            result = coint(S1, S2)
            score = result[0]
            pvalue = result[1]
            score_matrix[i, j] = score
            pvalue_matrix[i, j] = pvalue
            if pvalue < significance:
                pairs.append((keys[i], keys[j]))
    return score_matrix, pvalue_matrix, pairs





def get_coint_pairs(prices,clustered_series):

    valid_tickers = clustered_series.index.intersection(prices.columns)
    clustered_series = clustered_series.loc[valid_tickers]

    CLUSTER_SIZE_LIMIT = 9999
    counts = clustered_series.value_counts()
    ticker_count_reduced = counts[(counts>1) & (counts<=CLUSTER_SIZE_LIMIT)]

    cluster_dict = {}
    for i, which_clust in enumerate(ticker_count_reduced.index):
        tickers = clustered_series[clustered_series == which_clust].index
        score_matrix, pvalue_matrix, pairs = find_cointegrated_pairs(
            prices[tickers]
        )
        cluster_dict[which_clust] = {}
        cluster_dict[which_clust]['score_matrix'] = score_matrix
        cluster_dict[which_clust]['pvalue_matrix'] = pvalue_matrix
        cluster_dict[which_clust]['pairs'] = pairs

    pairs = []
    for clust in cluster_dict.keys():
        pairs.extend(cluster_dict[clust]['pairs'])

    return pairs



def add_stationary(spread_normalized):

    rolling_volatility = spread_normalized[:500].rolling(window=10).std()
    hurst_exponent = compute_Hc(spread_normalized[:500])[0]  # Hurst exponent

    skewness = skew(spread_normalized[:500])
    kurtosis_value = kurtosis(spread_normalized[:500])


    # Ensure spread_lagged starts from the second element to align with spread_diff which starts from the second element due to differencing and shifting
    spread_lagged = spread_normalized.shift(1).dropna()
    spread_diff = spread_normalized.diff().dropna()  # First difference to get spread_diff

    # Make sure indices are aligned by reindexing spread_diff to match spread_lagged
    spread_diff = spread_diff.reindex(spread_lagged.index)
    spread_diff += 1e-8

    # Now perform your regression with aligned indices
    model = sm.OLS(np.log(np.abs(spread_diff)), add_constant(spread_lagged))
    result = model.fit()
    phi = result.params[0]


    spread_normalized = spread_normalized[:500]  # Normalized spread

    features_df = pd.DataFrame({
        'spread_normalized': spread_normalized,
        'rolling_volatility': rolling_volatility[:500],
        'hurst_exponent': np.repeat(hurst_exponent, rolling_volatility.shape[0]),
    })

    # Mean Reversion Speed calculated as the absolute value of phi
    mean_reversion_speed = np.abs(phi)

    # Calculate half-life from the decay factor
    half_life = -np.log(2) / np.log(np.abs(phi))


    features_df['half_life'] = np.repeat(half_life, len(features_df))
    features_df['mean_reversion_speed'] = np.repeat(mean_reversion_speed, len(features_df))
    features_df['skewness'] = np.repeat(skewness, len(features_df))
    features_df['kurtosis'] = np.repeat(kurtosis_value, len(features_df))

    return features_df
