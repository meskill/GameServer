__author__ = 'meskill'
__date__ = '17.09.2014 19:58'

from random import randint, choice

PATH = ((-1, 0), (1, 0), (0, -1), (0, 1))


def add_trash(rmap, trash, trash_types):
    n, m = len(rmap), len(rmap[0])
    for _ in range(trash):
        i, j = randint(0, n - 1), randint(0, m - 1)
        rmap[i][j] = randint(-trash_types, -1)


def create_map(rmap, levels, startX, startY):
    n, m = len(rmap), len(rmap[0])
    queue = [(startX, startY, randint(1, levels))]
    while queue:
        i, j, l = queue.pop(randint(0, len(queue) - 1))
        if rmap[i][j]: continue
        l = min(max(l + randint(-1, 1), 1), levels)
        rmap[i][j] = l
        queue.extend((i + x, j + y, l) for x, y in PATH if 0 <= i + x < n and 0 <= j + y < m)


def add_objects(rmap, h, w, levels, objects_types):
    n, m = len(rmap), len(rmap[0])
    for i in range(0, n, h):
        for j in range(0, m, w):
            while True:
                k, l = randint(i, min(i + h - 1, n)), randint(j, min(j + w - 1, m))
                if rmap[k][l] > 0:
                    rmap[k][l] += (levels + 1) * randint(1, objects_types)
                    break


def generate_map(n, m, levels, trash, trash_types, h, w, objects_types=1):
    while True:
        rmap = [[0] * m for _ in range(n)]
        add_trash(rmap, trash, trash_types)
        create_map(rmap, levels, n // 2, m // 2)
        if not any(0 in x for x in rmap):
            break
    add_objects(rmap, h, w, levels, objects_types)
    for i in range(n):
        for j in range(m):
            if rmap[i][j] < 0:
                l = abs(choice([rmap[i + x][j + y] for x, y in PATH if 0 <= i + x < n and 0 <= j + y < m])) % (
                    levels + 1)
                rmap[i][j] = (rmap[i][j] + 1) * (levels + 1) - l
            elif rmap[i][j] > levels:
                if (i < h or n - i <= h) and (j < w or m - j <= w):
                    rmap[i][j] += levels + 1
    return rmap


def check(rmap):
    n, m = len(rmap), len(rmap[0])
    r = [[0] * m for _ in range(n)]

    def f(i, j):
        was = [[False] * m for _ in range(n)]
        queue = [(i, j)]
        c = 0
        while queue:
            i, j = queue.pop(0)
            if was[i][j]: continue
            c += 1
            was[i][j] = True
            k = rmap[i][j]
            for x, y in PATH:
                x, y = x + i, j + y
                if 0 <= x < n and 0 <= y < m and abs(k - rmap[x][y]) <= 1:
                    queue.append((x, y))
        return c

    for i in range(n):
        for j in range(m):
            r[i][j] = f(i, j)
    return r


def test():
    clrs = {1: '#00ff33', 2: '#00ff00', 3: '#00dd00', 4: '#00bb00', 5: '#009900', 6: '#007700', 7: '#005500',
            8: '#003300', 9: '#001100', 10: '#000000', -1: '#ff0000', -2: '#aa0000', -3: '#770000', -4: '#ff0000',
            -5: '#aa0000', -6: '#770000', -7: '#ff0000', -8: '#aa0000', -9: '#770000', -10: '#ff0000', -11: '#aa0000',
            -12: '#770000', 11: '#ffffff', 12: '#ffffff', 13: '#ffffff', 14: '#ffffff', 15: '#ffffff', 16: '#ffffff',
            17: '#ffffff', 18: '#ffffff', 19: '#ffffff', 20: '#ffffff', 21: '#ffffff', 22: '#aaaaaa', 23: '#aaaaaa',
            24: '#aaaaaa', 25: '#aaaaaa', 26: '#aaaaaa', 27: '#aaaaaa', 28: '#aaaaaa', 29: '#aaaaaa', 30: '#aaaaaa',
            31: '#aaaaaa', 32: '#aaaaaa'}
    n, m, l, t, tl, h, w, ot = 40, 40, 10, 55, 1, 5, 5, 1
    rmap = generate_map(n, m, l, t, tl, h, w, ot)
    # print('\n'.join(map(str, check(rmap))))
    # print()
    print('\n'.join(map(str, rmap)))
    # return rmap
    import tkinter

    tk = tkinter.Tk()
    width, height = 800, 800
    c = tkinter.Canvas(tk, width=width, height=height)
    w, h = width // m, height // n
    for i in range(n):
        for j in range(m):
            c.create_rectangle(j * h, i * w, j * h + h, i * w + w, fill=clrs[rmap[i][j]])
            # c.create_text(j * h + 10, i * w + 10, text=rmap[i][j], fill='red')
    c.pack()
    tkinter.mainloop()


if __name__ == '__main__':
    # test()
    from cProfile import run

    run('generate_map(400,400,10,100,5,10,10,1)')