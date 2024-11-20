def m2f_e(s: str, st: list[str]) -> list[int | None]:
    return [[st.index(ch), st.insert(0, st.pop(st.index(ch)))][0] for ch in s]


def m2f_d(sq: list[int | None], st: list[str]) -> str:
    return ''.join([st[i], st.insert(0, st.pop(i))][0] for i in sq)
