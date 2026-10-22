# Hand audit: 20 rows of results/sft-step/s2/chained

## t1_base_0017 (test, monotonic)

error `ok`, finish `stop`, valid True, clean True, exact True

```
RoLe.
R1 v(X) :- X = a.
R1 v(X) :- X = c.
Gen.
fact v(X) :- X = a.
R4? no.
R2 candidates: [v(X) :- p(X).] [v(X) :- s(X).] [v(X) :- dom(X).]
R2? [v(X) :- p(X).] yes.
R2 v(X) :- p(X).
fact v(X) :- X = c.
R4? yes, removed.
Done.

NEW RULES:
v(X) :- p(X).

NEW ASSUMPTIONS:
NONE
```

## t1_base_0022 (test, defeasible)

error `ok`, finish `stop`, valid True, clean True, exact True

```
RoLe.
R1 v(X) :- X = b.
R1 v(X) :- X = c.
Gen.
fact v(X) :- X = b.
R4? no.
R2 candidates: [v(X) :- p(X).] [v(X) :- s(X).] [v(X) :- dom(X).]
R2? [v(X) :- p(X).] no.
R3 on [v(X) :- p(X).]
R3 reuse: none.
R2 v(X) :- p(X).
R3 v(X) :- p(X), alpha_0(X).
alpha_0(X) defeated_by c_alpha_0(X)
R1 c_alpha_0(X) :- X = a.
fact v(X) :- X = c.
R4? yes, removed.
fact c_alpha_0(X) :- X = a.
R4? no.
R2 candidates: [c_alpha_0(X) :- p(X).] [c_alpha_0(X) :- q(X).] [c_alpha_0(X) :- s(X).] [c_alpha_0(X) :- dom(X).]
R2? [c_alpha_0(X) :- p(X).] no.
R3 on [c_alpha_0(X) :- p(X).]
R3 reuse: [alpha_0(X)].
R3 reuse? [alpha_0(X)] no.
R3 failed: no reusable assumption works.
R2? [c_alpha_0(X) :- q(X).] yes.
R2 c_alpha_0(X) :- q(X).
Done.

NEW RULES:
v(X) :- p(X), alpha_0(X).
c_alpha_0(X) :- q(X).

NEW ASSUMPTIONS:
alpha_0(X) defeated_by c_alpha_0(X)
```

## t1_base_0025 (test, monotonic)

error `ok`, finish `stop`, valid True, clean True, exact True

```
RoLe.
R1 v(X) :- X = c.
R1 v(X) :- X = a.
R1 v(X) :- X = b.
Gen.
fact v(X) :- X = c.
R4? no.
R2 candidates: [v(X) :- p(X).] [v(X) :- dom(X).]
R2? [v(X) :- p(X).] yes.
R2 v(X) :- p(X).
fact v(X) :- X = a.
R4? yes, removed.
fact v(X) :- X = b.
R4? yes, removed.
Done.

NEW RULES:
v(X) :- p(X).

NEW ASSUMPTIONS:
NONE
```

## t2_noise_0008 (test, defeasible)

error `ok`, finish `stop`, valid True, clean True, exact True

```
RoLe.
R1 p1(X) :- X = c.
R1 p1(X) :- X = b.
Gen.
fact p1(X) :- X = c.
R4? no.
R2 candidates: [p1(X) :- p(X).] [p1(X) :- s(X).] [p1(X) :- dom(X).]
R2? [p1(X) :- p(X).] no.
R3 on [p1(X) :- p(X).]
R3 reuse: none.
R2 p1(X) :- p(X).
R3 p1(X) :- p(X), alpha_0(X).
alpha_0(X) defeated_by c_alpha_0(X)
R1 c_alpha_0(X) :- X = a.
fact p1(X) :- X = b.
R4? yes, removed.
fact c_alpha_0(X) :- X = a.
R4? no.
R2 candidates: [c_alpha_0(X) :- p(X).] [c_alpha_0(X) :- q(X).] [c_alpha_0(X) :- r(X).] [c_alpha_0(X) :- s(X).] [c_alpha_0(X) :- t(X).] [c_alpha_0(X) :- dom(X).]
R2? [c_alpha_0(X) :- p(X).] no.
R3 on [c_alpha_0(X) :- p(X).]
R3 reuse: [alpha_0(X)].
R3 reuse? [alpha_0(X)] no.
R3 failed: no reusable assumption works.
R2? [c_alpha_0(X) :- q(X).] yes.
R2 c_alpha_0(X) :- q(X).
Done.

NEW RULES:
p1(X) :- p(X), alpha_0(X).
c_alpha_0(X) :- q(X).

NEW ASSUMPTIONS:
alpha_0(X) defeated_by c_alpha_0(X)
```

