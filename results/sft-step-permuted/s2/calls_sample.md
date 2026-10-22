# Hand audit: every call of 5 chained runs of results/sft-step-permuted/s2

# t8_decoy_0040 (heldout, decoy_first): 6 calls, stop `None`, exact True

## t8_decoy_0040 role (other): correct True, error `None`

```
STEP: RoLe (lines 3-12). List the facts that lines 8-10 learn: a minimal set
of facts p(X) :- X = t, with p in T, that makes the framework a solution.
One per line: R1 p(X) :- X = t.   or: none.
```

reference:
```
R1 r(X) :- X = b.
R1 r(X) :- X = c.
R1 r(X) :- X = a.
```
model:
```
R1 r(X) :- X = b.
R1 r(X) :- X = c.
R1 r(X) :- X = a.
```

## t8_decoy_0040 subsume (other): correct True, error `None`

```
=== RULES LEARNT SO FAR (Rl, without rho) ===
  r(X) :- X = c.
  r(X) :- X = a.

STEP: Fact Subsumption (line 16) on rho: r(X) :- X = b.
Is ASP(<Rt, A, C>, <E+, E->, {}) satisfiable?
Answer: fails: <examples, or none>. yes.   or   ... no.
```

reference:
```
no.
```
model:
```
fails: r(b). no.
```

## t8_decoy_0040 fold_candidates (other): correct True, error `None`

```
=== RULES LEARNT SO FAR (Rl, without rho) ===
  r(X) :- X = c.
  r(X) :- X = a.

STEP: applyFolding (line 17) on rho: r(X) :- X = b.
List every fold of rho, in order.
Answer: R2 candidates: [<rule>] [<rule>] ...
```

reference:
```
R2 candidates: [r(X) :- v(X).] [r(X) :- s(X).] [r(X) :- dom(X).]
```
model:
```
R2 candidates: [r(X) :- v(X).] [r(X) :- s(X).] [r(X) :- dom(X).]
```

## t8_decoy_0040 check (first_check): correct True, error `None`

```
=== RULES LEARNT SO FAR (Rl, without rho) ===
  r(X) :- X = c.
  r(X) :- X = a.

STEP: the test at line 18 on rho: r(X) :- X = b.
with rho_f: r(X) :- v(X).
Is ASP(<Rt u {rho_f}, A, C>, <E+, E->, {}) satisfiable?
Answer: fails: <examples, or none>. yes.   or   ... no.
```

reference:
```
yes.
```
model:
```
fails: none. yes.
```

## t8_decoy_0040 subsume (later_role_subsume): correct True, error `None`

```
=== RULES LEARNT SO FAR (Rl, without rho) ===
  r(X) :- v(X).
  r(X) :- X = a.

STEP: Fact Subsumption (line 16) on rho: r(X) :- X = c.
Is ASP(<Rt, A, C>, <E+, E->, {}) satisfiable?
Answer: fails: <examples, or none>. yes.   or   ... no.
```

reference:
```
yes.
```
model:
```
fails: none. yes.
```

## t8_decoy_0040 subsume (later_role_subsume): correct True, error `None`

```
=== RULES LEARNT SO FAR (Rl, without rho) ===
  r(X) :- v(X).

STEP: Fact Subsumption (line 16) on rho: r(X) :- X = a.
Is ASP(<Rt, A, C>, <E+, E->, {}) satisfiable?
Answer: fails: <examples, or none>. yes.   or   ... no.
```

reference:
```
yes.
```
model:
```
fails: none. yes.
```

# t1_base_0025 (test, monotonic): 6 calls, stop `None`, exact True

## t1_base_0025 role (other): correct True, error `None`

```
STEP: RoLe (lines 3-12). List the facts that lines 8-10 learn: a minimal set
of facts p(X) :- X = t, with p in T, that makes the framework a solution.
One per line: R1 p(X) :- X = t.   or: none.
```

reference:
```
R1 r(X) :- X = c.
R1 r(X) :- X = a.
R1 r(X) :- X = b.
```
model:
```
R1 r(X) :- X = c.
R1 r(X) :- X = a.
R1 r(X) :- X = b.
```

