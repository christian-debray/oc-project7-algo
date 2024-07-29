from collections import abc
from typing import TypeVar, Generic, SupportsIndex

T = TypeVar("T")


class SparseVector(Generic[T], abc.MutableSequence):
    """Sparse Vector is a mutable list of fixed size, containing mostly zeros"""

    def __init__(self, data: abc.Sequence = None, size: int = 0) -> None:
        super().__init__()
        self.data: dict[int, T] = dict()
        if data:
            self._import_data(data)
            self._size = max(len(data), size)
        else:
            self._size = size

    def _import_data(self, data: abc.Sequence) -> None:
        self.data = dict()
        for i, x in enumerate(data):
            if x != 0:
                self.data[i] = x
        self._size = len(data)

    def datalen(self):
        """Returns the length of non-zero data"""
        return len(self.data)

    def __len__(self):
        return self._size

    def __getitem__(self, key: int | slice) -> T | "SparseVector[T]":
        if isinstance(key, slice):
            return self._get_slice(key)
        else:
            return self.data.get(self._key_to_idx(key), 0)

    def _get_slice(self, sl: slice) -> "SparseVector[T]":
        if slice.start is None and slice.stop is None:
            vec = SparseVector(size=self._size)
            vec.data = self.data.copy()
            return vec
        start = sl.start or 0
        stop = sl.stop or self._size
        if start < 0:
            start = self._size + start
        if stop < 0:
            stop = self._size + stop
        if start < 0 or stop < 0:
            return SparseVector(size=0)
        if stop < start or start >= self._size:
            return SparseVector(size=0)
        slice_size = min(self._size, stop) - start
        vec = SparseVector(size=slice_size)
        for k, v in self.data.items():
            if k >= start and k < stop:
                vec[k - start] = v
            if k >= stop:
                break
        return vec

    def _key_to_idx(self, key: SupportsIndex) -> int:
        """Convert a key to a real index."""
        idx = key.__index__()
        if idx < 0:
            idx = self._size + idx
        if idx >= self._size or idx < 0:
            raise IndexError("Key Index out of bounds")
        else:
            return idx

    def __delitem__(self, key: SupportsIndex):
        idx = self._key_to_idx(key)
        if idx in self.data:
            del self.data[idx]

    def __setitem__(self, key: SupportsIndex, value: T):
        idx = self._key_to_idx(key)
        if value == 0 and idx in self.data:
            del self.data[idx]
        elif value != 0:
            self.data[idx] = value

    def insert(self, key: SupportsIndex, value: T):
        insert_idx = key.__index__()
        if insert_idx < 0:
            insert_idx = self.size + insert_idx
        if insert_idx < 0 or insert_idx > self._size:
            raise IndexError("Insertion index out of bounds.")
        max_key = max(self.data.keys())
        if insert_idx > max_key:
            # easy case: ni reindexing needed
            if value != 0:
                self.data[insert_idx] = value
            self._size += 1
            return
        # re-index the data dict
        new_data_map = {}
        it = iter(self.data.items())
        n = next(it, None)
        while n is not None and n[0] < insert_idx:
            new_data_map[n[0]] = n[1]
            n = next(it, None)
        new_data_map[insert_idx] = value
        while n is not None:
            new_data_map[n[0] + 1] = n[1]
            n = next(it, None)
        self.data = new_data_map
        self._size += 1

    def tolist(self) -> list[T]:
        dense = [0] * self._size
        for i, x in self.data.items():
            dense[i] = x
        return dense

    def __iadd__(self, values: abc.Iterable):
        shift = self._size
        self._size += len(values)
        if isinstance(values, SparseVector):
            for i, k in values.data.items():
                self.data[shift + i] = k
        else:
            it = iter(values)
            i = shift
            while v := next(it, None):
                if v != 0:
                    self.data[i] = v
                i += 1
        return self

    def __add__(self, other: "SparseVector") -> "SparseVector":
        """Returns a new vector as the concatenatoon of this vector and the other vector."""
        shift = self._size
        vec = SparseVector(size=len(self) + len(other))
        vec.data = self.data.copy()
        for i, k in other.data.items():
            vec[i + shift] = k
        return vec

    def copy(self) -> "SparseVector":
        vec = SparseVector(size=self._size)
        vec.data = self.data.copy()
        return vec

    def append(self, value: T) -> None:
        self._size += 1
        if value != 0:
            self.data[self._size - 1] = value

    def __contains__(self, value: T) -> bool:
        if value != 0:
            return value in self.data.values()
        else:
            return len(self.data) != self._size

    def non_zeros(self):
        return self.data.items()

    def non_zero_indices(self):
        return self.data.keys()

    def count_non_zeros(self):
        return len(self.data)