## t2_noise_0030 (test, defeasible)

error `ok`, finish `stop`, valid True, clean True, exact True

```
RoLe.
R1 p1(X) :- X = b.
R1 p1(X) :- X = c.
Gen.
fact p1(X) :- X = b.
R4? no.
R2 candidates: [p1(X) :- p(X).] [p1(X) :- s(X).] [p1(X) :- dom(X).]
R2? [p1(X) :- p(X).] no.
R3 on [p1(X) :- p(X).]
R3 reuse: none.
R2 p1(X) :- p(X).
R3 p1(X) :- p(X), alpha_0(X).
alpha_0(X) defeated_by c_alpha_0(X)
R1 c_alpha_0(X) :- X = a.
fact p1(X) :- X = c.
R4? yes, removed.
fact c_alpha_0(X) :- X = a.
R4? no.
R2 candidates: [c_alpha_0(X) :- p(X).] [c_alpha_0(X) :- q(X).] [c_alpha_0(X) :- t(X).] [c_alpha_0(X) :- dom(X).]
R2? [c_alpha_0(X) :- p(X).] no.
R3 on [c_alpha_0(X) :- p(X).]
R3 reuse: [alpha_0(X)].
R3 reuse? [alpha_0(X)] no.
R3 failed: no reusable assumption works.
R2? [c_alpha_0(X) :- q(X).] yes.
R2 c_alpha_0(X) :- q(X).
Done.

NEW RULES:
p1(X) :- p(X), alpha_0(X).
c_alpha_0(X) :- q(X).

NEW ASSUMPTIONS:
alpha_0(X) defeated_by c_alpha_0(X)
```

## t3_domain_0006 (test, defeasible)

error `ok`, finish `stop`, valid True, clean True, exact True

```
RoLe.
R1 v(X) :- X = a.
R1 v(X) :- X = b.
R1 v(X) :- X = e.
R1 v(X) :- X = d.
Gen.
fact v(X) :- X = a.
R4? no.
R2 candidates: [v(X) :- p(X).] [v(X) :- s(X).] [v(X) :- dom(X).]
R2? [v(X) :- p(X).] no.
R3 on [v(X) :- p(X).]
R3 reuse: none.
R2 v(X) :- p(X).
R3 v(X) :- p(X), alpha_0(X).
alpha_0(X) defeated_by c_alpha_0(X)
R1 c_alpha_0(X) :- X = c.
fact v(X) :- X = b.
R4? yes, removed.
fact v(X) :- X = e.
R4? yes, removed.
fact v(X) :- X = d.
R4? yes, removed.
fact c_alpha_0(X) :- X = c.
R4? no.
R2 candidates: [c_alpha_0(X) :- p(X).] [c_alpha_0(X) :- q(X).] [c_alpha_0(X) :- dom(X).]
R2? [c_alpha_0(X) :- p(X).] no.
R3 on [c_alpha_0(X) :- p(X).]
R3 reuse: [alpha_0(X)].
R3 reuse? [alpha_0(X)] no.
R3 failed: no reusable assumption works.
R2? [c_alpha_0(X) :- q(X).] yes.
R2 c_alpha_0(X) :- q(X).
Done.

NEW RULES:
v(X) :- p(X), alpha_0(X).
c_alpha_0(X) :- q(X).

NEW ASSUMPTIONS:
alpha_0(X) defeated_by c_alpha_0(X)
```

## t3_domain_0015 (test, monotonic)

error `ok`, finish `stop`, valid True, clean True, exact True