## t1_base_0025 subsume (other): correct True, error `None`

```
=== RULES LEARNT SO FAR (Rl, without rho) ===
  r(X) :- X = a.
  r(X) :- X = b.

STEP: Fact Subsumption (line 16) on rho: r(X) :- X = c.
Is ASP(<Rt, A, C>, <E+, E->, {}) satisfiable?
Answer: fails: <examples, or none>. yes.   or   ... no.
```

reference:
```
no.
```
model:
```
fails: r(c). no.
```

## t1_base_0025 fold_candidates (other): correct True, error `None`

```
=== RULES LEARNT SO FAR (Rl, without rho) ===
  r(X) :- X = a.
  r(X) :- X = b.

STEP: applyFolding (line 17) on rho: r(X) :- X = c.
List every fold of rho, in order.
Answer: R2 candidates: [<rule>] [<rule>] ...
```

reference:
```
R2 candidates: [r(X) :- t(X).] [r(X) :- dom(X).]
```
model:
```
R2 candidates: [r(X) :- t(X).] [r(X) :- dom(X).]
```

## t1_base_0025 check (first_check): correct True, error `None`

```
=== RULES LEARNT SO FAR (Rl, without rho) ===
  r(X) :- X = a.
  r(X) :- X = b.

STEP: the test at line 18 on rho: r(X) :- X = c.
with rho_f: r(X) :- t(X).
Is ASP(<Rt u {rho_f}, A, C>, <E+, E->, {}) satisfiable?
Answer: fails: <examples, or none>. yes.   or   ... no.
```

reference:
```
yes.
```
model:
```
fails: none. yes.
```

## t1_base_0025 subsume (later_role_subsume): correct True, error `None`

```
=== RULES LEARNT SO FAR (Rl, without rho) ===
  r(X) :- t(X).
  r(X) :- X = b.

STEP: Fact Subsumption (line 16) on rho: r(X) :- X = a.
Is ASP(<Rt, A, C>, <E+, E->, {}) satisfiable?
Answer: fails: <examples, or none>. yes.   or   ... no.
```

reference:
```
yes.
```
model:
```
fails: none. yes.
```

## t1_base_0025 subsume (later_role_subsume): correct True, error `None`

```
=== RULES LEARNT SO FAR (Rl, without rho) ===
  r(X) :- t(X).

STEP: Fact Subsumption (line 16) on rho: r(X) :- X = b.
Is ASP(<Rt, A, C>, <E+, E->, {}) satisfiable?
Answer: fails: <examples, or none>. yes.   or   ... no.
```

reference:
```
yes.
```
model:
```
fails: none. yes.
```

# t3_domain_0034 (test, defeasible): 16 calls, stop `None`, exact True

## t3_domain_0034 role (other): correct True, error `None`

```
STEP: RoLe (lines 3-12). List the facts that lines 8-10 learn: a minimal set
of facts p(X) :- X = t, with p in T, that makes the framework a solution.
One per line: R1 p(X) :- X = t.   or: none.
```

reference:
```
R1 q(X) :- X = a.
R1 q(X) :- X = c.
R1 q(X) :- X = d.
R1 q(X) :- X = f.
R1 q(X) :- X = e.
```
model:
```
R1 q(X) :- X = a.
R1 q(X) :- X = c.
R1 q(X) :- X = d.
R1 q(X) :- X = f.
R1 q(X) :- X = e.
```

## t3_domain_0034 subsume (other): correct True, error `None`

```
=== RULES LEARNT SO FAR (Rl, without rho) ===
  q(X) :- X = c.
  q(X) :- X = d.
  q(X) :- X = f.
  q(X) :- X = e.

STEP: Fact Subsumption (line 16) on rho: q(X) :- X = a.
Is ASP(<Rt, A, C>, <E+, E->, {}) satisfiable?
Answer: fails: <examples, or none>. yes.   or   ... no.
```

reference:
```
no.
```
model:
```
fails: q(a). no.
```

## t3_domain_0034 fold_candidates (other): correct True, error `None`

