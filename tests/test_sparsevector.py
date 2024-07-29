import unittest
from helpers.sparsevector import SparseVector
from operator import concat


class TestSparseVector(unittest.TestCase):
    """Test the Sparse Vector class"""

    def test_len(self):
        """Vector length is either length of input data or size param"""
        vec = SparseVector()
        self.assertEqual(len(vec), 0)
        data = [0, 0, 1, 0, 0, 0, 1]
        vec = SparseVector(data=data)
        self.assertEqual(len(vec), len(data))
        self.assertEqual(vec.datalen(), 2)
        vec = SparseVector(size=203)
        self.assertEqual(len(vec), 203)
        vec = SparseVector(data=data, size=203)
        self.assertEqual(len(vec), 203)
        vec = SparseVector(data=data, size=2)
        self.assertEqual(len(vec), len(data))

    def test_getitem(self):
        """"""
        data = [0, 0, 2, 0, 0, 0, 3]
        vec = SparseVector(data)
        for i, x in enumerate(data):
            self.assertEqual(vec[i], x)

    def test_key_to_idx(self):
        """Valid key is properly converted to actual index."""
        data = [0, 0, 2, 0, 0, 0, 3]
        vec = SparseVector(data)
        self.assertEqual(vec[-1], 3)
        self.assertEqual(vec[-5], 2)

    def test_invalid_key(self):
        """Accessing data with an invalid key raises an Error"""
        data = [0, 0, 2, 0, 0, 0, 3]
        vec = SparseVector(data)
        self.assertRaises(IndexError, vec.__getitem__, 543)
        self.assertRaises(IndexError, vec.__getitem__, -8)
        self.assertRaises(AttributeError, vec.__getitem__, "5")

    def test_setitem(self):
        data = [0, 0, 2, 0, 0, 0, 3]
        vec = SparseVector(data)
        self.assertEqual(sum(vec), 5)
        vec[0] = 5
        self.assertEqual(sum(vec), 10)
        vec[0] -= 3
        self.assertEqual(sum(vec), 7)

    def test_tolist(self):
        data = [0, 0, 2, 0, 0, 0, 3]
        vec = SparseVector(data)
        vec[0] = 10
        self.assertListEqual(vec.tolist(), [10, 0, 2, 0, 0, 0, 3])

    def test_insert(self):
        data = [0, 0, 2, 0, 0, 0, 3]
        vec = SparseVector(data)
        vec.insert(2, 42)
        self.assertEqual(len(vec), len(data) + 1)
        self.assertEqual(vec[2], 42)
        self.assertListEqual(vec.tolist(), [0, 0, 42, 2, 0, 0, 0, 3])

    def test_slice(self):
        data = [0, 0, 2, 0, 0, 0, 3]
        vec = SparseVector(data)
        self.assertListEqual(vec[:3].tolist(), data[:3])
        self.assertListEqual(vec[3:].tolist(), data[3:])
        self.assertListEqual(vec[1:5].tolist(), data[1:5])

    def test_addition(self):
        data1 = [0, 0, 2, 0, 0, 0, 3]
        data2 = [0, 0, 4]
        vec1 = SparseVector(data1)
        vec2 = SparseVector(data2)
        vec3 = concat(vec1, vec2)
        self.assertListEqual(vec3.tolist(), data1 + data2)

    def test_concatenation(self):
        vec = SparseVector()
        vec.append(1)
        vec.append(0)
        vec.append(0)
        vec.append(0)
        self.assertEqual(len(vec), 4)

    def test_non_zeros(self):
        data = [0, 0, 2, 0, 0, 0, 3]
        vec = SparseVector(data)
        for i, v in vec.non_zeros():
            if i == 2:
                self.assertEqual(v, 2)
            elif i == 6:
                self.assertEqual(v, 3)
            else:
                self.assertEqual(v, 0)

    def test_non_zero_indices(self):
        data = [0, 0, 0, 2, 0, 0, 3]
        vec = SparseVector(data)
        indices = [i for i in vec.non_zero_indices()]
        self.assertListEqual(indices, [3, 6])
