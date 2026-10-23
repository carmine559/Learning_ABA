# Hand audit: every call of 5 chained runs of results/sft-step/s2_s1/chained

# t8_decoy_0040 (heldout, decoy_first): 6 calls, stop `None`, exact True

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

## t8_decoy_0040 subsume (other): correct True, error `None`

```
=== RULES LEARNT SO FAR (Rl, without rho) ===
  v(X) :- X = c.
  v(X) :- X = a.

STEP: Fact Subsumption (line 16) on rho: v(X) :- X = b.
Is ASP(<Rt, A, C>, <E+, E->, {}) satisfiable?
Answer: fails: <examples, or none>. yes.   or   ... no.
```

reference:
```
no.
```
model:
```
fails: v(b). no.
```

## t8_decoy_0040 fold_candidates (other): correct True, error `None`

```
=== RULES LEARNT SO FAR (Rl, without rho) ===
  v(X) :- X = c.
  v(X) :- X = a.

STEP: applyFolding (line 17) on rho: v(X) :- X = b.
List every fold of rho, in order.
Answer: R2 candidates: [<rule>] [<rule>] ...
```

reference:
```
R2 candidates: [v(X) :- p(X).] [v(X) :- q(X).] [v(X) :- dom(X).]
```
model:
```
R2 candidates: [v(X) :- p(X).] [v(X) :- q(X).] [v(X) :- dom(X).]
```

## t8_decoy_0040 check (first_check): correct True, error `None`

```
=== RULES LEARNT SO FAR (Rl, without rho) ===
  v(X) :- X = c.
  v(X) :- X = a.

STEP: the test at line 18 on rho: v(X) :- X = b.
with rho_f: v(X) :- p(X).
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
  v(X) :- p(X).
  v(X) :- X = a.

STEP: Fact Subsumption (line 16) on rho: v(X) :- X = c.
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
  v(X) :- p(X).

STEP: Fact Subsumption (line 16) on rho: v(X) :- X = a.
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
R1 v(X) :- X = c.
R1 v(X) :- X = a.
R1 v(X) :- X = b.
```
model:
```
R1 v(X) :- X = c.
R1 v(X) :- X = a.
R1 v(X) :- X = b.
```

## t1_base_0025 subsume (other): correct True, error `None`

```
=== RULES LEARNT SO FAR (Rl, without rho) ===
  v(X) :- X = a.
  v(X) :- X = b.

STEP: Fact Subsumption (line 16) on rho: v(X) :- X = c.
Is ASP(<Rt, A, C>, <E+, E->, {}) satisfiable?
Answer: fails: <examples, or none>. yes.   or   ... no.
```

reference:
```
no.
```
model:
```
fails: v(c). no.
```

## t1_base_0025 fold_candidates (other): correct True, error `None`

```
=== RULES LEARNT SO FAR (Rl, without rho) ===
  v(X) :- X = a.
  v(X) :- X = b.

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

## t1_base_0025 check (first_check): correct True, error `None`

```
=== RULES LEARNT SO FAR (Rl, without rho) ===
  v(X) :- X = a.
  v(X) :- X = b.

STEP: the test at line 18 on rho: v(X) :- X = c.
with rho_f: v(X) :- p(X).
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
  v(X) :- p(X).
  v(X) :- X = b.

STEP: Fact Subsumption (line 16) on rho: v(X) :- X = a.
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
  v(X) :- p(X).

STEP: Fact Subsumption (line 16) on rho: v(X) :- X = b.
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

## t3_domain_0034 subsume (other): correct True, error `None`

```
=== RULES LEARNT SO FAR (Rl, without rho) ===
  v(X) :- X = c.
  v(X) :- X = d.
  v(X) :- X = f.
  v(X) :- X = e.

STEP: Fact Subsumption (line 16) on rho: v(X) :- X = a.
Is ASP(<Rt, A, C>, <E+, E->, {}) satisfiable?
Answer: fails: <examples, or none>. yes.   or   ... no.
```

reference:
```
no.
```
model:
```
fails: v(a). no.
```

