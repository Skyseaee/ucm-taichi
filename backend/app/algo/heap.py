def default_compare(x, y) -> bool:
    return x < y


class Heap:
    arr: list
    length: int

    def __init__(self, arr, compare=default_compare):
        self.arr = arr
        self.compare = compare
        self.length = len(arr)

    def heapify(self):
        i = (self.length - 2) // 2
        while i >= 0:
            self.heap_adjust(i)
            i -= 1

    def heap_adjust(self, largest):
        child = 2 * largest + 1
        while child < self.length:
            if child < self.length - 1 and self.compare(self.arr[child], self.arr[child + 1]):
                child += 1

            if self.compare(self.arr[largest], self.arr[child]):
                self.arr[child], self.arr[largest] = self.arr[largest], self.arr[child]
                largest = child
                child = 2 * largest + 1
            else:
                break

    def heap_push(self, items):
        self.length += 1
        self.arr.append(items)
        self._adjust_up(self.length - 1)

    def heap_pop(self):
        assert self.length > 0, "heap is empty."
        res = self._get_top()
        self.arr[0], self.arr[self.length - 1] = self.arr[self.length - 1], self.arr[0]
        self.arr = self.arr[:self.length - 1]
        self.length -= 1
        self.heap_adjust(0)
        return res

    def heap_empty(self) -> bool:
        return self.length == 0

    def _adjust_up(self, index):
        parent = (index - 1) >> 1
        while index > 0:
            if self.compare(self.arr[parent], self.arr[index]):
                self.arr[parent], self.arr[index] = self.arr[index], self.arr[parent]
                index = parent
                parent = (index - 1) >> 1
            else:
                break

    def _get_top(self):
        return self.arr[0]


# test
if __name__ == "__main__":
    arr = [4, 9, 12, 232, 12, 8, 12, 25, 64, 34]
    heaps = Heap(arr)
    heaps.heapify()
    print(heaps.arr)

    heaps.heap_push(23)
    print(heaps.heap_pop())
    print(heaps.heap_pop())
    print(heaps.heap_pop())
    print(heaps.heap_pop())
    print(heaps.heap_pop())
    print(heaps.heap_pop())