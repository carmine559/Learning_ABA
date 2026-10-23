# Hand audit: 3 asked states per kind of results/sft-step/s2_s1/gold

## t3_domain_0034 role (other): correct True, error `None`

```
STEP: RoLe (lines 3-12). List the facts that lines 8-10 learn: a minimal set
of facts p(X) :- X = t, with p in T, that makes the framework a solution.
One per line: R1 p(X) :- X = t.   or: none.
```

reference:
```
R1 v(X) :- X = a.
R1 v(X) :- X = c.
R1 v(X) :- X = d.
R1 v(X) :- X = f.
R1 v(X) :- X = e.
```
model:
```
R1 v(X) :- X = a.
R1 v(X) :- X = c.
R1 v(X) :- X = f.
R1 v(X) :- X = e.
R1 v(X) :- X = d.
```

## t3_domain_0031 role (other): correct True, error `None`

```
STEP: RoLe (lines 3-12). List the facts that lines 8-10 learn: a minimal set
of facts p(X) :- X = t, with p in T, that makes the framework a solution.
One per line: R1 p(X) :- X = t.   or: none.
```

reference:
```
R1 v(X) :- X = e.
R1 v(X) :- X = b.
R1 v(X) :- X = d.
R1 v(X) :- X = c.
```
model:
```
R1 v(X) :- X = e.
R1 v(X) :- X = b.
R1 v(X) :- X = d.
R1 v(X) :- X = c.
```

## t8_decoy_0040 role (other): correct True, error `None`

```
STEP: RoLe (lines 3-12). List the facts that lines 8-10 learn: a minimal set
of facts p(X) :- X = t, with p in T, that makes the framework a solution.
One per line: R1 p(X) :- X = t.   or: none.
```

reference:
```
R1 v(X) :- X = b.
R1 v(X) :- X = c.
R1 v(X) :- X = a.
```
model:
```
R1 v(X) :- X = b.
R1 v(X) :- X = c.
R1 v(X) :- X = a.
```

## t2_noise_0039 subsume (other): correct True, error `None`

```
=== RULES LEARNT SO FAR (Rl, without rho) ===
  p1(X) :- X = b.

STEP: Fact Subsumption (line 16) on rho: p1(X) :- X = c.
Is ASP(<Rt, A, C>, <E+, E->, {}) satisfiable?
Answer: fails: <examples, or none>. yes.   or   ... no.
```

reference:
```
fails: p1(c). no.
```
model:
```
fails: p1(c). no.
```

## t5_twopath_0037 subsume (later_role_subsume): correct True, error `None`

```
=== RULES LEARNT SO FAR (Rl, without rho) ===
  r1(X) :- p(X).

STEP: Fact Subsumption (line 16) on rho: r1(X) :- X = d.
Is ASP(<Rt, A, C>, <E+, E->, {}) satisfiable?
Answer: fails: <examples, or none>. yes.   or   ... no.
```

reference:
```
fails: r1(d). no.
```
model:
```
fails: r1(d). no.
```

## t5_twopath_0011 subsume (other): correct True, error `None`

```
=== RULES LEARNT SO FAR (Rl, without rho) ===
  r1(X) :- X = c.
  r1(X) :- X = d.

STEP: Fact Subsumption (line 16) on rho: r1(X) :- X = b.
Is ASP(<Rt, A, C>, <E+, E->, {}) satisfiable?
Answer: fails: <examples, or none>. yes.   or   ... no.
```

reference:
```
fails: r1(b). no.
```
model:
```
fails: r1(b). no.
```

## t5_twopath_0012 fold_candidates (other): correct True, error `None`

```
=== RULES LEARNT SO FAR (Rl, without rho) ===
  r1(X) :- q(X), alpha_0(X).
  r1(X) :- p(X), alpha_1(X).
  c_alpha_0(X) :- s(X).

=== ASSUMPTIONS INTRODUCED SO FAR ===
  alpha_0(X) defeated_by c_alpha_0(X)
  alpha_1(X) defeated_by c_alpha_1(X)

STEP: applyFolding (line 17) on rho: c_alpha_1(X) :- X = d.
List every fold of rho, in order.
Answer: R2 candidates: [<rule>] [<rule>] ...
```

reference:
```
R2 candidates: [c_alpha_1(X) :- p(X).] [c_alpha_1(X) :- r(X).] [c_alpha_1(X) :- t(X).] [c_alpha_1(X) :- u(X).] [c_alpha_1(X) :- dom(X).]
```
model:
```
R2 candidates: [c_alpha_1(X) :- p(X).] [c_alpha_1(X) :- r(X).] [c_alpha_1(X) :- t(X).] [c_alpha_1(X) :- u(X).] [c_alpha_1(X) :- dom(X).]
```

## t3_domain_0001 fold_candidates (other): correct True, error `None`

