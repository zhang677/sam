import pytest
import random
from sim.src.wr_scanner import ValsWrScan, CompressWrScan


TIMEOUT = 5000


@pytest.mark.parametrize("dim1", [4, 16, 32, 64])
def test_val_wr_scan_1d(dim1, max_val=1000, size=100, fill=0):
    in_val = [random.randint(0, max_val) for x in range(dim1)] + ['S', 'D']

    gold_val = in_val[:-2]

    wrscan = ValsWrScan(size=size, fill=fill)

    done = False
    time = 0
    out_val = []
    count = 0
    while not done and time < TIMEOUT:
        if count < len(in_val):
            wrscan.set_input(in_val[count])
            count += 1
        wrscan.update()
        print("Timestep", time)
        done = wrscan.out_done()
        time += 1

    # Assert the array stores values with the rest of the memory initialized to initial value
    assert (wrscan.get_arr() == gold_val + [fill]*(size-len(gold_val)))

    # Assert the array stores only the values
    wrscan.resize_arr(len(gold_val))
    assert (wrscan.get_arr() == gold_val)

@pytest.mark.parametrize("nnz", [1, 10, 100, 500, 1000])
def test_comp_wr_scan_1d(nnz, max_val=1000, size=1001, fill=0):
    debug = False

    in_val = [random.randint(0, max_val) for _ in range(nnz)]
    in_val = sorted(set(in_val)) + ['S', 'D']

    if debug:
        print("Crd Stream:\n", in_val)

    gold_crd = in_val[:-2]
    gold_seg = [0, len(gold_crd)]

    if debug:
        print("Gold Crd:\n", gold_crd)
        print("Gold Seg:\n", gold_seg)

    wrscan = CompressWrScan(size=size, fill=fill, debug=debug)

    done = False
    time = 0
    while not done and time < TIMEOUT:
        if len(in_val) > 0:
            wrscan.set_input(in_val.pop(0))
        wrscan.update()
        print("Timestep", time, "\t WrScan:", wrscan.out_done())
        done = wrscan.out_done()
        time += 1

    # Assert the array stores values with the rest of the memory initialized to initial value
    assert (wrscan.get_arr() == gold_crd + [fill]*(size-len(gold_crd)))
    assert (wrscan.get_seg_arr() == gold_seg + [fill]*(size-len(gold_seg)))

    # Assert the array stores only the coordinates
    wrscan.resize_arr(len(gold_crd))
    assert (wrscan.get_arr() == gold_crd)

    # Assert the array stores only the segment
    wrscan.resize_seg_arr(len(gold_seg))
    assert (wrscan.get_seg_arr() == gold_seg)


arrs_dict1 = {"in_crd": [0, 2, 3, 'S', 0, 2, 3, 'S', 'S', 'D'], "gold_crd": [0, 2, 3, 0, 2, 3],
              "gold_seg":[0, 3, 6]}


@pytest.mark.parametrize("arrs", [arrs_dict1])
def test_comp_wr_scan_direct(arrs, max_val=1000, size=1001, fill=0):
    debug = False

    in_val = arrs["in_crd"]

    if debug:
        print("Crd Stream:\n", in_val)

    gold_crd = arrs["gold_crd"]
    gold_seg = arrs["gold_seg"]

    if debug:
        print("Gold Crd:\n", gold_crd)
        print("Gold Seg:\n", gold_seg)

    wrscan = CompressWrScan(size=size, fill=fill, debug=debug)

    done = False
    time = 0
    while not done and time < TIMEOUT:
        if len(in_val) > 0:
            wrscan.set_input(in_val.pop(0))
        wrscan.update()
        print("Timestep", time, "\t WrScan:", wrscan.out_done())
        done = wrscan.out_done()
        time += 1

    # Assert the array stores values with the rest of the memory initialized to initial value
    assert (wrscan.get_arr() == gold_crd + [fill]*(size-len(gold_crd)))
    assert (wrscan.get_seg_arr() == gold_seg + [fill]*(size-len(gold_seg)))

    # Assert the array stores only the coordinates
    wrscan.resize_arr(len(gold_crd))
    assert (wrscan.get_arr() == gold_crd)

    # Assert the array stores only the segment
    wrscan.resize_seg_arr(len(gold_seg))
    assert (wrscan.get_seg_arr() == gold_seg)