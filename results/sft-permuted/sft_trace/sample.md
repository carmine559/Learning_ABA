# Hand audit: 20 rows of results/sft-permuted/sft_trace

## t1_base_0017 (test, monotonic)

error `ok`, finish `stop`, valid True, clean True, exact False

```
RoLe.
R1 t(X) :- X = a.
R1 t(X) :- X = c.
Gen.
fact t(X) :- X = a.
R4? no.
R2 candidates: [t(X) :- v(X).] [t(X) :- u(X).] [t(X) :- dom(X).]
R2? [t(X) :- v(X).] no.
R3 on [t(X) :- v(X).]
R3 reuse: none.
R2 t(X) :- v(X).
R3 t(X) :- v(X), alpha_0(X).
alpha_0(X) defeated_by c_alpha_0(X)
R1 c_alpha_0(X) :- X = b.
fact t(X) :- X = c.
R4? yes, removed.
fact c_alpha_0(X) :- X = b.
R4? no.
R2 candidates: [c_alpha_0(X) :- r(X).] [c_alpha_0(X) :- s(X).] [c_alpha_0(X) :- u(X).] [c_alpha_0(X) :- dom(X).]
R2? [c_alpha_0(X) :- r(X).] no.
R3 on [c_alpha_0(X) :- r(X).]
R3 reuse: [alpha_0(X)].
R3 reuse? [alpha_0(X)] no.
R3 failed: no reusable assumption works.
R2? [c_alpha_0(X) :- s(X).] yes.
R2 c_alpha_0(X) :- s(X).
Done.

NEW RULES:
t(X) :- v(X), alpha_0(X).
c_alpha_0(X) :- s(X).

NEW ASSUMPTIONS:
alpha_0(X) defeated_by c_alpha_0(X)
```

## t1_base_0022 (test, defeasible)

error `not_a_solution`, finish `stop`, valid False, clean False, exact False

```
RoLe.
R1 p(X) :- X = b.
R1 p(X) :- X = c.
Gen.
fact p(X) :- X = b.
R4? no.
R2 candidates: [p(X) :- v(X).] [p(X) :- r(X).] [p(X) :- dom(X).]
R2? [p(X) :- v(X).] no.
R3 on [p(X) :- v(X).]
R3 reuse: none.
R2 p(X) :- v(X).
R3 p(X) :- v(X), alpha_0(X).
alpha_0(X) defeated_by c_alpha_0(X)
R1 c_alpha_0(X) :- X = a.
fact p(X) :- X = c.
R4? yes, removed.
fact c_alpha_0(X) :- X = a.
R4? no.
R2 candidates: [c_alpha_0(X) :- v(X).] [c_alpha_0(X) :- r(X).] [c_alpha_0(X) :- t(X).] [c_alpha_0(X) :- dom(X).]
R2? [c_alpha_0(X) :- v(X).] no.
R3 on [c_alpha_0(X) :- v(X).]
R3 reuse: [alpha_0(X)].
R3 reuse? [alpha_0(X)] no.
R3 failed: no reusable assumption works.
R2? [c_alpha_0(X) :- r(X).] yes.
R2 c_alpha_0(X) :- r(X).
Done.

NEW RULES:
p(X) :- v(X), alpha_0(X).
c_alpha_0(X) :- r(X).

NEW ASSUMPTIONS:
alpha_0(X) defeated_by c_alpha_0(X)
```

## t1_base_0025 (test, monotonic)

error `ok`, finish `stop`, valid True, clean True, exact True

```
RoLe.
R1 r(X) :- X = c.
R1 r(X) :- X = a.
R1 r(X) :- X = b.
Gen.
fact r(X) :- X = c.
R4? no.
R2 candidates: [r(X) :- t(X).] [r(X) :- dom(X).]
R2? [r(X) :- t(X).] yes.
R2 r(X) :- t(X).
fact r(X) :- X = a.
R4? yes, removed.
fact r(X) :- X = b.
R4? yes, removed.
Done.

NEW RULES:
r(X) :- t(X).

NEW ASSUMPTIONS:
NONE
```

## t2_noise_0008 (test, defeasible)

error `not_a_solution`, finish `stop`, valid False, clean False, exact False