```
=== RULES LEARNT SO FAR (Rl, without rho) ===
  q(X) :- X = c.
  q(X) :- X = d.
  q(X) :- X = f.
  q(X) :- X = e.

STEP: applyFolding (line 17) on rho: q(X) :- X = a.
List every fold of rho, in order.
Answer: R2 candidates: [<rule>] [<rule>] ...
```

reference:
```
R2 candidates: [q(X) :- v(X).] [q(X) :- t(X).] [q(X) :- dom(X).]
```
model:
```
R2 candidates: [q(X) :- v(X).] [q(X) :- t(X).] [q(X) :- dom(X).]
```

## t3_domain_0034 check (first_check): correct True, error `None`

```
=== RULES LEARNT SO FAR (Rl, without rho) ===
  q(X) :- X = c.
  q(X) :- X = d.
  q(X) :- X = f.
  q(X) :- X = e.

STEP: the test at line 18 on rho: q(X) :- X = a.
with rho_f: q(X) :- v(X).
Is ASP(<Rt u {rho_f}, A, C>, <E+, E->, {}) satisfiable?
Answer: fails: <examples, or none>. yes.   or   ... no.
```

reference:
```
no.
```
model:
```
fails: q(b). no.
```

## t3_domain_0034 reuse_scan (other): correct True, error `None`

```
=== RULES LEARNT SO FAR (Rl, without rho) ===
  q(X) :- X = c.
  q(X) :- X = d.
  q(X) :- X = f.
  q(X) :- X = e.

STEP: applyAsmIntro (line 36) on rho_f: q(X) :- v(X).
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

## t3_domain_0034 contrary_facts (other): correct True, error `None`

```
=== RULES LEARNT SO FAR (Rl, without rho) ===
  q(X) :- X = c.
  q(X) :- X = d.
  q(X) :- X = f.
  q(X) :- X = e.

STEP: lines 41-44 on rho_f: q(X) :- v(X).
A new assumption alpha_0(X), with contrary c_alpha_0(X), gives
rho_d: q(X) :- v(X), alpha_0(X).
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

## t3_domain_0034 subsume (later_role_subsume): correct True, error `None`

```
=== RULES LEARNT SO FAR (Rl, without rho) ===
  q(X) :- v(X), alpha_0(X).
  q(X) :- X = d.
  q(X) :- X = f.
  q(X) :- X = e.
  c_alpha_0(X) :- X = b.

=== ASSUMPTIONS INTRODUCED SO FAR ===
  alpha_0(X) defeated_by c_alpha_0(X)

STEP: Fact Subsumption (line 16) on rho: q(X) :- X = c.
Is ASP(<Rt, A, C>, <E+, E->, {}) satisfiable?
Answer: fails: <examples, or none>. yes.   or   ... no.
```

reference:
```
yes.
```
model:
```
fails: none. yes.
```

## t3_domain_0034 subsume (later_role_subsume): correct True, error `None`

```
=== RULES LEARNT SO FAR (Rl, without rho) ===
  q(X) :- v(X), alpha_0(X).
  q(X) :- X = f.
  q(X) :- X = e.
  c_alpha_0(X) :- X = b.

=== ASSUMPTIONS INTRODUCED SO FAR ===
  alpha_0(X) defeated_by c_alpha_0(X)

STEP: Fact Subsumption (line 16) on rho: q(X) :- X = d.
Is ASP(<Rt, A, C>, <E+, E->, {}) satisfiable?
Answer: fails: <examples, or none>. yes.   or   ... no.
```

reference:
```
yes.
```
model:
```
fails: none. yes.
```

## t3_domain_0034 subsume (later_role_subsume): correct True, error `None`

```
=== RULES LEARNT SO FAR (Rl, without rho) ===
  q(X) :- v(X), alpha_0(X).
  q(X) :- X = e.
  c_alpha_0(X) :- X = b.

=== ASSUMPTIONS INTRODUCED SO FAR ===
  alpha_0(X) defeated_by c_alpha_0(X)

STEP: Fact Subsumption (line 16) on rho: q(X) :- X = f.
Is ASP(<Rt, A, C>, <E+, E->, {}) satisfiable?
Answer: fails: <examples, or none>. yes.   or   ... no.
```

