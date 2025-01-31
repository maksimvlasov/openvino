import numpy as np
import paddle as pdpd
from paddle.nn.functional import interpolate
from save_model import saveModel
import sys
pdpd.enable_static()


def run_and_save_model(input_x, name, feed, fetch_list, main_prog, start_prog):
    cpu = pdpd.static.cpu_places(1)
    exe = pdpd.static.Executor(cpu[0])
    exe.run(start_prog)
    outs = exe.run(
        feed={'x': input_x},
        fetch_list=fetch_list,
        program=main_prog)

    with pdpd.static.program_guard(main_prog, start_prog):
        saveModel(name, exe, feedkeys=['x'], fetchlist=fetch_list, inputs=[input_x],
                  outputs=[outs[0]], target_dir=sys.argv[1])

    return outs


def pdpd_interpolate(x, sizes=None, scale_factor=None, mode='nearest', align_corners=True,
                     align_mode=0, data_format='NCHW', name=None):
    pdpd.enable_static()
    main_program = pdpd.static.Program()
    startup_program = pdpd.static.Program()
    with pdpd.static.program_guard(main_program, startup_program):
        node_x = pdpd.static.data(name='x', shape=x.shape, dtype='float32')
        interp = interpolate(node_x, size=sizes, scale_factor=scale_factor,
                             mode=mode, align_corners=align_corners, align_mode=align_mode,
                             data_format=data_format, name=name)
        out = pdpd.static.nn.batch_norm(interp, use_global_stats=True, epsilon=0)
    outs = run_and_save_model(x, name, node_x, out, main_program, startup_program)
    return outs[0]


def resize_upsample_bilinear():
    data = np.array([[[
        [1, 2, 3, 4],
        [5, 6, 7, 8],
        [9, 10, 11, 12],
        [13, 14, 15, 16]
    ]]], dtype=np.float32)

    test_case = [{'name': 'bilinear_upsample_false_1', 'align_corners': False, 'align_mode': 1},
                 {'name': 'bilinear_upsample_false_0', 'align_corners': False, 'align_mode': 0},
                 {'name': 'bilinear_upsample_true_0', 'align_corners': True, 'align_mode': 0}]

    for test in test_case:
        pdpd_result = pdpd_interpolate(data, [64, 64], None, mode='bilinear', align_corners=test['align_corners'],
                                       align_mode=test['align_mode'], data_format='NCHW', name=test['name'])


def resize_downsample_bilinear():
    data = np.array([[[
        [1, 2, 3, 4],
        [5, 6, 7, 8],
        [9, 10, 11, 12],
        [13, 14, 15, 16]
    ]]], dtype=np.float32)
    data_28 = data.reshape([1, 1, 2, 8])
    test_case = [{'name': 'bilinear_downsample_false_1', 'align_corners': False, 'align_mode': 1},
                 {'name': 'bilinear_downsample_false_0', 'align_corners': False, 'align_mode': 0},
                 {'name': 'bilinear_downsample_true_0', 'align_corners': True, 'align_mode': 0}]

    for test in test_case:
        pdpd_result = pdpd_interpolate(data_28, [2, 4], None, mode='bilinear', align_corners=test['align_corners'],
                                       align_mode=test['align_mode'], data_format='NCHW', name=test['name'])

def resize_upsample_nearest():
    data = np.array([[[
        [1, 2, 3, 4],
        [5, 6, 7, 8],
        [9, 10, 11, 12],
        [13, 14, 15, 16]
    ]]], dtype=np.float32)

    test_case = [
        {'name': 'nearest_upsample_false_0', 'size': [64, 64], 'align_corners': False, 'align_mode': 0},
        {'name': 'nearest_upsample_false_1', 'size': [16, 64], 'align_corners': False, 'align_mode': 0}
    ]

    for test in test_case:
        pdpd_result = pdpd_interpolate(data, test['size'], None, mode='nearest', align_corners=test['align_corners'],
                                       align_mode=test['align_mode'], data_format='NCHW', name=test['name'])


def resize_downsample_nearest():
    data = np.arange(0, 4096).astype(np.float32)
    data_64 = data.reshape([1, 1, 64, 64])
    test_case = [
        {'name': 'nearest_downsample_false_0', 'size': [8, 8], 'align_corners': False, 'align_mode': 1},
        {'name': 'nearest_downsample_false_1', 'size': [4, 8], 'align_corners': False, 'align_mode': 1}
    ]

    for test in test_case:
        pdpd_result = pdpd_interpolate(data_64, test['size'], None, mode='nearest', align_corners=test['align_corners'],
                                       align_mode=test['align_mode'], data_format='NCHW', name=test['name'])