```
RoLe.
R1 u(X) :- X = c.
R1 u(X) :- X = b.
Gen.
fact u(X) :- X = c.
R4? no.
R2 candidates: [u(X) :- p(X).] [u(X) :- w(X).] [u(X) :- dom(X).]
R2? [u(X) :- p(X).] no.
R3 on [u(X) :- p(X).]
R3 reuse: none.
R2 u(X) :- p(X).
R3 u(X) :- p(X), alpha_0(X).
alpha_0(X) defeated_by c_alpha_0(X)
R1 c_alpha_0(X) :- X = a.
fact u(X) :- X = b.
R4? yes, removed.
fact c_alpha_0(X) :- X = a.
R4? no.
R2 candidates: [c_alpha_0(X) :- p(X).] [c_alpha_0(X) :- s(X).] [c_alpha_0(X) :- r(X).] [c_alpha_0(X) :- w(X).] [c_alpha_0(X) :- dom(X).]
R2? [c_alpha_0(X) :- p(X).] no.
R3 on [c_alpha_0(X) :- p(X).]
R3 reuse: [alpha_0(X)].
R3 reuse? [alpha_0(X)] no.
R3 failed: no reusable assumption works.
R2? [c_alpha_0(X) :- s(X).] yes.
R2 c_alpha_0(X) :- s(X).
Done.

NEW RULES:
u(X) :- p(X), alpha_0(X).
c_alpha_0(X) :- s(X).

NEW ASSUMPTIONS:
alpha_0(X) defeated_by c_alpha_0(X)
```

## t2_noise_0030 (test, defeasible)

error `not_a_solution`, finish `stop`, valid False, clean False, exact False

```
RoLe.
R1 t(X) :- X = b.
R1 t(X) :- X = c.
Gen.
fact t(X) :- X = b.
R4? no.
R2 candidates: [t(X) :- p(X).] [t(X) :- r(X).] [t(X) :- dom(X).]
R2? [t(X) :- p(X).] no.
R3 on [t(X) :- p(X).]
R3 reuse: none.
R2 t(X) :- p(X).
R3 t(X) :- p(X), alpha_0(X).
alpha_0(X) defeated_by c_alpha_0(X)
R1 c_alpha_0(X) :- X = a.
fact t(X) :- X = c.
R4? yes, removed.
fact c_alpha_0(X) :- X = a.
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
t(X) :- p(X), alpha_0(X).
c_alpha_0(X) :- r(X).

NEW ASSUMPTIONS:
alpha_0(X) defeated_by c_alpha_0(X)
```

## t2_noise_0036 (test, defeasible)

error `not_a_solution`, finish `stop`, valid False, clean False, exact False

```
RoLe.
R1 p(X) :- X = a.
R1 p(X) :- X = b.
R1 p(X) :- X = c.
Gen.
fact p(X) :- X = a.
R4? no.
R2 candidates: [p(X) :- v(X).] [p(X) :- t(X).] [p(X) :- p1(X).] [p(X) :- dom(X).]
R2? [p(X) :- v(X).] no.
R3 on [p(X) :- v(X).]
R3 reuse: none.
R2 p(X) :- v(X).
R3 p(X) :- v(X), alpha_0(X).
alpha_0(X) defeated_by c_alpha_0(X)
R1 c_alpha_0(X) :- X = d.
fact p(X) :- X = b.
R4? yes, removed.
fact p(X) :- X = c.
R4? yes, removed.
fact c_alpha_0(X) :- X = d.
R4? no.
R2 candidates: [c_alpha_0(X) :- r(X).] [c_alpha_0(X) :- t(X).] [c_alpha_0(X) :- p1(X).] [c_alpha_0(X) :- dom(X).]
R2? [c_alpha_0(X) :- r(X).] no.
R3 on [c_alpha_0(X) :- r(X).]
R3 reuse: [alpha_0(X)].
R3 reuse? [alpha_0(X)] no.
R3 failed: no reusable assumption works.
R2? [c_alpha_0(X) :- t(X).] yes.
R2 c_alpha_0(X) :- t(X).
Done.

NEW RULES:
p(X) :- v(X), alpha_0(X).
c_alpha_0(X) :- t(X).

NEW ASSUMPTIONS:
alpha_0(X) defeated_by c_alpha_0(X)
```

## t3_domain_0006 (test, defeasible)

error `not_a_solution`, finish `stop`, valid False, clean False, exact False

