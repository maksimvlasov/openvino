// Copyright (C) 2018-2021 Intel Corporation
// SPDX-License-Identifier: Apache-2.0
//

#include <gtest/gtest.h>

#include <openvino/core/except.hpp>
#include <openvino/runtime/remote_context.hpp>

using namespace ::testing;
using namespace std;

TEST(RemoteContextOVTests, throwsOnUninitializedReset) {
    ov::runtime::RemoteContext ctx;
    ASSERT_THROW(ctx.get_device_name(), ov::Exception);
}

TEST(RemoteContextOVTests, throwsOnUninitializedGetname) {
    ov::runtime::RemoteContext ctx;
    ASSERT_THROW(ctx.create_blob({}, {}), ov::Exception);
}

TEST(RemoteContextOVTests, throwsOnUninitializedGetParams) {
    ov::runtime::RemoteContext ctx;
    ASSERT_THROW(ctx.get_params(), ov::Exception);
}
