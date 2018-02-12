from __future__ import print_function

import sys


def execute_pipeline(similarity_map, *blocks):
    for block in blocks:
        if len(block) > 1:
            fn, params = block
            similarity_map  = fn(similarity_map, *params)
        else:
            fn = block[0]
            similarity_map = fn(similarity_map)
    return similarity_map