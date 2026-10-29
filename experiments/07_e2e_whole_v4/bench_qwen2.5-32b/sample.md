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
v(X) :- p(X), u(X).
s(X) :- r(X).

NEW ASSUMPTIONS:
NONE
```

## direct: t3_noise_0001_anon #0

error `ok`, finish `stop`, valid True, clean True, exact False, agreement 1.0

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
p1(X) :- p(X), w(X).

NEW ASSUMPTIONS:
NONE
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
v(X) :- p(X), u(X).
t(X) :- r(X).

NEW ASSUMPTIONS:
u(X) defeated_by t(X)
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
v(X) :- p(X), u(X).
t(X) :- r(X).

NEW ASSUMPTIONS:
u(X) defeated_by t(X)
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
p1(X) :- p(X), v(X).

NEW ASSUMPTIONS:
v(X) defeated_by t(X)
```

## cot: t3_noise_0008_anon #2

error `ok`, finish `stop`, valid True, clean True, exact False, agreement 1.0

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
Add: p1(b) :- p(b), w(b).
Add: p1(c) :- p(c), w(c).
Add: p1(e) :- p(e), w(e).

Fold p1(b) :- p(b), w(b) using p(b) -> p1(b) :- w(b).
Fold p1(c) :- p(c), w(c) using p(c) -> p1(c) :- w(c).
Fold p1(e) :- p(e), w(e) using p(e) -> p1(e) :- w(e).

Rule p1(b) :- w(b) violates -p1(a), -p1(f), -p1(g). Introduce alpha(X) defeated_by c_alpha(X). Contrary rule: c_alpha(X) :- v(X).
Rule p1(c) :- w(c) violates -p1(a), -p1(f), -p1(g). Introduce alpha(X) defeated_by c_alpha(X). Contrary rule: c_alpha(X) :- v(X).
Rule p1(e) :- w(e) violates -p1(a), -p1(f), -p1(g). Introduce alpha(X) defeated_by c_alpha(X). Contrary rule: c_alpha(X) :- v(X).

Remove p1(b) :- w(b) (solution preserved without it).
Remove p1(c) :- w(c) (solution preserved without it).
Remove p1(e) :- w(e) (solution preserved without it).

NEW RULES:
p1(X) :- p(X), alpha(X).
c_alpha(X) :- v(X).

NEW ASSUMPTIONS:
alpha(X) defeated_by c_alpha(X)
```

## cot: t3_noise_0018_anon #0

error `ok`, finish `stop`, valid True, clean True, exact False, agreement 1.0

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
Add: p1(b) :- p(b).
Add: p1(d) :- p(d).
Add: p1(c) :- p(c).

Fold p1(b) :- p(b) using p(a) -> p1(X) :- p(X).
Fold p1(d) :- p(d) using p(d) -> p1(X) :- p(X).
Fold p1(c) :- p(c) using p(c) -> p1(X) :- p(X).

Rule p1(X) :- p(X) violates -p1(a), -p1(h), -p1(f). Introduce w(X) defeated_by v(X).
Contrary rule: v(X) :- q(X).

Remove p1(b) :- p(b) (solution preserved without it).
Remove p1(d) :- p(d) (solution preserved without it).
Remove p1(c) :- p(c) (solution preserved without it).

NEW RULES:
p1(X) :- p(X), w(X).

NEW ASSUMPTIONS:
w(X) defeated_by v(X)
```

## cot: t4_domain_0006_anon #0

error `valid_but_degenerate`, finish `stop`, valid True, clean False, exact False, agreement 0.5

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
Add: v(g) :- g = g.
Add: v(e) :- e = e.
Add: v(f) :- f = f.
Add: v(c) :- c = c.

Fold v(g) :- g = g using p(g) -> v(g) :- p(g).
Fold v(e) :- e = e using p(e) -> v(e) :- p(e).
Fold v(f) :- f = f using p(f) :- p(f).
Fold v(c) :- c = c using p(c) :- p(c).

Rule v(g) :- p(g) violates [- v(a), - v(k), - v(h), - v(i)]. Introduce u(X) defeated_by t(X). Contrary rule: t(X) :- dom(X).
Rule v(e) :- p(e) violates [- v(a), - v(k), - v(h), - v(i)]. Introduce u(X) defeated_by t(X). Contrary rule: t(X) :- dom(X).
Rule v(f) :- p(f) violates [- v(a), - v(k), - v(h), - v(i)]. Introduce u(X) defeated_by t(X). Contrary rule: t(X) :- dom(X).
Rule v(c) :- p(c) violates [- v(a), - v(k), - v(h), - v(i)]. Introduce u(X) defeated_by t(X). Contrary rule: t(X) :- dom(X).

