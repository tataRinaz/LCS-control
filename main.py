import lcs


def main():
    system = lcs.LCS(32, [0.4, 0.2, 0.1, 0.1])
    res = system.process()
    print(res)


if __name__ == '__main__':
    main()