## t3_domain_0034 fold_candidates (other): correct True, error `None`

```
=== RULES LEARNT SO FAR (Rl, without rho) ===
  v(X) :- X = c.
  v(X) :- X = d.
  v(X) :- X = f.
  v(X) :- X = e.

STEP: applyFolding (line 17) on rho: v(X) :- X = a.
List every fold of rho, in order.
Answer: R2 candidates: [<rule>] [<rule>] ...
```

reference:
```
R2 candidates: [v(X) :- p(X).] [v(X) :- s(X).] [v(X) :- dom(X).]
```
model:
```
R2 candidates: [v(X) :- p(X).] [v(X) :- s(X).] [v(X) :- dom(X).]
```

## t3_domain_0034 check (first_check): correct True, error `None`

```
=== RULES LEARNT SO FAR (Rl, without rho) ===
  v(X) :- X = c.
  v(X) :- X = d.
  v(X) :- X = f.
  v(X) :- X = e.

STEP: the test at line 18 on rho: v(X) :- X = a.
with rho_f: v(X) :- p(X).
Is ASP(<Rt u {rho_f}, A, C>, <E+, E->, {}) satisfiable?
Answer: fails: <examples, or none>. yes.   or   ... no.
```

reference:
```
no.
```
model:
```
fails: v(b). no.
```

## t3_domain_0034 reuse_scan (other): correct True, error `None`

```
=== RULES LEARNT SO FAR (Rl, without rho) ===
  v(X) :- X = c.
  v(X) :- X = d.
  v(X) :- X = f.
  v(X) :- X = e.

STEP: applyAsmIntro (line 36) on rho_f: v(X) :- p(X).
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
  v(X) :- X = c.
  v(X) :- X = d.
  v(X) :- X = f.
  v(X) :- X = e.

STEP: lines 41-44 on rho_f: v(X) :- p(X).
A new assumption alpha_0(X), with contrary c_alpha_0(X), gives
rho_d: v(X) :- p(X), alpha_0(X).
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
  v(X) :- p(X), alpha_0(X).
  v(X) :- X = d.
  v(X) :- X = f.
  v(X) :- X = e.
  c_alpha_0(X) :- X = b.

=== ASSUMPTIONS INTRODUCED SO FAR ===
  alpha_0(X) defeated_by c_alpha_0(X)

STEP: Fact Subsumption (line 16) on rho: v(X) :- X = c.
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
  v(X) :- p(X), alpha_0(X).
  v(X) :- X = f.
  v(X) :- X = e.
  c_alpha_0(X) :- X = b.

=== ASSUMPTIONS INTRODUCED SO FAR ===
  alpha_0(X) defeated_by c_alpha_0(X)

STEP: Fact Subsumption (line 16) on rho: v(X) :- X = d.
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
  v(X) :- p(X), alpha_0(X).
  v(X) :- X = e.
  c_alpha_0(X) :- X = b.

=== ASSUMPTIONS INTRODUCED SO FAR ===
  alpha_0(X) defeated_by c_alpha_0(X)

STEP: Fact Subsumption (line 16) on rho: v(X) :- X = f.
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
  v(X) :- p(X), alpha_0(X).
  c_alpha_0(X) :- X = b.

=== ASSUMPTIONS INTRODUCED SO FAR ===
  alpha_0(X) defeated_by c_alpha_0(X)

STEP: Fact Subsumption (line 16) on rho: v(X) :- X = e.
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
  v(X) :- p(X), alpha_0(X).

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
fails: v(b). no.
```

## t3_domain_0034 fold_candidates (other): correct True, error `None`

```
=== RULES LEARNT SO FAR (Rl, without rho) ===
  v(X) :- p(X), alpha_0(X).

=== ASSUMPTIONS INTRODUCED SO FAR ===
  alpha_0(X) defeated_by c_alpha_0(X)

STEP: applyFolding (line 17) on rho: c_alpha_0(X) :- X = b.
List every fold of rho, in order.
Answer: R2 candidates: [<rule>] [<rule>] ...
```