Remove t(X) :- q(X) (solution preserved without it).

NEW RULES:
v(g) :- p(g), u(g).
v(e) :- p(e), u(e).
v(f) :- p(f), u(f).
v(c) :- p(c), u(c).

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
v(X) :- p(X), u(X).
v(X) :- s(X).

NEW ASSUMPTIONS:
u(X) defeated_by t(X)
```

## cot: t4_domain_0019_anon #2

error `ok`, finish `stop`, valid True, clean True, exact True, agreement 1.0

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
Add: v(b) :- p(b), u(b).
Add: v(d) :- p(d), u(d).
Add: v(c) :- p(c), u(c).
Add: v(f) :- p(f), u(f).

Fold v(b) :- p(b), u(b) using p(X) :- X = b -> v(b) :- p(b), u(b).
Fold v(d) :- p(d), u(d) using p(X) :- X = d -> v(d) :- p(d), u(d).
Fold v(c) :- p(c), u(c) using p(X) :- X = c -> v(c) :- p(c), u(c).
Fold v(f) :- p(f), u(f) using p(X) :- X = f -> v(f) :- p(f), u(f).

Rule violates [v(a)]. Introduce alpha(X) defeated_by c_alpha(X).
Contrary rule: c_alpha(X) :- q(X).

Remove v(b) :- p(b), u(b) (solution preserved without it).
Remove v(d) :- p(d), u(d) (solution preserved without it).
Remove v(c) :- p(c), u(c) (solution preserved without it).
Remove v(f) :- p(f), u(f) (solution preserved without it).

NEW RULES:
v(X) :- p(X), alpha(X).
c_alpha(X) :- q(X).

NEW ASSUMPTIONS:
alpha(X) defeated_by c_alpha(X)
```

## guided: t2_defeas_0000_anon #2

error `illformed`, finish `stop`, valid True, clean False, exact False, agreement None

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
v(X) :- p(X), u(X).
c_u(X) :- q(X).

NEW ASSUMPTIONS:
u(X) defeated_by c_u(X)
```

## guided: t2_defeas_0014_anon #0

error `ok`, finish `stop`, valid True, clean True, exact False, agreement None

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
v(X) :- p(X), u(X).
c_u(X) :- q(X).

NEW ASSUMPTIONS:
u(X) defeated_by t(X)
```

## guided: t3_noise_0005_anon #0

error `ok`, finish `stop`, valid True, clean True, exact False, agreement 1.0

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
p1(X) :- p(X), w(X).
c_w(X) :- v(X).

NEW ASSUMPTIONS:
w(X) defeated_by v(X)
```

## guided: t5_twopath_0003_anon #0

error `ok`, finish `stop`, valid True, clean True, exact False, agreement None

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
p1(X) :- p(X), v(X).
p1(X) :- q(X), w(X).

NEW ASSUMPTIONS:
v(X) defeated_by t(X)
w(X) defeated_by u(X)
```

## guided: t5_twopath_0016_anon #1

error `ok`, finish `stop`, valid True, clean True, exact False, agreement None

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
p1(X) :- p(X), v(X).
p1(X) :- q(X), w(X).

NEW ASSUMPTIONS:
v(X) defeated_by t(X)
w(X) defeated_by u(X)
```

## algorithm: t1_mono_0013_anon #0

error `illformed`, finish `stop`, valid False, clean False, exact False, agreement 0.0

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
v(X) :- p(X), u(X).
v(X) :- q(X), u(X).
u(X) :- r(X).

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
v(X) :- p(X), u(X).
v(X) :- s(X), u(X).
t(X) :- X = a.
t(X) :- X = f.

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
v(X) :- p(X), u(X).
v(X) :- s(X), u(X).

NEW ASSUMPTIONS:
u(X) defeated_by t(X)
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
p1(X) :- p(X), v(X).

NEW ASSUMPTIONS:
v(X) defeated_by t(X)
```

## algorithm: t5_twopath_0019_anon #2

error `ok`, finish `stop`, valid True, clean True, exact False, agreement None

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
p1(X) :- p(X), v(X).
p1(X) :- q(X), w(X).

NEW ASSUMPTIONS:
v(X) defeated_by t(X)
w(X) defeated_by u(X)
```