```
RoLe.
R1 v(X) :- X = d.
R1 v(X) :- X = f.
R1 v(X) :- X = e.
R1 v(X) :- X = b.
R1 v(X) :- X = c.
Gen.
fact v(X) :- X = d.
R4? no.
R2 candidates: [v(X) :- p(X).] [v(X) :- r(X).] [v(X) :- s(X).] [v(X) :- dom(X).]
R2? [v(X) :- p(X).] yes.
R2 v(X) :- p(X).
fact v(X) :- X = f.
R4? yes, removed.
fact v(X) :- X = e.
R4? yes, removed.
fact v(X) :- X = b.
R4? yes, removed.
fact v(X) :- X = c.
R4? yes, removed.
Done.

NEW RULES:
v(X) :- p(X).

NEW ASSUMPTIONS:
NONE
```

## t3_domain_0031 (test, monotonic)

error `ok`, finish `stop`, valid True, clean True, exact True

```
RoLe.
R1 v(X) :- X = e.
R1 v(X) :- X = b.
R1 v(X) :- X = d.
R1 v(X) :- X = c.
Gen.
fact v(X) :- X = e.
R4? no.
R2 candidates: [v(X) :- p(X).] [v(X) :- r(X).] [v(X) :- s(X).] [v(X) :- dom(X).]
R2? [v(X) :- p(X).] yes.
R2 v(X) :- p(X).
fact v(X) :- X = b.
R4? yes, removed.
fact v(X) :- X = d.
R4? yes, removed.
fact v(X) :- X = c.
R4? yes, removed.
Done.

NEW RULES:
v(X) :- p(X).

NEW ASSUMPTIONS:
NONE
```

## t3_domain_0034 (test, defeasible)

error `ok`, finish `stop`, valid True, clean True, exact True

```
RoLe.
R1 v(X) :- X = a.
R1 v(X) :- X = c.
R1 v(X) :- X = d.
R1 v(X) :- X = f.
R1 v(X) :- X = e.
Gen.
fact v(X) :- X = a.
R4? no.
R2 candidates: [v(X) :- p(X).] [v(X) :- s(X).] [v(X) :- dom(X).]
R2? [v(X) :- p(X).] no.
R3 on [v(X) :- p(X).]
R3 reuse: none.
R2 v(X) :- p(X).
R3 v(X) :- p(X), alpha_0(X).
alpha_0(X) defeated_by c_alpha_0(X)
R1 c_alpha_0(X) :- X = b.
fact v(X) :- X = c.
R4? yes, removed.
fact v(X) :- X = d.
R4? yes, removed.
fact v(X) :- X = f.
R4? yes, removed.
fact v(X) :- X = e.
R4? yes, removed.
fact c_alpha_0(X) :- X = b.
R4? no.
R2 candidates: [c_alpha_0(X) :- p(X).] [c_alpha_0(X) :- q(X).] [c_alpha_0(X) :- s(X).] [c_alpha_0(X) :- dom(X).]
R2? [c_alpha_0(X) :- p(X).] no.
R3 on [c_alpha_0(X) :- p(X).]
R3 reuse: [alpha_0(X)].
R3 reuse? [alpha_0(X)] no.
R3 failed: no reusable assumption works.
R2? [c_alpha_0(X) :- q(X).] yes.
R2 c_alpha_0(X) :- q(X).
Done.

NEW RULES:
v(X) :- p(X), alpha_0(X).
c_alpha_0(X) :- q(X).

NEW ASSUMPTIONS:
alpha_0(X) defeated_by c_alpha_0(X)
```

## t4_nested_0009 (test, monotonic)

error `ok`, finish `stop`, valid True, clean True, exact True

```
RoLe.
R1 q1(X) :- X = d.
R1 q1(X) :- X = e.
R1 q1(X) :- X = b.
Gen.
fact q1(X) :- X = d.
R4? no.
R2 candidates: [q1(X) :- q(X).] [q1(X) :- t(X).] [q1(X) :- dom(X).]
R2? [q1(X) :- q(X).] yes.
R2 q1(X) :- q(X).
fact q1(X) :- X = e.
R4? yes, removed.
fact q1(X) :- X = b.
R4? yes, removed.
Done.

NEW RULES:
q1(X) :- q(X).

NEW ASSUMPTIONS:
NONE
```