```
RoLe.
R1 t(X) :- X = a.
R1 t(X) :- X = b.
R1 t(X) :- X = e.
R1 t(X) :- X = d.
Gen.
fact t(X) :- X = a.
R4? no.
R2 candidates: [t(X) :- p(X).] [t(X) :- u(X).] [t(X) :- dom(X).]
R2? [t(X) :- p(X).] no.
R3 on [t(X) :- p(X).]
R3 reuse: none.
R2 t(X) :- p(X).
R3 t(X) :- p(X), alpha_0(X).
alpha_0(X) defeated_by c_alpha_0(X)
R1 c_alpha_0(X) :- X = c.
fact t(X) :- X = b.
R4? yes, removed.
fact t(X) :- X = e.
R4? yes, removed.
fact t(X) :- X = d.
R4? yes, removed.
fact c_alpha_0(X) :- X = c.
R4? no.
R2 candidates: [c_alpha_0(X) :- p(X).] [c_alpha_0(X) :- r(X).] [c_alpha_0(X) :- u(X).] [c_alpha_0(X) :- dom(X).]
R2? [c_alpha_0(X) :- p(X).] no.
R3 on [c_alpha_0(X) :- p(X).]
R3 reuse: [alpha_0(X)].
R3 reuse? [alpha_0(X)] no.
R3 failed: no reusable assumption works.
R2? [c_alpha_0(X) :- r(X).] yes.
R2 c_alpha_0(X) :- r(X).
Done.

NEW RULES:
t(X) :- p(X), alpha_0(X).
c_alpha_0(X) :- r(X).

NEW ASSUMPTIONS:
alpha_0(X) defeated_by c_alpha_0(X)
```

## t3_domain_0015 (test, monotonic)

error `not_a_solution`, finish `stop`, valid False, clean False, exact False

```
RoLe.
R1 u(X) :- X = d.
R1 u(X) :- X = f.
R1 u(X) :- X = e.
R1 u(X) :- X = b.
R1 u(X) :- X = c.
Gen.
fact u(X) :- X = d.
R4? no.
R2 candidates: [u(X) :- v(X).] [u(X) :- p(X).] [u(X) :- r(X).] [u(X) :- dom(X).]
R2? [u(X) :- v(X).] no.
R3 on [u(X) :- v(X).]
R3 reuse: none.
R2 u(X) :- v(X).
R3 u(X) :- v(X), alpha_0(X).
alpha_0(X) defeated_by c_alpha_0(X)
R1 c_alpha_0(X) :- X = a.
fact u(X) :- X = f.
R4? yes, removed.
fact u(X) :- X = e.
R4? yes, removed.
fact u(X) :- X = b.
R4? yes, removed.
fact u(X) :- X = c.
R4? yes, removed.
fact c_alpha_0(X) :- X = a.
R4? no.
R2 candidates: [c_alpha_0(X) :- p(X).] [c_alpha_0(X) :- r(X).] [c_alpha_0(X) :- dom(X).]
R2? [c_alpha_0(X) :- p(X).] no.
R3 on [c_alpha_0(X) :- p(X).]
R3 reuse: [alpha_0(X)].
R3 reuse? [alpha_0(X)] no.
R3 failed: no reusable assumption works.
R2? [c_alpha_0(X) :- r(X).] yes.
R2 c_alpha_0(X) :- r(X).
Done.

NEW RULES:
u(X) :- v(X), alpha_0(X).
c_alpha_0(X) :- r(X).

NEW ASSUMPTIONS:
alpha_0(X) defeated_by c_alpha_0(X)
```

## t3_domain_0031 (test, monotonic)

error `not_a_solution`, finish `stop`, valid False, clean False, exact False

