# Copyright (C) 2018-2021 Intel Corporation
# SPDX-License-Identifier: Apache-2.0

import unittest

import numpy as np
from generator import generator, generate

from mo.front.common.partial_infer.utils import int64_array, dynamic_dimension_value, shape_array, strict_compare_tensors
from mo.utils.broadcasting import uni_directional_broadcasting, uni_directional_shape_broadcasting, \
    bi_directional_shape_broadcasting


@generator
class TestingBroadcasting(unittest.TestCase):
    @generate(*[([], [20, 30, 10], [20, 30, 10]),
                ([1], [20, 30, 10], [20, 30, 10]),
                ([1, 1, 10], [20, 30, 10], [20, 30, 10]),
                ([20, 1, 10], [20, 30, 10], [20, 30, 10]),
                ([20, 30, 10], [20, 30, 10], [20, 30, 10]),
                ([20, 30, 10], [5, 7, 20, 30, 10], [5, 7, 20, 30, 10]),
                ([1, 2], [20, 3, 10, 2], [20, 3, 10, 2]),
                ([1, 1], [1], None),
                ([5, 10], [1, 10], None),
                ])
    def test_uni_directional_broadcasting(self, input_shape, target_shape, expected_shape):
        self.assertTrue(np.array_equal(uni_directional_shape_broadcasting(input_shape, target_shape), expected_shape))

        input_value = np.array(np.random.rand(*input_shape))
        if expected_shape is not None:
            expected_value = np.broadcast_to(input_value, int64_array(target_shape))
            self.assertTrue(np.array_equal(uni_directional_broadcasting(input_value, int64_array(target_shape)),
                                           expected_value))
        else:
            with self.assertRaisesRegex(Exception, '.*cannot be uni-directionally broadcasted.*'):
                uni_directional_broadcasting(input_value, int64_array(target_shape))

    @generate(*[([], [20, 30, 10], [20, 30, 10]),
                ([1], [20, 30, 10], [20, 30, 10]),
                ([1, 1, 10], [20, 30, 10], [20, 30, 10]),
                ([20, 1, 10], [20, 30, 10], [20, 30, 10]),
                ([20, 30, 10], [20, 30, 10], [20, 30, 10]),
                ([20, 30, 10], [5, 7, 20, 30, 10], [5, 7, 20, 30, 10]),
                ([1, 2], [20, 3, 10, 2], [20, 3, 10, 2]),
                ([1, 1], [1], None),
                ([5, 10], [1, 10], None),
                ([10, 2], shape_array([dynamic_dimension_value, 3, 10, 2]),
                 shape_array([dynamic_dimension_value, 3, 10, 2])),
                (shape_array([10, dynamic_dimension_value]), shape_array([dynamic_dimension_value, 3, 10, 2]),
                 shape_array([dynamic_dimension_value, 3, 10, 2])),
                (shape_array([dynamic_dimension_value, 2]), shape_array([dynamic_dimension_value, 3, 10, 2]),
                 shape_array([dynamic_dimension_value, 3, 10, 2])),
                (shape_array([dynamic_dimension_value]), shape_array([1]), shape_array([1])),
                (shape_array([1]), shape_array([dynamic_dimension_value]), shape_array([dynamic_dimension_value])),
                (shape_array([dynamic_dimension_value]), shape_array([6]), shape_array([6])),
                (shape_array([6]), shape_array([dynamic_dimension_value]), shape_array([6])),
                ])
    def test_uni_directional_shape_broadcasting(self, input_shape, target_shape, expected_shape):
        result = uni_directional_shape_broadcasting(input_shape, target_shape)
        if expected_shape is None:
            self.assertIsNone(result)
        else:
            self.assertTrue(strict_compare_tensors(result, expected_shape))

    @generate(*[([], [20, 30, 10], [20, 30, 10]),
                ([1], [20, 30, 10], [20, 30, 10]),
                ([1, 1, 10], [20, 30, 10], [20, 30, 10]),
                ([20, 1, 10], [20, 30, 10], [20, 30, 10]),
                ([20, 30, 10], [20, 30, 10], [20, 30, 10]),
                ([20, 30, 10], [5, 7, 20, 30, 10], [5, 7, 20, 30, 10]),
                ([1, 2], [20, 3, 10, 2], [20, 3, 10, 2]),
                ([3, 2], [3], None),
                ([5, 10], [1, 20], None),
                ([10, 2], shape_array([dynamic_dimension_value, 3, 1, 2]),
                 shape_array([dynamic_dimension_value, 3, 10, 2])),
                (shape_array([10, dynamic_dimension_value]), shape_array([dynamic_dimension_value, 3, 1, 2]),
                 shape_array([dynamic_dimension_value, 3, 10, 2])),
                (shape_array([dynamic_dimension_value, 2]), shape_array([dynamic_dimension_value, 3, 10, 1]),
                 shape_array([dynamic_dimension_value, 3, 10, 2])),
                (shape_array([dynamic_dimension_value]), shape_array([1]), shape_array([dynamic_dimension_value])),
                (shape_array([1]), shape_array([dynamic_dimension_value]), shape_array([dynamic_dimension_value])),
                (shape_array([dynamic_dimension_value]), shape_array([6]), shape_array([6])),
                (shape_array([6]), shape_array([dynamic_dimension_value]), shape_array([6])),
                ])
    def test_bi_directional_shape_broadcasting(self, input_shape, target_shape, expected_shape):
        result = bi_directional_shape_broadcasting(input_shape, target_shape)
        if expected_shape is None:
            self.assertIsNone(result)
        else:
            self.assertTrue(strict_compare_tensors(result, expected_shape))
