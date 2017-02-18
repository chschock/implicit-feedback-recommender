import numpy as np
from scipy import sparse
from sklearn.preprocessing import normalize
from collections import OrderedDict
import random
import time

FLT = np.float32

# cosine similarity of sparse row vectors and sparse row vector
def spacos(vecs, vec):
    div1 = np.sqrt(vecs.multiply(vecs).sum(axis=1))
    div2 = np.sqrt(vec.multiply(vec).sum(axis=1)[0,0])
    return (vecs * vec.T).multiply(1./div1/div2)

# cosine similarity of sparse row vectors and sparse row vector
def spadot(vecs, vec):
    return vecs * vec.T

def build_map(entities):
    return dict(zip(entities, range(len(entities))))

class Recommender(object):

    def __init__(self, row_ics, col_ics, ratings, users, items,
            min_item_freq=5, min_user_freq=1):

        self.M = sparse.coo_matrix(
            (ratings, (row_ics, col_ics)),
            shape=(len(users), len(items)),
            dtype=np.int32).astype(FLT).tocsr()

        frequent_items = np.array(
            (self.M > 0).sum(axis=0) >= min_item_freq).ravel()
        self.M = self.M[:, frequent_items]
        self.items = [
            item for i, item in enumerate(items) if frequent_items[i]]
        # self.item_map = build_map(self.items)

        active_users = np.array(
            (self.M > 0).sum(axis=1) >= min_user_freq).ravel()
        self.M = self.M[active_users, :]
        self.users = [
            user for i, user in enumerate(users) if active_users[i]]
        self.user_map = build_map(self.users)

        # idf transform
        n_users, n_items = self.M.shape
        idf = n_items / (np.array((self.M > 0).sum(axis=0)).ravel() + 1)
        log_idf_eye = sparse.dia_matrix(
            (np.log(idf), [0]), shape=[n_items, n_items])
        self.M_w = self.M.dot(log_idf_eye)

        # # square: no consistent improvement
        # self.M_w.data = np.power(self.M_w.data, 2)

        # normalize for cosine similarity
        self.M_w = normalize(self.M_w, axis=1, norm='l2')
        self.M_0 = sparse.csr_matrix(self.M_w.shape)

        # item bias
        self.popularity_item_bias = np.array(
            normalize(self.M.sum(axis=0), axis=1, norm='l1'), dtype=FLT).ravel()
        self.zero_item_bias = np.zeros(self.M.shape[1], dtype=FLT)

    def recommend(self, user_id, n_rec, alpha=1, beta=1,
            remove_seen=True, no_mat=False, no_bias=False, return_indices=False):
        uim = self.M_0 if no_mat else self.M_w.tocsr()
        item_bias = self.zero_item_bias if no_bias else self.popularity_item_bias
        i_user = self.user_map[user_id]

        user_score = spadot(uim, uim[i_user, :])
        user_score.data = np.power(user_score.data, alpha)
        item_score = (user_score.T * uim).toarray().ravel() + beta * item_bias
        if remove_seen:
            item_score[(uim[i_user, :] > 0).tocoo().col] = 0
        item_order = np.argsort(item_score)[-1:-n_rec-1:-1]

        if return_indices:
            return OrderedDict([(i, item_score[i]) for i in item_order])
        return [(self.items[i], round(float(item_score[i]),6)) for i in item_order]


# for evaluation
def build_recommender_from_triples(user_item_rating_triples, **kwargs):
    users, items, _ = zip(*user_item_rating_triples)
    users, items = list(set(users)), list(set(items))
    print('original counts: %d users, %d items' % (len(users), len(items)))

    user_map, item_map = build_map(users), build_map(items)

    user_ics, item_ics, ratings = zip(*[
        (user_map[u], item_map[i], r)
        for u, i, r in user_item_rating_triples])

    start = time.time()
    user_ics = np.array(user_ics, dtype=np.int32)
    item_ics = np.array(item_ics, dtype=np.int32)
    ratings = np.array(ratings, dtype=np.int32)

    rmdr = Recommender(user_ics, item_ics, ratings, users, items, **kwargs)
    print('construction took %4.2f secs' % (time.time()-start))
    return rmdr

# assessment metric
def ranking_stat(rmdr, samples, seed, **kwargs):
    ranks = []
    n_users, n_items = rmdr.M.shape
    uim = rmdr.M_w
    uim_coo = uim.tocoo()
    random.seed(seed)
    for s in random.sample(range(len(uim.data)), samples):
        i_user, i_item = uim_coo.row[s], uim_coo.col[s]
        user_id = rmdr.users[i_user]

        tmp, uim[i_user, i_item] = uim[i_user, i_item], 0
        rec_items = rmdr.recommend(user_id, n_items, return_indices=True, **kwargs)
        # n_unseen_items = n_items - (uim[i_user, :] > 0).sum()
        uim[i_user, i_item] = tmp

        rank = list(rec_items.keys()).index(i_item) / n_items # n_unseen_items
        ranks.append(rank)
    return ranks
