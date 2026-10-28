# Hand audit: 5 rows per mode

## direct: nixon_diamond_anon #0

error `not_a_solution`, finish `stop`, valid False, clean False, exact False, agreement None

The algorithm's answer:

```
NEW RULES:
v(X) :- q(X).
p1(X) :- r(X), alpha_0(X).
c_alpha_0(X) :- p(X), w(X).

NEW ASSUMPTIONS:
alpha_0(X) defeated_by c_alpha_0(X)
```

The model's output:

```
NEW RULES:
NONE

NEW ASSUMPTIONS:
NONE
```

## direct: t1_mono_0000_anon #0

error `not_a_solution`, finish `stop`, valid False, clean False, exact False, agreement 0.0

The algorithm's answer:

```
NEW RULES:
v(X) :- p(X).

NEW ASSUMPTIONS:
NONE
```

The model's output:

```
NEW RULES:
NONE

NEW ASSUMPTIONS:
u(v) defeated_by s(v)
```

## direct: t4_domain_0000_anon #0

error `not_a_solution`, finish `stop`, valid False, clean False, exact False, agreement 0.0

The algorithm's answer:

```
NEW RULES:
v(X) :- p(X), alpha_0(X).
c_alpha_0(X) :- q(X).

NEW ASSUMPTIONS:
alpha_0(X) defeated_by c_alpha_0(X)
```

The model's output:

```
NEW RULES:
NONE

NEW ASSUMPTIONS:
u(b) defeated_by t(b)
u(g) defeated_by t(g)
u(e) defeated_by t(e)
u(f) defeated_by t(f)
```

## direct: t5_twopath_0000_anon #1

error `not_a_solution`, finish `stop`, valid False, clean False, exact False, agreement None

The algorithm's answer:

```
NEW RULES:
p1(X) :- q(X), alpha_0(X).
p1(X) :- p(X), alpha_1(X).
c_alpha_0(X) :- s(X).
c_alpha_1(X) :- r(X).

NEW ASSUMPTIONS:
alpha_0(X) defeated_by c_alpha_0(X)
alpha_1(X) defeated_by c_alpha_1(X)
```

The model's output:

```
NEW RULES:
NONE

NEW ASSUMPTIONS:
NONE
```

## direct: tax_law_anon #0

error `illformed`, finish `stop`, valid False, clean False, exact False, agreement None

The algorithm's answer:

```
NEW RULES:
u(X) :- p(X), alpha_0(X).
u(X) :- q(X).
c_alpha_0(X) :- dom(X), alpha_1(X).
c_alpha_1(X) :- p(X), alpha_0(X).

NEW ASSUMPTIONS:
alpha_0(X) defeated_by c_alpha_0(X)
alpha_1(X) defeated_by c_alpha_1(X)
```

The model's output:

```
NEW RULES:
NONE

NEW ASSUMPTIONS:
t(a) defeated_by s(a)
t(c) defeated_by s(c)
```

## cot: t1_mono_0000_anon #0

error `not_a_solution`, finish `stop`, valid False, clean False, exact False, agreement 0.0

The algorithm's answer:

```
NEW RULES:
v(X) :- p(X).

NEW ASSUMPTIONS:
NONE
```

The model's output:

```
NEW RULES:
NONE

NEW ASSUMPTIONS:
u(X) defeated_by s(X)
```

## cot: t1_mono_0000_anon #1

error `not_a_solution`, finish `stop`, valid False, clean False, exact False, agreement 0.0

The algorithm's answer:

```
NEW RULES:
v(X) :- p(X).

NEW ASSUMPTIONS:
NONE
```

The model's output:

```
NEW RULES:
NONE

NEW ASSUMPTIONS:
u(X) defeated_by s(X)
```

## cot: t4_domain_0000_anon #0

error `not_a_solution`, finish `stop`, valid False, clean False, exact False, agreement 0.0

The algorithm's answer:

```
NEW RULES:
v(X) :- p(X), alpha_0(X).
c_alpha_0(X) :- q(X).

NEW ASSUMPTIONS:
alpha_0(X) defeated_by c_alpha_0(X)
```

The model's output:

```
NEW RULES:
NONE

NEW ASSUMPTIONS:
u(v) defeated_by t(v)
```

## cot: t5_twopath_0000_anon #1

error `not_a_solution`, finish `stop`, valid False, clean False, exact False, agreement None

The algorithm's answer:

```
NEW RULES:
p1(X) :- q(X), alpha_0(X).
p1(X) :- p(X), alpha_1(X).
c_alpha_0(X) :- s(X).
c_alpha_1(X) :- r(X).

NEW ASSUMPTIONS:
alpha_0(X) defeated_by c_alpha_0(X)
alpha_1(X) defeated_by c_alpha_1(X)
```

The model's output:

```
NEW RULES:
NONE

NEW ASSUMPTIONS:
p1(X) defeated_by q(X)
```

## cot: tax_law_anon #0

error `ok`, finish `stop`, valid True, clean True, exact False, agreement None

The algorithm's answer:

```
NEW RULES:
u(X) :- p(X), alpha_0(X).
u(X) :- q(X).
c_alpha_0(X) :- dom(X), alpha_1(X).
c_alpha_1(X) :- p(X), alpha_0(X).

NEW ASSUMPTIONS:
alpha_0(X) defeated_by c_alpha_0(X)
alpha_1(X) defeated_by c_alpha_1(X)
```

