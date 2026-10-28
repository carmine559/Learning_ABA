# Hand audit: 5 rows per mode

## direct: t1_mono_0003_anon #2

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
NONE
```

## direct: t3_noise_0001_anon #0

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
w(a) defeated_by v(a)
```

## direct: t4_domain_0002_anon #2

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
u(v(X)) defeated_by t(v(X))
```

## direct: t4_domain_0008_anon #2

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
u(d) defeated_by t(d)
u(g) defeated_by t(g)
u(e) defeated_by t(e)
```

## direct: t5_twopath_0004_anon #0

error `not_a_solution`, finish `stop`, valid False, clean False, exact False, agreement None

The algorithm's answer:

```
NEW RULES:
p1(X) :- p(X), alpha_0(X).
p1(X) :- q(X), alpha_1(X).
c_alpha_0(X) :- r(X).
c_alpha_1(X) :- s(X).

NEW ASSUMPTIONS:
alpha_0(X) defeated_by c_alpha_0(X)
alpha_1(X) defeated_by c_alpha_1(X)
```

The model's output:

```
NEW RULES:
p1(X) :- t(X), u(X).

NEW ASSUMPTIONS:
v(X) defeated_by t(X)
w(X) defeated_by u(X)
```

## cot: t3_noise_0008_anon #2

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
p1(v(X)) defeated_by v(X)
```

## cot: t3_noise_0018_anon #0

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
w(X) defeated_by v(X)
```

## cot: t4_domain_0006_anon #0

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

## cot: t4_domain_0018_anon #1

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
NONE
```

## cot: t4_domain_0019_anon #2

error `illformed`, finish `stop`, valid True, clean False, exact False, agreement 0.5

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
v(b) defeated_by t(b)
v(d) defeated_by t(d)
v(c) defeated_by t(c)
v(f) defeated_by t(f)
```

## guided: t2_defeas_0000_anon #2

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

## guided: t2_defeas_0014_anon #0

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

## guided: t3_noise_0005_anon #0

error `parse_error`, finish `stop`, valid False, clean False, exact False, agreement None

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
NONE
```

## guided: t5_twopath_0003_anon #0

error `not_a_solution`, finish `stop`, valid False, clean False, exact False, agreement None

The algorithm's answer:

```
NEW RULES:
p1(X) :- p(X), alpha_0(X).
p1(X) :- q(X), alpha_1(X).
c_alpha_0(X) :- r(X).
c_alpha_1(X) :- s(X).

NEW ASSUMPTIONS:
alpha_0(X) defeated_by c_alpha_0(X)
alpha_1(X) defeated_by c_alpha_1(X)
```

The model's output:

```
NEW RULES:
NONE

NEW ASSUMPTIONS:
v(d) defeated_by t(d)
v(b) defeated_by t(b)
v(f) defeated_by t(f)
v(c) defeated_by t(c)
```

## guided: t5_twopath_0016_anon #1

error `illformed`, finish `stop`, valid True, clean False, exact False, agreement None

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
p1(f) defeated_by p1_t(f)
p1(b) defeated_by p1_t(b)
p1(c) defeated_by p1_t(c)
p1(d) defeated_by p1_t(d)
```

## algorithm: t1_mono_0013_anon #0

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

## algorithm: t2_defeas_0000_anon #2

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

## algorithm: t2_defeas_0019_anon #2

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

=== BACKGROUND KNOWLEDGE (ABA framework) ===
% Domain: dom/1 holds for each constant below, and every
% assumption is instantiated once per constant.
  dom(e). dom(a). dom(b). dom(d). dom(f). dom(c).

% Rules R
  p(a).
  p(b).
  p(c).
  p(d).
  q(a).
  r(d).
  s(e).
  s(b).
  s(d).
  t(X) :- q(X).

% Assumptions A, with their contraries
  u(X) defeated_by t(X)

=== POSITIVE EXAMPLES E+ (all accepted in ONE common stable extension) ===
  + v(b)
  + v(d)
  + v(c)

=== NEGATIVE EXAMPLES E- (none accepted in that same extension) ===
  - v(a)
  - v(f)
  - v(e)

=== LEARNABLE PREDICATES T ===
  v, t

NEW RULES:
NONE

NEW ASSUMPTIONS:
NONE
```

## algorithm: t5_twopath_0007_anon #2

error `not_a_solution`, finish `stop`, valid False, clean False, exact False, agreement None

The algorithm's answer:

```
NEW RULES:
p1(X) :- p(X), alpha_0(X).
p1(X) :- q(X), alpha_1(X).
c_alpha_0(X) :- r(X).
c_alpha_1(X) :- s(X).

NEW ASSUMPTIONS:
alpha_0(X) defeated_by c_alpha_0(X)
alpha_1(X) defeated_by c_alpha_1(X)
```

The model's output:

```
NEW RULES:
NONE

NEW ASSUMPTIONS:
v(X) defeated_by t(X)
w(X) defeated_by u(X)
```

## algorithm: t5_twopath_0019_anon #2

error `not_a_solution`, finish `stop`, valid False, clean False, exact False, agreement None

The algorithm's answer:

```
NEW RULES:
p1(X) :- p(X), alpha_0(X).
p1(X) :- q(X), alpha_1(X).
c_alpha_0(X) :- r(X).
c_alpha_1(X) :- s(X).

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

