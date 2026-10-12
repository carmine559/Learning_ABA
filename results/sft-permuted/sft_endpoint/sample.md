# Hand audit: 20 rows of results/sft-permuted/sft_endpoint

## t1_base_0017 (test, monotonic)

error `ok`, finish `stop`, valid True, clean True, exact True

```
NEW RULES:
t(X) :- v(X).

NEW ASSUMPTIONS:
NONE
```

## t1_base_0022 (test, defeasible)

error `ok`, finish `stop`, valid True, clean True, exact True

```
NEW RULES:
p(X) :- v(X), alpha_0(X).
c_alpha_0(X) :- t(X).

NEW ASSUMPTIONS:
alpha_0(X) defeated_by c_alpha_0(X)
```

## t1_base_0025 (test, monotonic)

error `not_a_solution`, finish `stop`, valid False, clean False, exact False

```
NEW RULES:
r(X) :- p(X), alpha_0(X).
c_alpha_0(X) :- u(X).

NEW ASSUMPTIONS:
alpha_0(X) defeated_by c_alpha_0(X)
```

## t2_noise_0008 (test, defeasible)

error `not_a_solution`, finish `stop`, valid False, clean False, exact False

```
NEW RULES:
u(X) :- s(X), alpha_0(X).
c_alpha_0(X) :- p(X).

NEW ASSUMPTIONS:
alpha_0(X) defeated_by c_alpha_0(X)
```

## t2_noise_0030 (test, defeasible)

error `ok`, finish `stop`, valid True, clean True, exact False

```
NEW RULES:
t(X) :- p(X), alpha_0(X).
c_alpha_0(X) :- u(X).

NEW ASSUMPTIONS:
alpha_0(X) defeated_by c_alpha_0(X)
```

## t2_noise_0036 (test, defeasible)

error `ok`, finish `stop`, valid True, clean True, exact True

```
NEW RULES:
p(X) :- v(X), alpha_0(X).
c_alpha_0(X) :- r(X).

NEW ASSUMPTIONS:
alpha_0(X) defeated_by c_alpha_0(X)
```

## t3_domain_0006 (test, defeasible)

error `not_a_solution`, finish `stop`, valid False, clean False, exact False

```
NEW RULES:
t(X) :- p(X), alpha_0(X).
c_alpha_0(X) :- r(X).

NEW ASSUMPTIONS:
alpha_0(X) defeated_by c_alpha_0(X)
```

## t3_domain_0015 (test, monotonic)

error `ok`, finish `stop`, valid True, clean True, exact True

```
NEW RULES:
u(X) :- v(X).

NEW ASSUMPTIONS:
NONE
```

## t3_domain_0031 (test, monotonic)

error `ok`, finish `stop`, valid True, clean True, exact True

```
NEW RULES:
q(X) :- v(X).

NEW ASSUMPTIONS:
NONE
```

## t3_domain_0034 (test, defeasible)

error `ok`, finish `stop`, valid True, clean True, exact True

```
NEW RULES:
q(X) :- v(X), alpha_0(X).
c_alpha_0(X) :- u(X).

NEW ASSUMPTIONS:
alpha_0(X) defeated_by c_alpha_0(X)
```

## t4_nested_0009 (test, monotonic)

error `ok`, finish `stop`, valid True, clean True, exact True

```
NEW RULES:
r(X) :- t(X).

NEW ASSUMPTIONS:
NONE
```

## t4_nested_0017 (test, monotonic)

error `not_a_solution`, finish `stop`, valid False, clean False, exact False

```
NEW RULES:
r(X) :- q(X).

NEW ASSUMPTIONS:
NONE
```

## t4_nested_0037 (test, monotonic)

error `ok`, finish `stop`, valid True, clean True, exact False

```
NEW RULES:
v(X) :- p(X), alpha_0(X).
c_alpha_0(X) :- q1(X), q(X).

NEW ASSUMPTIONS:
alpha_0(X) defeated_by c_alpha_0(X)
```

## t5_twopath_0002 (test, defeasible)

error `not_a_solution`, finish `stop`, valid False, clean False, exact False

```
NEW RULES:
p1(X) :- s(X).

NEW ASSUMPTIONS:
NONE
```

## t5_twopath_0024 (test, defeasible)

error `ok`, finish `stop`, valid True, clean True, exact True

```
NEW RULES:
q(X) :- p(X), alpha_0(X).
q(X) :- q1(X).
c_alpha_0(X) :- v(X).

NEW ASSUMPTIONS:
alpha_0(X) defeated_by c_alpha_0(X)
```

## t5_twopath_0037 (test, monotonic)

error `not_a_solution`, finish `stop`, valid False, clean False, exact False

```
NEW RULES:
q1(X) :- v(X).

NEW ASSUMPTIONS:
NONE
```

## t8_decoy_0040 (heldout, decoy_first)

error `ok`, finish `stop`, valid True, clean True, exact False

```
NEW RULES:
r(X) :- s(X), alpha_0(X).
c_alpha_0(X) :- p(X).

NEW ASSUMPTIONS:
alpha_0(X) defeated_by c_alpha_0(X)
```

## t8_decoy_0047 (heldout, key_first)

error `not_a_solution`, finish `stop`, valid False, clean False, exact False

```
NEW RULES:
u(X) :- p(X), alpha_0(X).
c_alpha_0(X) :- q(X).

NEW ASSUMPTIONS:
alpha_0(X) defeated_by c_alpha_0(X)
```

## t9_reuse_0001 (heldout, reuse_fails)

error `not_a_solution`, finish `stop`, valid False, clean False, exact False

```
NEW RULES:
p(X) :- r(X), alpha_0(X).
c_alpha_0(X) :- w(X).

NEW ASSUMPTIONS:
alpha_0(X) defeated_by c_alpha_0(X)
```

## t9_reuse_0042 (heldout, reuse_ok)

error `ok`, finish `stop`, valid True, clean True, exact False

```
NEW RULES:
p(X) :- v(X), alpha_0(X).
c_alpha_0(X) :- u(X).

NEW ASSUMPTIONS:
alpha_0(X) defeated_by c_alpha_0(X)
```