reference:
```
yes.
```
model:
```
fails: none. yes.
```

## t3_domain_0034 subsume (later_role_subsume): correct True, error `None`

```
=== RULES LEARNT SO FAR (Rl, without rho) ===
  q(X) :- v(X), alpha_0(X).
  c_alpha_0(X) :- X = b.

=== ASSUMPTIONS INTRODUCED SO FAR ===
  alpha_0(X) defeated_by c_alpha_0(X)

STEP: Fact Subsumption (line 16) on rho: q(X) :- X = e.
Is ASP(<Rt, A, C>, <E+, E->, {}) satisfiable?
Answer: fails: <examples, or none>. yes.   or   ... no.
```

reference:
```
yes.
```
model:
```
fails: none. yes.
```

## t3_domain_0034 subsume (other): correct True, error `None`

```
=== RULES LEARNT SO FAR (Rl, without rho) ===
  q(X) :- v(X), alpha_0(X).

=== ASSUMPTIONS INTRODUCED SO FAR ===
  alpha_0(X) defeated_by c_alpha_0(X)

STEP: Fact Subsumption (line 16) on rho: c_alpha_0(X) :- X = b.
Is ASP(<Rt, A, C>, <E+, E->, {}) satisfiable?
Answer: fails: <examples, or none>. yes.   or   ... no.
```

reference:
```
no.
```
model:
```
fails: q(b). no.
```

## t3_domain_0034 fold_candidates (other): correct True, error `None`

```
=== RULES LEARNT SO FAR (Rl, without rho) ===
  q(X) :- v(X), alpha_0(X).

=== ASSUMPTIONS INTRODUCED SO FAR ===
  alpha_0(X) defeated_by c_alpha_0(X)

STEP: applyFolding (line 17) on rho: c_alpha_0(X) :- X = b.
List every fold of rho, in order.
Answer: R2 candidates: [<rule>] [<rule>] ...
```

reference:
```
R2 candidates: [c_alpha_0(X) :- v(X).] [c_alpha_0(X) :- u(X).] [c_alpha_0(X) :- t(X).] [c_alpha_0(X) :- dom(X).]
```
model:
```
R2 candidates: [c_alpha_0(X) :- v(X).] [c_alpha_0(X) :- u(X).] [c_alpha_0(X) :- t(X).] [c_alpha_0(X) :- dom(X).]
```

## t3_domain_0034 check (other): correct True, error `None`

```
=== RULES LEARNT SO FAR (Rl, without rho) ===
  q(X) :- v(X), alpha_0(X).

=== ASSUMPTIONS INTRODUCED SO FAR ===
  alpha_0(X) defeated_by c_alpha_0(X)

STEP: the test at line 18 on rho: c_alpha_0(X) :- X = b.
with rho_f: c_alpha_0(X) :- v(X).
Is ASP(<Rt u {rho_f}, A, C>, <E+, E->, {}) satisfiable?
Answer: fails: <examples, or none>. yes.   or   ... no.
```

reference:
```
no.
```
model:
```
fails: q(c), q(f), q(e), q(d), q(a). no.
```

## t3_domain_0034 reuse_scan (other): correct True, error `None`

```
=== RULES LEARNT SO FAR (Rl, without rho) ===
  q(X) :- v(X), alpha_0(X).

=== ASSUMPTIONS INTRODUCED SO FAR ===
  alpha_0(X) defeated_by c_alpha_0(X)

STEP: applyAsmIntro (line 36) on rho_f: c_alpha_0(X) :- v(X).
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

## t3_domain_0034 reuse_check (other): correct True, error `None`

```
=== RULES LEARNT SO FAR (Rl, without rho) ===
  q(X) :- v(X), alpha_0(X).

=== ASSUMPTIONS INTRODUCED SO FAR ===
  alpha_0(X) defeated_by c_alpha_0(X)