reference:
```
R2 candidates: [c_alpha_0(X) :- p(X).] [c_alpha_0(X) :- q(X).] [c_alpha_0(X) :- s(X).] [c_alpha_0(X) :- dom(X).]
```
model:
```
R2 candidates: [c_alpha_0(X) :- p(X).] [c_alpha_0(X) :- q(X).] [c_alpha_0(X) :- s(X).] [c_alpha_0(X) :- dom(X).]
```

## t3_domain_0034 check (other): correct True, error `None`

```
=== RULES LEARNT SO FAR (Rl, without rho) ===
  v(X) :- p(X), alpha_0(X).

=== ASSUMPTIONS INTRODUCED SO FAR ===
  alpha_0(X) defeated_by c_alpha_0(X)

STEP: the test at line 18 on rho: c_alpha_0(X) :- X = b.
with rho_f: c_alpha_0(X) :- p(X).
Is ASP(<Rt u {rho_f}, A, C>, <E+, E->, {}) satisfiable?
Answer: fails: <examples, or none>. yes.   or   ... no.
```

reference:
```
no.
```
model:
```
fails: v(c), v(f), v(e), v(d), v(a). no.
```

## t3_domain_0034 reuse_scan (other): correct True, error `None`

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

## t3_domain_0034 reuse_check (other): correct True, error `None`

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

## t3_domain_0034 check (other): correct True, error `None`

```
=== RULES LEARNT SO FAR (Rl, without rho) ===
  v(X) :- p(X), alpha_0(X).

=== ASSUMPTIONS INTRODUCED SO FAR ===
  alpha_0(X) defeated_by c_alpha_0(X)

STEP: the test at line 18 on rho: c_alpha_0(X) :- X = b.
with rho_f: c_alpha_0(X) :- q(X).
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

## t3_domain_0031 subsume (other): correct True, error `None`

```
=== RULES LEARNT SO FAR (Rl, without rho) ===
  v(X) :- X = b.
  v(X) :- X = d.
  v(X) :- X = c.

STEP: Fact Subsumption (line 16) on rho: v(X) :- X = e.
Is ASP(<Rt, A, C>, <E+, E->, {}) satisfiable?
Answer: fails: <examples, or none>. yes.   or   ... no.
```

reference:
```
no.
```
model:
```
fails: v(e). no.
```

## t3_domain_0031 fold_candidates (other): correct True, error `None`

```
=== RULES LEARNT SO FAR (Rl, without rho) ===
  v(X) :- X = b.
  v(X) :- X = d.
  v(X) :- X = c.

STEP: applyFolding (line 17) on rho: v(X) :- X = e.
List every fold of rho, in order.
Answer: R2 candidates: [<rule>] [<rule>] ...
```

reference:
```
R2 candidates: [v(X) :- p(X).] [v(X) :- r(X).] [v(X) :- s(X).] [v(X) :- dom(X).]
```
model:
```
R2 candidates: [v(X) :- p(X).] [v(X) :- r(X).] [v(X) :- s(X).] [v(X) :- dom(X).]
```

## t3_domain_0031 check (first_check): correct True, error `None`

```
=== RULES LEARNT SO FAR (Rl, without rho) ===
  v(X) :- X = b.
  v(X) :- X = d.
  v(X) :- X = c.

STEP: the test at line 18 on rho: v(X) :- X = e.
with rho_f: v(X) :- p(X).
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
  v(X) :- p(X).
  v(X) :- X = d.
  v(X) :- X = c.

STEP: Fact Subsumption (line 16) on rho: v(X) :- X = b.
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
  v(X) :- p(X).
  v(X) :- X = c.

STEP: Fact Subsumption (line 16) on rho: v(X) :- X = d.
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
  v(X) :- p(X).

STEP: Fact Subsumption (line 16) on rho: v(X) :- X = c.
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

# t5_twopath_0002 (test, defeasible): 18 calls, stop `None`, exact True

## t5_twopath_0002 role (other): correct True, error `None`

```
STEP: RoLe (lines 3-12). List the facts that lines 8-10 learn: a minimal set
of facts p(X) :- X = t, with p in T, that makes the framework a solution.
One per line: R1 p(X) :- X = t.   or: none.
```