```
=== RULES LEARNT SO FAR (Rl, without rho) ===
  v(X) :- X = d.
  v(X) :- X = e.
  v(X) :- X = a.

STEP: applyFolding (line 17) on rho: v(X) :- X = c.
List every fold of rho, in order.
Answer: R2 candidates: [<rule>] [<rule>] ...
```

reference:
```
R2 candidates: [v(X) :- p(X).] [v(X) :- dom(X).]
```
model:
```
R2 candidates: [v(X) :- p(X).] [v(X) :- dom(X).]
```

## t5_twopath_0029 fold_candidates (other): correct True, error `None`

```
=== RULES LEARNT SO FAR (Rl, without rho) ===
  r1(X) :- p(X).

STEP: applyFolding (line 17) on rho: r1(X) :- X = d.
List every fold of rho, in order.
Answer: R2 candidates: [<rule>] [<rule>] ...
```

reference:
```
R2 candidates: [r1(X) :- q(X).] [r1(X) :- dom(X).]
```
model:
```
R2 candidates: [r1(X) :- q(X).] [r1(X) :- dom(X).]
```

## t2_noise_0024 check (first_check): correct True, error `None`

```
=== RULES LEARNT SO FAR (Rl, without rho) ===
  p1(X) :- X = b.
  p1(X) :- X = a.

STEP: the test at line 18 on rho: p1(X) :- X = d.
with rho_f: p1(X) :- p(X).
Is ASP(<Rt u {rho_f}, A, C>, <E+, E->, {}) satisfiable?
Answer: fails: <examples, or none>. yes.   or   ... no.
```

reference:
```
fails: p1(c). no.
```
model:
```
fails: p1(c). no.
```

## t5_twopath_0010 check (other): correct True, error `None`

```
=== RULES LEARNT SO FAR (Rl, without rho) ===
  r1(X) :- p(X).
  r1(X) :- q(X), alpha_0(X).

=== ASSUMPTIONS INTRODUCED SO FAR ===
  alpha_0(X) defeated_by c_alpha_0(X)

STEP: the test at line 18 on rho: c_alpha_0(X) :- X = e.
with rho_f: c_alpha_0(X) :- q(X).
Is ASP(<Rt u {rho_f}, A, C>, <E+, E->, {}) satisfiable?
Answer: fails: <examples, or none>. yes.   or   ... no.
```

reference:
```
fails: r1(f). no.
```
model:
```
fails: r1(f). no.
```

## t9_reuse_0039 check (other): correct True, error `None`

```
=== RULES LEARNT SO FAR (Rl, without rho) ===
  r1(X) :- q(X), alpha_0(X).

=== ASSUMPTIONS INTRODUCED SO FAR ===
  alpha_0(X) defeated_by c_alpha_0(X)

STEP: the test at line 18 on rho: c_alpha_0(X) :- X = c.
with rho_f: c_alpha_0(X) :- q(X).
Is ASP(<Rt u {rho_f}, A, C>, <E+, E->, {}) satisfiable?
Answer: fails: <examples, or none>. yes.   or   ... no.
```

reference:
```
fails: r1(a), r1(b). no.
```
model:
```
fails: r1(a), r1(b). no.
```

## t3_domain_0002 reuse_scan (other): correct True, error `None`

```
=== RULES LEARNT SO FAR (Rl, without rho) ===
  v(X) :- p(X), alpha_0(X).

=== ASSUMPTIONS INTRODUCED SO FAR ===
  alpha_0(X) defeated_by c_alpha_0(X)

STEP: applyAsmIntro (line 36) on rho_f: c_alpha_0(X) :- p(X).
List the assumptions in A relative to the body of rho_f.
Answer: R3 reuse: [<assumption>] ... .   or: R3 reuse: none.
```

reference:
```
R3 reuse: [alpha_0(X)].
```
model:
```
R3 reuse: [alpha_0(X)].
```

## t9_reuse_0042 reuse_scan (other): correct True, error `None`

```
=== RULES LEARNT SO FAR (Rl, without rho) ===
  r1(X) :- X = b.
  r1(X) :- X = a.

STEP: applyAsmIntro (line 36) on rho_f: r1(X) :- p(X).
List the assumptions in A relative to the body of rho_f.
Answer: R3 reuse: [<assumption>] ... .   or: R3 reuse: none.
```

reference:
```
R3 reuse: [v(X)].
```
model:
```
R3 reuse: [v(X)].
```

## t9_reuse_0035 reuse_scan (other): correct True, error `None`

```
=== RULES LEARNT SO FAR (Rl, without rho) ===
  r1(X) :- X = a.

STEP: applyAsmIntro (line 36) on rho_f: r1(X) :- q(X).
List the assumptions in A relative to the body of rho_f.
Answer: R3 reuse: [<assumption>] ... .   or: R3 reuse: none.
```

