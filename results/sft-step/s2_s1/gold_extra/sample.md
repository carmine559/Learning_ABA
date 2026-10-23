# Hand audit: 3 asked states per kind of results/sft-step/s2_s1/gold_extra

## t4_nested_0014 check (extra_check): correct True, error `None`

```
=== RULES LEARNT SO FAR (Rl, without rho) ===
  q1(X) :- q(X), alpha_0(X).

=== ASSUMPTIONS INTRODUCED SO FAR ===
  alpha_0(X) defeated_by c_alpha_0(X)

STEP: the test at line 18 on rho: c_alpha_0(X) :- X = a.
with rho_f: c_alpha_0(X) :- s(X).
Is ASP(<Rt u {rho_f}, A, C>, <E+, E->, {}) satisfiable?
Answer: fails: <examples, or none>. yes.   or   ... no.
```

reference:
```
fails: none. yes.
```
model:
```
fails: none. yes.
```

## t4_nested_0032 check (extra_check): correct True, error `None`

```
=== RULES LEARNT SO FAR (Rl, without rho) ===
  q1(X) :- q(X), alpha_0(X).

=== ASSUMPTIONS INTRODUCED SO FAR ===
  alpha_0(X) defeated_by c_alpha_0(X)

STEP: the test at line 18 on rho: c_alpha_0(X) :- X = b.
with rho_f: c_alpha_0(X) :- t(X).
Is ASP(<Rt u {rho_f}, A, C>, <E+, E->, {}) satisfiable?
Answer: fails: <examples, or none>. yes.   or   ... no.
```

reference:
```
fails: q1(c), q1(e). no.
```
model:
```
fails: q1(c), q1(e). no.
```

## t8_decoy_0005 check (extra_check): correct True, error `None`

```
=== RULES LEARNT SO FAR (Rl, without rho) ===
  v(X) :- X = a.
  v(X) :- X = d.

STEP: the test at line 18 on rho: v(X) :- X = c.
with rho_f: v(X) :- s(X).
Is ASP(<Rt u {rho_f}, A, C>, <E+, E->, {}) satisfiable?
Answer: fails: <examples, or none>. yes.   or   ... no.
```

reference:
```
fails: v(f). no.
```
model:
```
fails: v(f). no.
```