## t4_nested_0017 (test, monotonic)

error `ok`, finish `stop`, valid True, clean True, exact True

```
RoLe.
R1 q1(X) :- X = c.
R1 q1(X) :- X = d.
R1 q1(X) :- X = e.
Gen.
fact q1(X) :- X = c.
R4? no.
R2 candidates: [q1(X) :- p(X).] [q1(X) :- q(X).] [q1(X) :- r(X).] [q1(X) :- dom(X).]
R2? [q1(X) :- p(X).] no.
R3 on [q1(X) :- p(X).]
R3 reuse: [v(X)].
R3 reuse? [v(X)] no.
R3 failed: no reusable assumption works.
R2? [q1(X) :- q(X).] yes.
R2 q1(X) :- q(X).
fact q1(X) :- X = d.
R4? yes, removed.
fact q1(X) :- X = e.
R4? yes, removed.
Done.

NEW RULES:
q1(X) :- q(X).

NEW ASSUMPTIONS:
NONE
```

## t4_nested_0037 (test, monotonic)

error `ok`, finish `stop`, valid True, clean True, exact True

```
RoLe.
R1 q1(X) :- X = a.
R1 q1(X) :- X = d.
Gen.
fact q1(X) :- X = a.
R4? no.
R2 candidates: [q1(X) :- p(X).] [q1(X) :- q(X).] [q1(X) :- r(X).] [q1(X) :- t(X).] [q1(X) :- dom(X).]
R2? [q1(X) :- p(X).] no.
R3 on [q1(X) :- p(X).]
R3 reuse: [v(X)].
R3 reuse? [v(X)] no.
R3 failed: no reusable assumption works.
R2? [q1(X) :- q(X).] yes.
R2 q1(X) :- q(X).
fact q1(X) :- X = d.
R4? yes, removed.
Done.

NEW RULES:
q1(X) :- q(X).

NEW ASSUMPTIONS:
NONE
```

## t5_twopath_0002 (test, defeasible)

error `ok`, finish `stop`, valid True, clean True, exact True

```
RoLe.
R1 r1(X) :- X = a.
R1 r1(X) :- X = c.
R1 r1(X) :- X = d.
R1 r1(X) :- X = b.
R1 r1(X) :- X = f.
Gen.
fact r1(X) :- X = a.
R4? no.
R2 candidates: [r1(X) :- p(X).] [r1(X) :- q(X).] [r1(X) :- t(X).] [r1(X) :- u(X).] [r1(X) :- dom(X).]
R2? [r1(X) :- p(X).] yes.
R2 r1(X) :- p(X).
fact r1(X) :- X = c.
R4? yes, removed.
fact r1(X) :- X = d.
R4? yes, removed.
fact r1(X) :- X = b.
R4? yes, removed.
fact r1(X) :- X = f.
R4? no.
R2 candidates: [r1(X) :- q(X).] [r1(X) :- dom(X).]
R2? [r1(X) :- q(X).] no.
R3 on [r1(X) :- q(X).]
R3 reuse: none.
R2 r1(X) :- q(X).
R3 r1(X) :- q(X), alpha_0(X).
alpha_0(X) defeated_by c_alpha_0(X)
R1 c_alpha_0(X) :- X = g.
fact c_alpha_0(X) :- X = g.
R4? no.
R2 candidates: [c_alpha_0(X) :- q(X).] [c_alpha_0(X) :- s(X).] [c_alpha_0(X) :- t(X).] [c_alpha_0(X) :- u(X).] [c_alpha_0(X) :- dom(X).]
R2? [c_alpha_0(X) :- q(X).] no.
R3 on [c_alpha_0(X) :- q(X).]
R3 reuse: [alpha_0(X)].
R3 reuse? [alpha_0(X)] no.
R3 failed: no reusable assumption works.
R2? [c_alpha_0(X) :- s(X).] yes.
R2 c_alpha_0(X) :- s(X).
Done.

NEW RULES:
r1(X) :- p(X).
r1(X) :- q(X), alpha_0(X).
c_alpha_0(X) :- s(X).

NEW ASSUMPTIONS:
alpha_0(X) defeated_by c_alpha_0(X)
```