```
RoLe.
R1 q(X) :- X = e.
R1 q(X) :- X = b.
R1 q(X) :- X = d.
R1 q(X) :- X = c.
Gen.
fact q(X) :- X = e.
R4? no.
R2 candidates: [q(X) :- v(X).] [q(X) :- r(X).] [q(X) :- t(X).] [q(X) :- dom(X).]
R2? [q(X) :- v(X).] no.
R3 on [q(X) :- v(X).]
R3 reuse: none.
R2 q(X) :- v(X).
R3 q(X) :- v(X), alpha_0(X).
alpha_0(X) defeated_by c_alpha_0(X)
R1 c_alpha_0(X) :- X = f.
fact q(X) :- X = b.
R4? yes, removed.
fact q(X) :- X = d.
R4? yes, removed.
fact q(X) :- X = c.
R4? yes, removed.
fact c_alpha_0(X) :- X = f.
R4? no.
R2 candidates: [c_alpha_0(X) :- u(X).] [c_alpha_0(X) :- t(X).] [c_alpha_0(X) :- dom(X).]
R2? [c_alpha_0(X) :- u(X).] no.
R3 on [c_alpha_0(X) :- u(X).]
R3 reuse: [alpha_0(X)].
R3 reuse? [alpha_0(X)] no.
R3 failed: no reusable assumption works.
R2? [c_alpha_0(X) :- t(X).] yes.
R2 c_alpha_0(X) :- t(X).
Done.

NEW RULES:
q(X) :- v(X), alpha_0(X).
c_alpha_0(X) :- t(X).

NEW ASSUMPTIONS:
alpha_0(X) defeated_by c_alpha_0(X)
```

## t3_domain_0034 (test, defeasible)

error `ok`, finish `stop`, valid True, clean True, exact True

```
RoLe.
R1 q(X) :- X = a.
R1 q(X) :- X = c.
R1 q(X) :- X = d.
R1 q(X) :- X = f.
R1 q(X) :- X = e.
Gen.
fact q(X) :- X = a.
R4? no.
R2 candidates: [q(X) :- v(X).] [q(X) :- t(X).] [q(X) :- dom(X).]
R2? [q(X) :- v(X).] no.
R3 on [q(X) :- v(X).]
R3 reuse: none.
R2 q(X) :- v(X).
R3 q(X) :- v(X), alpha_0(X).
alpha_0(X) defeated_by c_alpha_0(X)
R1 c_alpha_0(X) :- X = b.
fact q(X) :- X = c.
R4? yes, removed.
fact q(X) :- X = d.
R4? yes, removed.
fact q(X) :- X = f.
R4? yes, removed.
fact q(X) :- X = e.
R4? yes, removed.
fact c_alpha_0(X) :- X = b.
R4? no.
R2 candidates: [c_alpha_0(X) :- v(X).] [c_alpha_0(X) :- u(X).] [c_alpha_0(X) :- t(X).] [c_alpha_0(X) :- dom(X).]
R2? [c_alpha_0(X) :- v(X).] no.
R3 on [c_alpha_0(X) :- v(X).]
R3 reuse: [alpha_0(X)].
R3 reuse? [alpha_0(X)] no.
R3 failed: no reusable assumption works.
R2? [c_alpha_0(X) :- u(X).] yes.
R2 c_alpha_0(X) :- u(X).
Done.

NEW RULES:
q(X) :- v(X), alpha_0(X).
c_alpha_0(X) :- u(X).

NEW ASSUMPTIONS:
alpha_0(X) defeated_by c_alpha_0(X)
```

## t4_nested_0009 (test, monotonic)

error `ok`, finish `stop`, valid True, clean True, exact True

```
RoLe.
R1 r(X) :- X = d.
R1 r(X) :- X = e.
R1 r(X) :- X = b.
Gen.
fact r(X) :- X = d.
R4? no.
R2 candidates: [r(X) :- t(X).] [r(X) :- w(X).] [r(X) :- dom(X).]
R2? [r(X) :- t(X).] yes.
R2 r(X) :- t(X).
fact r(X) :- X = e.
R4? yes, removed.
fact r(X) :- X = b.
R4? yes, removed.
Done.

NEW RULES:
r(X) :- t(X).

NEW ASSUMPTIONS:
NONE
```

## t4_nested_0017 (test, monotonic)

error `ok`, finish `stop`, valid True, clean True, exact True

```
RoLe.
R1 r(X) :- X = c.
R1 r(X) :- X = d.
R1 r(X) :- X = e.
Gen.
fact r(X) :- X = c.
R4? no.
R2 candidates: [r(X) :- q1(X).] [r(X) :- w(X).] [r(X) :- dom(X).]
R2? [r(X) :- q1(X).] yes.
R2 r(X) :- q1(X).
fact r(X) :- X = d.
R4? yes, removed.
fact r(X) :- X = e.
R4? yes, removed.
Done.

NEW RULES:
r(X) :- q1(X).

NEW ASSUMPTIONS:
NONE
```

## t4_nested_0037 (test, monotonic)

error `not_a_solution`, finish `stop`, valid False, clean False, exact False