STEP: the test at line 38 with the relative assumption alpha_0(X)
rho_d: c_alpha_0(X) :- v(X), alpha_0(X).
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

## t3_domain_0034 check (other): correct True, error `None`

```
=== RULES LEARNT SO FAR (Rl, without rho) ===
  q(X) :- v(X), alpha_0(X).

=== ASSUMPTIONS INTRODUCED SO FAR ===
  alpha_0(X) defeated_by c_alpha_0(X)

STEP: the test at line 18 on rho: c_alpha_0(X) :- X = b.
with rho_f: c_alpha_0(X) :- u(X).
Is ASP(<Rt u {rho_f}, A, C>, <E+, E->, {}) satisfiable?
Answer: fails: <examples, or none>. yes.   or   ... no.
```

reference:
```
yes.
```
model:
```
fails: none. yes.
```

# t3_domain_0031 (test, monotonic): 7 calls, stop `None`, exact True

## t3_domain_0031 role (other): correct True, error `None`

```
STEP: RoLe (lines 3-12). List the facts that lines 8-10 learn: a minimal set
of facts p(X) :- X = t, with p in T, that makes the framework a solution.
One per line: R1 p(X) :- X = t.   or: none.
```

reference:
```
R1 q(X) :- X = e.
R1 q(X) :- X = b.
R1 q(X) :- X = d.
R1 q(X) :- X = c.
```
model:
```
R1 q(X) :- X = e.
R1 q(X) :- X = b.
R1 q(X) :- X = d.
R1 q(X) :- X = c.
```

## t3_domain_0031 subsume (other): correct True, error `None`

```
=== RULES LEARNT SO FAR (Rl, without rho) ===
  q(X) :- X = b.
  q(X) :- X = d.
  q(X) :- X = c.

STEP: Fact Subsumption (line 16) on rho: q(X) :- X = e.
Is ASP(<Rt, A, C>, <E+, E->, {}) satisfiable?
Answer: fails: <examples, or none>. yes.   or   ... no.
```

reference:
```
no.
```
model:
```
fails: q(e). no.
```

## t3_domain_0031 fold_candidates (other): correct True, error `None`

```
=== RULES LEARNT SO FAR (Rl, without rho) ===
  q(X) :- X = b.
  q(X) :- X = d.
  q(X) :- X = c.

STEP: applyFolding (line 17) on rho: q(X) :- X = e.
List every fold of rho, in order.
Answer: R2 candidates: [<rule>] [<rule>] ...
```

reference:
```
R2 candidates: [q(X) :- v(X).] [q(X) :- t(X).] [q(X) :- r(X).] [q(X) :- dom(X).]
```
model:
```
R2 candidates: [q(X) :- v(X).] [q(X) :- t(X).] [q(X) :- r(X).] [q(X) :- dom(X).]
```

## t3_domain_0031 check (first_check): correct True, error `None`

```
=== RULES LEARNT SO FAR (Rl, without rho) ===
  q(X) :- X = b.
  q(X) :- X = d.
  q(X) :- X = c.

STEP: the test at line 18 on rho: q(X) :- X = e.
with rho_f: q(X) :- v(X).
Is ASP(<Rt u {rho_f}, A, C>, <E+, E->, {}) satisfiable?
Answer: fails: <examples, or none>. yes.   or   ... no.
```

reference:
```
yes.
```
model:
```
fails: none. yes.
```

## t3_domain_0031 subsume (later_role_subsume): correct True, error `None`

```
=== RULES LEARNT SO FAR (Rl, without rho) ===
  q(X) :- v(X).
  q(X) :- X = d.
  q(X) :- X = c.

STEP: Fact Subsumption (line 16) on rho: q(X) :- X = b.
Is ASP(<Rt, A, C>, <E+, E->, {}) satisfiable?
Answer: fails: <examples, or none>. yes.   or   ... no.
```

reference:
```
yes.
```
model:
```
fails: none. yes.
```

## t3_domain_0031 subsume (later_role_subsume): correct True, error `None`

