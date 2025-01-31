// Copyright (C) 2018-2021 Intel Corporation
// SPDX-License-Identifier: Apache-2.0
//

#include "gtest/gtest.h"
#include "ngraph/ngraph.hpp"
#include "ngraph/runtime/tensor.hpp"
#include "runtime/backend.hpp"
#include "util/all_close_f.hpp"
#include "util/test_control.hpp"
#include "util/test_tools.hpp"

using namespace std;
using namespace ngraph;

static string s_manifest = "${MANIFEST}";

NGRAPH_TEST(${BACKEND_NAME}, reshape_v1) {
    auto arg = std::make_shared<op::Parameter>(element::i64, PartialShape::dynamic());
    auto pattern = make_shared<op::Parameter>(element::i64, PartialShape::dynamic(1));
    auto reshape_v1 = std::make_shared<op::v1::Reshape>(arg, pattern, false);

    auto f = std::make_shared<Function>(NodeVector{reshape_v1}, ParameterVector{arg, pattern});

    auto backend = runtime::Backend::create("${BACKEND_NAME}", true);
    auto ex = backend->compile(f);

    auto arg_data = vector<int64_t>{1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12};
    auto pattern_data = vector<int64_t>{2, 2, 3};

    auto arg_tensor = backend->create_tensor(element::i64, Shape{arg_data.size()});
    auto pattern_tensor = backend->create_tensor(element::i64, Shape{pattern_data.size()});
    copy_data(arg_tensor, arg_data);
    copy_data(pattern_tensor, pattern_data);

    auto output = backend->create_dynamic_tensor(element::i64, PartialShape::dynamic());
    ex->call_with_validate({output}, {arg_tensor, pattern_tensor});

    ASSERT_EQ(output->get_element_type(), element::i64);
    EXPECT_EQ(read_vector<int64_t>(output), vector<int64_t>({1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12}));
}