reference:
```
R3 reuse: none.
```
model:
```
R3 reuse: none.
```

## t9_reuse_0015 reuse_check (role_reuse_check): correct True, error `None`

```
=== RULES LEARNT SO FAR (Rl, without rho) ===
  r1(X) :- X = c.

STEP: the test at line 38 with the relative assumption v(X)
rho_d: r1(X) :- p(X), v(X).
Is ASP(<Rt u {rho_d}, A, C>, <E+, E->, {}) satisfiable?
Answer: yes.   or: no.
```

reference:
```
no.
```
model:
```
no.
```

## t9_reuse_0046 reuse_check (role_reuse_check): correct False, error `None`

```
=== RULES LEARNT SO FAR (Rl, without rho) ===
  r1(X) :- X = c.

STEP: the test at line 38 with the relative assumption v(X)
rho_d: r1(X) :- p(X), v(X).
Is ASP(<Rt u {rho_d}, A, C>, <E+, E->, {}) satisfiable?
Answer: yes.   or: no.
```

reference:
```
yes.
```
model:
```
no.
```

## t1_base_0006 reuse_check (other): correct True, error `None`

```
=== RULES LEARNT SO FAR (Rl, without rho) ===
  v(X) :- p(X), alpha_0(X).

=== ASSUMPTIONS INTRODUCED SO FAR ===
  alpha_0(X) defeated_by c_alpha_0(X)

STEP: the test at line 38 with the relative assumption alpha_0(X)
rho_d: c_alpha_0(X) :- p(X), alpha_0(X).
Is ASP(<Rt u {rho_d}, A, C>, <E+, E->, {}) satisfiable?
Answer: yes.   or: no.
```

reference:
```
no.
```
model:
```
no.
```

## t5_twopath_0008 contrary_facts (other): correct True, error `None`

```
=== RULES LEARNT SO FAR (Rl, without rho) ===
  r1(X) :- X = a.
  r1(X) :- X = e.
  r1(X) :- X = d.

STEP: lines 41-44 on rho_f: r1(X) :- p(X).
A new assumption alpha_0(X), with contrary c_alpha_0(X), gives
rho_d: r1(X) :- p(X), alpha_0(X).
List the facts for c_alpha_0 in S := getAS(ASP(F, <E+, E->, {c_alpha_0})), where
F = <Rt u {rho_d}, A u {alpha_0(X)}, C u {alpha_0(X) -> c_alpha_0(X)}>; lines 23-25 learn them.
One per line: R1 c_alpha_0(X) :- X = t.   or: none.
```

reference:
```
R1 c_alpha_0(X) :- X = b.
```
model:
```
R1 c_alpha_0(X) :- X = b.
```

## table1_06_anon contrary_facts (other): correct False, error `None`

```
=== RULES LEARNT SO FAR (Rl, without rho) ===
  v(X) :- p(X), alpha_0(X).
  c_alpha_0(X) :- q(X).

=== ASSUMPTIONS INTRODUCED SO FAR ===
  alpha_0(X) defeated_by c_alpha_0(X)

STEP: lines 41-44 on rho_f: c_alpha_0(X) :- r(X).
A new assumption alpha_1(X), with contrary c_alpha_1(X), gives
rho_d: c_alpha_0(X) :- r(X), alpha_1(X).
List the facts for c_alpha_1 in S := getAS(ASP(F, <E+, E->, {c_alpha_1})), where
F = <Rt u {rho_d}, A u {alpha_1(X)}, C u {alpha_1(X) -> c_alpha_1(X)}>; lines 23-25 learn them.
One per line: R1 c_alpha_1(X) :- X = t.   or: none.
```

reference:
```
R1 c_alpha_1(X) :- X = b.
R1 c_alpha_1(X) :- X = d.
```
model:
```
R1 c_alpha_1(X) :- X = b.
```

## t5_twopath_0032 contrary_facts (other): correct True, error `None`

```
=== RULES LEARNT SO FAR (Rl, without rho) ===
  r1(X) :- X = d.
  r1(X) :- X = f.
  r1(X) :- X = a.
  r1(X) :- X = c.

STEP: lines 41-44 on rho_f: r1(X) :- p(X).
A new assumption alpha_0(X), with contrary c_alpha_0(X), gives
rho_d: r1(X) :- p(X), alpha_0(X).
List the facts for c_alpha_0 in S := getAS(ASP(F, <E+, E->, {c_alpha_0})), where
F = <Rt u {rho_d}, A u {alpha_0(X)}, C u {alpha_0(X) -> c_alpha_0(X)}>; lines 23-25 learn them.
One per line: R1 c_alpha_0(X) :- X = t.   or: none.
```

reference:
```
R1 c_alpha_0(X) :- X = e.
```
model:
```
R1 c_alpha_0(X) :- X = e.
```

