import lcs


def main():
    system = lcs.LCS(5, [0.4, 0.2, 0.1, 0.1])
    res, time = system.process()
    print(res)
    print(time)


if __name__ == '__main__':
    main()
