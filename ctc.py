# -*- coding: utf-8 -*-

import numpy as np
import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
from itertools import product
from functools import lru_cache
import tensorflow as tf

# Demonstrate the CTC loss function
l = 'apple'
T = 8
L = ''.join(sorted(list(frozenset(l))))
L_ext = L + ' '
l_ext = ' ' + ' '.join(l) + ' '

y = np.array([
    [1, 0, 0, 0, 0],
    [1, 0, 0, 0, 0],
    [0, 0, 0, 0, 1],
    [0, 0, 0, 1, 0],
    [0, 0, 0, 0, 1],
    [0, 0, 0, 1, 0],
    [0, 0, 1, 0, 0],
    [0, 1, 0, 0, 0]
], dtype=np.float64)

y = np.divide(y, y.sum(axis=1).reshape([-1, 1]))

def alpha(t, s):
    if t < 0 or s < 0:
        return 0
    if t == 0:
        if s == 0:
            return y[0, L_ext.index(' ')]
        if s == 1:
            return y[0, L_ext.index(l[0])]
        return 0

    if 2 * s + 1 < t or 2 * t + 1 < s:
        return 0

    def _alpha():
        return alpha(t-1, s) + alpha(t-1, s-1)

    p = y[t, L_ext.index(l_ext[s])]
    if l_ext[s] == ' ' or (s > 1 and l_ext[s] == l_ext[s-2]):
        return _alpha() * p

    return (_alpha() + alpha(t-1, s-2)) * p

A = np.zeros([T, len(l_ext)]).astype(np.float64)
for t, s in product(range(0, T), range(0, len(l_ext))):
    A[t, s] = alpha(t, s)

C = A.sum(axis=1)
A = np.divide(A, C.reshape([-1, 1]))

df = pd.DataFrame(np.round(A, decimals=3).T)
df['label'] = [label if label != ' ' else '--' for label in l_ext]
df.set_index('label', inplace=True)

np.log(C).sum()

# Tensorflow CTC loss
import tensorflow as tf
labels = np.array([L.index(ch) for ch in l], np.int32).reshape([1, -1])
labels = labels.repeat(5, axis=0)

outputs = [
    '-ap-ple-',
    '-apple--',
    'apple---',
    'a-p-p-e-',
    '-p-ple--'
]

if isinstance(outputs, list):  # Check if 'outputs' is a list
    outputs = np.array([[L_ext.index(ch) for ch in output] for output in [output.replace('-', ' ') for output in outputs]])

y = np.zeros([labels.shape[0], outputs.shape[1], len(L_ext)]).astype(np.float32)

for i, j in product(range(0, labels.shape[0]), range(outputs.shape[1])):
    y[i, j, outputs[i, j]] = 1

y *= 4


sequence_length = np.array([y.shape[1]], dtype=np.int32).repeat(y.shape[0])
sparse_labels = tf.sparse.from_dense(labels)

losses = tf.nn.ctc_loss(
    labels=sparse_labels,
    logits=y,
    label_length=sequence_length,
    logit_length=tf.fill([tf.shape(y)[0]], tf.shape(y)[1]),  # Set logit length
    logits_time_major=False,  # Ensure batch-first format
    blank_index=-1,  # Assumes the last index is blank
)

df = pd.DataFrame.from_dict({
    'True labels': [l] * labels.shape[0],
    'Model output': outputs,
    'CTC Loss': losses
})

df.sort_values(by='CTC Loss', inplace=True)
df.drop(columns=['CTC Loss'], inplace=True)

## Tensorflow CTC Decoding

decoded = tf.nn.ctc_beam_search_decoder(y.swapaxes(0, 1), sequence_length, beam_width=100, top_paths=1)[0][0]
decoded = tf.sparse.to_dense(decoded, default_value=L_ext.index(' '))
predicted = ['"' + ''.join([L_ext[label] for label in labels]).replace(' ', '-') + '"' for labels in decoded]
df['Predicted labels'] = predicted
decoded_sparse = tf.sparse.from_dense(tf.cast(decoded, tf.int64))
labels_sparse = tf.sparse.from_dense(tf.cast(labels, tf.int64))
distances = tf.edit_distance(decoded_sparse, labels_sparse, normalize=False).numpy()

df['Edit distance'] = distances