def nearest_upsample_tensor_size():
    data = np.array([[[
        [1, 2, 3, 4],
        [5, 6, 7, 8],
        [9, 10, 11, 12],
        [13, 14, 15, 16]
    ]]], dtype=np.float32)
    sizes = np.array([8, 8], dtype=np.int32)
    pdpd.enable_static()
    test_case = [{'name': 'nearest_upsample_tensor_size', 'align_corners': False, 'align_mode': 0}]
    for test in test_case:
        main_program = pdpd.static.Program()
        startup_program = pdpd.static.Program()
        with pdpd.static.program_guard(main_program, startup_program):
            node_x = pdpd.static.data(name='x', shape=data.shape, dtype='float32')
            node_sizes = pdpd.static.data(name='sizes', shape=sizes.shape, dtype='int32')
            interp = interpolate(node_x, size=node_sizes, scale_factor=None,
                                 mode='nearest', align_corners=test['align_corners'], align_mode=test['align_mode'],
                                 data_format='NCHW', name=test['name'])
            out = pdpd.static.nn.batch_norm(interp, use_global_stats=True, epsilon=0)
            cpu = pdpd.static.cpu_places(1)
            exe = pdpd.static.Executor(cpu[0])
            exe.run(startup_program)
            outs = exe.run(
                feed={'x': data, 'sizes': sizes},
                fetch_list=out,
                program=main_program)
            saveModel(test['name'], exe, feedkeys=['x', 'sizes'], fetchlist=out, inputs=[data, sizes], outputs=[outs[0]], target_dir=sys.argv[1])


def bilinear_upsample_tensor_size():
    data = np.array([[[
        [1, 2, 3, 4],
        [5, 6, 7, 8],
        [9, 10, 11, 12],
        [13, 14, 15, 16]
    ]]], dtype=np.float32)
    sizes = np.array([8, 8], dtype="int32")

    test_case = [{'name': 'bilinear_upsample_tensor_size', 'align_corners': False, 'align_mode': 1}]

    for test in test_case:
        main_program = pdpd.static.Program()
        startup_program = pdpd.static.Program()
        with pdpd.static.program_guard(main_program, startup_program):
            node_x = pdpd.static.data(name='x', shape=data.shape, dtype='float32')
            node_sizes = pdpd.static.data(name='sizes', shape=sizes.shape, dtype='int32')
            interp = interpolate(node_x, size=node_sizes, scale_factor=None,
                                 mode='bilinear', align_corners=test['align_corners'], align_mode=test['align_mode'],
                                 data_format='NCHW', name=test['name'])
            out = pdpd.static.nn.batch_norm(interp, use_global_stats=True, epsilon=0)
            cpu = pdpd.static.cpu_places(1)
            exe = pdpd.static.Executor(cpu[0])
            exe.run(startup_program)
            outs = exe.run(
                feed={'x': data, 'sizes': sizes},
                fetch_list=out,
                program=main_program)
            saveModel(test['name'], exe, feedkeys=['x', 'sizes'], fetchlist=out, inputs=[data, sizes], outputs=[outs[0]], target_dir=sys.argv[1])


def bilinear_upsample_scales():
    data = np.array([[[
        [1, 2, 3, 4],
        [5, 6, 7, 8],
        [9, 10, 11, 12],
        [13, 14, 15, 16]
    ]]], dtype=np.float32)

    test_case = [{'name': 'bilinear_upsample_scales', 'align_corners': False, 'align_mode': 1, "scales": 2},
                 {'name': 'bilinear_upsample_scales2', 'align_corners': False, 'align_mode': 1, "scales": [2, 2]}]

    for test in test_case:
        pdpd_result = pdpd_interpolate(data, None, 2, mode='bilinear', align_corners=test['align_corners'],
                                       align_mode=test['align_mode'], data_format='NCHW', name=test['name'])


if __name__ == "__main__":
    resize_downsample_bilinear()
    resize_upsample_bilinear()
    resize_downsample_nearest()
    resize_upsample_nearest()
    nearest_upsample_tensor_size()
    bilinear_upsample_tensor_size()
    bilinear_upsample_scales()