## t5_twopath_0024 (test, defeasible)

error `ok`, finish `stop`, valid True, clean True, exact True

```
RoLe.
R1 r1(X) :- X = g.
R1 r1(X) :- X = a.
R1 r1(X) :- X = d.
R1 r1(X) :- X = b.
R1 r1(X) :- X = c.
Gen.
fact r1(X) :- X = g.
R4? no.
R2 candidates: [r1(X) :- q(X).] [r1(X) :- t(X).] [r1(X) :- dom(X).]
R2? [r1(X) :- q(X).] no.
R3 on [r1(X) :- q(X).]
R3 reuse: none.
R2 r1(X) :- q(X).
R3 r1(X) :- q(X), alpha_0(X).
alpha_0(X) defeated_by c_alpha_0(X)
R1 c_alpha_0(X) :- X = f.
fact r1(X) :- X = a.
R4? yes, removed.
fact r1(X) :- X = d.
R4? yes, removed.
fact r1(X) :- X = b.
R4? no.
R2 candidates: [r1(X) :- p(X).] [r1(X) :- dom(X).]
R2? [r1(X) :- p(X).] yes.
R2 r1(X) :- p(X).
fact r1(X) :- X = c.
R4? yes, removed.
fact c_alpha_0(X) :- X = f.
R4? no.
R2 candidates: [c_alpha_0(X) :- q(X).] [c_alpha_0(X) :- s(X).] [c_alpha_0(X) :- dom(X).]
R2? [c_alpha_0(X) :- q(X).] no.
R3 on [c_alpha_0(X) :- q(X).]
R3 reuse: [alpha_0(X)].
R3 reuse? [alpha_0(X)] no.
R3 failed: no reusable assumption works.
R2? [c_alpha_0(X) :- s(X).] yes.
R2 c_alpha_0(X) :- s(X).
Done.

NEW RULES:
r1(X) :- q(X), alpha_0(X).
r1(X) :- p(X).
c_alpha_0(X) :- s(X).

NEW ASSUMPTIONS:
alpha_0(X) defeated_by c_alpha_0(X)
```

## t5_twopath_0037 (test, monotonic)

error `ok`, finish `stop`, valid True, clean True, exact True

```
RoLe.
R1 r1(X) :- X = b.
R1 r1(X) :- X = c.
R1 r1(X) :- X = d.
Gen.
fact r1(X) :- X = b.
R4? no.
R2 candidates: [r1(X) :- p(X).] [r1(X) :- t(X).] [r1(X) :- dom(X).]
R2? [r1(X) :- p(X).] yes.
R2 r1(X) :- p(X).
fact r1(X) :- X = c.
R4? yes, removed.
fact r1(X) :- X = d.
R4? no.
R2 candidates: [r1(X) :- q(X).] [r1(X) :- t(X).] [r1(X) :- dom(X).]
R2? [r1(X) :- q(X).] yes.
R2 r1(X) :- q(X).
Done.

NEW RULES:
r1(X) :- p(X).
r1(X) :- q(X).

NEW ASSUMPTIONS:
NONE
```

## t8_decoy_0040 (heldout, decoy_first)

error `ok`, finish `stop`, valid True, clean True, exact True

```
RoLe.
R1 v(X) :- X = b.
R1 v(X) :- X = c.
R1 v(X) :- X = a.
Gen.
fact v(X) :- X = b.
R4? no.
R2 candidates: [v(X) :- p(X).] [v(X) :- q(X).] [v(X) :- dom(X).]
R2? [v(X) :- p(X).] yes.
R2 v(X) :- p(X).
fact v(X) :- X = c.
R4? yes, removed.
fact v(X) :- X = a.
R4? yes, removed.
Done.

NEW RULES:
v(X) :- p(X).

NEW ASSUMPTIONS:
NONE
```

## t8_decoy_0047 (heldout, key_first)

error `ok`, finish `stop`, valid True, clean True, exact True