The model's output:

```
NEW RULES:
NONE

NEW ASSUMPTIONS:
u(a) defeated_by t(a)
u(c) defeated_by t(c)
```

## guided: flies_anon #0

error `not_a_solution`, finish `stop`, valid False, clean False, exact False, agreement None

The algorithm's answer:

```
NEW RULES:
t(X) :- p(X), alpha_0(X).
c_alpha_0(X) :- q(X).

NEW ASSUMPTIONS:
alpha_0(X) defeated_by c_alpha_0(X)
```

The model's output:

```
NEW RULES:
NONE

NEW ASSUMPTIONS:
r(X) defeated_by s(X)
```

## guided: flies_anon #1

error `not_a_solution`, finish `stop`, valid False, clean False, exact False, agreement None

The algorithm's answer:

```
NEW RULES:
t(X) :- p(X), alpha_0(X).
c_alpha_0(X) :- q(X).

NEW ASSUMPTIONS:
alpha_0(X) defeated_by c_alpha_0(X)
```

The model's output:

```
NEW RULES:
NONE

NEW ASSUMPTIONS:
t(defeated_by s)
```

## guided: t2_defeas_0000_anon #0

error `parse_error`, finish `stop`, valid False, clean False, exact False, agreement None

The algorithm's answer:

```
NEW RULES:
v(X) :- p(X), alpha_0(X).
c_alpha_0(X) :- q(X).

NEW ASSUMPTIONS:
alpha_0(X) defeated_by c_alpha_0(X)
```

The model's output:

```
NONE
```

## guided: t2_defeas_0000_anon #1

error `not_a_solution`, finish `stop`, valid False, clean False, exact False, agreement None

The algorithm's answer:

```
NEW RULES:
v(X) :- p(X), alpha_0(X).
c_alpha_0(X) :- q(X).

NEW ASSUMPTIONS:
alpha_0(X) defeated_by c_alpha_0(X)
```

The model's output:

```
NEW RULES:
NONE

NEW ASSUMPTIONS:
u(v) defeated_by t(v)
```

## guided: t3_noise_0000_anon #1

error `not_a_solution`, finish `stop`, valid False, clean False, exact False, agreement 0.0

The algorithm's answer:

```
NEW RULES:
p1(X) :- p(X), alpha_0(X).
c_alpha_0(X) :- q(X).

NEW ASSUMPTIONS:
alpha_0(X) defeated_by c_alpha_0(X)
```

The model's output:

```
NEW RULES:
NONE

NEW ASSUMPTIONS:
w(v) defeated_by v(v)
```

## algorithm: flies_anon #0

error `not_a_solution`, finish `stop`, valid False, clean False, exact False, agreement None

The algorithm's answer:

```
NEW RULES:
t(X) :- p(X), alpha_0(X).
c_alpha_0(X) :- q(X).

NEW ASSUMPTIONS:
alpha_0(X) defeated_by c_alpha_0(X)
```

The model's output:

```
NEW RULES:
NONE

NEW ASSUMPTIONS:
r(X) defeated_by s(X)
```

## algorithm: nixon_diamond_anon #1

error `not_a_solution`, finish `stop`, valid False, clean False, exact False, agreement None

The algorithm's answer:

```
NEW RULES:
v(X) :- q(X).
p1(X) :- r(X), alpha_0(X).
c_alpha_0(X) :- p(X), w(X).

NEW ASSUMPTIONS:
alpha_0(X) defeated_by c_alpha_0(X)
```

The model's output:

```
NEW RULES:
NONE

NEW ASSUMPTIONS:
NONE
```

## algorithm: t2_defeas_0000_anon #1

error `not_a_solution`, finish `stop`, valid False, clean False, exact False, agreement None

The algorithm's answer:

```
NEW RULES:
v(X) :- p(X), alpha_0(X).
c_alpha_0(X) :- q(X).

NEW ASSUMPTIONS:
alpha_0(X) defeated_by c_alpha_0(X)
```

The model's output:

```
NEW RULES:
NONE

NEW ASSUMPTIONS:
u(X) defeated_by t(X)
```

## algorithm: t4_domain_0000_anon #0

error `not_a_solution`, finish `stop`, valid False, clean False, exact False, agreement 0.0

The algorithm's answer:

```
NEW RULES:
v(X) :- p(X), alpha_0(X).
c_alpha_0(X) :- q(X).

NEW ASSUMPTIONS:
alpha_0(X) defeated_by c_alpha_0(X)
```

The model's output:

```
NEW RULES:
NONE

NEW ASSUMPTIONS:
u(X) defeated_by t(X)
```

## algorithm: t5_twopath_0000_anon #1

error `not_a_solution`, finish `stop`, valid False, clean False, exact False, agreement None

The algorithm's answer:

```
NEW RULES:
p1(X) :- q(X), alpha_0(X).
p1(X) :- p(X), alpha_1(X).
c_alpha_0(X) :- s(X).
c_alpha_1(X) :- r(X).

NEW ASSUMPTIONS:
alpha_0(X) defeated_by c_alpha_0(X)
alpha_1(X) defeated_by c_alpha_1(X)
```

The model's output:

```
NEW RULES:
NONE

NEW ASSUMPTIONS:
v(a) defeated_by t(a)
w(e) defeated_by u(e)
```