```
RoLe.
R1 v(X) :- X = a.
R1 v(X) :- X = d.
Gen.
fact v(X) :- X = a.
R4? no.
R2 candidates: [v(X) :- p(X).] [v(X) :- r(X).] [v(X) :- dom(X).]
R2? [v(X) :- p(X).] no.
R3 on [v(X) :- p(X).]
R3 reuse: none.
R2 v(X) :- p(X).
R3 v(X) :- p(X), alpha_0(X).
alpha_0(X) defeated_by c_alpha_0(X)
R1 c_alpha_0(X) :- X = c.
fact v(X) :- X = d.
R4? yes, removed.
fact c_alpha_0(X) :- X = c.
R4? no.
R2 candidates: [c_alpha_0(X) :- q(X).] [c_alpha_0(X) :- w(X).] [c_alpha_0(X) :- dom(X).]
R2? [c_alpha_0(X) :- q(X).] no.
R3 on [c_alpha_0(X) :- q(X).]
R3 reuse: [q(X)].
R3 reuse? [q(X)] yes.
R2 c_alpha_0(X) :- q(X).
Done.

NEW RULES:
v(X) :- p(X), alpha_0(X).
c_alpha_0(X) :- q(X).

NEW ASSUMPTIONS:
alpha_0(X) defeated_by c_alpha_0(X)
```

## t5_twopath_0002 (test, defeasible)

error `illformed`, finish `stop`, valid False, clean False, exact False

```
RoLe.
R1 p1(X) :- X = a.
R1 p1(X) :- X = c.
R1 p1(X) :- X = d.
R1 p1(X) :- X = b.
R1 p1(X) :- X = f.
Gen.
fact p1(X) :- X = a.
R4? no.
R2 candidates: [p1(X) :- s(X).] [p1(X) :- q1(X).] [p1(X) :- p(X).] [p1(X) :- r1(X).] [p1(X) :- dom(X).]
R2? [p1(X) :- s(X).] no.
R3 on [p1(X) :- s(X).]
R3 reuse: none.
R2 p1(X) :- s(X).
R3 p1(X) :- s(X), alpha_0(X).
alpha_0(X) defeated_by c_alpha_0(X)
R1 c_alpha_0(X) :- X = g.
fact p1(X) :- X = c.
R4? yes, removed.
fact p1(X) :- X = d.
R4? yes, removed.
fact p1(X) :- X = b.
R4? yes, removed.
fact p1(X) :- X = f.
R4? no.
R2 candidates: [p1(X) :- q1(X).] [p1(X) :- dom(X).]
R2? [p1(X) :- q1(X).] no.
R3 on [p1(X) :- q1(X).]
R3 reuse: none.
R2 p1(X) :- q1(X).
R3 p1(X) :- q1(X), alpha_1(X).
alpha_1(X) defeated_by c_alpha_1(X)
R1 c_alpha_1(X) :- X = g.
fact c_alpha_0(X) :- X = g.
R4? reuse: [alpha_1(X)].
R4? none.
R2? [alpha_1(X)]? no.
R3? [alpha_1(X)]? no.
R2 on [alpha_1(X)].
R2 reuse: none.
R2 alpha_1(X) :- X = g.
R3 alpha_1(X) :- t(X).
fact c_alpha_1(X) :- X = g.
R4? reuse: [alpha_1(X)].
R4? none.
R2? [alpha_1(X)]? yes.
R2 alpha_1(X) :- t(X).
Done.

NEW RULES:
p1(X) :- s(X), alpha_0(X).
p1(X) :- q1(X), alpha_1(X).
alpha_0(X) :- X = g.
alpha_1(X) :- t(X).

NEW ASSUMPTIONS:
alpha_0(X) defeated_by c_alpha_0(X)
alpha_1(X) defeated_by c_alpha_1(X)
```

## t5_twopath_0024 (test, defeasible)

error `not_a_solution`, finish `stop`, valid False, clean False, exact False