```
RoLe.
R1 v(X) :- X = a.
R1 v(X) :- X = b.
Gen.
fact v(X) :- X = a.
R4? no.
R2 candidates: [v(X) :- p(X).] [v(X) :- q(X).] [v(X) :- s(X).] [v(X) :- dom(X).]
R2? [v(X) :- p(X).] no.
R3 on [v(X) :- p(X).]
R3 reuse: none.
R2 v(X) :- p(X).
R3 v(X) :- p(X), alpha_0(X).
alpha_0(X) defeated_by c_alpha_0(X)
R1 c_alpha_0(X) :- X = c.
fact v(X) :- X = b.
R4? yes, removed.
fact c_alpha_0(X) :- X = c.
R4? no.
R2 candidates: [c_alpha_0(X) :- p(X).] [c_alpha_0(X) :- r(X).] [c_alpha_0(X) :- s(X).] [c_alpha_0(X) :- dom(X).]
R2? [c_alpha_0(X) :- p(X).] no.
R3 on [c_alpha_0(X) :- p(X).]
R3 reuse: [alpha_0(X)].
R3 reuse? [alpha_0(X)] no.
R3 failed: no reusable assumption works.
R2? [c_alpha_0(X) :- r(X).] yes.
R2 c_alpha_0(X) :- r(X).
Done.

NEW RULES:
v(X) :- p(X), alpha_0(X).
c_alpha_0(X) :- r(X).

NEW ASSUMPTIONS:
alpha_0(X) defeated_by c_alpha_0(X)
```

## t9_reuse_0001 (heldout, reuse_fails)

error `not_a_solution`, finish `stop`, valid False, clean False, exact False

```
RoLe.
R1 r1(X) :- X = c.
R1 r1(X) :- X = a.
Gen.
fact r1(X) :- X = c.
R4? no.
R2 candidates: [r1(X) :- p(X).] [r1(X) :- q(X).] [r1(X) :- dom(X).]
R2? [r1(X) :- p(X).] no.
R3 on [r1(X) :- p(X).]
R3 reuse: [v(X)].
R3 reuse? [v(X)] no.
R3 failed: no reusable assumption works.
R2? [r1(X) :- q(X).] no.
R3 on [r1(X) :- q(X).]
R3 reuse: none.
R2 r1(X) :- q(X).
R3 r1(X) :- q(X), alpha_0(X).
alpha_0(X) defeated_by c_alpha_0(X)
R1 c_alpha_0(X) :- X = b.
fact r1(X) :- X = a.
R4? yes, removed.
fact c_alpha_0(X) :- X = b.
R4? no.
R2 candidates: [c_alpha_0(X) :- p(X).] [c_alpha_0(X) :- q(X).] [c_alpha_0(X) :- s(X).] [c_alpha_0(X) :- dom(X).]
R2? [c_alpha_0(X) :- p(X).] no.
R3 on [c_alpha_0(X) :- p(X).]
R3 reuse: [v(X)].
R3 reuse? [v(X)] yes.
R2 c_alpha_0(X) :- p(X).
R3 c_alpha_0(X) :- p(X), v(X).
Done.

NEW RULES:
r1(X) :- q(X), alpha_0(X).
c_alpha_0(X) :- p(X), v(X).

NEW ASSUMPTIONS:
alpha_0(X) defeated_by c_alpha_0(X)
```

## t9_reuse_0042 (heldout, reuse_ok)

error `not_a_solution`, finish `stop`, valid False, clean False, exact False

```
RoLe.
R1 r1(X) :- X = d.
R1 r1(X) :- X = b.
R1 r1(X) :- X = a.
Gen.
fact r1(X) :- X = d.
R4? no.
R2 candidates: [r1(X) :- p(X).] [r1(X) :- q(X).] [r1(X) :- dom(X).]
R2? [r1(X) :- p(X).] no.
R3 on [r1(X) :- p(X).]
R3 reuse: [v(X)].
R3 reuse? [v(X)] no.
R3 failed: no reusable assumption works.
R2? [r1(X) :- q(X).] no.
R3 on [r1(X) :- q(X).]
R3 reuse: none.
R2 r1(X) :- q(X).
R3 r1(X) :- q(X), alpha_0(X).
alpha_0(X) defeated_by c_alpha_0(X)
R1 c_alpha_0(X) :- X = c.
fact r1(X) :- X = b.
R4? yes, removed.
fact r1(X) :- X = a.
R4? yes, removed.
fact c_alpha_0(X) :- X = c.
R4? no.
R2 candidates: [c_alpha_0(X) :- p(X).] [c_alpha_0(X) :- q(X).] [c_alpha_0(X) :- r(X).] [c_alpha_0(X) :- s(X).] [c_alpha_0(X) :- dom(X).]
R2? [c_alpha_0(X) :- p(X).] no.
R3 on [c_alpha_0(X) :- p(X).]
R3 reuse: [v(X)].
R3 reuse? [v(X)] yes.
R2 c_alpha_0(X) :- p(X).
R3 c_alpha_0(X) :- p(X), v(X).
Done.

NEW RULES:
r1(X) :- q(X), alpha_0(X).
c_alpha_0(X) :- p(X), v(X).

NEW ASSUMPTIONS:
alpha_0(X) defeated_by c_alpha_0(X)
```

