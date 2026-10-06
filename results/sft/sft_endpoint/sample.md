# Hand audit: 20 rows of results/sft/sft_endpoint

## t1_base_0017 (test, monotonic)

error `ok`, finish `stop`, valid True, clean True, exact True

```
NEW RULES:
v(X) :- p(X).

NEW ASSUMPTIONS:
NONE
```

## t1_base_0022 (test, defeasible)

error `ok`, finish `stop`, valid True, clean True, exact True

```
NEW RULES:
v(X) :- p(X), alpha_0(X).
c_alpha_0(X) :- q(X).

NEW ASSUMPTIONS:
alpha_0(X) defeated_by c_alpha_0(X)
```

## t1_base_0025 (test, monotonic)

error `ok`, finish `stop`, valid True, clean True, exact True

```
NEW RULES:
v(X) :- p(X).

NEW ASSUMPTIONS:
NONE
```

## t2_noise_0008 (test, defeasible)

error `ok`, finish `stop`, valid True, clean True, exact True

```
NEW RULES:
p1(X) :- p(X), alpha_0(X).
c_alpha_0(X) :- q(X).

NEW ASSUMPTIONS:
alpha_0(X) defeated_by c_alpha_0(X)
```

## t2_noise_0030 (test, defeasible)

error `ok`, finish `stop`, valid True, clean True, exact True

```
NEW RULES:
p1(X) :- p(X), alpha_0(X).
c_alpha_0(X) :- q(X).

NEW ASSUMPTIONS:
alpha_0(X) defeated_by c_alpha_0(X)
```

## t3_domain_0006 (test, defeasible)

error `ok`, finish `stop`, valid True, clean True, exact True

```
NEW RULES:
v(X) :- p(X), alpha_0(X).
c_alpha_0(X) :- q(X).

NEW ASSUMPTIONS:
alpha_0(X) defeated_by c_alpha_0(X)
```

## t3_domain_0015 (test, monotonic)

error `ok`, finish `stop`, valid True, clean True, exact True

```
NEW RULES:
v(X) :- p(X).

NEW ASSUMPTIONS:
NONE
```

## t3_domain_0031 (test, monotonic)

error `ok`, finish `stop`, valid True, clean True, exact True

```
NEW RULES:
v(X) :- p(X).

NEW ASSUMPTIONS:
NONE
```

## t3_domain_0034 (test, defeasible)

error `ok`, finish `stop`, valid True, clean True, exact True

```
NEW RULES:
v(X) :- p(X), alpha_0(X).
c_alpha_0(X) :- q(X).

NEW ASSUMPTIONS:
alpha_0(X) defeated_by c_alpha_0(X)
```

## t4_nested_0009 (test, monotonic)

error `ok`, finish `stop`, valid True, clean True, exact True

```
NEW RULES:
q1(X) :- q(X).

NEW ASSUMPTIONS:
NONE
```

## t4_nested_0017 (test, monotonic)

error `ok`, finish `stop`, valid True, clean True, exact True

```
NEW RULES:
q1(X) :- q(X).

NEW ASSUMPTIONS:
NONE
```

## t4_nested_0037 (test, monotonic)

error `ok`, finish `stop`, valid True, clean True, exact True

```
NEW RULES:
q1(X) :- q(X).

NEW ASSUMPTIONS:
NONE
```

## t5_twopath_0002 (test, defeasible)

error `ok`, finish `stop`, valid True, clean True, exact True

```
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
NEW RULES:
r1(X) :- p(X).
r1(X) :- q(X).

NEW ASSUMPTIONS:
NONE
```

## t8_decoy_0040 (heldout, decoy_first)

error `ok`, finish `stop`, valid True, clean True, exact True

```
NEW RULES:
v(X) :- p(X).

NEW ASSUMPTIONS:
NONE
```

## t8_decoy_0047 (heldout, key_first)

error `not_a_solution`, finish `stop`, valid False, clean False, exact False

```
NEW RULES:
v(X) :- p(X), alpha_0(X).
c_alpha_0(X) :- q(X).

NEW ASSUMPTIONS:
alpha_0(X) defeated_by c_alpha_0(X)
```

## t9_reuse_0001 (heldout, reuse_fails)

error `not_a_solution`, finish `stop`, valid False, clean False, exact False

```
NEW RULES:
r1(X) :- q(X), alpha_0(X).
r1(X) :- p(X), alpha_1(X).
c_alpha_0(X) :- s(X).
c_alpha_1(X) :- r(X).

NEW ASSUMPTIONS:
alpha_0(X) defeated_by c_alpha_0(X)
alpha_1(X) defeated_by c_alpha_1(X)
```

## t9_reuse_0042 (heldout, reuse_ok)

error `ok`, finish `stop`, valid True, clean True, exact False

```
NEW RULES:
r1(X) :- q(X), alpha_0(X).
r1(X) :- p(X), alpha_1(X).
c_alpha_0(X) :- s(X).
c_alpha_1(X) :- r(X).

NEW ASSUMPTIONS:
alpha_0(X) defeated_by c_alpha_0(X)
alpha_1(X) defeated_by c_alpha_1(X)
```

## table1_05_named (table1, named)

error `not_a_solution`, finish `stop`, valid False, clean False, exact False

```
NEW RULES:
pacifist(X) :- quaker(X), alpha_0(X).
c_alpha_0(X) :- normal_quaker(X).

NEW ASSUMPTIONS:
alpha_0(X) defeated_by c_alpha_0(X)
```

