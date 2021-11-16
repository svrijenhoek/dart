import numpy as np


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
    for bin, s_score in s.items():
        try:
            if not s_score == 0:
                q_score = q.get(bin, 0.)
                q_score = (1 - alpha) * q_score + alpha * s_score
                kl_div += s_score * np.log2(s_score / q_score)
        except ZeroDivisionError:
            print(s_score)
            print(q_score)
            print()
    return kl_div