```
=== RULES LEARNT SO FAR (Rl, without rho) ===
  q(X) :- v(X).
  q(X) :- X = c.

STEP: Fact Subsumption (line 16) on rho: q(X) :- X = d.
Is ASP(<Rt, A, C>, <E+, E->, {}) satisfiable?
Answer: fails: <examples, or none>. yes.   or   ... no.
```

reference:
```
yes.
```
model:
```
fails: none. yes.
```

## t3_domain_0031 subsume (later_role_subsume): correct True, error `None`

```
=== RULES LEARNT SO FAR (Rl, without rho) ===
  q(X) :- v(X).

STEP: Fact Subsumption (line 16) on rho: q(X) :- X = c.
Is ASP(<Rt, A, C>, <E+, E->, {}) satisfiable?
Answer: fails: <examples, or none>. yes.   or   ... no.
```

reference:
```
yes.
```
model:
```
fails: none. yes.
```

# t5_twopath_0002 (test, defeasible): 15 calls, stop `None`, exact False

## t5_twopath_0002 role (other): correct True, error `None`

```
STEP: RoLe (lines 3-12). List the facts that lines 8-10 learn: a minimal set
of facts p(X) :- X = t, with p in T, that makes the framework a solution.
One per line: R1 p(X) :- X = t.   or: none.
```

reference:
```
R1 p1(X) :- X = a.
R1 p1(X) :- X = c.
R1 p1(X) :- X = d.
R1 p1(X) :- X = b.
R1 p1(X) :- X = f.
```
model:
```
R1 p1(X) :- X = a.
R1 p1(X) :- X = c.
R1 p1(X) :- X = d.
R1 p1(X) :- X = b.
R1 p1(X) :- X = f.
```

## t5_twopath_0002 subsume (other): correct True, error `None`

```
=== RULES LEARNT SO FAR (Rl, without rho) ===
  p1(X) :- X = c.
  p1(X) :- X = d.
  p1(X) :- X = b.
  p1(X) :- X = f.

STEP: Fact Subsumption (line 16) on rho: p1(X) :- X = a.
Is ASP(<Rt, A, C>, <E+, E->, {}) satisfiable?
Answer: fails: <examples, or none>. yes.   or   ... no.
```

reference:
```
no.
```
model:
```
fails: p1(a). no.
```

## t5_twopath_0002 fold_candidates (other): correct False, error `None`

```
=== RULES LEARNT SO FAR (Rl, without rho) ===
  p1(X) :- X = c.
  p1(X) :- X = d.
  p1(X) :- X = b.
  p1(X) :- X = f.

STEP: applyFolding (line 17) on rho: p1(X) :- X = a.
List every fold of rho, in order.
Answer: R2 candidates: [<rule>] [<rule>] ...
```

reference:
```
R2 candidates: [p1(X) :- s(X).] [p1(X) :- q1(X).] [p1(X) :- p(X).] [p1(X) :- r1(X).] [p1(X) :- dom(X).]
```
model:
```
R2 candidates: [p1(X) :- q1(X).] [p1(X) :- p(X).] [p1(X) :- r1(X).] [p1(X) :- dom(X).]
```

## t5_twopath_0002 check (first_check): correct True, error `None`

```
=== RULES LEARNT SO FAR (Rl, without rho) ===
  p1(X) :- X = c.
  p1(X) :- X = d.
  p1(X) :- X = b.
  p1(X) :- X = f.

STEP: the test at line 18 on rho: p1(X) :- X = a.
with rho_f: p1(X) :- q1(X).
Is ASP(<Rt u {rho_f}, A, C>, <E+, E->, {}) satisfiable?
Answer: fails: <examples, or none>. yes.   or   ... no.
```

reference:
```
no.
```
model:
```
fails: p1(g). no.
```

## t5_twopath_0002 reuse_scan (other): correct True, error `None`

```
=== RULES LEARNT SO FAR (Rl, without rho) ===
  p1(X) :- X = c.
  p1(X) :- X = d.
  p1(X) :- X = b.
  p1(X) :- X = f.

STEP: applyAsmIntro (line 36) on rho_f: p1(X) :- q1(X).
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

## t5_twopath_0002 contrary_facts (other): correct True, error `None`

```
=== RULES LEARNT SO FAR (Rl, without rho) ===
  p1(X) :- X = c.
  p1(X) :- X = d.
  p1(X) :- X = b.
  p1(X) :- X = f.

