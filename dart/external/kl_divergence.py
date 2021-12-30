import numpy as np
from scipy.stats import entropy
from numpy.linalg import norm


# def compute_kl_divergence(s, q, alpha=0.01):
#     """
#     KL (p || q), the lower the better.
#     alpha is not really a tuning parameter, it's just there to make the
#     computation more numerically stable.
#     """
#     try:
#         assert 0.99 <= sum(s.values()) <= 1.01
#         assert 0.99 <= sum(q.values()) <= 1.01
#     except AssertionError:
#         print("Assertion Error")
#         pass
#     kl_div = 0.
#     for bin, s_score in s.items():
#         try:
#             if not s_score == 0:
#                 q_score = q.get(bin, 0.)
#                 q_score = (1 - alpha) * q_score + alpha * s_score
#                 kl_div += s_score * np.log2(s_score / q_score)
#         except ZeroDivisionError:
#             print(s_score)
#             print(q_score)
#             print()
#     return kl_div

def compute_kl_divergence(s, q, alpha=0.01):
    """
    KL (p || q), the lower the better.
    alpha is not really a tuning parameter, it's just there to make the
    computation more numerically stable.
    """
    try:
        assert 0.99 <= sum(s.values()) <= 1.01
        assert 0.99 <= sum(q.values()) <= 1.01
    except AssertionError:
        print("Assertion Error")
        pass
    kl_div = 0.
    a = []
    b = []
    for bin, s_score in s.items():
        try:
            if not s_score == 0:
                q_score = q.get(bin, 0.)
                q_score = (1 - alpha) * q_score + alpha * s_score
                # kl_div += s_score * np.log2(s_score / q_score)
                a.append(s_score)
                b.append(q_score)

        except ZeroDivisionError:
            print(s_score)
            print(q_score)
            print()
    for bin, q_score in q.items():
        if bin not in s:
            # s_score = 0.000001
            s_score = s.get(bin, 0.)
            s_score = (1 - alpha) * s_score + alpha * q_score
            a.append(s_score)
            b.append(q_score)


    kl = entropy(a, b, base=2)
    jsd = JSD(a,b)
    kl_symmetric = (kl + entropy(b, a, base=2))/2
    return [kl, jsd, kl_symmetric]


def KL(a, b):
    a = np.asarray(a, dtype=np.float)
    b = np.asarray(b, dtype=np.float)
    # return np.sum(np.where(a != 0, a * np.log2(a / b), 0))
    # return np.sum(np.where(a != 0, np.where(b != 0, a * np.log2(a / b), 0), 0))
    return np.sum(a * np.log2(a / b))


def KL_symmetric(a, b):
    return (entropy(a, b, base=2) + entropy(b, a, base=2))/2


def JSD(P, Q):
    _P = P / norm(P, ord=1)
    _Q = Q / norm(Q, ord=1)
    _M = 0.5 * (_P + _Q)
    # return 0.5 * (KL(_P, _M) + KL(_Q, _M))
    return 0.5 * (entropy(_P, _M, base=2) + entropy(_Q, _M, base=2))