```
RoLe.
R1 q(X) :- X = g.
R1 q(X) :- X = a.
R1 q(X) :- X = d.
R1 q(X) :- X = b.
R1 q(X) :- X = c.
Gen.
fact q(X) :- X = g.
R4? no.
R2 candidates: [q(X) :- p(X).] [q(X) :- r(X).] [q(X) :- dom(X).]
R2? [q(X) :- p(X).] no.
R3 on [q(X) :- p(X).]
R3 reuse: none.
R2 q(X) :- p(X).
R3 q(X) :- p(X), alpha_0(X).
alpha_0(X) defeated_by c_alpha_0(X)
R1 c_alpha_0(X) :- X = f.
fact q(X) :- X = a.
R4? yes, removed.
fact q(X) :- X = d.
R4? yes, removed.
fact q(X) :- X = b.
R4? yes, removed.
fact q(X) :- X = c.
R4? yes, removed.
fact c_alpha_0(X) :- X = f.
R4? no.
R2 candidates: [c_alpha_0(X) :- p(X).] [c_alpha_0(X) :- v(X).] [c_alpha_0(X) :- dom(X).]
R2? [c_alpha_0(X) :- p(X).] no.
R3 on [c_alpha_0(X) :- p(X).]
R3 reuse: [alpha_0(X)].
R3 reuse? [alpha_0(X)] no.
R3 failed: no reusable assumption works.
R2? [c_alpha_0(X) :- v(X).] yes.
R2 c_alpha_0(X) :- v(X).
Done.

NEW RULES:
q(X) :- p(X), alpha_0(X).
c_alpha_0(X) :- v(X).

NEW ASSUMPTIONS:
alpha_0(X) defeated_by c_alpha_0(X)
```

## t5_twopath_0037 (test, monotonic)

error `not_a_solution`, finish `stop`, valid False, clean False, exact False

```
RoLe.
R1 q1(X) :- X = b.
R1 q1(X) :- X = c.
R1 q1(X) :- X = d.
Gen.
fact q1(X) :- X = b.
R4? no.
R2 candidates: [q1(X) :- u(X).] [q1(X) :- s(X).] [q1(X) :- dom(X).]
R2? [q1(X) :- u(X).] no.
R3 on [q1(X) :- u(X).]
R3 reuse: none.
R2 q1(X) :- u(X).
R3 q1(X) :- u(X), alpha_0(X).
alpha_0(X) defeated_by c_alpha_0(X)
R1 c_alpha_0(X) :- X = f.
fact q1(X) :- X = c.
R4? yes, removed.
fact q1(X) :- X = d.
R4? yes, removed.
fact c_alpha_0(X) :- X = f.
R4? no.
R2 candidates: [c_alpha_0(X) :- p(X).] [c_alpha_0(X) :- p1(X).] [c_alpha_0(X) :- s(X).] [c_alpha_0(X) :- dom(X).]
R2? [c_alpha_0(X) :- p(X).] no.
R3 on [c_alpha_0(X) :- p(X).]
R3 reuse: [alpha_0(X)].
R3 reuse? [alpha_0(X)] no.
R3 failed: no reusable assumption works.
R2? [c_alpha_0(X) :- p1(X).] yes.
R2 c_alpha_0(X) :- p1(X).
Done.

NEW RULES:
q1(X) :- u(X), alpha_0(X).
c_alpha_0(X) :- p1(X).

NEW ASSUMPTIONS:
alpha_0(X) defeated_by c_alpha_0(X)
```

## t8_decoy_0040 (heldout, decoy_first)

error `not_a_solution`, finish `stop`, valid False, clean False, exact False

```
RoLe.
R1 r(X) :- X = b.
R1 r(X) :- X = c.
R1 r(X) :- X = a.
Gen.
fact r(X) :- X = b.
R4? no.
R2 candidates: [r(X) :- v(X).] [r(X) :- s(X).] [r(X) :- dom(X).]
R2? [r(X) :- v(X).] no.
R3 on [r(X) :- v(X).]
R3 reuse: none.
R2 r(X) :- v(X).
R3 r(X) :- v(X), alpha_0(X).
alpha_0(X) defeated_by c_alpha_0(X)
R1 c_alpha_0(X) :- X = d.
fact r(X) :- X = c.
R4? yes, removed.
fact r(X) :- X = a.
R4? yes, removed.
fact c_alpha_0(X) :- X = d.
R4? no.
R2 candidates: [c_alpha_0(X) :- p(X).] [c_alpha_0(X) :- s(X).] [c_alpha_0(X) :- dom(X).]
R2? [c_alpha_0(X) :- p(X).] no.
R3 on [c_alpha_0(X) :- p(X).]
R3 reuse: [q(X)].
R3 reuse? [q(X)] yes.
R2 q(X).
R3 q(X) defeated_by u(X)
fact c_alpha_0(X) :- X = d.
R4? yes, removed.
Done.

NEW RULES:
r(X) :- v(X), alpha_0(X).
c_alpha_0(X) :- q(X).

NEW ASSUMPTIONS:
alpha_0(X) defeated_by c_alpha_0(X)
```