## table1_05_named (table1, named)

error `not_a_solution`, finish `stop`, valid False, clean False, exact False

```
RoLe.
R1 pacifist(X) :- X = a.
R1 pacifist(X) :- X = e.
R1 pacifist(X) :- X = c.
Gen.
fact pacifist(X) :- X = a.
R4? no.
R2 candidates: [pacifist(X) :- quaker(X).] [pacifist(X) :- republican(X).] [pacifist(X) :- person(X).] [pacifist(X) :- dom(X).]
R2? [pacifist(X) :- quaker(X).] no.
R3 on [pacifist(X) :- quaker(X).]
R3 reuse: [normal_quaker(X)].
R3 reuse? [normal_quaker(X)] no.
R3 failed: no reusable assumption works.
R2? [pacifist(X) :- republican(X).] no.
R3 on [pacifist(X) :- republican(X).]
R3 reuse: none.
R2 pacifist(X) :- republican(X).
R3 pacifist(X) :- republican(X), alpha_0(X).
alpha_0(X) defeated_by c_alpha_0(X)
R1 c_alpha_0(X) :- X = b.
fact pacifist(X) :- X = e.
R4? no.
R2 candidates: [pacifist(X) :- quaker(X).] [pacifist(X) :- dom(X).]
R2? [pacifist(X) :- quaker(X).] yes.
R2 pacifist(X) :- quaker(X).
fact pacifist(X) :- X = c.
R4? no.
R2 candidates: [pacifist(X) :- person(X).] [pacifist(X) :- dom(X).]
R2? [pacifist(X) :- person(X).] no.
R3 on [pacifist(X) :- person(X).]
R3 reuse: none.
R2 pacifist(X) :- person(X).
R3 pacifist(X) :- person(X), alpha_1(X).
alpha_1(X) defeated_by c_alpha_1(X)
R1 c_alpha_1(X) :- X = d.
fact c_alpha_0(X) :- X = b.
R4? no.
R2 candidates: [c_alpha_0(X) :- republican(X).] [c_alpha_0(X) :- person(X).] [c_alpha_0(X) :- dom(X).]
R2? [c_alpha_0(X) :- republican(X).] yes.
R2 c_alpha_0(X) :- republican(X).
fact c_alpha_1(X) :- X = d.
R4? no.
R2 candidates: [c_alpha_1(X) :- person(X).] [c_alpha_1(X) :- republican(X).] [c_alpha_1(X) :- dom(X).]
R2? [c_alpha_1(X) :- person(X).] no.
R3 on [c_alpha_1(X) :- person(X).]
R3 reuse: [alpha_1(X)].
R3 reuse? [alpha_1(X)] no.
R3 failed: no reusable assumption works.
R2? [c_alpha_1(X) :- republican(X).] yes.
R2 c_alpha_1(X) :- republican(X).
Done.

NEW RULES:
pacifist(X) :- republican(X), alpha_0(X).
pacifist(X) :- quaker(X).
pacifist(X) :- person(X), alpha_1(X).
c_alpha_0(X) :- republican(X).
c_alpha_1(X) :- republican(X).

NEW ASSUMPTIONS:
alpha_0(X) defeated_by c_alpha_0(X)
alpha_1(X) defeated_by c_alpha_1(X)
```