STEP: lines 41-44 on rho_f: p1(X) :- q1(X).
A new assumption alpha_0(X), with contrary c_alpha_0(X), gives
rho_d: p1(X) :- q1(X), alpha_0(X).
List the facts for c_alpha_0 in S := getAS(ASP(F, <E+, E->, {c_alpha_0})), where
F = <Rt u {rho_d}, A u {alpha_0(X)}, C u {alpha_0(X) -> c_alpha_0(X)}>; lines 23-25 learn them.
One per line: R1 c_alpha_0(X) :- X = t.   or: none.
```

reference:
```
R1 c_alpha_0(X) :- X = g.
```
model:
```
R1 c_alpha_0(X) :- X = g.
```

## t5_twopath_0002 subsume (later_role_subsume): correct True, error `None`

```
=== RULES LEARNT SO FAR (Rl, without rho) ===
  p1(X) :- q1(X), alpha_0(X).
  p1(X) :- X = d.
  p1(X) :- X = b.
  p1(X) :- X = f.
  c_alpha_0(X) :- X = g.

=== ASSUMPTIONS INTRODUCED SO FAR ===
  alpha_0(X) defeated_by c_alpha_0(X)

STEP: Fact Subsumption (line 16) on rho: p1(X) :- X = c.
Is ASP(<Rt, A, C>, <E+, E->, {}) satisfiable?
Answer: fails: <examples, or none>. yes.   or   ... no.
```

reference:
```
no.
```
model:
```
fails: p1(c). no.
```

## t5_twopath_0002 fold_candidates (other): correct True, error `None`

```
=== RULES LEARNT SO FAR (Rl, without rho) ===
  p1(X) :- q1(X), alpha_0(X).
  p1(X) :- X = d.
  p1(X) :- X = b.
  p1(X) :- X = f.
  c_alpha_0(X) :- X = g.

=== ASSUMPTIONS INTRODUCED SO FAR ===
  alpha_0(X) defeated_by c_alpha_0(X)

STEP: applyFolding (line 17) on rho: p1(X) :- X = c.
List every fold of rho, in order.
Answer: R2 candidates: [<rule>] [<rule>] ...
```

reference:
```
R2 candidates: [p1(X) :- s(X).] [p1(X) :- dom(X).]
```
model:
```
R2 candidates: [p1(X) :- s(X).] [p1(X) :- dom(X).]
```

## t5_twopath_0002 check (second_path_check): correct True, error `None`

```
=== RULES LEARNT SO FAR (Rl, without rho) ===
  p1(X) :- q1(X), alpha_0(X).
  p1(X) :- X = d.
  p1(X) :- X = b.
  p1(X) :- X = f.
  c_alpha_0(X) :- X = g.

=== ASSUMPTIONS INTRODUCED SO FAR ===
  alpha_0(X) defeated_by c_alpha_0(X)

STEP: the test at line 18 on rho: p1(X) :- X = c.
with rho_f: p1(X) :- s(X).
Is ASP(<Rt u {rho_f}, A, C>, <E+, E->, {}) satisfiable?
Answer: fails: <examples, or none>. yes.   or   ... no.
```

reference:
```
yes.
```
model:
```
fails: none. yes.
```

## t5_twopath_0002 subsume (later_role_subsume): correct True, error `None`

```
=== RULES LEARNT SO FAR (Rl, without rho) ===
  p1(X) :- q1(X), alpha_0(X).
  p1(X) :- s(X).
  p1(X) :- X = b.
  p1(X) :- X = f.
  c_alpha_0(X) :- X = g.

=== ASSUMPTIONS INTRODUCED SO FAR ===
  alpha_0(X) defeated_by c_alpha_0(X)