## t8_decoy_0047 (heldout, key_first)

error `not_a_solution`, finish `stop`, valid False, clean False, exact False

```
RoLe.
R1 u(X) :- X = a.
R1 u(X) :- X = b.
Gen.
fact u(X) :- X = a.
R4? no.
R2 candidates: [u(X) :- p(X).] [u(X) :- t(X).] [u(X) :- v(X).] [u(X) :- dom(X).]
R2? [u(X) :- p(X).] no.
R3 on [u(X) :- p(X).]
R3 reuse: none.
R2 u(X) :- p(X).
R3 u(X) :- p(X), alpha_0(X).
alpha_0(X) defeated_by c_alpha_0(X)
R1 c_alpha_0(X) :- X = c.
fact u(X) :- X = b.
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
u(X) :- p(X), alpha_0(X).
c_alpha_0(X) :- q(X).

NEW ASSUMPTIONS:
alpha_0(X) defeated_by c_alpha_0(X)
```

## t9_reuse_0001 (heldout, reuse_fails)

error `ok`, finish `stop`, valid True, clean True, exact True

```
RoLe.
R1 p(X) :- X = c.
R1 p(X) :- X = a.
Gen.
fact p(X) :- X = c.
R4? no.
R2 candidates: [p(X) :- r(X).] [p(X) :- dom(X).]
R2? [p(X) :- r(X).] no.
R3 on [p(X) :- r(X).]
R3 reuse: none.
R2 p(X) :- r(X).
R3 p(X) :- r(X), alpha_0(X).
alpha_0(X) defeated_by c_alpha_0(X)
R1 c_alpha_0(X) :- X = b.
fact p(X) :- X = a.
R4? yes, removed.
fact c_alpha_0(X) :- X = b.
R4? no.
R2 candidates: [c_alpha_0(X) :- q1(X).] [c_alpha_0(X) :- r(X).] [c_alpha_0(X) :- dom(X).]
R2? [c_alpha_0(X) :- q1(X).] no.
R3 on [c_alpha_0(X) :- q1(X).]
R3 reuse: none.
R2 c_alpha_0(X) :- q1(X).
Done.

NEW RULES:
p(X) :- r(X), alpha_0(X).
c_alpha_0(X) :- q1(X).

NEW ASSUMPTIONS:
alpha_0(X) defeated_by c_alpha_0(X)
```

## t9_reuse_0042 (heldout, reuse_ok)

error `not_a_solution`, finish `stop`, valid False, clean False, exact False

```
RoLe.
R1 p(X) :- X = d.
R1 p(X) :- X = b.
R1 p(X) :- X = a.
Gen.
fact p(X) :- X = d.
R4? no.
R2 candidates: [p(X) :- v(X).] [p(X) :- t(X).] [p(X) :- dom(X).]
R2? [p(X) :- v(X).] no.
R3 on [p(X) :- v(X).]
R3 reuse: none.
R2 p(X) :- v(X).
R3 p(X) :- v(X), alpha_0(X).
alpha_0(X) defeated_by c_alpha_0(X)
R1 c_alpha_0(X) :- X = c.
fact p(X) :- X = b.
R4? yes, removed.
fact p(X) :- X = a.
R4? yes, removed.
fact c_alpha_0(X) :- X = c.
R4? no.
R2 candidates: [c_alpha_0(X) :- p(X).] [c_alpha_0(X) :- t(X).] [c_alpha_0(X) :- u(X).] [c_alpha_0(X) :- dom(X).]
R2? [c_alpha_0(X) :- p(X).] no.
R3 on [c_alpha_0(X) :- p(X).]
R3 reuse: [q1(X)].
R3 reuse? [q1(X)] no.
R3 failed: no reusable assumption works.
R2? [c_alpha_0(X) :- t(X).] yes.
R2 c_alpha_0(X) :- t(X).
Done.

NEW RULES:
p(X) :- v(X), alpha_0(X).
c_alpha_0(X) :- t(X).

NEW ASSUMPTIONS:
alpha_0(X) defeated_by c_alpha_0(X)
```