reference:
```
R1 r1(X) :- X = a.
R1 r1(X) :- X = c.
R1 r1(X) :- X = d.
R1 r1(X) :- X = b.
R1 r1(X) :- X = f.
```
model:
```
R1 r1(X) :- X = a.
R1 r1(X) :- X = d.
R1 r1(X) :- X = c.
R1 r1(X) :- X = b.
R1 r1(X) :- X = f.
```

## t5_twopath_0002 subsume (other): correct True, error `None`

```
=== RULES LEARNT SO FAR (Rl, without rho) ===
  r1(X) :- X = c.
  r1(X) :- X = d.
  r1(X) :- X = b.
  r1(X) :- X = f.

STEP: Fact Subsumption (line 16) on rho: r1(X) :- X = a.
Is ASP(<Rt, A, C>, <E+, E->, {}) satisfiable?
Answer: fails: <examples, or none>. yes.   or   ... no.
```

reference:
```
no.
```
model:
```
fails: r1(a). no.
```

## t5_twopath_0002 fold_candidates (other): correct True, error `None`

```
=== RULES LEARNT SO FAR (Rl, without rho) ===
  r1(X) :- X = c.
  r1(X) :- X = d.
  r1(X) :- X = b.
  r1(X) :- X = f.

STEP: applyFolding (line 17) on rho: r1(X) :- X = a.
List every fold of rho, in order.
Answer: R2 candidates: [<rule>] [<rule>] ...
```

reference:
```
R2 candidates: [r1(X) :- p(X).] [r1(X) :- q(X).] [r1(X) :- t(X).] [r1(X) :- u(X).] [r1(X) :- dom(X).]
```
model:
```
R2 candidates: [r1(X) :- p(X).] [r1(X) :- q(X).] [r1(X) :- t(X).] [r1(X) :- u(X).] [r1(X) :- dom(X).]
```

## t5_twopath_0002 check (first_check): correct True, error `None`

```
=== RULES LEARNT SO FAR (Rl, without rho) ===
  r1(X) :- X = c.
  r1(X) :- X = d.
  r1(X) :- X = b.
  r1(X) :- X = f.

STEP: the test at line 18 on rho: r1(X) :- X = a.
with rho_f: r1(X) :- p(X).
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
  r1(X) :- p(X).
  r1(X) :- X = d.
  r1(X) :- X = b.
  r1(X) :- X = f.

STEP: Fact Subsumption (line 16) on rho: r1(X) :- X = c.
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
  r1(X) :- p(X).
  r1(X) :- X = b.
  r1(X) :- X = f.

STEP: Fact Subsumption (line 16) on rho: r1(X) :- X = d.
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
  r1(X) :- p(X).
  r1(X) :- X = f.

STEP: Fact Subsumption (line 16) on rho: r1(X) :- X = b.
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
  r1(X) :- p(X).

STEP: Fact Subsumption (line 16) on rho: r1(X) :- X = f.
Is ASP(<Rt, A, C>, <E+, E->, {}) satisfiable?
Answer: fails: <examples, or none>. yes.   or   ... no.
```

reference:
```
no.
```
model:
```
fails: r1(f). no.
```

## t5_twopath_0002 fold_candidates (other): correct True, error `None`

```
=== RULES LEARNT SO FAR (Rl, without rho) ===
  r1(X) :- p(X).

STEP: applyFolding (line 17) on rho: r1(X) :- X = f.
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

## t5_twopath_0002 check (second_path_check): correct True, error `None`

```
=== RULES LEARNT SO FAR (Rl, without rho) ===
  r1(X) :- p(X).

STEP: the test at line 18 on rho: r1(X) :- X = f.
with rho_f: r1(X) :- q(X).
Is ASP(<Rt u {rho_f}, A, C>, <E+, E->, {}) satisfiable?
Answer: fails: <examples, or none>. yes.   or   ... no.
```

reference:
```
no.
```
model:
```
fails: r1(g). no.
```

## t5_twopath_0002 reuse_scan (other): correct True, error `None`

```
=== RULES LEARNT SO FAR (Rl, without rho) ===
  r1(X) :- p(X).

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