STEP: Fact Subsumption (line 16) on rho: p1(X) :- X = d.
Is ASP(<Rt, A, C>, <E+, E->, {}) satisfiable?
Answer: fails: <examples, or none>. yes.   or   ... no.
```

reference:
```
yes.
```
model:
```
fails: none. yes.
```

## t5_twopath_0002 subsume (later_role_subsume): correct True, error `None`

```
=== RULES LEARNT SO FAR (Rl, without rho) ===
  p1(X) :- q1(X), alpha_0(X).
  p1(X) :- s(X).
  p1(X) :- X = f.
  c_alpha_0(X) :- X = g.

=== ASSUMPTIONS INTRODUCED SO FAR ===
  alpha_0(X) defeated_by c_alpha_0(X)

STEP: Fact Subsumption (line 16) on rho: p1(X) :- X = b.
Is ASP(<Rt, A, C>, <E+, E->, {}) satisfiable?
Answer: fails: <examples, or none>. yes.   or   ... no.
```

reference:
```
yes.
```
model:
```
fails: none. yes.
```

## t5_twopath_0002 subsume (later_role_subsume): correct True, error `None`

```
=== RULES LEARNT SO FAR (Rl, without rho) ===
  p1(X) :- q1(X), alpha_0(X).
  p1(X) :- s(X).
  c_alpha_0(X) :- X = g.

=== ASSUMPTIONS INTRODUCED SO FAR ===
  alpha_0(X) defeated_by c_alpha_0(X)

STEP: Fact Subsumption (line 16) on rho: p1(X) :- X = f.
Is ASP(<Rt, A, C>, <E+, E->, {}) satisfiable?
Answer: fails: <examples, or none>. yes.   or   ... no.
```

reference:
```
yes.
```
model:
```
fails: none. yes.
```

## t5_twopath_0002 subsume (other): correct True, error `None`

```
=== RULES LEARNT SO FAR (Rl, without rho) ===
  p1(X) :- q1(X), alpha_0(X).
  p1(X) :- s(X).

=== ASSUMPTIONS INTRODUCED SO FAR ===
  alpha_0(X) defeated_by c_alpha_0(X)

STEP: Fact Subsumption (line 16) on rho: c_alpha_0(X) :- X = g.
Is ASP(<Rt, A, C>, <E+, E->, {}) satisfiable?
Answer: fails: <examples, or none>. yes.   or   ... no.
```

reference:
```
no.
```
model:
```
fails: p1(g). no.
```

## t5_twopath_0002 fold_candidates (other): correct False, error `None`

```
=== RULES LEARNT SO FAR (Rl, without rho) ===
  p1(X) :- q1(X), alpha_0(X).
  p1(X) :- s(X).

=== ASSUMPTIONS INTRODUCED SO FAR ===
  alpha_0(X) defeated_by c_alpha_0(X)

STEP: applyFolding (line 17) on rho: c_alpha_0(X) :- X = g.
List every fold of rho, in order.
Answer: R2 candidates: [<rule>] [<rule>] ...
```

reference:
```
R2 candidates: [c_alpha_0(X) :- q1(X).] [c_alpha_0(X) :- t(X).] [c_alpha_0(X) :- p(X).] [c_alpha_0(X) :- r1(X).] [c_alpha_0(X) :- dom(X).]
```
model:
```
R2 candidates: [c_alpha_0(X) :- p(X).] [c_alpha_0(X) :- r1(X).] [c_alpha_0(X) :- dom(X).]
```

## t5_twopath_0002 check (other): correct True, error `None`

```
=== RULES LEARNT SO FAR (Rl, without rho) ===
  p1(X) :- q1(X), alpha_0(X).
  p1(X) :- s(X).

=== ASSUMPTIONS INTRODUCED SO FAR ===
  alpha_0(X) defeated_by c_alpha_0(X)

STEP: the test at line 18 on rho: c_alpha_0(X) :- X = g.
with rho_f: c_alpha_0(X) :- p(X).
Is ASP(<Rt u {rho_f}, A, C>, <E+, E->, {}) satisfiable?
Answer: fails: <examples, or none>. yes.   or   ... no.
```

reference:
```
yes.
```
model:
```
fails: none. yes.
```

