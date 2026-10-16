"""MyChip_FP_MAC datapath bit-accurate model (rtl/IR.v, FPU.v, ACC_adder.v, ACC.v, ACC_R.v)"""


def ir_decode(b, mode):
    """8-bit input + mode -> 9-bit E5M3 (IR.v)"""
    s = (b >> 7) & 1
    if mode == 0:                       # E4M3: exp=b[6:3], mant=b[2:0]
        e4 = (b >> 3) & 0xF
        if e4 == 0:
            return s << 8
        return (s << 8) | (((e4 + 8) & 0x1F) << 3) | (b & 7)
    e5 = (b >> 2) & 0x1F                # E5M2
    if e5 == 0:
        return s << 8
    return (b << 1) & 0x1FF


def fpu(w, i, st=None):
    sw, si = (w >> 8) & 1, (i >> 8) & 1
    so = sw ^ si
    ew, ei = (w >> 3) & 0x1F, (i >> 3) & 0x1F
    mw, mi = w & 7, i & 7
    w_zero = ew == 0 and mw == 0
    i_zero = ei == 0 and mi == 0
    w_ni = ew == 31
    i_ni = ei == 31
    exp_added = ew + ei - 15
    mp = (8 | mw) * (8 | mi)            # 8-bit
    if mp & 0x80:
        en, mn = exp_added + 1, mp
    else:
        en, mn = exp_added, (mp << 1) & 0xFF
    cand = (mn >> 4) & 7
    guard = (mn >> 3) & 1
    rnd = (mn >> 2) & 1
    sticky = 1 if (mn & 3) else 0
    ru = guard & (rnd | sticky | (cand & 1))
    mr = cand + ru                      # 4-bit
    if mr & 8:
        mf, ef = 0, en + 1
    else:
        mf, ef = mr & 7, en
    if st is not None and not (w_ni or i_ni or w_zero or i_zero):
        st.add("fpu_norm%d" % ((mp >> 7) & 1))
        if ru:
            st.add("fpu_roundup")
        if mr & 8:
            st.add("fpu_round_ovf")
        if ef > 30:
            st.add("fpu_sat")
        elif ef <= 0:
            st.add("fpu_unf")
    if w_ni or i_ni:
        return (so << 8) | (31 << 3) | 1
    if w_zero or i_zero:
        return so << 8
    if ef > 30:
        return (so << 8) | (30 << 3) | 7
    if ef <= 0:
        return so << 8
    return (so << 8) | ((ef & 0x1F) << 3) | mf


def acc_add(a, b, st=None):
    sa, sb = (a >> 12) & 1, (b >> 12) & 1
    ea, eb = (a >> 7) & 0x1F, (b >> 7) & 0x1F
    ma, mb = a & 0x7F, b & 0x7F
    a_ni, b_ni = ea == 31, eb == 31
    a_z = ea == 0 and ma == 0
    b_z = eb == 0 and mb == 0
    fa, fb = 0x80 | ma, 0x80 | mb
    a_larger = (ea > eb) or (ea == eb and ma >= mb)
    el = ea if a_larger else eb
    ed = (ea - eb) if a_larger else (eb - ea)
    sl = sa if a_larger else sb
    ss = sb if a_larger else sa
    ml = fa if a_larger else fb
    msm = fb if a_larger else fa
    shifted = 0 if ed >= 8 else (msm >> ed)
    same = sl == ss
    opb = shifted if same else ((~shifted) & 0x1FF)
    raw = (ml + opb + (0 if same else 1)) & 0x1FF
    if raw & 0x100:
        en, mn = el + 1, (raw >> 1) & 0x7F
    else:
        en, mn = 0, 0
        for k in range(7, -1, -1):      # bit7 .. bit0
            if raw & (1 << k):
                sh = 7 - k
                en = el - sh
                mn = ((raw << sh) & 0x7F) if k > 0 else 0
                break
    ovf = en >= 31
    unf = en <= 0
    if st is not None and not (a_ni or b_ni or a_z or b_z):
        op = "add" if same else "sub"
        if raw & 0x100:
            st.add("add_carry")
        elif raw == 0:
            st.add("sub_exact_zero")
        else:
            st.add("%s_lz%d" % (op, 7 - raw.bit_length() + 1))
        st.add("%s_ed%d" % (op, min(ed, 8)))
        if ovf:
            st.add("add_ovf")
        if unf and raw:
            st.add("add_unf")
    if a_ni or b_ni:
        return (31 << 7) | 1
    if a_z and b_z:
        return 0
    if a_z:
        return b
    if b_z:
        return a
    if ovf:
        return (sl << 12) | (30 << 7) | 0x7F
    if unf:
        return sl << 12
    return (sl << 12) | ((en & 0x1F) << 7) | mn


def acc_r(d, mode, st=None):
    s = (d >> 12) & 1
    er = (d >> 7) & 0x1F
    m = d & 0x7F
    is_nan = er == 31 and m != 0
    is_zero = er == 0 and m == 0
    relu = s and not is_nan
    if mode:
        trunc, guard, rb, sticky, lsb = (m >> 5) & 3, (m >> 4) & 1, (m >> 3) & 1, 1 if (m & 7) else 0, (m >> 5) & 1
    else:
        trunc, guard, rb, sticky, lsb = (m >> 4) & 7, (m >> 3) & 1, (m >> 2) & 1, 1 if (m & 3) else 0, (m >> 4) & 1
    ru = guard & (rb | sticky | lsb)
    mr = trunc + ru
    carry = ((mr >> 2) & 1) if mode else ((mr >> 3) & 1)
    if st is not None and not relu and not is_nan and not is_zero:
        st.add("accr_m%d_ru%d_c%d" % (mode, ru, carry))
    if relu:
        return 0
    if mode == 0:
        e = er - 8 + carry
        if is_nan:
            return (s << 7) | 0x7F
        if e > 15:
            return (s << 7) | (15 << 3) | 6
        if is_zero or e <= 0:
            return s << 7
        return (s << 7) | ((e & 0xF) << 3) | (mr & 7)
    e = er + carry
    if is_nan:
        return (s << 7) | (31 << 2) | 1
    if e >= 31:
        return (s << 7) | (30 << 2) | 3
    if is_zero:
        return s << 7
    return (s << 7) | ((e & 0x1F) << 2) | (mr & 3)


def mac(W, I, mode_in, mode_out, st=None):
    """W, I: 8-bit raw lists (len 9). returns 8-bit result as read via MISO (low byte)."""
    acc = 0
    for k in range(9):
        p = fpu(ir_decode(W[k], mode_in), ir_decode(I[k], mode_in), st)
        acc = acc_add(acc, p << 4, st)
    return acc_r(acc, mode_out, st)


def mac_rf(Wd, Id, mode_out):
    """already-decoded 9-bit RF contents"""
    acc = 0
    for k in range(9):
        acc = acc_add(acc, fpu(Wd[k], Id[k]) << 4)
    return acc_r(acc, mode_out)