## t5_twopath_0002 contrary_facts (other): correct True, error `None`

```
=== RULES LEARNT SO FAR (Rl, without rho) ===
  r1(X) :- p(X).

STEP: lines 41-44 on rho_f: r1(X) :- q(X).
A new assumption alpha_0(X), with contrary c_alpha_0(X), gives
rho_d: r1(X) :- q(X), alpha_0(X).
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

## t5_twopath_0002 subsume (other): correct True, error `None`

```
=== RULES LEARNT SO FAR (Rl, without rho) ===
  r1(X) :- p(X).
  r1(X) :- q(X), alpha_0(X).

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
fails: r1(g). no.
```

## t5_twopath_0002 fold_candidates (other): correct True, error `None`

```
=== RULES LEARNT SO FAR (Rl, without rho) ===
  r1(X) :- p(X).
  r1(X) :- q(X), alpha_0(X).

=== ASSUMPTIONS INTRODUCED SO FAR ===
  alpha_0(X) defeated_by c_alpha_0(X)

STEP: applyFolding (line 17) on rho: c_alpha_0(X) :- X = g.
List every fold of rho, in order.
Answer: R2 candidates: [<rule>] [<rule>] ...
```

reference:
```
R2 candidates: [c_alpha_0(X) :- q(X).] [c_alpha_0(X) :- s(X).] [c_alpha_0(X) :- t(X).] [c_alpha_0(X) :- u(X).] [c_alpha_0(X) :- dom(X).]
```
model:
```
R2 candidates: [c_alpha_0(X) :- q(X).] [c_alpha_0(X) :- s(X).] [c_alpha_0(X) :- t(X).] [c_alpha_0(X) :- u(X).] [c_alpha_0(X) :- dom(X).]
```

## t5_twopath_0002 check (other): correct True, error `None`

```
=== RULES LEARNT SO FAR (Rl, without rho) ===
  r1(X) :- p(X).
  r1(X) :- q(X), alpha_0(X).

=== ASSUMPTIONS INTRODUCED SO FAR ===
  alpha_0(X) defeated_by c_alpha_0(X)

STEP: the test at line 18 on rho: c_alpha_0(X) :- X = g.
with rho_f: c_alpha_0(X) :- q(X).
Is ASP(<Rt u {rho_f}, A, C>, <E+, E->, {}) satisfiable?
Answer: fails: <examples, or none>. yes.   or   ... no.
```

reference:
```
no.
```
model:
```
fails: r1(f). no.
```

## t5_twopath_0002 reuse_scan (other): correct True, error `None`

```
=== RULES LEARNT SO FAR (Rl, without rho) ===
  r1(X) :- p(X).
  r1(X) :- q(X), alpha_0(X).

=== ASSUMPTIONS INTRODUCED SO FAR ===
  alpha_0(X) defeated_by c_alpha_0(X)

STEP: applyAsmIntro (line 36) on rho_f: c_alpha_0(X) :- q(X).
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

## t5_twopath_0002 reuse_check (other): correct True, error `None`

```
=== RULES LEARNT SO FAR (Rl, without rho) ===
  r1(X) :- p(X).
  r1(X) :- q(X), alpha_0(X).

=== ASSUMPTIONS INTRODUCED SO FAR ===
  alpha_0(X) defeated_by c_alpha_0(X)

STEP: the test at line 38 with the relative assumption alpha_0(X)
rho_d: c_alpha_0(X) :- q(X), alpha_0(X).
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

## t5_twopath_0002 check (other): correct True, error `None`

```
=== RULES LEARNT SO FAR (Rl, without rho) ===
  r1(X) :- p(X).
  r1(X) :- q(X), alpha_0(X).

=== ASSUMPTIONS INTRODUCED SO FAR ===
  alpha_0(X) defeated_by c_alpha_0(X)

STEP: the test at line 18 on rho: c_alpha_0(X) :- X = g.
with rho_f: c_alpha_0(X) :- s(X).
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

