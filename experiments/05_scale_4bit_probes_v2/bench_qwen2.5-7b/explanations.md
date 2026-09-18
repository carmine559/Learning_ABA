# Per-problem explanations


## Mode: direct

### nixon_diamond_anon  (gen@1=0%, gen@k=no)
On 'nixon_diamond_anon', the candidate is NOT a legal solution: new assumption predicate 'p1' repurposes background non-assumption predicate 'p1'. The outcome below is reported for diagnosis only. On 'nixon_diamond_anon', the model failed to fit the training examples. It introduced 1 new rule(s): 1 assumption guarded. It also introduced the assumption(s) p1(X) to make a rule defeasible, capturing exceptions. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- p(X), w(X).']; p1: model wrote ['nothing'], reference has ['p1(X) :- p(X), alpha_0(X).']; v: model wrote ['v(X) :- p1(X), s(X), w(X).'], reference has ['v(X) :- q(X).'].

### flies_anon  (gen@1=0%, gen@k=no)
On 'flies_anon', the model failed to fit the training examples. It introduced 1 new rule(s): 1 assumption guarded. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; t: model wrote ['t(X) :- p(X), r(X).'], reference has ['t(X) :- p(X), alpha_0(X).'].

### tax_law_anon  (gen@1=0%, gen@k=no)
On 'tax_law_anon', the model failed to fit the training examples. It introduced 2 new rule(s): 1 assumption guarded, 1 contrary rule. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- p(X), alpha_1(X).']; c_alpha_1: model wrote ['nothing'], reference has ['c_alpha_1(X) :- p(X), alpha_0(X).']; t: model wrote ['t(X) :- r(X).'], reference has ['nothing'].

### t1_mono_0000_anon  (gen@1=0%, gen@k=no)
On 't1_mono_0000_anon', the model failed to fit the training examples. It introduced 2 new rule(s): 2 intensional copy. The rule 'v(X) :- s(X), v_def(X).' generalises by conditioning the target on the background predicate(s) s, v_def, so it applies to any constant satisfying them — including unseen ones. The rule 'c_v_def(X) :- v_notdef(X).' generalises by conditioning the target on the background predicate(s) v_notdef, so it applies to any constant satisfying them — including unseen ones. It also introduced the assumption(s) v_def(X) to make a rule defeasible, capturing exceptions. It differs from the symbolic reference on: c_v_def: model wrote ['c_v_def(X) :- v_notdef(X).'], reference has ['nothing']; v: model wrote ['v(X) :- s(X), v_def(X).'], reference has ['v(X) :- p(X).'].

### t1_mono_0001_anon  (gen@1=0%, gen@k=no)
On 't1_mono_0001_anon', the model failed to fit the training examples. It introduced 1 new rule(s): 1 assumption guarded. It differs from the symbolic reference on: u: model wrote ['u(X) :- r(X), t(X).'], reference has ['u(X) :- p(X).'].

### t1_mono_0002_anon  (gen@1=0%, gen@k=no)
On 't1_mono_0002_anon', the model failed to fit the training examples. It introduced 2 new rule(s): 2 intensional copy. The rule 'v(X) :- s(X), v_def(X).' generalises by conditioning the target on the background predicate(s) s, v_def, so it applies to any constant satisfying them — including unseen ones. The rule 'c_v_def(X) :- v_f_ex(X).' generalises by conditioning the target on the background predicate(s) v_f_ex, so it applies to any constant satisfying them — including unseen ones. It also introduced the assumption(s) v_def(X) to make a rule defeasible, capturing exceptions. It differs from the symbolic reference on: c_v_def: model wrote ['c_v_def(X) :- v_f_ex(X).'], reference has ['nothing']; v: model wrote ['v(X) :- s(X), v_def(X).'], reference has ['v(X) :- p(X).'].

### t1_mono_0003_anon  (gen@1=0%, gen@k=no)
On 't1_mono_0003_anon', the model failed to fit the training examples. It introduced 1 new rule(s): 1 assumption guarded. It differs from the symbolic reference on: v: model wrote ['v(X) :- s(X), u(X).'], reference has ['v(X) :- p(X).'].

### t1_mono_0004_anon  (gen@1=0%, gen@k=no)
On 't1_mono_0004_anon', the model failed to fit the training examples. It introduced 2 new rule(s): 2 intensional copy. The rule 'v(X) :- s(X), v_def(X).' generalises by conditioning the target on the background predicate(s) s, v_def, so it applies to any constant satisfying them — including unseen ones. The rule 'c_v_def(X) :- v_notdef(X).' generalises by conditioning the target on the background predicate(s) v_notdef, so it applies to any constant satisfying them — including unseen ones. It also introduced the assumption(s) v_def(X) to make a rule defeasible, capturing exceptions. It differs from the symbolic reference on: c_v_def: model wrote ['c_v_def(X) :- v_notdef(X).'], reference has ['nothing']; v: model wrote ['v(X) :- s(X), v_def(X).'], reference has ['v(X) :- p(X).'].

### t1_mono_0005_anon  (gen@1=0%, gen@k=no)
On 't1_mono_0005_anon', the model failed to fit the training examples. It introduced 1 new rule(s): 1 assumption guarded. It differs from the symbolic reference on: v: model wrote ['v(X) :- s(X), u(X).'], reference has ['v(X) :- p(X).'].

### t1_mono_0006_anon  (gen@1=0%, gen@k=no)
On 't1_mono_0006_anon', the model failed to fit the training examples. It introduced 1 new rule(s): 1 assumption guarded. It differs from the symbolic reference on: v: model wrote ['v(X) :- s(X), u(X).'], reference has ['v(X) :- p(X).'].

### t1_mono_0007_anon  (gen@1=33%, gen@k=yes)
On 't1_mono_0007_anon', the model produced a framework that fits the training examples and solves the full problem in one stable extension. It introduced 2 new rule(s): 1 assumption guarded, 1 intensional copy. The rule 'v(X) :- p(X), u(X).' generalises by conditioning the target on the background predicate(s) p, u, so it applies to any constant satisfying them — including unseen ones. The rule 'v(X) :- q(X).' generalises by conditioning the target on the background predicate(s) q, so it applies to any constant satisfying them — including unseen ones. Semantically, the learned framework is equivalent to the symbolic reference (same entailments over the whole domain), even though some rules are written differently.

### t1_mono_0008_anon  (gen@1=0%, gen@k=no)
On 't1_mono_0008_anon', the model failed to fit the training examples. It introduced 2 new rule(s): 1 intensional copy, 1 contrary rule. The rule 'u(X) :- p(X), r(X).' generalises by conditioning the target on the background predicate(s) p, r, so it applies to any constant satisfying them — including unseen ones. The rule 'r(X) :- t(X).' generalises by conditioning the target on the background predicate(s) t, so it applies to any constant satisfying them — including unseen ones. It differs from the symbolic reference on: r: model wrote ['r(X) :- t(X).'], reference has ['nothing']; u: model wrote ['u(X) :- p(X), r(X).'], reference has ['u(X) :- p(X).'].

### t1_mono_0009_anon  (gen@1=0%, gen@k=no)
On 't1_mono_0009_anon', the candidate is NOT a legal solution: flatness violated: assumption 'v' used as rule head. The outcome below is reported for diagnosis only. On 't1_mono_0009_anon', the model failed to fit the training examples. It introduced 2 new rule(s): 1 intensional copy, 1 ground fact. The rule 'v(X) :- s(X), v(X) defeated_by c_v(X).' generalises by conditioning the target on the background predicate(s) s, v, so it applies to any constant satisfying them — including unseen ones. It also introduced the assumption(s) v(f) to make a rule defeasible, capturing exceptions. It differs from the symbolic reference on: c_v: model wrote ['c_v(X) :- X = f.'], reference has ['nothing']; v: model wrote ['v(X) :- s(X), v(X) defeated_by c_v(X).'], reference has ['v(X) :- p(X).'].

### t1_mono_0010_anon  (gen@1=0%, gen@k=no)
On 't1_mono_0010_anon', the model failed to fit the training examples. It introduced 1 new rule(s): 1 assumption guarded. It differs from the symbolic reference on: v: model wrote ['v(X) :- s(X), u(X).'], reference has ['v(X) :- p(X).'].

### t1_mono_0011_anon  (gen@1=0%, gen@k=no)
On 't1_mono_0011_anon', the model failed to fit the training examples. It introduced 2 new rule(s): 1 assumption guarded, 1 contrary rule. It differs from the symbolic reference on: s: model wrote ['s(X) :- t(X), u(X).'], reference has ['nothing']; v: model wrote ['v(X) :- v(X), u(X).'], reference has ['v(X) :- p(X).'].

### t1_mono_0012_anon  (gen@1=0%, gen@k=no)
On 't1_mono_0012_anon', the model failed to fit the training examples. It introduced 1 new rule(s): 1 assumption guarded. It differs from the symbolic reference on: v: model wrote ['v(X) :- s(X), u(X).'], reference has ['v(X) :- p(X).'].

### t1_mono_0013_anon  (gen@1=0%, gen@k=no)
On 't1_mono_0013_anon', the model failed to fit the training examples. It introduced 1 new rule(s): 1 assumption guarded. It differs from the symbolic reference on: v: model wrote ['v(X) :- s(X), u(X).'], reference has ['v(X) :- p(X).'].

### t1_mono_0014_anon  (gen@1=0%, gen@k=no)
On 't1_mono_0014_anon', the model failed to fit the training examples. It introduced 1 new rule(s): 1 assumption guarded. It differs from the symbolic reference on: v: model wrote ['v(X) :- q(X), u(X).'], reference has ['v(X) :- p(X).'].

### t1_mono_0015_anon  (gen@1=0%, gen@k=no)
On 't1_mono_0015_anon', the model failed to fit the training examples. It introduced 1 new rule(s): 1 assumption guarded. It differs from the symbolic reference on: v: model wrote ['v(X) :- v(X), u(X).'], reference has ['v(X) :- p(X).'].

### t1_mono_0016_anon  (gen@1=0%, gen@k=no)
On 't1_mono_0016_anon', the model failed to fit the training examples. It introduced 1 new rule(s): 1 assumption guarded. It differs from the symbolic reference on: v: model wrote ['v(X) :- s(X), u(X).'], reference has ['v(X) :- p(X).'].

### t1_mono_0017_anon  (gen@1=0%, gen@k=no)
On 't1_mono_0017_anon', the model failed to fit the training examples. It introduced 2 new rule(s): 1 assumption guarded, 1 contrary rule. It differs from the symbolic reference on: s: model wrote ['s(X) :- r(X), u(X).'], reference has ['nothing']; v: model wrote ['v(X) :- q(X), u(X).'], reference has ['v(X) :- p(X).'].

### t1_mono_0018_anon  (gen@1=0%, gen@k=no)
On 't1_mono_0018_anon', the model failed to fit the training examples. It introduced 2 new rule(s): 1 assumption guarded, 1 contrary rule. It differs from the symbolic reference on: s: model wrote ['s(X) :- r(X).'], reference has ['nothing']; v: model wrote ['v(X) :- p(X), u(X).'], reference has ['v(X) :- p(X).'].

### t1_mono_0019_anon  (gen@1=33%, gen@k=yes)
On 't1_mono_0019_anon', the model produced a framework that fits the training examples and solves the full problem in one stable extension. It introduced 2 new rule(s): 1 assumption guarded, 1 intensional copy. The rule 'v(X) :- s(X), u(X).' generalises by conditioning the target on the background predicate(s) s, u, so it applies to any constant satisfying them — including unseen ones. The rule 'v(X) :- q(X).' generalises by conditioning the target on the background predicate(s) q, so it applies to any constant satisfying them — including unseen ones. It differs from the symbolic reference on: v: model wrote ['v(X) :- q(X).', 'v(X) :- s(X), u(X).'], reference has ['v(X) :- p(X).'].

### t2_defeas_0000_anon  (gen@1=0%, gen@k=no)
On 't2_defeas_0000_anon', the model failed to fit the training examples. It introduced 1 new rule(s): 1 intensional copy. The rule 'v(X) :- t(X).' generalises by conditioning the target on the background predicate(s) t, so it applies to any constant satisfying them — including unseen ones. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; v: model wrote ['v(X) :- t(X).'], reference has ['v(X) :- p(X), alpha_0(X).'].

### t2_defeas_0001_anon  (gen@1=0%, gen@k=no)
On 't2_defeas_0001_anon', the model failed to fit the training examples. It introduced 1 new rule(s): 1 intensional copy. The rule 'v(X) :- t(X).' generalises by conditioning the target on the background predicate(s) t, so it applies to any constant satisfying them — including unseen ones. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; v: model wrote ['v(X) :- t(X).'], reference has ['v(X) :- p(X), alpha_0(X).'].

### t2_defeas_0002_anon  (gen@1=0%, gen@k=no)
On 't2_defeas_0002_anon', the model failed to fit the training examples. It introduced 2 new rule(s): 1 assumption guarded, 1 contrary rule. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; t: model wrote ['t(X) :- v(X).'], reference has ['nothing']; v: model wrote ['v(X) :- t(X), u(X).'], reference has ['v(X) :- p(X), alpha_0(X).'].

### t2_defeas_0003_anon  (gen@1=0%, gen@k=no)
On 't2_defeas_0003_anon', the model failed to fit the training examples. It introduced 1 new rule(s): 1 intensional copy. The rule 'v(X) :- t(X).' generalises by conditioning the target on the background predicate(s) t, so it applies to any constant satisfying them — including unseen ones. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; v: model wrote ['v(X) :- t(X).'], reference has ['v(X) :- p(X), alpha_0(X).'].

### t2_defeas_0004_anon  (gen@1=0%, gen@k=no)
On 't2_defeas_0004_anon', the model failed to fit the training examples. It introduced 1 new rule(s): 1 mixed. These are all ground facts — the model MEMORISED the training positives rather than learning a general rule, which is why it fails on held-out examples. It also introduced the assumption(s) u(c), u(d) to make a rule defeasible, capturing exceptions. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; t: model wrote ['t(v(X)) :- v(X).'], reference has ['nothing']; v: model wrote ['nothing'], reference has ['v(X) :- p(X), alpha_0(X).'].

### t2_defeas_0005_anon  (gen@1=0%, gen@k=no)
On 't2_defeas_0005_anon', the model failed to fit the training examples. It introduced 1 new rule(s): 1 contrary rule. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; t: model wrote ['t(X) :- v(X), u(X).'], reference has ['nothing']; v: model wrote ['nothing'], reference has ['v(X) :- p(X), alpha_0(X).'].

### t2_defeas_0006_anon  (gen@1=0%, gen@k=no)
On 't2_defeas_0006_anon', the model failed to fit the training examples. It introduced 2 new rule(s): 1 assumption guarded, 1 contrary rule. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; t: model wrote ['t(X) :- v(X), u(X).'], reference has ['nothing']; v: model wrote ['v(X) :- t(X), u(X).'], reference has ['v(X) :- p(X), alpha_0(X).', 'v(X) :- r(X).'].

### t2_defeas_0007_anon  (gen@1=0%, gen@k=no)
On 't2_defeas_0007_anon', the model failed to fit the training examples. It introduced 2 new rule(s): 1 assumption guarded, 1 contrary rule. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; t: model wrote ['t(X) :- v(X), u(X).'], reference has ['nothing']; v: model wrote ['v(X) :- t(X), u(X).'], reference has ['v(X) :- p(X), alpha_0(X).'].

### t2_defeas_0008_anon  (gen@1=0%, gen@k=no)
On 't2_defeas_0008_anon', the model failed to fit the training examples. It introduced 2 new rule(s): 1 assumption guarded, 1 mixed. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; v: model wrote ['v(X) :- t(X), not(u(X)).', 'v(X) :- t(X), u(X).'], reference has ['v(X) :- p(X), alpha_0(X).'].

### t2_defeas_0009_anon  (gen@1=0%, gen@k=no)
On 't2_defeas_0009_anon', the model failed to fit the training examples. It introduced 2 new rule(s): 1 assumption guarded, 1 contrary rule. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; t: model wrote ['t(X) :- q(X), u(X).'], reference has ['nothing']; v: model wrote ['v(X) :- t(X), u(X).'], reference has ['v(X) :- p(X), alpha_0(X).'].

### t2_defeas_0010_anon  (gen@1=0%, gen@k=no)
On 't2_defeas_0010_anon', the model failed to fit the training examples. It introduced 1 new rule(s): 1 assumption guarded. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; v: model wrote ['v(X) :- t(X), u(X).'], reference has ['v(X) :- p(X), alpha_0(X).'].

### t2_defeas_0011_anon  (gen@1=0%, gen@k=no)
On 't2_defeas_0011_anon', the model failed to fit the training examples. It introduced 1 new rule(s): 1 assumption guarded. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; v: model wrote ['v(X) :- t(X), u(X).'], reference has ['v(X) :- p(X), alpha_0(X).'].

### t2_defeas_0012_anon  (gen@1=0%, gen@k=no)
On 't2_defeas_0012_anon', the model failed to fit the training examples. It introduced 1 new rule(s): 1 intensional copy. The rule 'v(X) :- t(X).' generalises by conditioning the target on the background predicate(s) t, so it applies to any constant satisfying them — including unseen ones. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; v: model wrote ['v(X) :- t(X).'], reference has ['v(X) :- p(X), alpha_0(X).'].

### t2_defeas_0013_anon  (gen@1=0%, gen@k=no)
On 't2_defeas_0013_anon', the model failed to fit the training examples. It introduced 1 new rule(s): 1 assumption guarded. It differs from the symbolic reference on: v: model wrote ['v(X) :- t(X), u(X).'], reference has ['v(X) :- r(X).'].

### t2_defeas_0014_anon  (gen@1=0%, gen@k=no)
On 't2_defeas_0014_anon', the model failed to fit the training examples. It introduced 1 new rule(s): 1 intensional copy. The rule 'v(X) :- t(X).' generalises by conditioning the target on the background predicate(s) t, so it applies to any constant satisfying them — including unseen ones. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; v: model wrote ['v(X) :- t(X).'], reference has ['v(X) :- p(X), alpha_0(X).'].

### t2_defeas_0015_anon  (gen@1=0%, gen@k=no)
On 't2_defeas_0015_anon', the model failed to fit the training examples. It introduced 2 new rule(s): 1 assumption guarded, 1 contrary rule. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; t: model wrote ['t(X) :- v(X), u(X).'], reference has ['nothing']; v: model wrote ['v(X) :- t(X), u(X).'], reference has ['v(X) :- p(X), alpha_0(X).'].

### t2_defeas_0016_anon  (gen@1=0%, gen@k=no)
On 't2_defeas_0016_anon', the model failed to fit the training examples. It introduced 2 new rule(s): 2 assumption guarded. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; v: model wrote ['v(X) :- t(X), u(X), v(X).', 'v(X) :- t(X), u(X).'], reference has ['v(X) :- p(X), alpha_0(X).'].

### t2_defeas_0017_anon  (gen@1=0%, gen@k=no)
On 't2_defeas_0017_anon', the model failed to fit the training examples. It introduced 1 new rule(s): 1 assumption guarded. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; v: model wrote ['v(X) :- t(X), u(X).'], reference has ['v(X) :- p(X), alpha_0(X).'].

### t2_defeas_0018_anon  (gen@1=0%, gen@k=no)
On 't2_defeas_0018_anon', the model failed to fit the training examples. It introduced 1 new rule(s): 1 assumption guarded. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; v: model wrote ['v(X) :- t(X), u(X).'], reference has ['v(X) :- p(X), alpha_0(X).'].

### t2_defeas_0019_anon  (gen@1=0%, gen@k=no)
On 't2_defeas_0019_anon', the model failed to fit the training examples. It introduced 1 new rule(s): 1 assumption guarded. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; v: model wrote ['v(X) :- t(X), u(X).'], reference has ['v(X) :- p(X), alpha_0(X).'].

### t3_noise_0000_anon  (gen@1=0%, gen@k=no)
On 't3_noise_0000_anon', the model failed to fit the training examples. It introduced 2 new rule(s): 1 assumption guarded, 1 contrary rule. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; p1: model wrote ['p1(X) :- p(X), w(X).'], reference has ['p1(X) :- p(X), alpha_0(X).']; v: model wrote ['v(X) :- r(X), w(X).'], reference has ['nothing'].

### t3_noise_0001_anon  (gen@1=33%, gen@k=yes)
On 't3_noise_0001_anon', the model produced a framework that fits the training examples and solves the full problem in one stable extension. It introduced 2 new rule(s): 1 assumption guarded, 1 contrary rule. Semantically, the learned framework is equivalent to the symbolic reference (same entailments over the whole domain), even though some rules are written differently.

### t3_noise_0002_anon  (gen@1=33%, gen@k=yes)
On 't3_noise_0002_anon', the model produced a framework that fits the training examples and solves the full problem in one stable extension. It introduced 1 new rule(s): 1 assumption guarded. Semantically, the learned framework is equivalent to the symbolic reference (same entailments over the whole domain), even though some rules are written differently.

### t3_noise_0003_anon  (gen@1=67%, gen@k=yes)
On 't3_noise_0003_anon', the model produced a framework that fits the training examples and solves the full problem in one stable extension. It introduced 2 new rule(s): 1 assumption guarded, 1 contrary rule. Semantically, the learned framework is equivalent to the symbolic reference (same entailments over the whole domain), even though some rules are written differently.

### t3_noise_0004_anon  (gen@1=0%, gen@k=no)
On 't3_noise_0004_anon', the model failed to fit the training examples. It introduced 2 new rule(s): 1 assumption guarded, 1 contrary rule. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; p1: model wrote ['p1(X) :- p(X), w(X).'], reference has ['p1(X) :- p(X), alpha_0(X).']; v: model wrote ['v(X) :- r(X), w(X).'], reference has ['nothing'].

### t3_noise_0005_anon  (gen@1=0%, gen@k=no)
On 't3_noise_0005_anon', the model failed to fit the training examples. It introduced 1 new rule(s): 1 intensional copy. The rule 'p1(X) :- v(X).' generalises by conditioning the target on the background predicate(s) v, so it applies to any constant satisfying them — including unseen ones. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; p1: model wrote ['p1(X) :- v(X).'], reference has ['p1(X) :- p(X), alpha_0(X).'].

### t3_noise_0006_anon  (gen@1=33%, gen@k=yes)
On 't3_noise_0006_anon', the model produced a framework that fits the training examples and solves the full problem in one stable extension. It introduced 2 new rule(s): 1 assumption guarded, 1 contrary rule. Semantically, the learned framework is equivalent to the symbolic reference (same entailments over the whole domain), even though some rules are written differently.

### t3_noise_0007_anon  (gen@1=67%, gen@k=yes)
On 't3_noise_0007_anon', the model produced a framework that fits the training examples and solves the full problem in one stable extension. It introduced 2 new rule(s): 1 assumption guarded, 1 contrary rule. Semantically, the learned framework is equivalent to the symbolic reference (same entailments over the whole domain), even though some rules are written differently.

### t3_noise_0008_anon  (gen@1=33%, gen@k=yes)
On 't3_noise_0008_anon', the model produced a framework that fits the training examples and solves the full problem in one stable extension. It introduced 2 new rule(s): 1 assumption guarded, 1 contrary rule. Semantically, the learned framework is equivalent to the symbolic reference (same entailments over the whole domain), even though some rules are written differently.

### t3_noise_0009_anon  (gen@1=33%, gen@k=yes)
On 't3_noise_0009_anon', the model produced a framework that fits the training examples and solves the full problem in one stable extension. It introduced 2 new rule(s): 1 assumption guarded, 1 contrary rule. Semantically, the learned framework is equivalent to the symbolic reference (same entailments over the whole domain), even though some rules are written differently.

### t3_noise_0010_anon  (gen@1=67%, gen@k=yes)
On 't3_noise_0010_anon', the model produced a framework that fits the training examples and solves the full problem in one stable extension. It introduced 2 new rule(s): 1 assumption guarded, 1 contrary rule. Semantically, the learned framework is equivalent to the symbolic reference (same entailments over the whole domain), even though some rules are written differently.

### t3_noise_0011_anon  (gen@1=0%, gen@k=no)
On 't3_noise_0011_anon', the model failed to fit the training examples. It introduced 2 new rule(s): 1 assumption guarded, 1 contrary rule. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; p1: model wrote ['p1(X) :- p(X), w(X).'], reference has ['p1(X) :- p(X), alpha_0(X).', 'p1(X) :- t(X).']; v: model wrote ['v(X) :- r(X), w(X).'], reference has ['nothing'].

### t3_noise_0012_anon  (gen@1=33%, gen@k=yes)
On 't3_noise_0012_anon', the model produced a framework that fits the training examples and solves the full problem in one stable extension. It introduced 2 new rule(s): 1 assumption guarded, 1 contrary rule. Semantically, the learned framework is equivalent to the symbolic reference (same entailments over the whole domain), even though some rules are written differently.

### t3_noise_0013_anon  (gen@1=0%, gen@k=no)
On 't3_noise_0013_anon', the model failed to fit the training examples. It introduced 2 new rule(s): 1 assumption guarded, 1 contrary rule. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; p1: model wrote ['p1(X) :- p(X), w(X).'], reference has ['p1(X) :- p(X), alpha_0(X).']; v: model wrote ['v(X) :- t(X), w(X).'], reference has ['nothing'].

### t3_noise_0014_anon  (gen@1=0%, gen@k=no)
On 't3_noise_0014_anon', the model failed to fit the training examples. It introduced 2 new rule(s): 1 assumption guarded, 1 contrary rule. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; p1: model wrote ['p1(X) :- p(X), w(X).'], reference has ['p1(X) :- p(X), alpha_0(X).', 'p1(X) :- t(X).']; v: model wrote ['v(X) :- s(X), w(X).'], reference has ['nothing'].

### t3_noise_0015_anon  (gen@1=0%, gen@k=no)
On 't3_noise_0015_anon', the model failed to fit the training examples. It introduced 2 new rule(s): 1 assumption guarded, 1 contrary rule. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; p1: model wrote ['p1(X) :- p(X), w(X).'], reference has ['p1(X) :- p(X), alpha_0(X).']; v: model wrote ['v(X) :- r(X), w(X).'], reference has ['nothing'].

### t3_noise_0016_anon  (gen@1=0%, gen@k=no)
On 't3_noise_0016_anon', the model failed to fit the training examples. It introduced 1 new rule(s): 1 intensional copy. The rule 'p1(X) :- v(X), p(X).' generalises by conditioning the target on the background predicate(s) v, p, so it applies to any constant satisfying them — including unseen ones. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; p1: model wrote ['p1(X) :- v(X), p(X).'], reference has ['p1(X) :- p(X), alpha_0(X).'].

### t3_noise_0017_anon  (gen@1=0%, gen@k=no)
On 't3_noise_0017_anon', the model failed to fit the training examples. It introduced 1 new rule(s): 1 intensional copy. The rule 'p1(X) :- v(X).' generalises by conditioning the target on the background predicate(s) v, so it applies to any constant satisfying them — including unseen ones. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; p1: model wrote ['p1(X) :- v(X).'], reference has ['p1(X) :- p(X), alpha_0(X).'].

### t3_noise_0018_anon  (gen@1=0%, gen@k=no)
On 't3_noise_0018_anon', the model fits the training examples but only classifies 50% of held-out examples correctly — partial generalisation. It introduced 2 new rule(s): 1 assumption guarded, 1 contrary rule. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; p1: model wrote ['p1(X) :- p(X), w(X).'], reference has ['p1(X) :- p(X), alpha_0(X).']; v: model wrote ['v(X) :- r(X).'], reference has ['nothing'].

### t3_noise_0019_anon  (gen@1=67%, gen@k=yes)
On 't3_noise_0019_anon', the model produced a framework that fits the training examples and solves the full problem in one stable extension. It introduced 2 new rule(s): 1 assumption guarded, 1 contrary rule. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; p1: model wrote ['p1(X) :- p(X), w(X).'], reference has ['p1(X) :- p(X), alpha_0(X).', 'p1(X) :- t(X).']; v: model wrote ['v(X) :- q(X), w(X).'], reference has ['nothing'].

### t4_domain_0000_anon  (gen@1=0%, gen@k=no)
On 't4_domain_0000_anon', the candidate is NOT a legal solution: flatness violated: assumption 'u' used as rule head. The outcome below is reported for diagnosis only. On 't4_domain_0000_anon', the model failed to fit the training examples. It introduced 3 new rule(s): 1 assumption guarded, 1 contrary rule, 1 intensional copy. The rule 'v(X) :- t(X), u(X).' generalises by conditioning the target on the background predicate(s) t, u, so it applies to any constant satisfying them — including unseen ones. The rule 't(X) :- q(X), v(X).' generalises by conditioning the target on the background predicate(s) q, v, so it applies to any constant satisfying them — including unseen ones. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; t: model wrote ['t(X) :- q(X), v(X).'], reference has ['nothing']; u: model wrote ['u(X) defeated_by t(X).'], reference has ['nothing'].

### t4_domain_0001_anon  (gen@1=0%, gen@k=no)
On 't4_domain_0001_anon', the model failed to fit the training examples. It introduced 2 new rule(s): 1 assumption guarded, 1 contrary rule. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; t: model wrote ['t(X) :- r(X), v(X).'], reference has ['nothing']; v: model wrote ['v(X) :- q(X), u(X).'], reference has ['v(X) :- p(X), alpha_0(X).'].

### t4_domain_0002_anon  (gen@1=0%, gen@k=no)
On 't4_domain_0002_anon', the candidate is NOT a legal solution: flatness violated: assumption 'u' used as rule head. The outcome below is reported for diagnosis only. On 't4_domain_0002_anon', the model failed to fit the training examples. It introduced 3 new rule(s): 1 assumption guarded, 1 contrary rule, 1 intensional copy. The rule 'v(X) :- t(X), u(X).' generalises by conditioning the target on the background predicate(s) t, u, so it applies to any constant satisfying them — including unseen ones. The rule 't(X) :- q(X), u(X).' generalises by conditioning the target on the background predicate(s) q, u, so it applies to any constant satisfying them — including unseen ones. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; t: model wrote ['t(X) :- q(X), u(X).'], reference has ['nothing']; u: model wrote ['u(X) defeated_by t(X).'], reference has ['nothing'].

### t4_domain_0003_anon  (gen@1=0%, gen@k=no)
On 't4_domain_0003_anon', the model failed to fit the training examples. It introduced 1 new rule(s): 1 intensional copy. The rule 'v(X) :- t(X).' generalises by conditioning the target on the background predicate(s) t, so it applies to any constant satisfying them — including unseen ones. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; v: model wrote ['v(X) :- t(X).'], reference has ['v(X) :- p(X), alpha_0(X).'].

### t4_domain_0004_anon  (gen@1=0%, gen@k=no)
On 't4_domain_0004_anon', the model failed to fit the training examples. It introduced 2 new rule(s): 1 assumption guarded, 1 contrary rule. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; t: model wrote ['t(X) :- q(X), not v(X).'], reference has ['nothing']; v: model wrote ['v(X) :- t(X), u(X).'], reference has ['v(X) :- p(X), alpha_0(X).'].

### t4_domain_0005_anon  (gen@1=0%, gen@k=no)
On 't4_domain_0005_anon', the model failed to fit the training examples. It introduced 2 new rule(s): 1 intensional copy, 1 assumption guarded. The rule 'v(X) :- t(X), v(X).' generalises by conditioning the target on the background predicate(s) t, v, so it applies to any constant satisfying them — including unseen ones. The rule 'v(X) :- t(X), u(X).' generalises by conditioning the target on the background predicate(s) t, u, so it applies to any constant satisfying them — including unseen ones. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; v: model wrote ['v(X) :- t(X), u(X).', 'v(X) :- t(X), v(X).'], reference has ['v(X) :- p(X), alpha_0(X).'].

### t4_domain_0006_anon  (gen@1=0%, gen@k=no)
On 't4_domain_0006_anon', the model failed to fit the training examples. It introduced 1 new rule(s): 1 assumption guarded. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; v: model wrote ['v(X) :- t(X), u(X).'], reference has ['v(X) :- p(X), alpha_0(X).'].

### t4_domain_0007_anon  (gen@1=0%, gen@k=no)
On 't4_domain_0007_anon', the model failed to fit the training examples. It introduced 2 new rule(s): 1 contrary rule, 1 assumption guarded. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; t: model wrote ['t(X) :- v(X), u(X).'], reference has ['nothing']; v: model wrote ['v(X) :- q(X), u(X).'], reference has ['v(X) :- p(X), alpha_0(X).'].

### t4_domain_0008_anon  (gen@1=0%, gen@k=no)
On 't4_domain_0008_anon', the model failed to fit the training examples. It introduced 2 new rule(s): 1 assumption guarded, 1 contrary rule. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; t: model wrote ['t(X) :- q(X).'], reference has ['nothing']; v: model wrote ['v(X) :- t(X), u(X).'], reference has ['v(X) :- p(X), alpha_0(X).', 'v(X) :- s(X).'].

### t4_domain_0009_anon  (gen@1=0%, gen@k=no)
On 't4_domain_0009_anon', the model failed to fit the training examples. It introduced 1 new rule(s): 1 assumption guarded. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; v: model wrote ['v(X) :- t(X), u(X).'], reference has ['v(X) :- p(X), alpha_0(X).'].

### t4_domain_0010_anon  (gen@1=0%, gen@k=no)
On 't4_domain_0010_anon', the model failed to fit the training examples. It introduced 2 new rule(s): 1 assumption guarded, 1 contrary rule. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; t: model wrote ['t(X) :- q(X), v(X).'], reference has ['nothing']; v: model wrote ['v(X) :- t(X), u(X).'], reference has ['v(X) :- p(X), alpha_0(X).'].

### t4_domain_0011_anon  (gen@1=0%, gen@k=no)
On 't4_domain_0011_anon', the model failed to fit the training examples. It introduced 2 new rule(s): 1 contrary rule, 1 assumption guarded. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; t: model wrote ['t(X) :- v(X).'], reference has ['nothing']; v: model wrote ['v(X) :- t(X), u(X).'], reference has ['v(X) :- p(X), alpha_0(X).'].

### t4_domain_0012_anon  (gen@1=0%, gen@k=no)
On 't4_domain_0012_anon', the model failed to fit the training examples. It introduced 1 new rule(s): 1 intensional copy. The rule 'v(X) :- t(X).' generalises by conditioning the target on the background predicate(s) t, so it applies to any constant satisfying them — including unseen ones. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; v: model wrote ['v(X) :- t(X).'], reference has ['v(X) :- p(X), alpha_0(X).'].

### t4_domain_0013_anon  (gen@1=0%, gen@k=no)
On 't4_domain_0013_anon', the model failed to fit the training examples. It introduced 2 new rule(s): 2 assumption guarded. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; v: model wrote ['v(X) :- t(X), u(X).', 'v(X) :- t(X), v(X), t(Y), X = Y, u(X).'], reference has ['v(X) :- p(X), alpha_0(X).', 'v(X) :- s(X).'].

### t4_domain_0014_anon  (gen@1=0%, gen@k=no)
On 't4_domain_0014_anon', the model failed to fit the training examples. It introduced 2 new rule(s): 1 intensional copy, 1 contrary rule. The rule 'v(X) :- t(X).' generalises by conditioning the target on the background predicate(s) t, so it applies to any constant satisfying them — including unseen ones. The rule 't(X) :- q(X).' generalises by conditioning the target on the background predicate(s) q, so it applies to any constant satisfying them — including unseen ones. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; t: model wrote ['t(X) :- q(X).'], reference has ['nothing']; v: model wrote ['v(X) :- t(X).'], reference has ['v(X) :- p(X), alpha_0(X).'].

### t4_domain_0015_anon  (gen@1=0%, gen@k=no)
On 't4_domain_0015_anon', the model failed to fit the training examples. It introduced 4 new rule(s): 1 contrary rule, 3 assumption guarded. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; t: model wrote ['t(X) :- v(X), u(X).'], reference has ['nothing']; v: model wrote ['v(e) :- r(e), u(X).', 'v(f) :- q(f), u(X).', 'v(j) :- s(j), u(X).'], reference has ['v(X) :- p(X), alpha_0(X).'].

### t4_domain_0016_anon  (gen@1=0%, gen@k=no)
On 't4_domain_0016_anon', the model failed to fit the training examples. It introduced 1 new rule(s): 1 contrary rule. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; t: model wrote ['t(X) :- q(X), v(X).'], reference has ['nothing']; v: model wrote ['nothing'], reference has ['v(X) :- p(X), alpha_0(X).'].

### t4_domain_0017_anon  (gen@1=0%, gen@k=no)
On 't4_domain_0017_anon', the model failed to fit the training examples. It introduced 1 new rule(s): 1 intensional copy. The rule 'v(X) :- t(X).' generalises by conditioning the target on the background predicate(s) t, so it applies to any constant satisfying them — including unseen ones. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; v: model wrote ['v(X) :- t(X).'], reference has ['v(X) :- p(X), alpha_0(X).'].

### t4_domain_0018_anon  (gen@1=0%, gen@k=no)
On 't4_domain_0018_anon', the model failed to fit the training examples. It introduced 2 new rule(s): 1 assumption guarded, 1 contrary rule. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; t: model wrote ['t(X) :- v(X), u(X).'], reference has ['nothing']; v: model wrote ['v(X) :- t(X), u(X).'], reference has ['v(X) :- p(X), alpha_0(X).'].

### t4_domain_0019_anon  (gen@1=0%, gen@k=no)
On 't4_domain_0019_anon', the model failed to fit the training examples. It introduced 2 new rule(s): 1 intensional copy, 1 contrary rule. The rule 'v(X) :- t(X).' generalises by conditioning the target on the background predicate(s) t, so it applies to any constant satisfying them — including unseen ones. The rule 't(X) :- q(X), u(X).' generalises by conditioning the target on the background predicate(s) q, u, so it applies to any constant satisfying them — including unseen ones. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; t: model wrote ['t(X) :- q(X), u(X).'], reference has ['nothing']; v: model wrote ['v(X) :- t(X).'], reference has ['v(X) :- p(X), alpha_0(X).'].

### t5_twopath_0000_anon  (gen@1=33%, gen@k=yes)
On 't5_twopath_0000_anon', the model produced a framework that fits the training examples and solves the full problem in one stable extension. It introduced 2 new rule(s): 2 assumption guarded. Semantically, the learned framework is equivalent to the symbolic reference (same entailments over the whole domain), even though some rules are written differently.

### t5_twopath_0001_anon  (gen@1=67%, gen@k=yes)
On 't5_twopath_0001_anon', the model produced a framework that fits the training examples and solves the full problem in one stable extension. It introduced 2 new rule(s): 2 assumption guarded. Semantically, the learned framework is equivalent to the symbolic reference (same entailments over the whole domain), even though some rules are written differently.

### t5_twopath_0002_anon  (gen@1=100%, gen@k=yes)
On 't5_twopath_0002_anon', the model produced a framework that fits the training examples and solves the full problem in one stable extension. It introduced 2 new rule(s): 2 assumption guarded. Semantically, the learned framework is equivalent to the symbolic reference (same entailments over the whole domain), even though some rules are written differently.

### t5_twopath_0003_anon  (gen@1=33%, gen@k=yes)
On 't5_twopath_0003_anon', the model produced a framework that fits the training examples and solves the full problem in one stable extension. It introduced 2 new rule(s): 2 assumption guarded. Semantically, the learned framework is equivalent to the symbolic reference (same entailments over the whole domain), even though some rules are written differently.

### t5_twopath_0004_anon  (gen@1=100%, gen@k=yes)
On 't5_twopath_0004_anon', the model produced a framework that fits the training examples and solves the full problem in one stable extension. It introduced 2 new rule(s): 2 assumption guarded. Semantically, the learned framework is equivalent to the symbolic reference (same entailments over the whole domain), even though some rules are written differently.

### t5_twopath_0005_anon  (gen@1=0%, gen@k=no)
On 't5_twopath_0005_anon', the model failed to fit the training examples. It introduced 1 new rule(s): 1 assumption guarded. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- r(X).']; c_alpha_1: model wrote ['nothing'], reference has ['c_alpha_1(X) :- s(X).']; p1: model wrote ['p1(X) :- p(X), v(X).'], reference has ['p1(X) :- p(X), alpha_0(X).', 'p1(X) :- q(X), alpha_1(X).'].

### t5_twopath_0006_anon  (gen@1=67%, gen@k=yes)
On 't5_twopath_0006_anon', the model produced a framework that fits the training examples and solves the full problem in one stable extension. It introduced 2 new rule(s): 2 assumption guarded. Semantically, the learned framework is equivalent to the symbolic reference (same entailments over the whole domain), even though some rules are written differently.

### t5_twopath_0007_anon  (gen@1=0%, gen@k=no)
On 't5_twopath_0007_anon', the model failed to fit the training examples. It introduced 1 new rule(s): 1 assumption guarded. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- r(X).']; c_alpha_1: model wrote ['nothing'], reference has ['c_alpha_1(X) :- s(X).']; p1: model wrote ['p1(X) :- p(X), v(X).'], reference has ['p1(X) :- p(X), alpha_0(X).', 'p1(X) :- q(X), alpha_1(X).'].

### t5_twopath_0008_anon  (gen@1=33%, gen@k=yes)
On 't5_twopath_0008_anon', the model produced a framework that fits the training examples and solves the full problem in one stable extension. It introduced 2 new rule(s): 2 assumption guarded. Semantically, the learned framework is equivalent to the symbolic reference (same entailments over the whole domain), even though some rules are written differently.

### t5_twopath_0009_anon  (gen@1=100%, gen@k=yes)
On 't5_twopath_0009_anon', the model produced a framework that fits the training examples and solves the full problem in one stable extension. It introduced 2 new rule(s): 2 assumption guarded. Semantically, the learned framework is equivalent to the symbolic reference (same entailments over the whole domain), even though some rules are written differently.

### t5_twopath_0010_anon  (gen@1=67%, gen@k=yes)
On 't5_twopath_0010_anon', the model produced a framework that fits the training examples and solves the full problem in one stable extension. It introduced 2 new rule(s): 2 assumption guarded. Semantically, the learned framework is equivalent to the symbolic reference (same entailments over the whole domain), even though some rules are written differently.

### t5_twopath_0011_anon  (gen@1=100%, gen@k=yes)
On 't5_twopath_0011_anon', the model produced a framework that fits the training examples and solves the full problem in one stable extension. It introduced 2 new rule(s): 2 assumption guarded. Semantically, the learned framework is equivalent to the symbolic reference (same entailments over the whole domain), even though some rules are written differently.

### t5_twopath_0012_anon  (gen@1=67%, gen@k=yes)
On 't5_twopath_0012_anon', the model produced a framework that fits the training examples and solves the full problem in one stable extension. It introduced 2 new rule(s): 2 assumption guarded. Semantically, the learned framework is equivalent to the symbolic reference (same entailments over the whole domain), even though some rules are written differently.

### t5_twopath_0013_anon  (gen@1=33%, gen@k=yes)
On 't5_twopath_0013_anon', the model produced a framework that fits the training examples and solves the full problem in one stable extension. It introduced 2 new rule(s): 2 assumption guarded. Semantically, the learned framework is equivalent to the symbolic reference (same entailments over the whole domain), even though some rules are written differently.

### t5_twopath_0014_anon  (gen@1=33%, gen@k=yes)
On 't5_twopath_0014_anon', the model produced a framework that fits the training examples and solves the full problem in one stable extension. It introduced 2 new rule(s): 2 assumption guarded. Semantically, the learned framework is equivalent to the symbolic reference (same entailments over the whole domain), even though some rules are written differently.

### t5_twopath_0015_anon  (gen@1=33%, gen@k=yes)
On 't5_twopath_0015_anon', the model produced a framework that fits the training examples and solves the full problem in one stable extension. It introduced 2 new rule(s): 2 assumption guarded. Semantically, the learned framework is equivalent to the symbolic reference (same entailments over the whole domain), even though some rules are written differently.

### t5_twopath_0016_anon  (gen@1=67%, gen@k=yes)
On 't5_twopath_0016_anon', the model produced a framework that fits the training examples and solves the full problem in one stable extension. It introduced 2 new rule(s): 2 assumption guarded. Semantically, the learned framework is equivalent to the symbolic reference (same entailments over the whole domain), even though some rules are written differently.

### t5_twopath_0017_anon  (gen@1=67%, gen@k=yes)
On 't5_twopath_0017_anon', the model produced a framework that fits the training examples and solves the full problem in one stable extension. It introduced 2 new rule(s): 2 assumption guarded. Semantically, the learned framework is equivalent to the symbolic reference (same entailments over the whole domain), even though some rules are written differently.

### t5_twopath_0018_anon  (gen@1=67%, gen@k=yes)
On 't5_twopath_0018_anon', the model produced a framework that fits the training examples and solves the full problem in one stable extension. It introduced 2 new rule(s): 2 assumption guarded. Semantically, the learned framework is equivalent to the symbolic reference (same entailments over the whole domain), even though some rules are written differently.

### t5_twopath_0019_anon  (gen@1=33%, gen@k=yes)
On 't5_twopath_0019_anon', the model produced a framework that fits the training examples and solves the full problem in one stable extension. It introduced 2 new rule(s): 2 assumption guarded. Semantically, the learned framework is equivalent to the symbolic reference (same entailments over the whole domain), even though some rules are written differently.


## Mode: cot

### nixon_diamond_anon  (gen@1=0%, gen@k=no)
On 'nixon_diamond_anon', the model failed to fit the training examples. It introduced 2 new rule(s): 2 intensional copy. The rule 'v(X) :- r(X), s(X).' generalises by conditioning the target on the background predicate(s) r, s, so it applies to any constant satisfying them — including unseen ones. The rule 'v(X) :- p(X), s(X).' generalises by conditioning the target on the background predicate(s) p, s, so it applies to any constant satisfying them — including unseen ones. It also introduced the assumption(s) alpha(a), alpha(b) to make a rule defeasible, capturing exceptions. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- p(X), w(X).']; p1: model wrote ['nothing'], reference has ['p1(X) :- p(X), alpha_0(X).']; v: model wrote ['v(X) :- p(X), s(X).', 'v(X) :- r(X), s(X).'], reference has ['v(X) :- q(X).'].

### flies_anon  (gen@1=0%, gen@k=no)
On 'flies_anon', the model failed to fit the training examples. It introduced 1 new rule(s): 1 intensional copy. The rule 't(X) :- p(X).' generalises by conditioning the target on the background predicate(s) p, so it applies to any constant satisfying them — including unseen ones. It also introduced the assumption(s) alpha(b) to make a rule defeasible, capturing exceptions. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; t: model wrote ['t(X) :- p(X).'], reference has ['t(X) :- p(X), alpha_0(X).'].

### tax_law_anon  (gen@1=0%, gen@k=no)
On 'tax_law_anon', the model failed to fit the training examples. It introduced 2 new rule(s): 1 assumption guarded, 1 intensional copy. The rule 'u(X) :- p(X), s(X).' generalises by conditioning the target on the background predicate(s) p, s, so it applies to any constant satisfying them — including unseen ones. The rule 'u(X) :- q(X), t(X).' generalises by conditioning the target on the background predicate(s) q, t, so it applies to any constant satisfying them — including unseen ones. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- p(X), alpha_1(X).']; c_alpha_1: model wrote ['nothing'], reference has ['c_alpha_1(X) :- p(X), alpha_0(X).']; u: model wrote ['u(X) :- p(X), s(X).', 'u(X) :- q(X), t(X).'], reference has ['u(X) :- p(X), alpha_0(X).', 'u(X) :- q(X).'].

### t1_mono_0000_anon  (gen@1=0%, gen@k=no)
On 't1_mono_0000_anon', the model failed to fit the training examples. It introduced 2 new rule(s): 2 intensional copy. The rule 'v(X) :- q(X), alpha(X).' generalises by conditioning the target on the background predicate(s) q, alpha, so it applies to any constant satisfying them — including unseen ones. The rule 'v(X) :- r(X).' generalises by conditioning the target on the background predicate(s) r, so it applies to any constant satisfying them — including unseen ones. It also introduced the assumption(s) alpha(X) to make a rule defeasible, capturing exceptions. It differs from the symbolic reference on: v: model wrote ['v(X) :- q(X), alpha(X).', 'v(X) :- r(X).'], reference has ['v(X) :- p(X).'].

### t1_mono_0001_anon  (gen@1=0%, gen@k=no)
On 't1_mono_0001_anon', the model failed to fit the training examples. It introduced 1 new rule(s): 1 intensional copy. The rule 'u(X) :- q(X), r(X).' generalises by conditioning the target on the background predicate(s) q, r, so it applies to any constant satisfying them — including unseen ones. It also introduced the assumption(s) alpha(X) to make a rule defeasible, capturing exceptions. It differs from the symbolic reference on: u: model wrote ['u(X) :- q(X), r(X).'], reference has ['u(X) :- p(X).'].

### t1_mono_0002_anon  (gen@1=0%, gen@k=no)
On 't1_mono_0002_anon', the model failed to fit the training examples. It introduced 2 new rule(s): 1 intensional copy, 1 mixed. The rule 'v(X) :- r(X), s(X).' generalises by conditioning the target on the background predicate(s) r, s, so it applies to any constant satisfying them — including unseen ones. It also introduced the assumption(s) alpha(e) to make a rule defeasible, capturing exceptions. It differs from the symbolic reference on: c_alpha: model wrote ['c_alpha(e) :- s(f).'], reference has ['nothing']; v: model wrote ['v(X) :- r(X), s(X).'], reference has ['v(X) :- p(X).'].

### t1_mono_0003_anon  (gen@1=0%, gen@k=no)
On 't1_mono_0003_anon', the model failed to fit the training examples. It introduced 2 new rule(s): 2 intensional copy. The rule 'v(X) :- s(X).' generalises by conditioning the target on the background predicate(s) s, so it applies to any constant satisfying them — including unseen ones. The rule 'v(X) :- q(X).' generalises by conditioning the target on the background predicate(s) q, so it applies to any constant satisfying them — including unseen ones. It differs from the symbolic reference on: v: model wrote ['v(X) :- q(X).', 'v(X) :- s(X).'], reference has ['v(X) :- p(X).'].

### t1_mono_0004_anon  (gen@1=0%, gen@k=no)
On 't1_mono_0004_anon', the model failed to fit the training examples. It introduced 2 new rule(s): 1 intensional copy, 1 mixed. The rule 'v(X) :- q(X).' generalises by conditioning the target on the background predicate(s) q, so it applies to any constant satisfying them — including unseen ones. It also introduced the assumption(s) alpha(e) to make a rule defeasible, capturing exceptions. It differs from the symbolic reference on: v: model wrote ['v(X) :- q(X), alpha(e).', 'v(X) :- q(X).'], reference has ['v(X) :- p(X).'].

### t1_mono_0005_anon  (gen@1=0%, gen@k=no)
On 't1_mono_0005_anon', the model failed to fit the training examples. It introduced 2 new rule(s): 1 intensional copy, 1 assumption guarded. The rule 'v(X) :- p(X), r(X).' generalises by conditioning the target on the background predicate(s) p, r, so it applies to any constant satisfying them — including unseen ones. The rule 'v(X) :- q(X), u(X).' generalises by conditioning the target on the background predicate(s) q, u, so it applies to any constant satisfying them — including unseen ones. It differs from the symbolic reference on: v: model wrote ['v(X) :- p(X), r(X).', 'v(X) :- q(X), u(X).'], reference has ['v(X) :- p(X).'].

### t1_mono_0006_anon  (gen@1=0%, gen@k=no)
On 't1_mono_0006_anon', the model failed to fit the training examples. It introduced 2 new rule(s): 1 assumption guarded, 1 intensional copy. The rule 'v(X) :- q(X), u(X).' generalises by conditioning the target on the background predicate(s) q, u, so it applies to any constant satisfying them — including unseen ones. The rule 'v(X) :- s(X).' generalises by conditioning the target on the background predicate(s) s, so it applies to any constant satisfying them — including unseen ones. It differs from the symbolic reference on: v: model wrote ['v(X) :- q(X), u(X).', 'v(X) :- s(X).'], reference has ['v(X) :- p(X).'].

### t1_mono_0007_anon  (gen@1=0%, gen@k=no)
On 't1_mono_0007_anon', the model failed to fit the training examples. It introduced 1 new rule(s): 1 assumption guarded. It differs from the symbolic reference on: v: model wrote ['v(X) :- t(X), u(X).'], reference has ['v(X) :- p(X).'].

### t1_mono_0008_anon  (gen@1=67%, gen@k=yes)
On 't1_mono_0008_anon', the model produced a framework that fits the training examples and solves the full problem in one stable extension. It introduced 1 new rule(s): 1 intensional copy. The rule 'u(X) :- p(X).' generalises by conditioning the target on the background predicate(s) p, so it applies to any constant satisfying them — including unseen ones. It also introduced the assumption(s) alpha(e) to make a rule defeasible, capturing exceptions. Semantically, the learned framework is equivalent to the symbolic reference (same entailments over the whole domain), via identical rules.

### t1_mono_0009_anon  (gen@1=0%, gen@k=no)
On 't1_mono_0009_anon', the candidate is NOT a legal solution: new assumption predicate 's' repurposes background non-assumption predicate 's'. The outcome below is reported for diagnosis only. On 't1_mono_0009_anon', the model fits the training examples but only classifies 50% of held-out examples correctly — partial generalisation. It introduced 2 new rule(s): 2 intensional copy. The rule 'v(X) :- r(X), s(X).' generalises by conditioning the target on the background predicate(s) r, s, so it applies to any constant satisfying them — including unseen ones. The rule 'v(X) :- q(X), s(X).' generalises by conditioning the target on the background predicate(s) q, s, so it applies to any constant satisfying them — including unseen ones. It also introduced the assumption(s) s(X) to make a rule defeasible, capturing exceptions. It differs from the symbolic reference on: v: model wrote ['v(X) :- q(X), s(X).', 'v(X) :- r(X), s(X).'], reference has ['v(X) :- p(X).'].

### t1_mono_0010_anon  (gen@1=33%, gen@k=yes)
On 't1_mono_0010_anon', the model produced a framework that fits the training examples and solves the full problem in one stable extension. It introduced 1 new rule(s): 1 assumption guarded. Semantically, the learned framework is equivalent to the symbolic reference (same entailments over the whole domain), even though some rules are written differently.

### t1_mono_0011_anon  (gen@1=0%, gen@k=no)
On 't1_mono_0011_anon', the model failed to fit the training examples. It introduced 2 new rule(s): 2 mixed. These are all ground facts — the model MEMORISED the training positives rather than learning a general rule, which is why it fails on held-out examples. It differs from the symbolic reference on: v: model wrote ['v(b) :- q(b).', 'v(d) :- p(d).'], reference has ['v(X) :- p(X).'].

### t1_mono_0012_anon  (gen@1=33%, gen@k=yes)
On 't1_mono_0012_anon', the model produced a framework that fits the training examples and solves the full problem in one stable extension. It introduced 1 new rule(s): 1 intensional copy. The rule 'v(X) :- p(X).' generalises by conditioning the target on the background predicate(s) p, so it applies to any constant satisfying them — including unseen ones. It also introduced the assumption(s) alpha(X) to make a rule defeasible, capturing exceptions. Semantically, the learned framework is equivalent to the symbolic reference (same entailments over the whole domain), via identical rules.

### t1_mono_0013_anon  (gen@1=0%, gen@k=no)
On 't1_mono_0013_anon', the model failed to fit the training examples. It introduced 2 new rule(s): 2 intensional copy. The rule 'v(X) :- p(X).' generalises by conditioning the target on the background predicate(s) p, so it applies to any constant satisfying them — including unseen ones. The rule 'v(X) :- q(X).' generalises by conditioning the target on the background predicate(s) q, so it applies to any constant satisfying them — including unseen ones. It differs from the symbolic reference on: v: model wrote ['v(X) :- p(X).', 'v(X) :- q(X).'], reference has ['v(X) :- p(X).'].

### t1_mono_0014_anon  (gen@1=0%, gen@k=no)
On 't1_mono_0014_anon', the model failed to fit the training examples. It introduced 2 new rule(s): 2 intensional copy. The rule 'v(X) :- p(X).' generalises by conditioning the target on the background predicate(s) p, so it applies to any constant satisfying them — including unseen ones. The rule 'v(X) :- q(X).' generalises by conditioning the target on the background predicate(s) q, so it applies to any constant satisfying them — including unseen ones. It also introduced the assumption(s) alpha(X) to make a rule defeasible, capturing exceptions. It differs from the symbolic reference on: v: model wrote ['v(X) :- p(X).', 'v(X) :- q(X).'], reference has ['v(X) :- p(X).'].

### t1_mono_0015_anon  (gen@1=33%, gen@k=yes)
On 't1_mono_0015_anon', the model produced a framework that fits the training examples and solves the full problem in one stable extension. It introduced 2 new rule(s): 2 intensional copy. The rule 'v(X) :- p(X).' generalises by conditioning the target on the background predicate(s) p, so it applies to any constant satisfying them — including unseen ones. The rule 'v(X) :- s(X).' generalises by conditioning the target on the background predicate(s) s, so it applies to any constant satisfying them — including unseen ones. It also introduced the assumption(s) alpha(X) to make a rule defeasible, capturing exceptions. Semantically, the learned framework is equivalent to the symbolic reference (same entailments over the whole domain), even though some rules are written differently.

### t1_mono_0016_anon  (gen@1=0%, gen@k=no)
On 't1_mono_0016_anon', the model failed to fit the training examples. It introduced 2 new rule(s): 2 intensional copy. The rule 'v(X) :- q(X).' generalises by conditioning the target on the background predicate(s) q, so it applies to any constant satisfying them — including unseen ones. The rule 'v(X) :- s(X).' generalises by conditioning the target on the background predicate(s) s, so it applies to any constant satisfying them — including unseen ones. It also introduced the assumption(s) alpha(d) to make a rule defeasible, capturing exceptions. It differs from the symbolic reference on: v: model wrote ['v(X) :- q(X).', 'v(X) :- s(X).'], reference has ['v(X) :- p(X).'].

### t1_mono_0017_anon  (gen@1=33%, gen@k=yes)
On 't1_mono_0017_anon', the model produced a framework that fits the training examples and solves the full problem in one stable extension. It introduced 2 new rule(s): 2 intensional copy. The rule 'v(X) :- p(X).' generalises by conditioning the target on the background predicate(s) p, so it applies to any constant satisfying them — including unseen ones. The rule 'v(X) :- q(X).' generalises by conditioning the target on the background predicate(s) q, so it applies to any constant satisfying them — including unseen ones. Semantically, the learned framework is equivalent to the symbolic reference (same entailments over the whole domain), even though some rules are written differently.

### t1_mono_0018_anon  (gen@1=33%, gen@k=yes)
On 't1_mono_0018_anon', the model produced a framework that fits the training examples and solves the full problem in one stable extension. It introduced 1 new rule(s): 1 intensional copy. The rule 'v(X) :- p(X).' generalises by conditioning the target on the background predicate(s) p, so it applies to any constant satisfying them — including unseen ones. It also introduced the assumption(s) alpha(X) to make a rule defeasible, capturing exceptions. Semantically, the learned framework is equivalent to the symbolic reference (same entailments over the whole domain), via identical rules.

### t1_mono_0019_anon  (gen@1=33%, gen@k=yes)
On 't1_mono_0019_anon', the model produced a framework that fits the training examples and solves the full problem in one stable extension. It introduced 1 new rule(s): 1 intensional copy. The rule 'v(X) :- q(X).' generalises by conditioning the target on the background predicate(s) q, so it applies to any constant satisfying them — including unseen ones. It differs from the symbolic reference on: v: model wrote ['v(X) :- q(X).'], reference has ['v(X) :- p(X).'].

### t2_defeas_0000_anon  (gen@1=0%, gen@k=no)
On 't2_defeas_0000_anon', the model failed to fit the training examples. It introduced 2 new rule(s): 1 assumption guarded, 1 mixed. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; v: model wrote ['v(X) :- t(X), not(u(X)).', 'v(X) :- t(X), u(X).'], reference has ['v(X) :- p(X), alpha_0(X).'].

### t2_defeas_0001_anon  (gen@1=0%, gen@k=no)
On 't2_defeas_0001_anon', the model failed to fit the training examples. It introduced 1 new rule(s): 1 intensional copy. The rule 'v(X) :- s(X).' generalises by conditioning the target on the background predicate(s) s, so it applies to any constant satisfying them — including unseen ones. It also introduced the assumption(s) alpha(b), alpha(c) to make a rule defeasible, capturing exceptions. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; v: model wrote ['v(X) :- s(X).'], reference has ['v(X) :- p(X), alpha_0(X).'].

### t2_defeas_0002_anon  (gen@1=0%, gen@k=no)
On 't2_defeas_0002_anon', the model failed to fit the training examples. It introduced 2 new rule(s): 1 assumption guarded, 1 intensional copy. The rule 'v(X) :- r(X), u(X).' generalises by conditioning the target on the background predicate(s) r, u, so it applies to any constant satisfying them — including unseen ones. The rule 'v(X) :- s(X).' generalises by conditioning the target on the background predicate(s) s, so it applies to any constant satisfying them — including unseen ones. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; v: model wrote ['v(X) :- r(X), u(X).', 'v(X) :- s(X).'], reference has ['v(X) :- p(X), alpha_0(X).'].

### t2_defeas_0003_anon  (gen@1=0%, gen@k=no)
On 't2_defeas_0003_anon', the model failed to fit the training examples. It introduced 2 new rule(s): 2 assumption guarded. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; v: model wrote ['v(X) :- q(X), u(X).', 'v(X) :- s(X), u(X).'], reference has ['v(X) :- p(X), alpha_0(X).'].

### t2_defeas_0004_anon  (gen@1=0%, gen@k=no)
On 't2_defeas_0004_anon', the model failed to fit the training examples. It introduced 1 new rule(s): 1 assumption guarded. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; v: model wrote ['v(X) :- q(X), u(X).'], reference has ['v(X) :- p(X), alpha_0(X).'].

### t2_defeas_0005_anon  (gen@1=0%, gen@k=no)
On 't2_defeas_0005_anon', the model failed to fit the training examples. It introduced 2 new rule(s): 1 contrary rule, 1 assumption guarded. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; t: model wrote ['t(X) :- v(X).'], reference has ['nothing']; v: model wrote ['v(X) :- t(X), u(X).'], reference has ['v(X) :- p(X), alpha_0(X).'].

### t2_defeas_0006_anon  (gen@1=0%, gen@k=no)
On 't2_defeas_0006_anon', the model fits the training examples but only classifies 50% of held-out examples correctly — partial generalisation. It introduced 2 new rule(s): 2 assumption guarded. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; v: model wrote ['v(X) :- q(X), u(X).', 'v(X) :- r(X), u(X).'], reference has ['v(X) :- p(X), alpha_0(X).', 'v(X) :- r(X).'].

### t2_defeas_0007_anon  (gen@1=0%, gen@k=no)
On 't2_defeas_0007_anon', the model failed to fit the training examples. It introduced 1 new rule(s): 1 assumption guarded. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; v: model wrote ['v(X) :- r(X), u(X).'], reference has ['v(X) :- p(X), alpha_0(X).'].

### t2_defeas_0008_anon  (gen@1=0%, gen@k=no)
On 't2_defeas_0008_anon', the candidate is NOT a legal solution: new assumption predicate 't' repurposes background non-assumption predicate 't'. The outcome below is reported for diagnosis only. On 't2_defeas_0008_anon', the model failed to fit the training examples. It introduced 2 new rule(s): 2 intensional copy. The rule 'v(X) :- q(X), t(X).' generalises by conditioning the target on the background predicate(s) q, t, so it applies to any constant satisfying them — including unseen ones. The rule 'v(X) :- p(X), t(X).' generalises by conditioning the target on the background predicate(s) p, t, so it applies to any constant satisfying them — including unseen ones. It also introduced the assumption(s) t(a) to make a rule defeasible, capturing exceptions. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; v: model wrote ['v(X) :- p(X), t(X).', 'v(X) :- q(X), t(X).'], reference has ['v(X) :- p(X), alpha_0(X).'].

### t2_defeas_0009_anon  (gen@1=0%, gen@k=no)
On 't2_defeas_0009_anon', the model failed to fit the training examples. It introduced 2 new rule(s): 2 intensional copy. The rule 'v(X) :- r(X).' generalises by conditioning the target on the background predicate(s) r, so it applies to any constant satisfying them — including unseen ones. The rule 'v(X) :- s(X).' generalises by conditioning the target on the background predicate(s) s, so it applies to any constant satisfying them — including unseen ones. It also introduced the assumption(s) alpha(d) to make a rule defeasible, capturing exceptions. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; v: model wrote ['v(X) :- r(X).', 'v(X) :- s(X).'], reference has ['v(X) :- p(X), alpha_0(X).'].

### t2_defeas_0010_anon  (gen@1=0%, gen@k=no)
On 't2_defeas_0010_anon', the model failed to fit the training examples. It introduced 2 new rule(s): 1 intensional copy, 1 contrary rule. The rule 'v(X) :- t(X), q(X).' generalises by conditioning the target on the background predicate(s) t, q, so it applies to any constant satisfying them — including unseen ones. The rule 't(X) :- v(X), u(X).' generalises by conditioning the target on the background predicate(s) v, u, so it applies to any constant satisfying them — including unseen ones. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; t: model wrote ['t(X) :- v(X), u(X).'], reference has ['nothing']; v: model wrote ['v(X) :- t(X), q(X).'], reference has ['v(X) :- p(X), alpha_0(X).'].

### t2_defeas_0011_anon  (gen@1=0%, gen@k=no)
On 't2_defeas_0011_anon', the model failed to fit the training examples. It introduced 1 new rule(s): 1 contrary rule. It also introduced the assumption(s) v(X) to make a rule defeasible, capturing exceptions. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; t: model wrote ['t(X) :- q(X), v(X).'], reference has ['nothing']; v: model wrote ['nothing'], reference has ['v(X) :- p(X), alpha_0(X).'].

### t2_defeas_0012_anon  (gen@1=0%, gen@k=no)
On 't2_defeas_0012_anon', the model failed to fit the training examples. It introduced 1 new rule(s): 1 assumption guarded. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; v: model wrote ['v(X) :- r(X), u(X).'], reference has ['v(X) :- p(X), alpha_0(X).'].

### t2_defeas_0013_anon  (gen@1=0%, gen@k=no)
On 't2_defeas_0013_anon', the model failed to fit the training examples. It introduced 1 new rule(s): 1 intensional copy. The rule 'v(X) :- t(X), q(X).' generalises by conditioning the target on the background predicate(s) t, q, so it applies to any constant satisfying them — including unseen ones. It differs from the symbolic reference on: v: model wrote ['v(X) :- t(X), q(X).'], reference has ['v(X) :- r(X).'].

### t2_defeas_0014_anon  (gen@1=0%, gen@k=no)
On 't2_defeas_0014_anon', the model failed to fit the training examples. It introduced 2 new rule(s): 2 intensional copy. The rule 'v(X) :- p(X), q(X).' generalises by conditioning the target on the background predicate(s) p, q, so it applies to any constant satisfying them — including unseen ones. The rule 'v(X) :- r(X).' generalises by conditioning the target on the background predicate(s) r, so it applies to any constant satisfying them — including unseen ones. It also introduced the assumption(s) alpha(b), alpha(d) to make a rule defeasible, capturing exceptions. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; v: model wrote ['v(X) :- p(X), q(X).', 'v(X) :- r(X).'], reference has ['v(X) :- p(X), alpha_0(X).'].

### t2_defeas_0015_anon  (gen@1=0%, gen@k=no)
On 't2_defeas_0015_anon', the model failed to fit the training examples. It introduced 1 new rule(s): 1 assumption guarded. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; v: model wrote ['v(X) :- q(X), u(X).'], reference has ['v(X) :- p(X), alpha_0(X).'].

### t2_defeas_0016_anon  (gen@1=0%, gen@k=no)
On 't2_defeas_0016_anon', the model failed to fit the training examples. It introduced 2 new rule(s): 2 intensional copy. The rule 'v(X) :- q(X).' generalises by conditioning the target on the background predicate(s) q, so it applies to any constant satisfying them — including unseen ones. The rule 'v(X) :- s(X).' generalises by conditioning the target on the background predicate(s) s, so it applies to any constant satisfying them — including unseen ones. It also introduced the assumption(s) alpha(c), alpha(d) to make a rule defeasible, capturing exceptions. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; v: model wrote ['v(X) :- q(X).', 'v(X) :- s(X).'], reference has ['v(X) :- p(X), alpha_0(X).'].

### t2_defeas_0017_anon  (gen@1=0%, gen@k=no)
On 't2_defeas_0017_anon', the model failed to fit the training examples. It introduced 2 new rule(s): 1 intensional copy, 1 assumption guarded. The rule 'v(X) :- q(X), t(X).' generalises by conditioning the target on the background predicate(s) q, t, so it applies to any constant satisfying them — including unseen ones. The rule 'v(X) :- q(X), u(X).' generalises by conditioning the target on the background predicate(s) q, u, so it applies to any constant satisfying them — including unseen ones. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; v: model wrote ['v(X) :- q(X), t(X).', 'v(X) :- q(X), u(X).'], reference has ['v(X) :- p(X), alpha_0(X).'].

### t2_defeas_0018_anon  (gen@1=0%, gen@k=no)
On 't2_defeas_0018_anon', the candidate is NOT a legal solution: new assumption predicate 't' repurposes background non-assumption predicate 't'. The outcome below is reported for diagnosis only. On 't2_defeas_0018_anon', the model failed to fit the training examples. It introduced 2 new rule(s): 2 intensional copy. The rule 'v(X) :- q(X), t(X).' generalises by conditioning the target on the background predicate(s) q, t, so it applies to any constant satisfying them — including unseen ones. The rule 'c_t(X) :- r(X).' generalises by conditioning the target on the background predicate(s) r, so it applies to any constant satisfying them — including unseen ones. It also introduced the assumption(s) t(X) to make a rule defeasible, capturing exceptions. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; c_t: model wrote ['c_t(X) :- r(X).'], reference has ['nothing']; v: model wrote ['v(X) :- q(X), t(X).'], reference has ['v(X) :- p(X), alpha_0(X).'].

### t2_defeas_0019_anon  (gen@1=0%, gen@k=no)
On 't2_defeas_0019_anon', the model failed to fit the training examples. It introduced 2 new rule(s): 1 intensional copy, 1 contrary rule. The rule 'v(X) :- t(X).' generalises by conditioning the target on the background predicate(s) t, so it applies to any constant satisfying them — including unseen ones. The rule 't(X) :- q(X).' generalises by conditioning the target on the background predicate(s) q, so it applies to any constant satisfying them — including unseen ones. It also introduced the assumption(s) alpha(X) to make a rule defeasible, capturing exceptions. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; t: model wrote ['t(X) :- q(X).'], reference has ['nothing']; v: model wrote ['v(X) :- t(X).'], reference has ['v(X) :- p(X), alpha_0(X).'].

### t3_noise_0000_anon  (gen@1=33%, gen@k=yes)
On 't3_noise_0000_anon', the model produced a framework that fits the training examples and solves the full problem in one stable extension. It introduced 2 new rule(s): 1 assumption guarded, 1 contrary rule. Semantically, the learned framework is equivalent to the symbolic reference (same entailments over the whole domain), even though some rules are written differently.

### t3_noise_0001_anon  (gen@1=0%, gen@k=no)
On 't3_noise_0001_anon', the model failed to fit the training examples. It introduced 1 new rule(s): 1 intensional copy. The rule 'p1(X) :- q(X).' generalises by conditioning the target on the background predicate(s) q, so it applies to any constant satisfying them — including unseen ones. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; p1: model wrote ['p1(X) :- q(X).'], reference has ['p1(X) :- p(X), alpha_0(X).'].

### t3_noise_0002_anon  (gen@1=33%, gen@k=yes)
On 't3_noise_0002_anon', the model produced a framework that fits the training examples and solves the full problem in one stable extension. It introduced 2 new rule(s): 1 assumption guarded, 1 contrary rule. Semantically, the learned framework is equivalent to the symbolic reference (same entailments over the whole domain), even though some rules are written differently.

### t3_noise_0003_anon  (gen@1=100%, gen@k=yes)
On 't3_noise_0003_anon', the model produced a framework that fits the training examples and solves the full problem in one stable extension. It introduced 1 new rule(s): 1 assumption guarded. Semantically, the learned framework is equivalent to the symbolic reference (same entailments over the whole domain), even though some rules are written differently.

### t3_noise_0004_anon  (gen@1=67%, gen@k=yes)
On 't3_noise_0004_anon', the model produced a framework that fits the training examples and solves the full problem in one stable extension. It introduced 2 new rule(s): 2 assumption guarded. Semantically, the learned framework is equivalent to the symbolic reference (same entailments over the whole domain), even though some rules are written differently.

### t3_noise_0005_anon  (gen@1=0%, gen@k=no)
On 't3_noise_0005_anon', the model failed to fit the training examples. It introduced 1 new rule(s): 1 assumption guarded. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; p1: model wrote ['p1(X) :- q(X), w(X).'], reference has ['p1(X) :- p(X), alpha_0(X).'].

### t3_noise_0006_anon  (gen@1=33%, gen@k=yes)
On 't3_noise_0006_anon', the model produced a framework that fits the training examples and solves the full problem in one stable extension. It introduced 2 new rule(s): 2 assumption guarded. Semantically, the learned framework is equivalent to the symbolic reference (same entailments over the whole domain), even though some rules are written differently.

### t3_noise_0007_anon  (gen@1=0%, gen@k=no)
On 't3_noise_0007_anon', the model failed to fit the training examples. It introduced 1 new rule(s): 1 intensional copy. The rule 'p1(X) :- v(X).' generalises by conditioning the target on the background predicate(s) v, so it applies to any constant satisfying them — including unseen ones. It also introduced the assumption(s) alpha(X) to make a rule defeasible, capturing exceptions. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; p1: model wrote ['p1(X) :- v(X).'], reference has ['p1(X) :- p(X), alpha_0(X).', 'p1(X) :- t(X).'].

### t3_noise_0008_anon  (gen@1=0%, gen@k=no)
On 't3_noise_0008_anon', the model failed to fit the training examples. It introduced 1 new rule(s): 1 assumption guarded. It differs from the symbolic reference on: p1: model wrote ['p1(X) :- q(X), w(X).'], reference has ['p1(X) :- r(X).'].

### t3_noise_0009_anon  (gen@1=33%, gen@k=yes)
On 't3_noise_0009_anon', the model produced a framework that fits the training examples and solves the full problem in one stable extension. It introduced 2 new rule(s): 1 assumption guarded, 1 contrary rule. Semantically, the learned framework is equivalent to the symbolic reference (same entailments over the whole domain), even though some rules are written differently.

### t3_noise_0010_anon  (gen@1=0%, gen@k=no)
On 't3_noise_0010_anon', the model failed to fit the training examples. It introduced 1 new rule(s): 1 assumption guarded. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; p1: model wrote ['p1(X) :- q(X), w(X).'], reference has ['p1(X) :- p(X), alpha_0(X).'].

### t3_noise_0011_anon  (gen@1=33%, gen@k=yes)
On 't3_noise_0011_anon', the model produced a framework that fits the training examples and solves the full problem in one stable extension. It introduced 1 new rule(s): 1 assumption guarded. Semantically, the learned framework is equivalent to the symbolic reference (same entailments over the whole domain), even though some rules are written differently.

### t3_noise_0012_anon  (gen@1=0%, gen@k=no)
On 't3_noise_0012_anon', the model failed to fit the training examples. It introduced 2 new rule(s): 1 intensional copy, 1 assumption guarded. The rule 'p1(X) :- v(X).' generalises by conditioning the target on the background predicate(s) v, so it applies to any constant satisfying them — including unseen ones. The rule 'p1(X) :- q(X), w(X).' generalises by conditioning the target on the background predicate(s) q, w, so it applies to any constant satisfying them — including unseen ones. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; p1: model wrote ['p1(X) :- q(X), w(X).', 'p1(X) :- v(X).'], reference has ['p1(X) :- p(X), alpha_0(X).'].

### t3_noise_0013_anon  (gen@1=0%, gen@k=no)
On 't3_noise_0013_anon', the model failed to fit the training examples. It introduced 2 new rule(s): 2 intensional copy. The rule 'p1(X) :- q(X).' generalises by conditioning the target on the background predicate(s) q, so it applies to any constant satisfying them — including unseen ones. The rule 'p1(X) :- r(X).' generalises by conditioning the target on the background predicate(s) r, so it applies to any constant satisfying them — including unseen ones. It also introduced the assumption(s) alpha(h), alpha(a) to make a rule defeasible, capturing exceptions. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; p1: model wrote ['p1(X) :- q(X).', 'p1(X) :- r(X).'], reference has ['p1(X) :- p(X), alpha_0(X).'].

### t3_noise_0014_anon  (gen@1=33%, gen@k=yes)
On 't3_noise_0014_anon', the model produced a framework that fits the training examples and solves the full problem in one stable extension. It introduced 1 new rule(s): 1 assumption guarded. Semantically, the learned framework is equivalent to the symbolic reference (same entailments over the whole domain), even though some rules are written differently.

### t3_noise_0015_anon  (gen@1=33%, gen@k=yes)
On 't3_noise_0015_anon', the model produced a framework that fits the training examples and solves the full problem in one stable extension. It introduced 2 new rule(s): 1 assumption guarded, 1 contrary rule. Semantically, the learned framework is equivalent to the symbolic reference (same entailments over the whole domain), even though some rules are written differently.

### t3_noise_0016_anon  (gen@1=67%, gen@k=yes)
On 't3_noise_0016_anon', the model produced a framework that fits the training examples and solves the full problem in one stable extension. It introduced 2 new rule(s): 2 assumption guarded. Semantically, the learned framework is equivalent to the symbolic reference (same entailments over the whole domain), even though some rules are written differently.

### t3_noise_0017_anon  (gen@1=0%, gen@k=no)
On 't3_noise_0017_anon', the model failed to fit the training examples. It introduced 2 new rule(s): 2 intensional copy. The rule 'p1(X) :- q(X).' generalises by conditioning the target on the background predicate(s) q, so it applies to any constant satisfying them — including unseen ones. The rule 'p1(X) :- r(X).' generalises by conditioning the target on the background predicate(s) r, so it applies to any constant satisfying them — including unseen ones. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; p1: model wrote ['p1(X) :- q(X).', 'p1(X) :- r(X).'], reference has ['p1(X) :- p(X), alpha_0(X).'].

### t3_noise_0018_anon  (gen@1=0%, gen@k=no)
On 't3_noise_0018_anon', the model failed to fit the training examples. It introduced 1 new rule(s): 1 assumption guarded. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; p1: model wrote ['p1(X) :- v(X), w(X).'], reference has ['p1(X) :- p(X), alpha_0(X).'].

### t3_noise_0019_anon  (gen@1=33%, gen@k=yes)
On 't3_noise_0019_anon', the model produced a framework that fits the training examples and solves the full problem in one stable extension. It introduced 1 new rule(s): 1 assumption guarded. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; p1: model wrote ['p1(X) :- p(X), w(X).'], reference has ['p1(X) :- p(X), alpha_0(X).', 'p1(X) :- t(X).'].

### t4_domain_0000_anon  (gen@1=0%, gen@k=no)
On 't4_domain_0000_anon', the model failed to fit the training examples. It introduced 3 new rule(s): 3 mixed. These are all ground facts — the model MEMORISED the training positives rather than learning a general rule, which is why it fails on held-out examples. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; v: model wrote ['v(b) :- q(b).', 'v(f) :- q(f).', 'v(g) :- q(g).'], reference has ['v(X) :- p(X), alpha_0(X).'].

### t4_domain_0001_anon  (gen@1=0%, gen@k=no)
On 't4_domain_0001_anon', the model failed to fit the training examples. It introduced 3 new rule(s): 3 mixed. These are all ground facts — the model MEMORISED the training positives rather than learning a general rule, which is why it fails on held-out examples. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; v: model wrote ['v(d) :- q(d).', 'v(e) :- q(e).', 'v(g) :- q(g).'], reference has ['v(X) :- p(X), alpha_0(X).'].

### t4_domain_0002_anon  (gen@1=0%, gen@k=no)
On 't4_domain_0002_anon', the model failed to fit the training examples. It introduced 1 new rule(s): 1 assumption guarded. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; v: model wrote ['v(X) :- q(X), u(X).'], reference has ['v(X) :- p(X), alpha_0(X).'].

### t4_domain_0003_anon  (gen@1=0%, gen@k=no)
On 't4_domain_0003_anon', the model failed to fit the training examples. It introduced 2 new rule(s): 2 assumption guarded. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; v: model wrote ['v(X) :- q(X), u(X).', 'v(X) :- t(X), u(X).'], reference has ['v(X) :- p(X), alpha_0(X).'].

### t4_domain_0004_anon  (gen@1=0%, gen@k=no)
On 't4_domain_0004_anon', the model failed to fit the training examples. It introduced 1 new rule(s): 1 assumption guarded. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; v: model wrote ['v(X) :- q(X), u(X).'], reference has ['v(X) :- p(X), alpha_0(X).'].

### t4_domain_0005_anon  (gen@1=0%, gen@k=no)
On 't4_domain_0005_anon', the model failed to fit the training examples. It introduced 3 new rule(s): 2 intensional copy, 1 assumption guarded. The rule 'v(X) :- t(X).' generalises by conditioning the target on the background predicate(s) t, so it applies to any constant satisfying them — including unseen ones. The rule 'v(X) :- s(X).' generalises by conditioning the target on the background predicate(s) s, so it applies to any constant satisfying them — including unseen ones. It also introduced the assumption(s) alpha(X) to make a rule defeasible, capturing exceptions. It differs from the symbolic reference on: c_alpha: model wrote ['c_alpha(X) :- u(X).'], reference has ['nothing']; c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; v: model wrote ['v(X) :- s(X).', 'v(X) :- t(X).'], reference has ['v(X) :- p(X), alpha_0(X).'].

### t4_domain_0006_anon  (gen@1=0%, gen@k=no)
On 't4_domain_0006_anon', the model failed to fit the training examples. It introduced 2 new rule(s): 1 intensional copy, 1 assumption guarded. The rule 'v(X) :- q(X), t(X).' generalises by conditioning the target on the background predicate(s) q, t, so it applies to any constant satisfying them — including unseen ones. The rule 'v(X) :- r(X), u(X).' generalises by conditioning the target on the background predicate(s) r, u, so it applies to any constant satisfying them — including unseen ones. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; v: model wrote ['v(X) :- q(X), t(X).', 'v(X) :- r(X), u(X).'], reference has ['v(X) :- p(X), alpha_0(X).'].

### t4_domain_0007_anon  (gen@1=0%, gen@k=no)
On 't4_domain_0007_anon', the model failed to fit the training examples. It introduced 2 new rule(s): 1 assumption guarded, 1 contrary rule. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; t: model wrote ['t(X) :- q(X).'], reference has ['nothing']; v: model wrote ['v(X) :- q(X), u(X).'], reference has ['v(X) :- p(X), alpha_0(X).'].

### t4_domain_0008_anon  (gen@1=0%, gen@k=no)
On 't4_domain_0008_anon', the model failed to fit the training examples. It introduced 2 new rule(s): 2 assumption guarded. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; v: model wrote ['v(X) :- q(X), u(X).', 'v(X) :- t(X), u(X).'], reference has ['v(X) :- p(X), alpha_0(X).', 'v(X) :- s(X).'].

### t4_domain_0009_anon  (gen@1=0%, gen@k=no)
On 't4_domain_0009_anon', the model failed to fit the training examples. It introduced 2 new rule(s): 1 intensional copy, 1 contrary rule. The rule 'v(X) :- q(X), t(X).' generalises by conditioning the target on the background predicate(s) q, t, so it applies to any constant satisfying them — including unseen ones. The rule 't(X) :- r(X).' generalises by conditioning the target on the background predicate(s) r, so it applies to any constant satisfying them — including unseen ones. It also introduced the assumption(s) alpha(a), alpha(d) to make a rule defeasible, capturing exceptions. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; t: model wrote ['t(X) :- r(X).'], reference has ['nothing']; v: model wrote ['v(X) :- q(X), t(X).'], reference has ['v(X) :- p(X), alpha_0(X).'].

### t4_domain_0010_anon  (gen@1=0%, gen@k=no)
On 't4_domain_0010_anon', the model failed to fit the training examples. It introduced 2 new rule(s): 1 intensional copy, 1 assumption guarded. The rule 'v(X) :- q(X), t(X).' generalises by conditioning the target on the background predicate(s) q, t, so it applies to any constant satisfying them — including unseen ones. The rule 'v(X) :- q(X), u(X).' generalises by conditioning the target on the background predicate(s) q, u, so it applies to any constant satisfying them — including unseen ones. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; v: model wrote ['v(X) :- q(X), t(X).', 'v(X) :- q(X), u(X).'], reference has ['v(X) :- p(X), alpha_0(X).'].

### t4_domain_0011_anon  (gen@1=0%, gen@k=no)
On 't4_domain_0011_anon', the model failed to fit the training examples. It introduced 2 new rule(s): 1 intensional copy, 1 contrary rule. The rule 'v(X) :- q(X), t(X).' generalises by conditioning the target on the background predicate(s) q, t, so it applies to any constant satisfying them — including unseen ones. The rule 't(X) :- q(X).' generalises by conditioning the target on the background predicate(s) q, so it applies to any constant satisfying them — including unseen ones. It also introduced the assumption(s) alpha(X) to make a rule defeasible, capturing exceptions. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; t: model wrote ['t(X) :- q(X).'], reference has ['nothing']; v: model wrote ['v(X) :- q(X), t(X).'], reference has ['v(X) :- p(X), alpha_0(X).'].

### t4_domain_0012_anon  (gen@1=0%, gen@k=no)
On 't4_domain_0012_anon', the model failed to fit the training examples. It introduced 2 new rule(s): 2 intensional copy. The rule 'v(X) :- q(X).' generalises by conditioning the target on the background predicate(s) q, so it applies to any constant satisfying them — including unseen ones. The rule 'v(X) :- t(X).' generalises by conditioning the target on the background predicate(s) t, so it applies to any constant satisfying them — including unseen ones. It also introduced the assumption(s) alpha(X) to make a rule defeasible, capturing exceptions. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; v: model wrote ['v(X) :- q(X).', 'v(X) :- t(X).'], reference has ['v(X) :- p(X), alpha_0(X).'].

### t4_domain_0013_anon  (gen@1=0%, gen@k=no)
On 't4_domain_0013_anon', the model failed to fit the training examples. It introduced 2 new rule(s): 2 intensional copy. The rule 'v(X) :- t(X).' generalises by conditioning the target on the background predicate(s) t, so it applies to any constant satisfying them — including unseen ones. The rule 'v(X) :- r(X).' generalises by conditioning the target on the background predicate(s) r, so it applies to any constant satisfying them — including unseen ones. It also introduced the assumption(s) alpha(a), alpha(i) to make a rule defeasible, capturing exceptions. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; v: model wrote ['v(X) :- r(X).', 'v(X) :- t(X).'], reference has ['v(X) :- p(X), alpha_0(X).', 'v(X) :- s(X).'].

### t4_domain_0014_anon  (gen@1=0%, gen@k=no)
On 't4_domain_0014_anon', the model failed to fit the training examples. It introduced 2 new rule(s): 1 intensional copy, 1 assumption guarded. The rule 'v(X) :- q(X), t(X).' generalises by conditioning the target on the background predicate(s) q, t, so it applies to any constant satisfying them — including unseen ones. The rule 'v(X) :- q(X), u(X).' generalises by conditioning the target on the background predicate(s) q, u, so it applies to any constant satisfying them — including unseen ones. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; v: model wrote ['v(X) :- q(X), t(X).', 'v(X) :- q(X), u(X).'], reference has ['v(X) :- p(X), alpha_0(X).'].

### t4_domain_0015_anon  (gen@1=0%, gen@k=no)
On 't4_domain_0015_anon', the model failed to fit the training examples. It introduced 2 new rule(s): 2 assumption guarded. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; v: model wrote ['v(X) :- q(X), u(X).', 'v(X) :- t(X), u(X).'], reference has ['v(X) :- p(X), alpha_0(X).'].

### t4_domain_0016_anon  (gen@1=0%, gen@k=no)
On 't4_domain_0016_anon', the model failed to fit the training examples. It introduced 2 new rule(s): 1 assumption guarded, 1 contrary rule. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; t: model wrote ['t(X) :- q(X).'], reference has ['nothing']; v: model wrote ['v(X) :- q(X), u(X).'], reference has ['v(X) :- p(X), alpha_0(X).'].

### t4_domain_0017_anon  (gen@1=0%, gen@k=no)
On 't4_domain_0017_anon', the model failed to fit the training examples. It introduced 1 new rule(s): 1 assumption guarded. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; v: model wrote ['v(X) :- q(X), u(X).'], reference has ['v(X) :- p(X), alpha_0(X).'].

### t4_domain_0018_anon  (gen@1=0%, gen@k=no)
On 't4_domain_0018_anon', the model failed to fit the training examples. It introduced 2 new rule(s): 1 intensional copy, 1 assumption guarded. The rule 'v(X) :- t(X).' generalises by conditioning the target on the background predicate(s) t, so it applies to any constant satisfying them — including unseen ones. The rule 'v(X) :- q(X), u(X).' generalises by conditioning the target on the background predicate(s) q, u, so it applies to any constant satisfying them — including unseen ones. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; v: model wrote ['v(X) :- q(X), u(X).', 'v(X) :- t(X).'], reference has ['v(X) :- p(X), alpha_0(X).'].

### t4_domain_0019_anon  (gen@1=0%, gen@k=no)
On 't4_domain_0019_anon', the model failed to fit the training examples. It introduced 1 new rule(s): 1 assumption guarded. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; v: model wrote ['v(X) :- q(X), u(X).'], reference has ['v(X) :- p(X), alpha_0(X).'].

### t5_twopath_0000_anon  (gen@1=0%, gen@k=no)
On 't5_twopath_0000_anon', the model fits the training examples but only classifies 50% of held-out examples correctly — partial generalisation. It introduced 1 new rule(s): 1 assumption guarded. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- s(X).']; c_alpha_1: model wrote ['nothing'], reference has ['c_alpha_1(X) :- r(X).']; p1: model wrote ['p1(X) :- p(X), v(X).'], reference has ['p1(X) :- p(X), alpha_1(X).', 'p1(X) :- q(X), alpha_0(X).'].

### t5_twopath_0001_anon  (gen@1=0%, gen@k=no)
On 't5_twopath_0001_anon', the model failed to fit the training examples. It introduced 2 new rule(s): 2 intensional copy. The rule 'p1(X) :- p(X).' generalises by conditioning the target on the background predicate(s) p, so it applies to any constant satisfying them — including unseen ones. The rule 'p1(X) :- q(X).' generalises by conditioning the target on the background predicate(s) q, so it applies to any constant satisfying them — including unseen ones. It also introduced the assumption(s) alpha(a), alpha(g), alpha(h) to make a rule defeasible, capturing exceptions. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- s(X).']; c_alpha_1: model wrote ['nothing'], reference has ['c_alpha_1(X) :- r(X).']; p1: model wrote ['p1(X) :- p(X).', 'p1(X) :- q(X).'], reference has ['p1(X) :- p(X), alpha_1(X).', 'p1(X) :- q(X), alpha_0(X).'].

### t5_twopath_0002_anon  (gen@1=0%, gen@k=no)
On 't5_twopath_0002_anon', the model failed to fit the training examples. It introduced 1 new rule(s): 1 intensional copy. The rule 'p1(X) :- p(X).' generalises by conditioning the target on the background predicate(s) p, so it applies to any constant satisfying them — including unseen ones. It also introduced the assumption(s) v(a), w(a) to make a rule defeasible, capturing exceptions. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- r(X).']; c_alpha_1: model wrote ['nothing'], reference has ['c_alpha_1(X) :- s(X).']; p1: model wrote ['p1(X) :- p(X).'], reference has ['p1(X) :- p(X), alpha_0(X).', 'p1(X) :- q(X), alpha_1(X).'].

### t5_twopath_0003_anon  (gen@1=0%, gen@k=no)
On 't5_twopath_0003_anon', the model failed to fit the training examples. It introduced 2 new rule(s): 2 intensional copy. The rule 'p1(X) :- p(X), q(X).' generalises by conditioning the target on the background predicate(s) p, q, so it applies to any constant satisfying them — including unseen ones. The rule 'p1(X) :- q(X), r(X).' generalises by conditioning the target on the background predicate(s) q, r, so it applies to any constant satisfying them — including unseen ones. It also introduced the assumption(s) alpha(d), alpha(f), alpha(b), alpha(e), alpha(g) to make a rule defeasible, capturing exceptions. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- r(X).']; c_alpha_1: model wrote ['nothing'], reference has ['c_alpha_1(X) :- s(X).']; p1: model wrote ['p1(X) :- p(X), q(X).', 'p1(X) :- q(X), r(X).'], reference has ['p1(X) :- p(X), alpha_0(X).', 'p1(X) :- q(X), alpha_1(X).'].

### t5_twopath_0004_anon  (gen@1=0%, gen@k=no)
On 't5_twopath_0004_anon', the model failed to fit the training examples. It introduced 1 new rule(s): 1 intensional copy. The rule 'p1(X) :- p(X), q(X).' generalises by conditioning the target on the background predicate(s) p, q, so it applies to any constant satisfying them — including unseen ones. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- r(X).']; c_alpha_1: model wrote ['nothing'], reference has ['c_alpha_1(X) :- s(X).']; p1: model wrote ['p1(X) :- p(X), q(X).'], reference has ['p1(X) :- p(X), alpha_0(X).', 'p1(X) :- q(X), alpha_1(X).'].

### t5_twopath_0005_anon  (gen@1=0%, gen@k=no)
On 't5_twopath_0005_anon', the model failed to fit the training examples. It introduced 1 new rule(s): 1 intensional copy. The rule 'p1(X) :- p(X).' generalises by conditioning the target on the background predicate(s) p, so it applies to any constant satisfying them — including unseen ones. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- r(X).']; c_alpha_1: model wrote ['nothing'], reference has ['c_alpha_1(X) :- s(X).']; p1: model wrote ['p1(X) :- p(X).'], reference has ['p1(X) :- p(X), alpha_0(X).', 'p1(X) :- q(X), alpha_1(X).'].

### t5_twopath_0006_anon  (gen@1=0%, gen@k=no)
On 't5_twopath_0006_anon', the model failed to fit the training examples. It introduced 1 new rule(s): 1 intensional copy. The rule 'p1(X) :- p(X), q(X).' generalises by conditioning the target on the background predicate(s) p, q, so it applies to any constant satisfying them — including unseen ones. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- s(X).']; c_alpha_1: model wrote ['nothing'], reference has ['c_alpha_1(X) :- r(X).']; p1: model wrote ['p1(X) :- p(X), q(X).'], reference has ['p1(X) :- p(X), alpha_1(X).', 'p1(X) :- q(X), alpha_0(X).'].

### t5_twopath_0007_anon  (gen@1=0%, gen@k=no)
On 't5_twopath_0007_anon', the model failed to fit the training examples. It introduced 1 new rule(s): 1 intensional copy. The rule 'p1(X) :- p(X).' generalises by conditioning the target on the background predicate(s) p, so it applies to any constant satisfying them — including unseen ones. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- r(X).']; c_alpha_1: model wrote ['nothing'], reference has ['c_alpha_1(X) :- s(X).']; p1: model wrote ['p1(X) :- p(X).'], reference has ['p1(X) :- p(X), alpha_0(X).', 'p1(X) :- q(X), alpha_1(X).'].

### t5_twopath_0008_anon  (gen@1=0%, gen@k=no)
On 't5_twopath_0008_anon', the model failed to fit the training examples. It introduced 1 new rule(s): 1 intensional copy. The rule 'p1(X) :- p(X).' generalises by conditioning the target on the background predicate(s) p, so it applies to any constant satisfying them — including unseen ones. It also introduced the assumption(s) alpha(X) to make a rule defeasible, capturing exceptions. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- r(X).']; c_alpha_1: model wrote ['nothing'], reference has ['c_alpha_1(X) :- s(X).']; p1: model wrote ['p1(X) :- p(X).'], reference has ['p1(X) :- p(X), alpha_0(X).', 'p1(X) :- q(X), alpha_1(X).'].

### t5_twopath_0009_anon  (gen@1=0%, gen@k=no)
On 't5_twopath_0009_anon', the model failed to fit the training examples. It introduced 1 new rule(s): 1 intensional copy. The rule 'p1(X) :- p(X).' generalises by conditioning the target on the background predicate(s) p, so it applies to any constant satisfying them — including unseen ones. It also introduced the assumption(s) alpha(a), alpha(e) to make a rule defeasible, capturing exceptions. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- r(X).']; c_alpha_1: model wrote ['nothing'], reference has ['c_alpha_1(X) :- s(X).']; p1: model wrote ['p1(X) :- p(X).'], reference has ['p1(X) :- p(X), alpha_0(X).', 'p1(X) :- q(X), alpha_1(X).'].

### t5_twopath_0010_anon  (gen@1=0%, gen@k=no)
On 't5_twopath_0010_anon', the model failed to fit the training examples. It introduced 2 new rule(s): 2 intensional copy. The rule 'p1(X) :- p(X).' generalises by conditioning the target on the background predicate(s) p, so it applies to any constant satisfying them — including unseen ones. The rule 'p1(X) :- q(X).' generalises by conditioning the target on the background predicate(s) q, so it applies to any constant satisfying them — including unseen ones. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- r(X).']; c_alpha_1: model wrote ['nothing'], reference has ['c_alpha_1(X) :- s(X).']; p1: model wrote ['p1(X) :- p(X).', 'p1(X) :- q(X).'], reference has ['p1(X) :- p(X), alpha_0(X).', 'p1(X) :- q(X), alpha_1(X).'].

### t5_twopath_0011_anon  (gen@1=0%, gen@k=no)
On 't5_twopath_0011_anon', the model failed to fit the training examples. It introduced 1 new rule(s): 1 intensional copy. The rule 'p1(X) :- p(X).' generalises by conditioning the target on the background predicate(s) p, so it applies to any constant satisfying them — including unseen ones. It also introduced the assumption(s) alpha(X) to make a rule defeasible, capturing exceptions. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- r(X).']; c_alpha_1: model wrote ['nothing'], reference has ['c_alpha_1(X) :- s(X).']; p1: model wrote ['p1(X) :- p(X).'], reference has ['p1(X) :- p(X), alpha_0(X).', 'p1(X) :- q(X), alpha_1(X).'].

### t5_twopath_0012_anon  (gen@1=0%, gen@k=no)
On 't5_twopath_0012_anon', the model failed to fit the training examples. It introduced 1 new rule(s): 1 intensional copy. The rule 'p1(X) :- q(X).' generalises by conditioning the target on the background predicate(s) q, so it applies to any constant satisfying them — including unseen ones. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- r(X).']; c_alpha_1: model wrote ['nothing'], reference has ['c_alpha_1(X) :- s(X).']; p1: model wrote ['p1(X) :- q(X).'], reference has ['p1(X) :- p(X), alpha_0(X).', 'p1(X) :- q(X), alpha_1(X).'].

### t5_twopath_0013_anon  (gen@1=0%, gen@k=no)
On 't5_twopath_0013_anon', the model fits the training examples but only classifies 50% of held-out examples correctly — partial generalisation. It introduced 1 new rule(s): 1 assumption guarded. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- r(X).']; c_alpha_1: model wrote ['nothing'], reference has ['c_alpha_1(X) :- s(X).']; p1: model wrote ['p1(X) :- p(X), v(X).'], reference has ['p1(X) :- p(X), alpha_0(X).', 'p1(X) :- q(X), alpha_1(X).'].

### t5_twopath_0014_anon  (gen@1=0%, gen@k=no)
On 't5_twopath_0014_anon', the model failed to fit the training examples. It introduced 1 new rule(s): 1 intensional copy. The rule 'p1(X) :- p(X).' generalises by conditioning the target on the background predicate(s) p, so it applies to any constant satisfying them — including unseen ones. It also introduced the assumption(s) alpha(X) to make a rule defeasible, capturing exceptions. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- r(X).']; c_alpha_1: model wrote ['nothing'], reference has ['c_alpha_1(X) :- s(X).']; p1: model wrote ['p1(X) :- p(X).'], reference has ['p1(X) :- p(X), alpha_0(X).', 'p1(X) :- q(X), alpha_1(X).'].

### t5_twopath_0015_anon  (gen@1=0%, gen@k=no)
On 't5_twopath_0015_anon', the model failed to fit the training examples. It introduced 1 new rule(s): 1 intensional copy. The rule 'p1(X) :- p(X).' generalises by conditioning the target on the background predicate(s) p, so it applies to any constant satisfying them — including unseen ones. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- r(X).']; c_alpha_1: model wrote ['nothing'], reference has ['c_alpha_1(X) :- s(X).']; p1: model wrote ['p1(X) :- p(X).'], reference has ['p1(X) :- p(X), alpha_0(X).', 'p1(X) :- q(X), alpha_1(X).'].

### t5_twopath_0016_anon  (gen@1=0%, gen@k=no)
On 't5_twopath_0016_anon', the model failed to fit the training examples. It introduced 1 new rule(s): 1 intensional copy. The rule 'p1(X) :- p(X).' generalises by conditioning the target on the background predicate(s) p, so it applies to any constant satisfying them — including unseen ones. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- s(X).']; c_alpha_1: model wrote ['nothing'], reference has ['c_alpha_1(X) :- r(X).']; p1: model wrote ['p1(X) :- p(X).'], reference has ['p1(X) :- p(X), alpha_1(X).', 'p1(X) :- q(X), alpha_0(X).'].

### t5_twopath_0017_anon  (gen@1=33%, gen@k=yes)
On 't5_twopath_0017_anon', the model produced a framework that fits the training examples and solves the full problem in one stable extension. It introduced 2 new rule(s): 2 assumption guarded. Semantically, the learned framework is equivalent to the symbolic reference (same entailments over the whole domain), even though some rules are written differently.

### t5_twopath_0018_anon  (gen@1=0%, gen@k=no)
On 't5_twopath_0018_anon', the model failed to fit the training examples. It introduced 3 new rule(s): 3 intensional copy. The rule 'p1(X) :- p(X), q(X).' generalises by conditioning the target on the background predicate(s) p, q, so it applies to any constant satisfying them — including unseen ones. The rule 'p1(X) :- p(X), q(X), r(X).' generalises by conditioning the target on the background predicate(s) p, q, r, so it applies to any constant satisfying them — including unseen ones. It also introduced the assumption(s) alpha(X) to make a rule defeasible, capturing exceptions. It differs from the symbolic reference on: c_alpha: model wrote ['c_alpha(X) :- s(X).'], reference has ['nothing']; c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- r(X).']; c_alpha_1: model wrote ['nothing'], reference has ['c_alpha_1(X) :- s(X).'].

### t5_twopath_0019_anon  (gen@1=0%, gen@k=no)
On 't5_twopath_0019_anon', the model failed to fit the training examples. It introduced 2 new rule(s): 2 intensional copy. The rule 'p1(X) :- p(X).' generalises by conditioning the target on the background predicate(s) p, so it applies to any constant satisfying them — including unseen ones. The rule 'p1(X) :- q(X).' generalises by conditioning the target on the background predicate(s) q, so it applies to any constant satisfying them — including unseen ones. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- r(X).']; c_alpha_1: model wrote ['nothing'], reference has ['c_alpha_1(X) :- s(X).']; p1: model wrote ['p1(X) :- p(X).', 'p1(X) :- q(X).'], reference has ['p1(X) :- p(X), alpha_0(X).', 'p1(X) :- q(X), alpha_1(X).'].


## Mode: guided

### nixon_diamond_anon  (gen@1=0%, gen@k=no)
On 'nixon_diamond_anon', the candidate is NOT a legal solution: flatness violated: assumption 'p1' used as rule head; new assumption predicate 'p1' repurposes background non-assumption predicate 'p1'. The outcome below is reported for diagnosis only. On 'nixon_diamond_anon', the model failed to fit the training examples. It introduced 3 new rule(s): 1 assumption guarded, 1 contrary rule, 1 ground fact. It also introduced the assumption(s) p1(X) to make a rule defeasible, capturing exceptions. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- p(X), w(X).']; c_p1: model wrote ['c_p1(X) :- X = b.'], reference has ['nothing']; p1: model wrote ['p1(X) :- r(X), t(X).'], reference has ['p1(X) :- p(X), alpha_0(X).'].

### flies_anon  (gen@1=0%, gen@k=no)
On 'flies_anon', the model failed to fit the training examples. It introduced 1 new rule(s): 1 intensional copy. The rule 't(X) :- p(X).' generalises by conditioning the target on the background predicate(s) p, so it applies to any constant satisfying them — including unseen ones. It also introduced the assumption(s) alpha(b) to make a rule defeasible, capturing exceptions. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; t: model wrote ['t(X) :- p(X).'], reference has ['t(X) :- p(X), alpha_0(X).'].

### tax_law_anon  (gen@1=0%, gen@k=no)
On 'tax_law_anon', the model failed to fit the training examples. It introduced 2 new rule(s): 1 intensional copy, 1 contrary rule. The rule 'u(X) :- p(X).' generalises by conditioning the target on the background predicate(s) p, so it applies to any constant satisfying them — including unseen ones. The rule 't(X) :- s(X).' generalises by conditioning the target on the background predicate(s) s, so it applies to any constant satisfying them — including unseen ones. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- p(X), alpha_1(X).']; c_alpha_1: model wrote ['nothing'], reference has ['c_alpha_1(X) :- p(X), alpha_0(X).']; t: model wrote ['t(X) :- s(X).'], reference has ['nothing'].

### t1_mono_0000_anon  (gen@1=33%, gen@k=yes)
On 't1_mono_0000_anon', the model produced a framework that fits the training examples and solves the full problem in one stable extension. It introduced 2 new rule(s): 2 intensional copy. The rule 'v(X) :- p(X).' generalises by conditioning the target on the background predicate(s) p, so it applies to any constant satisfying them — including unseen ones. The rule 'v(X) :- r(X).' generalises by conditioning the target on the background predicate(s) r, so it applies to any constant satisfying them — including unseen ones. It also introduced the assumption(s) alpha(a), alpha(d) to make a rule defeasible, capturing exceptions. Semantically, the learned framework is equivalent to the symbolic reference (same entailments over the whole domain), even though some rules are written differently.

### t1_mono_0001_anon  (gen@1=0%, gen@k=no)
On 't1_mono_0001_anon', the model failed to fit the training examples. It introduced 1 new rule(s): 1 intensional copy. The rule 'u(X) :- q(X).' generalises by conditioning the target on the background predicate(s) q, so it applies to any constant satisfying them — including unseen ones. It also introduced the assumption(s) alpha(f) to make a rule defeasible, capturing exceptions. It differs from the symbolic reference on: u: model wrote ['u(X) :- q(X).'], reference has ['u(X) :- p(X).'].

### t1_mono_0002_anon  (gen@1=0%, gen@k=no)
On 't1_mono_0002_anon', the model failed to fit the training examples. It introduced 1 new rule(s): 1 intensional copy. The rule 'v(X) :- v(X) :- t(X).' generalises by conditioning the target on the background predicate(s) v, so it applies to any constant satisfying them — including unseen ones. It also introduced the assumption(s) alpha(d), alpha(c) to make a rule defeasible, capturing exceptions. It differs from the symbolic reference on: v: model wrote ['v(X) :- v(X) :- t(X).'], reference has ['v(X) :- p(X).'].

### t1_mono_0003_anon  (gen@1=0%, gen@k=no)
On 't1_mono_0003_anon', the model failed to fit the training examples. It introduced 4 new rule(s): 1 intensional copy, 1 assumption guarded, 2 ground fact. The rule 'v(X) :- t(X).' generalises by conditioning the target on the background predicate(s) t, so it applies to any constant satisfying them — including unseen ones. The rule 'v(X) :- u(X), alpha(X).' generalises by conditioning the target on the background predicate(s) u, alpha, so it applies to any constant satisfying them — including unseen ones. It also introduced the assumption(s) alpha(X) to make a rule defeasible, capturing exceptions. It differs from the symbolic reference on: c_alpha: model wrote ['c_alpha(b) :- X = b.', 'c_alpha(c) :- X = c.'], reference has ['nothing']; v: model wrote ['v(X) :- t(X).', 'v(X) :- u(X), alpha(X).'], reference has ['v(X) :- p(X).'].

### t1_mono_0004_anon  (gen@1=0%, gen@k=no)
On 't1_mono_0004_anon', the model failed to fit the training examples. It introduced 2 new rule(s): 2 intensional copy. The rule 'v(X) :- t(X).' generalises by conditioning the target on the background predicate(s) t, so it applies to any constant satisfying them — including unseen ones. The rule 'v(X) :- q(X).' generalises by conditioning the target on the background predicate(s) q, so it applies to any constant satisfying them — including unseen ones. It also introduced the assumption(s) alpha(b), alpha(d) to make a rule defeasible, capturing exceptions. It differs from the symbolic reference on: v: model wrote ['v(X) :- q(X).', 'v(X) :- t(X).'], reference has ['v(X) :- p(X).'].

### t1_mono_0005_anon  (gen@1=0%, gen@k=no)
On 't1_mono_0005_anon', the model failed to fit the training examples. It introduced 1 new rule(s): 1 intensional copy. The rule 'v(X) :- t(X).' generalises by conditioning the target on the background predicate(s) t, so it applies to any constant satisfying them — including unseen ones. It differs from the symbolic reference on: v: model wrote ['v(X) :- t(X).'], reference has ['v(X) :- p(X).'].

### t1_mono_0006_anon  (gen@1=0%, gen@k=no)
On 't1_mono_0006_anon', the candidate is NOT a legal solution: flatness violated: assumption 'u' used as rule head. The outcome below is reported for diagnosis only. On 't1_mono_0006_anon', the model failed to fit the training examples. It introduced 3 new rule(s): 1 intensional copy, 1 contrary rule, 1 ground fact. The rule 'v(X) :- q(X).' generalises by conditioning the target on the background predicate(s) q, so it applies to any constant satisfying them — including unseen ones. The rule 's(X) :- t(X), u(X).' generalises by conditioning the target on the background predicate(s) t, u, so it applies to any constant satisfying them — including unseen ones. It differs from the symbolic reference on: s: model wrote ['s(X) :- t(X), u(X).'], reference has ['nothing']; u: model wrote ['u(a) defeated_by s(a).'], reference has ['nothing']; v: model wrote ['v(X) :- q(X).'], reference has ['v(X) :- p(X).'].

### t1_mono_0007_anon  (gen@1=0%, gen@k=no)
On 't1_mono_0007_anon', the model failed to fit the training examples. It introduced 1 new rule(s): 1 intensional copy. The rule 'v(X) :- t(X).' generalises by conditioning the target on the background predicate(s) t, so it applies to any constant satisfying them — including unseen ones. It differs from the symbolic reference on: v: model wrote ['v(X) :- t(X).'], reference has ['v(X) :- p(X).'].

### t1_mono_0008_anon  (gen@1=33%, gen@k=yes)
On 't1_mono_0008_anon', the model produced a framework that fits the training examples and solves the full problem in one stable extension. It introduced 2 new rule(s): 1 intensional copy, 1 contrary rule. The rule 'u(X) :- p(X).' generalises by conditioning the target on the background predicate(s) p, so it applies to any constant satisfying them — including unseen ones. The rule 'r(X) :- s(X), t(X).' generalises by conditioning the target on the background predicate(s) s, t, so it applies to any constant satisfying them — including unseen ones. Semantically, the learned framework is equivalent to the symbolic reference (same entailments over the whole domain), even though some rules are written differently.

### t1_mono_0009_anon  (gen@1=0%, gen@k=no)
On 't1_mono_0009_anon', the model fits the training examples but only classifies 50% of held-out examples correctly — partial generalisation. It introduced 2 new rule(s): 2 intensional copy. The rule 'v(X) :- t(X).' generalises by conditioning the target on the background predicate(s) t, so it applies to any constant satisfying them — including unseen ones. The rule 'v(X) :- r(X).' generalises by conditioning the target on the background predicate(s) r, so it applies to any constant satisfying them — including unseen ones. It also introduced the assumption(s) alpha(X) to make a rule defeasible, capturing exceptions. It differs from the symbolic reference on: v: model wrote ['v(X) :- r(X).', 'v(X) :- t(X).'], reference has ['v(X) :- p(X).'].

### t1_mono_0010_anon  (gen@1=0%, gen@k=no)
On 't1_mono_0010_anon', the model failed to fit the training examples. It introduced 2 new rule(s): 2 intensional copy. The rule 'v(X) :- t(X).' generalises by conditioning the target on the background predicate(s) t, so it applies to any constant satisfying them — including unseen ones. The rule 'v(X) :- s(X), alpha(X).' generalises by conditioning the target on the background predicate(s) s, alpha, so it applies to any constant satisfying them — including unseen ones. It also introduced the assumption(s) alpha(X) to make a rule defeasible, capturing exceptions. It differs from the symbolic reference on: v: model wrote ['v(X) :- s(X), alpha(X).', 'v(X) :- t(X).'], reference has ['v(X) :- p(X).'].

### t1_mono_0011_anon  (gen@1=0%, gen@k=no)
On 't1_mono_0011_anon', the model failed to fit the training examples. It introduced 2 new rule(s): 2 intensional copy. The rule 'v(X) :- t(X).' generalises by conditioning the target on the background predicate(s) t, so it applies to any constant satisfying them — including unseen ones. The rule 'v(X) :- s(X), alpha(X).' generalises by conditioning the target on the background predicate(s) s, alpha, so it applies to any constant satisfying them — including unseen ones. It also introduced the assumption(s) alpha(X) to make a rule defeasible, capturing exceptions. It differs from the symbolic reference on: v: model wrote ['v(X) :- s(X), alpha(X).', 'v(X) :- t(X).'], reference has ['v(X) :- p(X).'].

### t1_mono_0012_anon  (gen@1=0%, gen@k=no)
On 't1_mono_0012_anon', the model failed to fit the training examples. It introduced 1 new rule(s): 1 intensional copy. The rule 'v(X) :- v(X) :- dom(X).' generalises by conditioning the target on the background predicate(s) v, so it applies to any constant satisfying them — including unseen ones. It also introduced the assumption(s) alpha(d) to make a rule defeasible, capturing exceptions. It differs from the symbolic reference on: v: model wrote ['v(X) :- v(X) :- dom(X).'], reference has ['v(X) :- p(X).'].

### t1_mono_0013_anon  (gen@1=0%, gen@k=no)
On 't1_mono_0013_anon', the model failed to fit the training examples. It introduced 2 new rule(s): 1 intensional copy, 1 assumption guarded. The rule 'v(X) :- t(X).' generalises by conditioning the target on the background predicate(s) t, so it applies to any constant satisfying them — including unseen ones. The rule 'v(X) :- u(X), alpha(X).' generalises by conditioning the target on the background predicate(s) u, alpha, so it applies to any constant satisfying them — including unseen ones. It also introduced the assumption(s) alpha(X) to make a rule defeasible, capturing exceptions. It differs from the symbolic reference on: v: model wrote ['v(X) :- t(X).', 'v(X) :- u(X), alpha(X).'], reference has ['v(X) :- p(X).'].

### t1_mono_0014_anon  (gen@1=0%, gen@k=no)
On 't1_mono_0014_anon', the model failed to fit the training examples. It introduced 2 new rule(s): 2 intensional copy. The rule 'v(X) :- q(X).' generalises by conditioning the target on the background predicate(s) q, so it applies to any constant satisfying them — including unseen ones. The rule 'v(X) :- r(X).' generalises by conditioning the target on the background predicate(s) r, so it applies to any constant satisfying them — including unseen ones. It also introduced the assumption(s) alpha(d), alpha(b) to make a rule defeasible, capturing exceptions. It differs from the symbolic reference on: v: model wrote ['v(X) :- q(X).', 'v(X) :- r(X).'], reference has ['v(X) :- p(X).'].

### t1_mono_0015_anon  (gen@1=0%, gen@k=no)
On 't1_mono_0015_anon', the model failed to fit the training examples. It introduced 2 new rule(s): 1 intensional copy, 1 assumption guarded. The rule 'v(X) :- t(X).' generalises by conditioning the target on the background predicate(s) t, so it applies to any constant satisfying them — including unseen ones. The rule 'v(X) :- u(X).' generalises by conditioning the target on the background predicate(s) u, so it applies to any constant satisfying them — including unseen ones. It differs from the symbolic reference on: v: model wrote ['v(X) :- t(X).', 'v(X) :- u(X).'], reference has ['v(X) :- p(X).'].

### t1_mono_0016_anon  (gen@1=0%, gen@k=no)
On 't1_mono_0016_anon', the model failed to fit the training examples. It introduced 3 new rule(s): 2 mixed, 1 intensional copy. The rule 'v(X) :- t(X).' generalises by conditioning the target on the background predicate(s) t, so it applies to any constant satisfying them — including unseen ones. It also introduced the assumption(s) alpha(X) to make a rule defeasible, capturing exceptions. It differs from the symbolic reference on: v: model wrote ['v(X) :- t(X).', 'v(X) :- v(a).', 'v(X) :- v(d).'], reference has ['v(X) :- p(X).'].

### t1_mono_0017_anon  (gen@1=0%, gen@k=no)
On 't1_mono_0017_anon', the model failed to fit the training examples. It introduced 2 new rule(s): 2 intensional copy. The rule 'v(X) :- dom(X), r(X).' generalises by conditioning the target on the background predicate(s) r, so it applies to any constant satisfying them — including unseen ones. The rule 'v(X) :- dom(X), s(X).' generalises by conditioning the target on the background predicate(s) s, so it applies to any constant satisfying them — including unseen ones. It also introduced the assumption(s) alpha(X) to make a rule defeasible, capturing exceptions. It differs from the symbolic reference on: v: model wrote ['v(X) :- dom(X), r(X).', 'v(X) :- dom(X), s(X).'], reference has ['v(X) :- p(X).'].

### t1_mono_0018_anon  (gen@1=0%, gen@k=no)
On 't1_mono_0018_anon', the model failed to fit the training examples. It introduced 2 new rule(s): 2 intensional copy. The rule 'v(X) :- t(X).' generalises by conditioning the target on the background predicate(s) t, so it applies to any constant satisfying them — including unseen ones. The rule 'v(X) :- r(X).' generalises by conditioning the target on the background predicate(s) r, so it applies to any constant satisfying them — including unseen ones. It also introduced the assumption(s) alpha(b), alpha(c) to make a rule defeasible, capturing exceptions. It differs from the symbolic reference on: v: model wrote ['v(X) :- r(X).', 'v(X) :- t(X).'], reference has ['v(X) :- p(X).'].

### t1_mono_0019_anon  (gen@1=0%, gen@k=no)
On 't1_mono_0019_anon', the model failed to fit the training examples. It introduced 3 new rule(s): 1 intensional copy, 1 assumption guarded, 1 ground fact. The rule 'v(X) :- t(X).' generalises by conditioning the target on the background predicate(s) t, so it applies to any constant satisfying them — including unseen ones. The rule 'v(X) :- u(X), alpha(X).' generalises by conditioning the target on the background predicate(s) u, alpha, so it applies to any constant satisfying them — including unseen ones. It differs from the symbolic reference on: c_alpha: model wrote ['c_alpha(X) :- X = f.'], reference has ['nothing']; v: model wrote ['v(X) :- t(X).', 'v(X) :- u(X), alpha(X).'], reference has ['v(X) :- p(X).'].

### t2_defeas_0000_anon  (gen@1=0%, gen@k=no)
On 't2_defeas_0000_anon', the model failed to fit the training examples. It introduced 3 new rule(s): 2 intensional copy, 1 contrary rule. The rule 'v(X) :- q(X).' generalises by conditioning the target on the background predicate(s) q, so it applies to any constant satisfying them — including unseen ones. The rule 't(X) :- q(X), u(X).' generalises by conditioning the target on the background predicate(s) q, u, so it applies to any constant satisfying them — including unseen ones. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; c_u: model wrote ['c_u(X) :- e.'], reference has ['nothing']; t: model wrote ['t(X) :- q(X), u(X).'], reference has ['nothing'].

### t2_defeas_0001_anon  (gen@1=0%, gen@k=no)
On 't2_defeas_0001_anon', the model failed to fit the training examples. It introduced 2 new rule(s): 1 intensional copy, 1 contrary rule. The rule 'v(X) :- q(X).' generalises by conditioning the target on the background predicate(s) q, so it applies to any constant satisfying them — including unseen ones. The rule 't(X) :- q(X), u(X).' generalises by conditioning the target on the background predicate(s) q, u, so it applies to any constant satisfying them — including unseen ones. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; t: model wrote ['t(X) :- q(X), u(X).'], reference has ['nothing']; v: model wrote ['v(X) :- q(X).'], reference has ['v(X) :- p(X), alpha_0(X).'].

### t2_defeas_0002_anon  (gen@1=0%, gen@k=no)
On 't2_defeas_0002_anon', the model failed to fit the training examples. It introduced 2 new rule(s): 1 intensional copy, 1 contrary rule. The rule 'v(X) :- q(X).' generalises by conditioning the target on the background predicate(s) q, so it applies to any constant satisfying them — including unseen ones. The rule 't(X) :- q(X), u(X).' generalises by conditioning the target on the background predicate(s) q, u, so it applies to any constant satisfying them — including unseen ones. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; t: model wrote ['t(X) :- q(X), u(X).'], reference has ['nothing']; v: model wrote ['v(X) :- q(X).'], reference has ['v(X) :- p(X), alpha_0(X).'].

### t2_defeas_0003_anon  (gen@1=0%, gen@k=no)
On 't2_defeas_0003_anon', the model failed to fit the training examples. It introduced 2 new rule(s): 1 intensional copy, 1 contrary rule. The rule 'v(X) :- q(X).' generalises by conditioning the target on the background predicate(s) q, so it applies to any constant satisfying them — including unseen ones. The rule 't(X) :- v(X), alpha(X).' generalises by conditioning the target on the background predicate(s) v, alpha, so it applies to any constant satisfying them — including unseen ones. It also introduced the assumption(s) alpha(X) to make a rule defeasible, capturing exceptions. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; t: model wrote ['t(X) :- v(X), alpha(X).'], reference has ['nothing']; v: model wrote ['v(X) :- q(X).'], reference has ['v(X) :- p(X), alpha_0(X).'].

### t2_defeas_0004_anon  (gen@1=0%, gen@k=no)
On 't2_defeas_0004_anon', the model failed to fit the training examples. It introduced 3 new rule(s): 1 intensional copy, 1 contrary rule, 1 ground fact. The rule 'v(X) :- q(X).' generalises by conditioning the target on the background predicate(s) q, so it applies to any constant satisfying them — including unseen ones. The rule 't(X) :- q(X), u(X).' generalises by conditioning the target on the background predicate(s) q, u, so it applies to any constant satisfying them — including unseen ones. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; c_u: model wrote ['c_u(X) :- X = a.'], reference has ['nothing']; t: model wrote ['t(X) :- q(X), u(X).'], reference has ['nothing'].

### t2_defeas_0005_anon  (gen@1=0%, gen@k=no)
On 't2_defeas_0005_anon', the model failed to fit the training examples. It introduced 2 new rule(s): 1 intensional copy, 1 contrary rule. The rule 'v(X) :- q(X).' generalises by conditioning the target on the background predicate(s) q, so it applies to any constant satisfying them — including unseen ones. The rule 't(X) :- q(X), u(X).' generalises by conditioning the target on the background predicate(s) q, u, so it applies to any constant satisfying them — including unseen ones. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; t: model wrote ['t(X) :- q(X), u(X).'], reference has ['nothing']; v: model wrote ['v(X) :- q(X).'], reference has ['v(X) :- p(X), alpha_0(X).'].

### t2_defeas_0006_anon  (gen@1=0%, gen@k=no)
On 't2_defeas_0006_anon', the model failed to fit the training examples. It introduced 2 new rule(s): 1 intensional copy, 1 contrary rule. The rule 'v(X) :- q(X).' generalises by conditioning the target on the background predicate(s) q, so it applies to any constant satisfying them — including unseen ones. The rule 't(X) :- u(X).' generalises by conditioning the target on the background predicate(s) u, so it applies to any constant satisfying them — including unseen ones. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; t: model wrote ['t(X) :- u(X).'], reference has ['nothing']; v: model wrote ['v(X) :- q(X).'], reference has ['v(X) :- p(X), alpha_0(X).', 'v(X) :- r(X).'].

### t2_defeas_0007_anon  (gen@1=0%, gen@k=no)
On 't2_defeas_0007_anon', the model failed to fit the training examples. It introduced 2 new rule(s): 1 intensional copy, 1 contrary rule. The rule 'v(X) :- q(X).' generalises by conditioning the target on the background predicate(s) q, so it applies to any constant satisfying them — including unseen ones. The rule 't(X) :- q(X), u(X).' generalises by conditioning the target on the background predicate(s) q, u, so it applies to any constant satisfying them — including unseen ones. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; t: model wrote ['t(X) :- q(X), u(X).'], reference has ['nothing']; v: model wrote ['v(X) :- q(X).'], reference has ['v(X) :- p(X), alpha_0(X).'].

### t2_defeas_0008_anon  (gen@1=0%, gen@k=no)
On 't2_defeas_0008_anon', the model failed to fit the training examples. It introduced 1 new rule(s): 1 intensional copy. The rule 'v(X) :- q(X).' generalises by conditioning the target on the background predicate(s) q, so it applies to any constant satisfying them — including unseen ones. It also introduced the assumption(s) alpha(X) to make a rule defeasible, capturing exceptions. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; v: model wrote ['v(X) :- q(X).'], reference has ['v(X) :- p(X), alpha_0(X).'].

### t2_defeas_0009_anon  (gen@1=0%, gen@k=no)
On 't2_defeas_0009_anon', the model failed to fit the training examples. It introduced 2 new rule(s): 1 intensional copy, 1 contrary rule. The rule 'v(X) :- q(X).' generalises by conditioning the target on the background predicate(s) q, so it applies to any constant satisfying them — including unseen ones. The rule 't(X) :- q(X), u(X).' generalises by conditioning the target on the background predicate(s) q, u, so it applies to any constant satisfying them — including unseen ones. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; t: model wrote ['t(X) :- q(X), u(X).'], reference has ['nothing']; v: model wrote ['v(X) :- q(X).'], reference has ['v(X) :- p(X), alpha_0(X).'].

### t2_defeas_0010_anon  (gen@1=0%, gen@k=no)
On 't2_defeas_0010_anon', the model failed to fit the training examples. It introduced 4 new rule(s): 1 intensional copy, 1 contrary rule, 2 ground fact. The rule 'v(X) :- q(X).' generalises by conditioning the target on the background predicate(s) q, so it applies to any constant satisfying them — including unseen ones. The rule 't(X) :- q(X), alpha(X).' generalises by conditioning the target on the background predicate(s) q, alpha, so it applies to any constant satisfying them — including unseen ones. It also introduced the assumption(s) alpha(X) to make a rule defeasible, capturing exceptions. It differs from the symbolic reference on: c_alpha: model wrote ['c_alpha(X) :- X = a.', 'c_alpha(X) :- X = e.'], reference has ['nothing']; c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; t: model wrote ['t(X) :- q(X), alpha(X).'], reference has ['nothing'].

### t2_defeas_0011_anon  (gen@1=0%, gen@k=no)
On 't2_defeas_0011_anon', the model failed to fit the training examples. It introduced 2 new rule(s): 1 intensional copy, 1 contrary rule. The rule 'v(X) :- q(X).' generalises by conditioning the target on the background predicate(s) q, so it applies to any constant satisfying them — including unseen ones. The rule 't(X) :- u(X).' generalises by conditioning the target on the background predicate(s) u, so it applies to any constant satisfying them — including unseen ones. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; t: model wrote ['t(X) :- u(X).'], reference has ['nothing']; v: model wrote ['v(X) :- q(X).'], reference has ['v(X) :- p(X), alpha_0(X).'].

### t2_defeas_0012_anon  (gen@1=0%, gen@k=no)
On 't2_defeas_0012_anon', the model failed to fit the training examples. It introduced 2 new rule(s): 1 intensional copy, 1 contrary rule. The rule 'v(X) :- q(X).' generalises by conditioning the target on the background predicate(s) q, so it applies to any constant satisfying them — including unseen ones. The rule 't(X) :- u(X).' generalises by conditioning the target on the background predicate(s) u, so it applies to any constant satisfying them — including unseen ones. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; t: model wrote ['t(X) :- u(X).'], reference has ['nothing']; v: model wrote ['v(X) :- q(X).'], reference has ['v(X) :- p(X), alpha_0(X).'].

### t2_defeas_0013_anon  (gen@1=0%, gen@k=no)
On 't2_defeas_0013_anon', the model failed to fit the training examples. It introduced 2 new rule(s): 1 intensional copy, 1 contrary rule. The rule 'v(X) :- q(X).' generalises by conditioning the target on the background predicate(s) q, so it applies to any constant satisfying them — including unseen ones. The rule 't(X) :- v(X), u(X).' generalises by conditioning the target on the background predicate(s) v, u, so it applies to any constant satisfying them — including unseen ones. It differs from the symbolic reference on: t: model wrote ['t(X) :- v(X), u(X).'], reference has ['nothing']; v: model wrote ['v(X) :- q(X).'], reference has ['v(X) :- r(X).'].

### t2_defeas_0014_anon  (gen@1=0%, gen@k=no)
On 't2_defeas_0014_anon', the model failed to fit the training examples. It introduced 2 new rule(s): 2 intensional copy. The rule 'v(X) :- q(X).' generalises by conditioning the target on the background predicate(s) q, so it applies to any constant satisfying them — including unseen ones. The rule 'v(X) :- s(X).' generalises by conditioning the target on the background predicate(s) s, so it applies to any constant satisfying them — including unseen ones. It also introduced the assumption(s) alpha(b), alpha(d) to make a rule defeasible, capturing exceptions. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; v: model wrote ['v(X) :- q(X).', 'v(X) :- s(X).'], reference has ['v(X) :- p(X), alpha_0(X).'].

### t2_defeas_0015_anon  (gen@1=0%, gen@k=no)
On 't2_defeas_0015_anon', the model failed to fit the training examples. It introduced 2 new rule(s): 1 intensional copy, 1 contrary rule. The rule 'v(X) :- q(X).' generalises by conditioning the target on the background predicate(s) q, so it applies to any constant satisfying them — including unseen ones. The rule 't(X) :- u(X).' generalises by conditioning the target on the background predicate(s) u, so it applies to any constant satisfying them — including unseen ones. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; t: model wrote ['t(X) :- u(X).'], reference has ['nothing']; v: model wrote ['v(X) :- q(X).'], reference has ['v(X) :- p(X), alpha_0(X).'].

### t2_defeas_0016_anon  (gen@1=0%, gen@k=no)
On 't2_defeas_0016_anon', the model failed to fit the training examples. It introduced 2 new rule(s): 1 intensional copy, 1 contrary rule. The rule 'v(X) :- q(X).' generalises by conditioning the target on the background predicate(s) q, so it applies to any constant satisfying them — including unseen ones. The rule 't(X) :- q(X), u(X).' generalises by conditioning the target on the background predicate(s) q, u, so it applies to any constant satisfying them — including unseen ones. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; t: model wrote ['t(X) :- q(X), u(X).'], reference has ['nothing']; v: model wrote ['v(X) :- q(X).'], reference has ['v(X) :- p(X), alpha_0(X).'].

### t2_defeas_0017_anon  (gen@1=0%, gen@k=no)
On 't2_defeas_0017_anon', the model failed to fit the training examples. It introduced 2 new rule(s): 1 intensional copy, 1 contrary rule. The rule 'v(X) :- q(X).' generalises by conditioning the target on the background predicate(s) q, so it applies to any constant satisfying them — including unseen ones. The rule 't(X) :- u(X).' generalises by conditioning the target on the background predicate(s) u, so it applies to any constant satisfying them — including unseen ones. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; t: model wrote ['t(X) :- u(X).'], reference has ['nothing']; v: model wrote ['v(X) :- q(X).'], reference has ['v(X) :- p(X), alpha_0(X).'].

### t2_defeas_0018_anon  (gen@1=0%, gen@k=no)
On 't2_defeas_0018_anon', the model failed to fit the training examples. It introduced 2 new rule(s): 1 intensional copy, 1 contrary rule. The rule 'v(X) :- q(X).' generalises by conditioning the target on the background predicate(s) q, so it applies to any constant satisfying them — including unseen ones. The rule 't(X) :- r(X), u(X).' generalises by conditioning the target on the background predicate(s) r, u, so it applies to any constant satisfying them — including unseen ones. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; t: model wrote ['t(X) :- r(X), u(X).'], reference has ['nothing']; v: model wrote ['v(X) :- q(X).'], reference has ['v(X) :- p(X), alpha_0(X).'].

### t2_defeas_0019_anon  (gen@1=0%, gen@k=no)
On 't2_defeas_0019_anon', the model failed to fit the training examples. It introduced 2 new rule(s): 1 intensional copy, 1 contrary rule. The rule 'v(X) :- q(X).' generalises by conditioning the target on the background predicate(s) q, so it applies to any constant satisfying them — including unseen ones. The rule 't(X) :- q(X), u(X).' generalises by conditioning the target on the background predicate(s) q, u, so it applies to any constant satisfying them — including unseen ones. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; t: model wrote ['t(X) :- q(X), u(X).'], reference has ['nothing']; v: model wrote ['v(X) :- q(X).'], reference has ['v(X) :- p(X), alpha_0(X).'].

### t3_noise_0000_anon  (gen@1=0%, gen@k=no)
On 't3_noise_0000_anon', the model failed to fit the training examples. It introduced 2 new rule(s): 1 intensional copy, 1 contrary rule. The rule 'p1(X) :- q(X).' generalises by conditioning the target on the background predicate(s) q, so it applies to any constant satisfying them — including unseen ones. The rule 'v(X) :- r(X).' generalises by conditioning the target on the background predicate(s) r, so it applies to any constant satisfying them — including unseen ones. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; p1: model wrote ['p1(X) :- q(X).'], reference has ['p1(X) :- p(X), alpha_0(X).']; v: model wrote ['v(X) :- r(X).'], reference has ['nothing'].

### t3_noise_0001_anon  (gen@1=0%, gen@k=no)
On 't3_noise_0001_anon', the model failed to fit the training examples. It introduced 1 new rule(s): 1 intensional copy. The rule 'p1(X) :- q(X).' generalises by conditioning the target on the background predicate(s) q, so it applies to any constant satisfying them — including unseen ones. It also introduced the assumption(s) alpha(e), alpha(d) to make a rule defeasible, capturing exceptions. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; p1: model wrote ['p1(X) :- q(X).'], reference has ['p1(X) :- p(X), alpha_0(X).'].

### t3_noise_0002_anon  (gen@1=0%, gen@k=no)
On 't3_noise_0002_anon', the model failed to fit the training examples. It introduced 2 new rule(s): 1 intensional copy, 1 contrary rule. The rule 'p1(X) :- q(X).' generalises by conditioning the target on the background predicate(s) q, so it applies to any constant satisfying them — including unseen ones. The rule 'v(X) :- r(X), w(X).' generalises by conditioning the target on the background predicate(s) r, w, so it applies to any constant satisfying them — including unseen ones. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; p1: model wrote ['p1(X) :- q(X).'], reference has ['p1(X) :- p(X), alpha_0(X).']; v: model wrote ['v(X) :- r(X), w(X).'], reference has ['nothing'].

### t3_noise_0003_anon  (gen@1=0%, gen@k=no)
On 't3_noise_0003_anon', the model failed to fit the training examples. It introduced 2 new rule(s): 1 intensional copy, 1 contrary rule. The rule 'p1(X) :- q(X).' generalises by conditioning the target on the background predicate(s) q, so it applies to any constant satisfying them — including unseen ones. The rule 'v(X) :- r(X).' generalises by conditioning the target on the background predicate(s) r, so it applies to any constant satisfying them — including unseen ones. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; p1: model wrote ['p1(X) :- q(X).'], reference has ['p1(X) :- p(X), alpha_0(X).', 'p1(X) :- u(X).']; v: model wrote ['v(X) :- r(X).'], reference has ['nothing'].

### t3_noise_0004_anon  (gen@1=0%, gen@k=no)
On 't3_noise_0004_anon', the model failed to fit the training examples. It introduced 2 new rule(s): 2 intensional copy. The rule 'p1(X) :- q(X).' generalises by conditioning the target on the background predicate(s) q, so it applies to any constant satisfying them — including unseen ones. The rule 'p1(X) :- r(X).' generalises by conditioning the target on the background predicate(s) r, so it applies to any constant satisfying them — including unseen ones. It also introduced the assumption(s) alpha(X) to make a rule defeasible, capturing exceptions. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; p1: model wrote ['p1(X) :- q(X).', 'p1(X) :- r(X).'], reference has ['p1(X) :- p(X), alpha_0(X).'].

### t3_noise_0005_anon  (gen@1=0%, gen@k=no)
On 't3_noise_0005_anon', the model failed to fit the training examples. It introduced 2 new rule(s): 2 intensional copy. The rule 'p1(X) :- q(X).' generalises by conditioning the target on the background predicate(s) q, so it applies to any constant satisfying them — including unseen ones. The rule 'p1(X) :- r(X).' generalises by conditioning the target on the background predicate(s) r, so it applies to any constant satisfying them — including unseen ones. It also introduced the assumption(s) alpha(c), alpha(e) to make a rule defeasible, capturing exceptions. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; p1: model wrote ['p1(X) :- q(X).', 'p1(X) :- r(X).'], reference has ['p1(X) :- p(X), alpha_0(X).'].

### t3_noise_0006_anon  (gen@1=0%, gen@k=no)
On 't3_noise_0006_anon', the model failed to fit the training examples. It introduced 2 new rule(s): 1 intensional copy, 1 contrary rule. The rule 'p1(X) :- q(X).' generalises by conditioning the target on the background predicate(s) q, so it applies to any constant satisfying them — including unseen ones. The rule 'v(X) :- r(X).' generalises by conditioning the target on the background predicate(s) r, so it applies to any constant satisfying them — including unseen ones. It also introduced the assumption(s) alpha(X) to make a rule defeasible, capturing exceptions. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; p1: model wrote ['p1(X) :- q(X).'], reference has ['p1(X) :- p(X), alpha_0(X).']; v: model wrote ['v(X) :- r(X).'], reference has ['nothing'].

### t3_noise_0007_anon  (gen@1=0%, gen@k=no)
On 't3_noise_0007_anon', the model failed to fit the training examples. It introduced 1 new rule(s): 1 intensional copy. The rule 'p1(X) :- q(X).' generalises by conditioning the target on the background predicate(s) q, so it applies to any constant satisfying them — including unseen ones. It also introduced the assumption(s) alpha(X) to make a rule defeasible, capturing exceptions. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; p1: model wrote ['p1(X) :- q(X).'], reference has ['p1(X) :- p(X), alpha_0(X).', 'p1(X) :- t(X).'].

### t3_noise_0008_anon  (gen@1=0%, gen@k=no)
On 't3_noise_0008_anon', the model failed to fit the training examples. It introduced 2 new rule(s): 1 intensional copy, 1 contrary rule. The rule 'p1(X) :- q(X).' generalises by conditioning the target on the background predicate(s) q, so it applies to any constant satisfying them — including unseen ones. The rule 'v(X) :- r(X).' generalises by conditioning the target on the background predicate(s) r, so it applies to any constant satisfying them — including unseen ones. It differs from the symbolic reference on: p1: model wrote ['p1(X) :- q(X).'], reference has ['p1(X) :- r(X).']; v: model wrote ['v(X) :- r(X).'], reference has ['nothing'].

### t3_noise_0009_anon  (gen@1=0%, gen@k=no)
On 't3_noise_0009_anon', the model failed to fit the training examples. It introduced 1 new rule(s): 1 intensional copy. The rule 'p1(X) :- q(X).' generalises by conditioning the target on the background predicate(s) q, so it applies to any constant satisfying them — including unseen ones. It also introduced the assumption(s) alpha(X) to make a rule defeasible, capturing exceptions. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; p1: model wrote ['p1(X) :- q(X).'], reference has ['p1(X) :- p(X), alpha_0(X).'].

### t3_noise_0010_anon  (gen@1=0%, gen@k=no)
On 't3_noise_0010_anon', the model failed to fit the training examples. It introduced 2 new rule(s): 2 intensional copy. The rule 'p1(X) :- p(X).' generalises by conditioning the target on the background predicate(s) p, so it applies to any constant satisfying them — including unseen ones. The rule 'p1(X) :- q(X).' generalises by conditioning the target on the background predicate(s) q, so it applies to any constant satisfying them — including unseen ones. It also introduced the assumption(s) alpha(X) to make a rule defeasible, capturing exceptions. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; p1: model wrote ['p1(X) :- p(X).', 'p1(X) :- q(X).'], reference has ['p1(X) :- p(X), alpha_0(X).'].

### t3_noise_0011_anon  (gen@1=0%, gen@k=no)
On 't3_noise_0011_anon', the model failed to fit the training examples. It introduced 2 new rule(s): 2 intensional copy. The rule 'p1(X) :- q(X).' generalises by conditioning the target on the background predicate(s) q, so it applies to any constant satisfying them — including unseen ones. The rule 'p1(X) :- r(X).' generalises by conditioning the target on the background predicate(s) r, so it applies to any constant satisfying them — including unseen ones. It also introduced the assumption(s) alpha(e) to make a rule defeasible, capturing exceptions. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; p1: model wrote ['p1(X) :- q(X).', 'p1(X) :- r(X).'], reference has ['p1(X) :- p(X), alpha_0(X).', 'p1(X) :- t(X).'].

### t3_noise_0012_anon  (gen@1=0%, gen@k=no)
On 't3_noise_0012_anon', the model failed to fit the training examples. It introduced 2 new rule(s): 2 intensional copy. The rule 'p1(X) :- q(X).' generalises by conditioning the target on the background predicate(s) q, so it applies to any constant satisfying them — including unseen ones. The rule 'p1(X) :- r(X).' generalises by conditioning the target on the background predicate(s) r, so it applies to any constant satisfying them — including unseen ones. It also introduced the assumption(s) alpha(X) to make a rule defeasible, capturing exceptions. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; p1: model wrote ['p1(X) :- q(X).', 'p1(X) :- r(X).'], reference has ['p1(X) :- p(X), alpha_0(X).'].

### t3_noise_0013_anon  (gen@1=0%, gen@k=no)
On 't3_noise_0013_anon', the model failed to fit the training examples. It introduced 2 new rule(s): 2 intensional copy. The rule 'p1(X) :- p(X).' generalises by conditioning the target on the background predicate(s) p, so it applies to any constant satisfying them — including unseen ones. The rule 'p1(X) :- r(X).' generalises by conditioning the target on the background predicate(s) r, so it applies to any constant satisfying them — including unseen ones. It also introduced the assumption(s) alpha(e), alpha(d) to make a rule defeasible, capturing exceptions. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; p1: model wrote ['p1(X) :- p(X).', 'p1(X) :- r(X).'], reference has ['p1(X) :- p(X), alpha_0(X).'].

### t3_noise_0014_anon  (gen@1=0%, gen@k=no)
On 't3_noise_0014_anon', the model failed to fit the training examples. It introduced 2 new rule(s): 2 intensional copy. The rule 'p1(X) :- q(X).' generalises by conditioning the target on the background predicate(s) q, so it applies to any constant satisfying them — including unseen ones. The rule 'p1(X) :- r(X).' generalises by conditioning the target on the background predicate(s) r, so it applies to any constant satisfying them — including unseen ones. It also introduced the assumption(s) alpha(X) to make a rule defeasible, capturing exceptions. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; p1: model wrote ['p1(X) :- q(X).', 'p1(X) :- r(X).'], reference has ['p1(X) :- p(X), alpha_0(X).', 'p1(X) :- t(X).'].

### t3_noise_0015_anon  (gen@1=0%, gen@k=no)
On 't3_noise_0015_anon', the model failed to fit the training examples. It introduced 2 new rule(s): 1 intensional copy, 1 contrary rule. The rule 'p1(X) :- q(X).' generalises by conditioning the target on the background predicate(s) q, so it applies to any constant satisfying them — including unseen ones. The rule 'v(X) :- r(X).' generalises by conditioning the target on the background predicate(s) r, so it applies to any constant satisfying them — including unseen ones. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; p1: model wrote ['p1(X) :- q(X).'], reference has ['p1(X) :- p(X), alpha_0(X).']; v: model wrote ['v(X) :- r(X).'], reference has ['nothing'].

### t3_noise_0016_anon  (gen@1=0%, gen@k=no)
On 't3_noise_0016_anon', the model failed to fit the training examples. It introduced 1 new rule(s): 1 intensional copy. The rule 'p1(X) :- q(X).' generalises by conditioning the target on the background predicate(s) q, so it applies to any constant satisfying them — including unseen ones. It also introduced the assumption(s) alpha(X) to make a rule defeasible, capturing exceptions. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; p1: model wrote ['p1(X) :- q(X).'], reference has ['p1(X) :- p(X), alpha_0(X).'].

### t3_noise_0017_anon  (gen@1=0%, gen@k=no)
On 't3_noise_0017_anon', the model failed to fit the training examples. It introduced 2 new rule(s): 2 intensional copy. The rule 'p1(X) :- q(X).' generalises by conditioning the target on the background predicate(s) q, so it applies to any constant satisfying them — including unseen ones. The rule 'p1(X) :- r(X).' generalises by conditioning the target on the background predicate(s) r, so it applies to any constant satisfying them — including unseen ones. It also introduced the assumption(s) alpha(g), alpha(a) to make a rule defeasible, capturing exceptions. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; p1: model wrote ['p1(X) :- q(X).', 'p1(X) :- r(X).'], reference has ['p1(X) :- p(X), alpha_0(X).'].

### t3_noise_0018_anon  (gen@1=0%, gen@k=no)
On 't3_noise_0018_anon', the model failed to fit the training examples. It introduced 2 new rule(s): 1 intensional copy, 1 contrary rule. The rule 'p1(X) :- q(X).' generalises by conditioning the target on the background predicate(s) q, so it applies to any constant satisfying them — including unseen ones. The rule 'v(X) :- r(X).' generalises by conditioning the target on the background predicate(s) r, so it applies to any constant satisfying them — including unseen ones. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; p1: model wrote ['p1(X) :- q(X).'], reference has ['p1(X) :- p(X), alpha_0(X).']; v: model wrote ['v(X) :- r(X).'], reference has ['nothing'].

### t3_noise_0019_anon  (gen@1=0%, gen@k=no)
On 't3_noise_0019_anon', the model failed to fit the training examples. It introduced 2 new rule(s): 2 intensional copy. The rule 'p1(X) :- q(X).' generalises by conditioning the target on the background predicate(s) q, so it applies to any constant satisfying them — including unseen ones. The rule 'p1(X) :- r(X).' generalises by conditioning the target on the background predicate(s) r, so it applies to any constant satisfying them — including unseen ones. It also introduced the assumption(s) alpha(d), alpha(c) to make a rule defeasible, capturing exceptions. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; p1: model wrote ['p1(X) :- q(X).', 'p1(X) :- r(X).'], reference has ['p1(X) :- p(X), alpha_0(X).', 'p1(X) :- t(X).'].

### t4_domain_0000_anon  (gen@1=0%, gen@k=no)
On 't4_domain_0000_anon', the model failed to fit the training examples. It introduced 2 new rule(s): 1 intensional copy, 1 contrary rule. The rule 'v(X) :- q(X).' generalises by conditioning the target on the background predicate(s) q, so it applies to any constant satisfying them — including unseen ones. The rule 't(X) :- r(X), u(X).' generalises by conditioning the target on the background predicate(s) r, u, so it applies to any constant satisfying them — including unseen ones. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; t: model wrote ['t(X) :- r(X), u(X).'], reference has ['nothing']; v: model wrote ['v(X) :- q(X).'], reference has ['v(X) :- p(X), alpha_0(X).'].

### t4_domain_0001_anon  (gen@1=0%, gen@k=no)
On 't4_domain_0001_anon', the model failed to fit the training examples. It introduced 2 new rule(s): 1 intensional copy, 1 contrary rule. The rule 'v(X) :- q(X).' generalises by conditioning the target on the background predicate(s) q, so it applies to any constant satisfying them — including unseen ones. The rule 't(X) :- s(X).' generalises by conditioning the target on the background predicate(s) s, so it applies to any constant satisfying them — including unseen ones. It also introduced the assumption(s) alpha(j), alpha(b), alpha(d) to make a rule defeasible, capturing exceptions. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; t: model wrote ['t(X) :- s(X).'], reference has ['nothing']; v: model wrote ['v(X) :- q(X).'], reference has ['v(X) :- p(X), alpha_0(X).'].

### t4_domain_0002_anon  (gen@1=0%, gen@k=no)
On 't4_domain_0002_anon', the model failed to fit the training examples. It introduced 3 new rule(s): 2 intensional copy, 1 contrary rule. The rule 'v(X) :- q(X).' generalises by conditioning the target on the background predicate(s) q, so it applies to any constant satisfying them — including unseen ones. The rule 't(X) :- q(X), u(X).' generalises by conditioning the target on the background predicate(s) q, u, so it applies to any constant satisfying them — including unseen ones. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; c_u: model wrote ['c_u(X) :- r(X).'], reference has ['nothing']; t: model wrote ['t(X) :- q(X), u(X).'], reference has ['nothing'].

### t4_domain_0003_anon  (gen@1=0%, gen@k=no)
On 't4_domain_0003_anon', the model failed to fit the training examples. It introduced 2 new rule(s): 1 intensional copy, 1 contrary rule. The rule 'v(X) :- q(X).' generalises by conditioning the target on the background predicate(s) q, so it applies to any constant satisfying them — including unseen ones. The rule 't(X) :- r(X), u(X).' generalises by conditioning the target on the background predicate(s) r, u, so it applies to any constant satisfying them — including unseen ones. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; t: model wrote ['t(X) :- r(X), u(X).'], reference has ['nothing']; v: model wrote ['v(X) :- q(X).'], reference has ['v(X) :- p(X), alpha_0(X).'].

### t4_domain_0004_anon  (gen@1=0%, gen@k=no)
On 't4_domain_0004_anon', the model failed to fit the training examples. It introduced 2 new rule(s): 2 intensional copy. The rule 'v(X) :- q(X).' generalises by conditioning the target on the background predicate(s) q, so it applies to any constant satisfying them — including unseen ones. The rule 'v(X) :- r(X).' generalises by conditioning the target on the background predicate(s) r, so it applies to any constant satisfying them — including unseen ones. It also introduced the assumption(s) alpha(X) to make a rule defeasible, capturing exceptions. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; v: model wrote ['v(X) :- q(X).', 'v(X) :- r(X).'], reference has ['v(X) :- p(X), alpha_0(X).'].

### t4_domain_0005_anon  (gen@1=0%, gen@k=no)
On 't4_domain_0005_anon', the model failed to fit the training examples. It introduced 2 new rule(s): 1 intensional copy, 1 contrary rule. The rule 'v(X) :- q(X).' generalises by conditioning the target on the background predicate(s) q, so it applies to any constant satisfying them — including unseen ones. The rule 't(X) :- r(X), u(X).' generalises by conditioning the target on the background predicate(s) r, u, so it applies to any constant satisfying them — including unseen ones. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; t: model wrote ['t(X) :- r(X), u(X).'], reference has ['nothing']; v: model wrote ['v(X) :- q(X).'], reference has ['v(X) :- p(X), alpha_0(X).'].

### t4_domain_0006_anon  (gen@1=0%, gen@k=no)
On 't4_domain_0006_anon', the model failed to fit the training examples. It introduced 2 new rule(s): 1 intensional copy, 1 contrary rule. The rule 'v(X) :- q(X).' generalises by conditioning the target on the background predicate(s) q, so it applies to any constant satisfying them — including unseen ones. The rule 't(X) :- q(X), u(X).' generalises by conditioning the target on the background predicate(s) q, u, so it applies to any constant satisfying them — including unseen ones. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; t: model wrote ['t(X) :- q(X), u(X).'], reference has ['nothing']; v: model wrote ['v(X) :- q(X).'], reference has ['v(X) :- p(X), alpha_0(X).'].

### t4_domain_0007_anon  (gen@1=0%, gen@k=no)
On 't4_domain_0007_anon', the model failed to fit the training examples. It introduced 2 new rule(s): 2 intensional copy. The rule 'v(X) :- q(X).' generalises by conditioning the target on the background predicate(s) q, so it applies to any constant satisfying them — including unseen ones. The rule 'v(X) :- r(X).' generalises by conditioning the target on the background predicate(s) r, so it applies to any constant satisfying them — including unseen ones. It also introduced the assumption(s) alpha(b), alpha(c), alpha(d) to make a rule defeasible, capturing exceptions. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; v: model wrote ['v(X) :- q(X).', 'v(X) :- r(X).'], reference has ['v(X) :- p(X), alpha_0(X).'].

### t4_domain_0008_anon  (gen@1=0%, gen@k=no)
On 't4_domain_0008_anon', the model failed to fit the training examples. It introduced 4 new rule(s): 1 intensional copy, 1 contrary rule, 2 ground fact. The rule 'v(X) :- q(X).' generalises by conditioning the target on the background predicate(s) q, so it applies to any constant satisfying them — including unseen ones. The rule 't(X) :- q(X), u(X).' generalises by conditioning the target on the background predicate(s) q, u, so it applies to any constant satisfying them — including unseen ones. It differs from the symbolic reference on: c_alpha: model wrote ['c_alpha(X) :- X = a.', 'c_alpha(X) :- X = h.'], reference has ['nothing']; c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; t: model wrote ['t(X) :- q(X), u(X).'], reference has ['nothing'].

### t4_domain_0009_anon  (gen@1=0%, gen@k=no)
On 't4_domain_0009_anon', the model failed to fit the training examples. It introduced 3 new rule(s): 1 intensional copy, 1 contrary rule, 1 ground fact. The rule 'v(X) :- q(X).' generalises by conditioning the target on the background predicate(s) q, so it applies to any constant satisfying them — including unseen ones. The rule 't(X) :- r(X), u(X).' generalises by conditioning the target on the background predicate(s) r, u, so it applies to any constant satisfying them — including unseen ones. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; c_u: model wrote ['c_u(X) :- X = i.'], reference has ['nothing']; t: model wrote ['t(X) :- r(X), u(X).'], reference has ['nothing'].

### t4_domain_0010_anon  (gen@1=0%, gen@k=no)
On 't4_domain_0010_anon', the model failed to fit the training examples. It introduced 2 new rule(s): 1 intensional copy, 1 contrary rule. The rule 'v(X) :- q(X).' generalises by conditioning the target on the background predicate(s) q, so it applies to any constant satisfying them — including unseen ones. The rule 't(X) :- q(X), u(X).' generalises by conditioning the target on the background predicate(s) q, u, so it applies to any constant satisfying them — including unseen ones. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; t: model wrote ['t(X) :- q(X), u(X).'], reference has ['nothing']; v: model wrote ['v(X) :- q(X).'], reference has ['v(X) :- p(X), alpha_0(X).'].

### t4_domain_0011_anon  (gen@1=0%, gen@k=no)
On 't4_domain_0011_anon', the model failed to fit the training examples. It introduced 2 new rule(s): 1 intensional copy, 1 contrary rule. The rule 'v(X) :- q(X).' generalises by conditioning the target on the background predicate(s) q, so it applies to any constant satisfying them — including unseen ones. The rule 't(X) :- r(X).' generalises by conditioning the target on the background predicate(s) r, so it applies to any constant satisfying them — including unseen ones. It also introduced the assumption(s) alpha(X) to make a rule defeasible, capturing exceptions. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; t: model wrote ['t(X) :- r(X).'], reference has ['nothing']; v: model wrote ['v(X) :- q(X).'], reference has ['v(X) :- p(X), alpha_0(X).'].

### t4_domain_0012_anon  (gen@1=0%, gen@k=no)
On 't4_domain_0012_anon', the model failed to fit the training examples. It introduced 2 new rule(s): 1 intensional copy, 1 contrary rule. The rule 'v(X) :- q(X).' generalises by conditioning the target on the background predicate(s) q, so it applies to any constant satisfying them — including unseen ones. The rule 't(X) :- q(X), u(X).' generalises by conditioning the target on the background predicate(s) q, u, so it applies to any constant satisfying them — including unseen ones. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; t: model wrote ['t(X) :- q(X), u(X).'], reference has ['nothing']; v: model wrote ['v(X) :- q(X).'], reference has ['v(X) :- p(X), alpha_0(X).'].

### t4_domain_0013_anon  (gen@1=0%, gen@k=no)
On 't4_domain_0013_anon', the model failed to fit the training examples. It introduced 2 new rule(s): 1 intensional copy, 1 contrary rule. The rule 'v(X) :- q(X).' generalises by conditioning the target on the background predicate(s) q, so it applies to any constant satisfying them — including unseen ones. The rule 't(X) :- s(X), u(X).' generalises by conditioning the target on the background predicate(s) s, u, so it applies to any constant satisfying them — including unseen ones. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; t: model wrote ['t(X) :- s(X), u(X).'], reference has ['nothing']; v: model wrote ['v(X) :- q(X).'], reference has ['v(X) :- p(X), alpha_0(X).', 'v(X) :- s(X).'].

### t4_domain_0014_anon  (gen@1=0%, gen@k=no)
On 't4_domain_0014_anon', the model failed to fit the training examples. It introduced 2 new rule(s): 1 intensional copy, 1 contrary rule. The rule 'v(X) :- q(X).' generalises by conditioning the target on the background predicate(s) q, so it applies to any constant satisfying them — including unseen ones. The rule 't(X) :- r(X), u(X).' generalises by conditioning the target on the background predicate(s) r, u, so it applies to any constant satisfying them — including unseen ones. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; t: model wrote ['t(X) :- r(X), u(X).'], reference has ['nothing']; v: model wrote ['v(X) :- q(X).'], reference has ['v(X) :- p(X), alpha_0(X).'].

### t4_domain_0015_anon  (gen@1=0%, gen@k=no)
On 't4_domain_0015_anon', the model failed to fit the training examples. It introduced 2 new rule(s): 2 intensional copy. The rule 'v(X) :- q(X).' generalises by conditioning the target on the background predicate(s) q, so it applies to any constant satisfying them — including unseen ones. The rule 'v(X) :- r(X).' generalises by conditioning the target on the background predicate(s) r, so it applies to any constant satisfying them — including unseen ones. It also introduced the assumption(s) alpha(X) to make a rule defeasible, capturing exceptions. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; v: model wrote ['v(X) :- q(X).', 'v(X) :- r(X).'], reference has ['v(X) :- p(X), alpha_0(X).'].

### t4_domain_0016_anon  (gen@1=0%, gen@k=no)
On 't4_domain_0016_anon', the model failed to fit the training examples. It introduced 2 new rule(s): 1 intensional copy, 1 contrary rule. The rule 'v(X) :- q(X).' generalises by conditioning the target on the background predicate(s) q, so it applies to any constant satisfying them — including unseen ones. The rule 't(X) :- r(X), u(X).' generalises by conditioning the target on the background predicate(s) r, u, so it applies to any constant satisfying them — including unseen ones. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; t: model wrote ['t(X) :- r(X), u(X).'], reference has ['nothing']; v: model wrote ['v(X) :- q(X).'], reference has ['v(X) :- p(X), alpha_0(X).'].

### t4_domain_0017_anon  (gen@1=0%, gen@k=no)
On 't4_domain_0017_anon', the model failed to fit the training examples. It introduced 2 new rule(s): 1 intensional copy, 1 contrary rule. The rule 'v(X) :- q(X).' generalises by conditioning the target on the background predicate(s) q, so it applies to any constant satisfying them — including unseen ones. The rule 't(X) :- r(X).' generalises by conditioning the target on the background predicate(s) r, so it applies to any constant satisfying them — including unseen ones. It also introduced the assumption(s) alpha(X) to make a rule defeasible, capturing exceptions. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; t: model wrote ['t(X) :- r(X).'], reference has ['nothing']; v: model wrote ['v(X) :- q(X).'], reference has ['v(X) :- p(X), alpha_0(X).'].

### t4_domain_0018_anon  (gen@1=0%, gen@k=no)
On 't4_domain_0018_anon', the model failed to fit the training examples. It introduced 2 new rule(s): 1 intensional copy, 1 contrary rule. The rule 'v(X) :- q(X).' generalises by conditioning the target on the background predicate(s) q, so it applies to any constant satisfying them — including unseen ones. The rule 't(X) :- r(X).' generalises by conditioning the target on the background predicate(s) r, so it applies to any constant satisfying them — including unseen ones. It also introduced the assumption(s) alpha(b), alpha(c), alpha(e) to make a rule defeasible, capturing exceptions. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; t: model wrote ['t(X) :- r(X).'], reference has ['nothing']; v: model wrote ['v(X) :- q(X).'], reference has ['v(X) :- p(X), alpha_0(X).'].

### t4_domain_0019_anon  (gen@1=0%, gen@k=no)
On 't4_domain_0019_anon', the model failed to fit the training examples. It introduced 2 new rule(s): 1 intensional copy, 1 contrary rule. The rule 'v(X) :- q(X).' generalises by conditioning the target on the background predicate(s) q, so it applies to any constant satisfying them — including unseen ones. The rule 't(X) :- u(X).' generalises by conditioning the target on the background predicate(s) u, so it applies to any constant satisfying them — including unseen ones. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; t: model wrote ['t(X) :- u(X).'], reference has ['nothing']; v: model wrote ['v(X) :- q(X).'], reference has ['v(X) :- p(X), alpha_0(X).'].

### t5_twopath_0000_anon  (gen@1=0%, gen@k=no)
On 't5_twopath_0000_anon', the model failed to fit the training examples. It introduced 2 new rule(s): 2 intensional copy. The rule 'p1(X) :- p(X).' generalises by conditioning the target on the background predicate(s) p, so it applies to any constant satisfying them — including unseen ones. The rule 'p1(X) :- q(X).' generalises by conditioning the target on the background predicate(s) q, so it applies to any constant satisfying them — including unseen ones. It also introduced the assumption(s) alpha(b), alpha(d) to make a rule defeasible, capturing exceptions. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- s(X).']; c_alpha_1: model wrote ['nothing'], reference has ['c_alpha_1(X) :- r(X).']; p1: model wrote ['p1(X) :- p(X).', 'p1(X) :- q(X).'], reference has ['p1(X) :- p(X), alpha_1(X).', 'p1(X) :- q(X), alpha_0(X).'].

### t5_twopath_0001_anon  (gen@1=0%, gen@k=no)
On 't5_twopath_0001_anon', the model failed to fit the training examples. It introduced 1 new rule(s): 1 intensional copy. The rule 'p1(X) :- p(X).' generalises by conditioning the target on the background predicate(s) p, so it applies to any constant satisfying them — including unseen ones. It also introduced the assumption(s) alpha(X) to make a rule defeasible, capturing exceptions. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- s(X).']; c_alpha_1: model wrote ['nothing'], reference has ['c_alpha_1(X) :- r(X).']; p1: model wrote ['p1(X) :- p(X).'], reference has ['p1(X) :- p(X), alpha_1(X).', 'p1(X) :- q(X), alpha_0(X).'].

### t5_twopath_0002_anon  (gen@1=0%, gen@k=no)
On 't5_twopath_0002_anon', the model failed to fit the training examples. It introduced 1 new rule(s): 1 intensional copy. The rule 'p1(X) :- p(X).' generalises by conditioning the target on the background predicate(s) p, so it applies to any constant satisfying them — including unseen ones. It also introduced the assumption(s) alpha(b), alpha(d), alpha(f) to make a rule defeasible, capturing exceptions. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- r(X).']; c_alpha_1: model wrote ['nothing'], reference has ['c_alpha_1(X) :- s(X).']; p1: model wrote ['p1(X) :- p(X).'], reference has ['p1(X) :- p(X), alpha_0(X).', 'p1(X) :- q(X), alpha_1(X).'].

### t5_twopath_0003_anon  (gen@1=0%, gen@k=no)
On 't5_twopath_0003_anon', the model failed to fit the training examples. It introduced 1 new rule(s): 1 intensional copy. The rule 'p1(X) :- p(X).' generalises by conditioning the target on the background predicate(s) p, so it applies to any constant satisfying them — including unseen ones. It also introduced the assumption(s) alpha(d), alpha(b), alpha(f) to make a rule defeasible, capturing exceptions. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- r(X).']; c_alpha_1: model wrote ['nothing'], reference has ['c_alpha_1(X) :- s(X).']; p1: model wrote ['p1(X) :- p(X).'], reference has ['p1(X) :- p(X), alpha_0(X).', 'p1(X) :- q(X), alpha_1(X).'].

### t5_twopath_0004_anon  (gen@1=0%, gen@k=no)
On 't5_twopath_0004_anon', the model failed to fit the training examples. It introduced 1 new rule(s): 1 intensional copy. The rule 'p1(X) :- p(X).' generalises by conditioning the target on the background predicate(s) p, so it applies to any constant satisfying them — including unseen ones. It also introduced the assumption(s) alpha(X) to make a rule defeasible, capturing exceptions. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- r(X).']; c_alpha_1: model wrote ['nothing'], reference has ['c_alpha_1(X) :- s(X).']; p1: model wrote ['p1(X) :- p(X).'], reference has ['p1(X) :- p(X), alpha_0(X).', 'p1(X) :- q(X), alpha_1(X).'].

### t5_twopath_0005_anon  (gen@1=0%, gen@k=no)
On 't5_twopath_0005_anon', the model failed to fit the training examples. It introduced 2 new rule(s): 1 intensional copy, 1 ground fact. The rule 'p1(X) :- p(X).' generalises by conditioning the target on the background predicate(s) p, so it applies to any constant satisfying them — including unseen ones. It also introduced the assumption(s) alpha(X) to make a rule defeasible, capturing exceptions. It differs from the symbolic reference on: c_alpha: model wrote ['c_alpha(X) :- X = e.'], reference has ['nothing']; c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- r(X).']; c_alpha_1: model wrote ['nothing'], reference has ['c_alpha_1(X) :- s(X).'].

### t5_twopath_0006_anon  (gen@1=0%, gen@k=no)
On 't5_twopath_0006_anon', the model failed to fit the training examples. It introduced 1 new rule(s): 1 intensional copy. The rule 'p1(X) :- p(X).' generalises by conditioning the target on the background predicate(s) p, so it applies to any constant satisfying them — including unseen ones. It also introduced the assumption(s) alpha(f), alpha(d), alpha(c) to make a rule defeasible, capturing exceptions. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- s(X).']; c_alpha_1: model wrote ['nothing'], reference has ['c_alpha_1(X) :- r(X).']; p1: model wrote ['p1(X) :- p(X).'], reference has ['p1(X) :- p(X), alpha_1(X).', 'p1(X) :- q(X), alpha_0(X).'].

### t5_twopath_0007_anon  (gen@1=0%, gen@k=no)
On 't5_twopath_0007_anon', the model failed to fit the training examples. It introduced 1 new rule(s): 1 intensional copy. The rule 'p1(X) :- p(X).' generalises by conditioning the target on the background predicate(s) p, so it applies to any constant satisfying them — including unseen ones. It also introduced the assumption(s) alpha(X) to make a rule defeasible, capturing exceptions. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- r(X).']; c_alpha_1: model wrote ['nothing'], reference has ['c_alpha_1(X) :- s(X).']; p1: model wrote ['p1(X) :- p(X).'], reference has ['p1(X) :- p(X), alpha_0(X).', 'p1(X) :- q(X), alpha_1(X).'].

### t5_twopath_0008_anon  (gen@1=0%, gen@k=no)
On 't5_twopath_0008_anon', the model failed to fit the training examples. It introduced 2 new rule(s): 2 intensional copy. The rule 'p1(X) :- p(X).' generalises by conditioning the target on the background predicate(s) p, so it applies to any constant satisfying them — including unseen ones. The rule 'p1(X) :- q(X).' generalises by conditioning the target on the background predicate(s) q, so it applies to any constant satisfying them — including unseen ones. It also introduced the assumption(s) alpha(d), alpha(f) to make a rule defeasible, capturing exceptions. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- r(X).']; c_alpha_1: model wrote ['nothing'], reference has ['c_alpha_1(X) :- s(X).']; p1: model wrote ['p1(X) :- p(X).', 'p1(X) :- q(X).'], reference has ['p1(X) :- p(X), alpha_0(X).', 'p1(X) :- q(X), alpha_1(X).'].

### t5_twopath_0009_anon  (gen@1=0%, gen@k=no)
On 't5_twopath_0009_anon', the model failed to fit the training examples. It introduced 1 new rule(s): 1 intensional copy. The rule 'p1(X) :- p(X).' generalises by conditioning the target on the background predicate(s) p, so it applies to any constant satisfying them — including unseen ones. It also introduced the assumption(s) alpha(X) to make a rule defeasible, capturing exceptions. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- r(X).']; c_alpha_1: model wrote ['nothing'], reference has ['c_alpha_1(X) :- s(X).']; p1: model wrote ['p1(X) :- p(X).'], reference has ['p1(X) :- p(X), alpha_0(X).', 'p1(X) :- q(X), alpha_1(X).'].

### t5_twopath_0010_anon  (gen@1=0%, gen@k=no)
On 't5_twopath_0010_anon', the model failed to fit the training examples. It introduced 2 new rule(s): 2 intensional copy. The rule 'p1(X) :- p(X).' generalises by conditioning the target on the background predicate(s) p, so it applies to any constant satisfying them — including unseen ones. The rule 'p1(X) :- q(X).' generalises by conditioning the target on the background predicate(s) q, so it applies to any constant satisfying them — including unseen ones. It also introduced the assumption(s) alpha(b), alpha(d), alpha(f) to make a rule defeasible, capturing exceptions. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- r(X).']; c_alpha_1: model wrote ['nothing'], reference has ['c_alpha_1(X) :- s(X).']; p1: model wrote ['p1(X) :- p(X).', 'p1(X) :- q(X).'], reference has ['p1(X) :- p(X), alpha_0(X).', 'p1(X) :- q(X), alpha_1(X).'].

### t5_twopath_0011_anon  (gen@1=0%, gen@k=no)
On 't5_twopath_0011_anon', the model failed to fit the training examples. It introduced 2 new rule(s): 2 intensional copy. The rule 'p1(X) :- p(X).' generalises by conditioning the target on the background predicate(s) p, so it applies to any constant satisfying them — including unseen ones. The rule 'p1(X) :- q(X).' generalises by conditioning the target on the background predicate(s) q, so it applies to any constant satisfying them — including unseen ones. It also introduced the assumption(s) alpha(b), alpha(d), alpha(f) to make a rule defeasible, capturing exceptions. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- r(X).']; c_alpha_1: model wrote ['nothing'], reference has ['c_alpha_1(X) :- s(X).']; p1: model wrote ['p1(X) :- p(X).', 'p1(X) :- q(X).'], reference has ['p1(X) :- p(X), alpha_0(X).', 'p1(X) :- q(X), alpha_1(X).'].

### t5_twopath_0012_anon  (gen@1=0%, gen@k=no)
On 't5_twopath_0012_anon', the model failed to fit the training examples. It introduced 1 new rule(s): 1 intensional copy. The rule 'p1(X) :- p(X).' generalises by conditioning the target on the background predicate(s) p, so it applies to any constant satisfying them — including unseen ones. It also introduced the assumption(s) alpha(c), alpha(f), alpha(b) to make a rule defeasible, capturing exceptions. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- r(X).']; c_alpha_1: model wrote ['nothing'], reference has ['c_alpha_1(X) :- s(X).']; p1: model wrote ['p1(X) :- p(X).'], reference has ['p1(X) :- p(X), alpha_0(X).', 'p1(X) :- q(X), alpha_1(X).'].

### t5_twopath_0013_anon  (gen@1=0%, gen@k=no)
On 't5_twopath_0013_anon', the model failed to fit the training examples. It introduced 1 new rule(s): 1 intensional copy. The rule 'p1(X) :- p(X).' generalises by conditioning the target on the background predicate(s) p, so it applies to any constant satisfying them — including unseen ones. It also introduced the assumption(s) alpha(e), alpha(g) to make a rule defeasible, capturing exceptions. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- r(X).']; c_alpha_1: model wrote ['nothing'], reference has ['c_alpha_1(X) :- s(X).']; p1: model wrote ['p1(X) :- p(X).'], reference has ['p1(X) :- p(X), alpha_0(X).', 'p1(X) :- q(X), alpha_1(X).'].

### t5_twopath_0014_anon  (gen@1=0%, gen@k=no)
On 't5_twopath_0014_anon', the model failed to fit the training examples. It introduced 2 new rule(s): 2 intensional copy. The rule 'p1(X) :- p(X).' generalises by conditioning the target on the background predicate(s) p, so it applies to any constant satisfying them — including unseen ones. The rule 'p1(X) :- q(X).' generalises by conditioning the target on the background predicate(s) q, so it applies to any constant satisfying them — including unseen ones. It also introduced the assumption(s) alpha(c), alpha(b) to make a rule defeasible, capturing exceptions. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- r(X).']; c_alpha_1: model wrote ['nothing'], reference has ['c_alpha_1(X) :- s(X).']; p1: model wrote ['p1(X) :- p(X).', 'p1(X) :- q(X).'], reference has ['p1(X) :- p(X), alpha_0(X).', 'p1(X) :- q(X), alpha_1(X).'].

### t5_twopath_0015_anon  (gen@1=0%, gen@k=no)
On 't5_twopath_0015_anon', the model failed to fit the training examples. It introduced 1 new rule(s): 1 intensional copy. The rule 'p1(X) :- p(X).' generalises by conditioning the target on the background predicate(s) p, so it applies to any constant satisfying them — including unseen ones. It also introduced the assumption(s) alpha(X) to make a rule defeasible, capturing exceptions. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- r(X).']; c_alpha_1: model wrote ['nothing'], reference has ['c_alpha_1(X) :- s(X).']; p1: model wrote ['p1(X) :- p(X).'], reference has ['p1(X) :- p(X), alpha_0(X).', 'p1(X) :- q(X), alpha_1(X).'].

### t5_twopath_0016_anon  (gen@1=0%, gen@k=no)
On 't5_twopath_0016_anon', the model failed to fit the training examples. It introduced 1 new rule(s): 1 intensional copy. The rule 'p1(X) :- p(X).' generalises by conditioning the target on the background predicate(s) p, so it applies to any constant satisfying them — including unseen ones. It also introduced the assumption(s) alpha(X) to make a rule defeasible, capturing exceptions. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- s(X).']; c_alpha_1: model wrote ['nothing'], reference has ['c_alpha_1(X) :- r(X).']; p1: model wrote ['p1(X) :- p(X).'], reference has ['p1(X) :- p(X), alpha_1(X).', 'p1(X) :- q(X), alpha_0(X).'].

### t5_twopath_0017_anon  (gen@1=0%, gen@k=no)
On 't5_twopath_0017_anon', the model failed to fit the training examples. It introduced 1 new rule(s): 1 intensional copy. The rule 'p1(X) :- p(X).' generalises by conditioning the target on the background predicate(s) p, so it applies to any constant satisfying them — including unseen ones. It also introduced the assumption(s) alpha(f), alpha(b), alpha(d) to make a rule defeasible, capturing exceptions. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- s(X).']; c_alpha_1: model wrote ['nothing'], reference has ['c_alpha_1(X) :- r(X).']; p1: model wrote ['p1(X) :- p(X).'], reference has ['p1(X) :- p(X), alpha_1(X).', 'p1(X) :- q(X), alpha_0(X).'].

### t5_twopath_0018_anon  (gen@1=0%, gen@k=no)
On 't5_twopath_0018_anon', the model failed to fit the training examples. It introduced 2 new rule(s): 2 intensional copy. The rule 'p1(X) :- p(X).' generalises by conditioning the target on the background predicate(s) p, so it applies to any constant satisfying them — including unseen ones. The rule 'p1(X) :- q(X).' generalises by conditioning the target on the background predicate(s) q, so it applies to any constant satisfying them — including unseen ones. It also introduced the assumption(s) alpha(c), alpha(d) to make a rule defeasible, capturing exceptions. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- r(X).']; c_alpha_1: model wrote ['nothing'], reference has ['c_alpha_1(X) :- s(X).']; p1: model wrote ['p1(X) :- p(X).', 'p1(X) :- q(X).'], reference has ['p1(X) :- p(X), alpha_0(X).', 'p1(X) :- q(X), alpha_1(X).'].

### t5_twopath_0019_anon  (gen@1=0%, gen@k=no)
On 't5_twopath_0019_anon', the model failed to fit the training examples. It introduced 1 new rule(s): 1 intensional copy. The rule 'p1(X) :- p(X).' generalises by conditioning the target on the background predicate(s) p, so it applies to any constant satisfying them — including unseen ones. It also introduced the assumption(s) alpha(c), alpha(b), alpha(d) to make a rule defeasible, capturing exceptions. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- r(X).']; c_alpha_1: model wrote ['nothing'], reference has ['c_alpha_1(X) :- s(X).']; p1: model wrote ['p1(X) :- p(X).'], reference has ['p1(X) :- p(X), alpha_0(X).', 'p1(X) :- q(X), alpha_1(X).'].


## Mode: algorithm

### nixon_diamond_anon  (gen@1=0%, gen@k=no)
On 'nixon_diamond_anon', the model failed to fit the training examples. It introduced 2 new rule(s): 1 assumption guarded, 1 contrary rule. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- p(X), w(X).']; p1: model wrote ['p1(X) :- t(X).'], reference has ['p1(X) :- p(X), alpha_0(X).']; v: model wrote ['v(X) :- s(X), u(X).'], reference has ['v(X) :- q(X).'].

### flies_anon  (gen@1=0%, gen@k=no)
On 'flies_anon', the model failed to fit the training examples. It introduced 1 new rule(s): 1 intensional copy. The rule 't(X) :- p(X).' generalises by conditioning the target on the background predicate(s) p, so it applies to any constant satisfying them — including unseen ones. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; t: model wrote ['t(X) :- p(X).'], reference has ['t(X) :- p(X), alpha_0(X).'].

### tax_law_anon  (gen@1=0%, gen@k=no)
On 'tax_law_anon', the candidate is NOT a legal solution: flatness violated: assumption 's' used as rule head. The outcome below is reported for diagnosis only. On 'tax_law_anon', the model failed to fit the training examples. It introduced 2 new rule(s): 1 intensional copy, 1 ground fact. The rule 'u(X) :- r(X).' generalises by conditioning the target on the background predicate(s) r, so it applies to any constant satisfying them — including unseen ones. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- p(X), alpha_1(X).']; c_alpha_1: model wrote ['nothing'], reference has ['c_alpha_1(X) :- p(X), alpha_0(X).']; s: model wrote ['s(b) defeated_by t(b).'], reference has ['nothing'].

### t1_mono_0000_anon  (gen@1=0%, gen@k=no)
On 't1_mono_0000_anon', the model fits the training examples but only classifies 50% of held-out examples correctly — partial generalisation. It introduced 3 new rule(s): 2 mixed, 1 assumption guarded. It differs from the symbolic reference on: v: model wrote ['v(X) :- s(X), u(X).', 'v(a) :- p(a).', 'v(d) :- p(d).'], reference has ['v(X) :- p(X).'].

### t1_mono_0001_anon  (gen@1=0%, gen@k=no)
On 't1_mono_0001_anon', the model failed to fit the training examples. It introduced 1 new rule(s): 1 contrary rule. It also introduced the assumption(s) u(f) to make a rule defeasible, capturing exceptions. It differs from the symbolic reference on: r: model wrote ['r(X) :- s(X).'], reference has ['nothing']; u: model wrote ['nothing'], reference has ['u(X) :- p(X).'].

### t1_mono_0002_anon  (gen@1=0%, gen@k=no)
On 't1_mono_0002_anon', the model failed to fit the training examples. It differs from the symbolic reference on: v: model wrote ['nothing'], reference has ['v(X) :- p(X).'].

### t1_mono_0003_anon  (gen@1=0%, gen@k=no)
On 't1_mono_0003_anon', the model failed to fit the training examples. It introduced 2 new rule(s): 2 mixed. These are all ground facts — the model MEMORISED the training positives rather than learning a general rule, which is why it fails on held-out examples. It also introduced the assumption(s) u(b), u(c) to make a rule defeasible, capturing exceptions. It differs from the symbolic reference on: v: model wrote ['v(b) :- v(b), u(b).', 'v(c) :- v(c), u(c).'], reference has ['v(X) :- p(X).'].

### t1_mono_0004_anon  (gen@1=0%, gen@k=no)
On 't1_mono_0004_anon', the model failed to fit the training examples. It introduced 1 new rule(s): 1 intensional copy. The rule 'v(X) :- s(X).' generalises by conditioning the target on the background predicate(s) s, so it applies to any constant satisfying them — including unseen ones. It differs from the symbolic reference on: v: model wrote ['v(X) :- s(X).'], reference has ['v(X) :- p(X).'].

### t1_mono_0005_anon  (gen@1=0%, gen@k=no)
On 't1_mono_0005_anon', the model failed to fit the training examples. It introduced 4 new rule(s): 2 assumption guarded, 2 mixed. These are all ground facts — the model MEMORISED the training positives rather than learning a general rule, which is why it fails on held-out examples. It differs from the symbolic reference on: v: model wrote ['v(X) :- v(a), s(X).', 'v(X) :- v(a), u(X).', 'v(X) :- v(b), s(X).', 'v(X) :- v(b), u(X).'], reference has ['v(X) :- p(X).'].

### t1_mono_0006_anon  (gen@1=0%, gen@k=no)
On 't1_mono_0006_anon', the candidate is NOT a legal solution: condition (ii) violated: head 'p' is a background predicate not in the learnable set. The outcome below is reported for diagnosis only. On 't1_mono_0006_anon', the model failed to fit the training examples. It introduced 1 new rule(s): 1 intensional copy. The rule 'p(X) :- v(X).' generalises by conditioning the target on the background predicate(s) v, so it applies to any constant satisfying them — including unseen ones. It differs from the symbolic reference on: p: model wrote ['p(X) :- v(X).'], reference has ['nothing']; v: model wrote ['nothing'], reference has ['v(X) :- p(X).'].

### t1_mono_0007_anon  (gen@1=0%, gen@k=no)
On 't1_mono_0007_anon', the candidate is NOT a legal solution: condition (ii) violated: head 'r' is a background predicate not in the learnable set. The outcome below is reported for diagnosis only. On 't1_mono_0007_anon', the model failed to fit the training examples. It introduced 1 new rule(s): 1 mixed. These are all ground facts — the model MEMORISED the training positives rather than learning a general rule, which is why it fails on held-out examples. It also introduced the assumption(s) u(e) to make a rule defeasible, capturing exceptions. It differs from the symbolic reference on: r: model wrote ['r(e) :- t(e).'], reference has ['nothing']; v: model wrote ['nothing'], reference has ['v(X) :- p(X).'].

### t1_mono_0008_anon  (gen@1=0%, gen@k=no)
On 't1_mono_0008_anon', the model fits the training examples but only classifies 50% of held-out examples correctly — partial generalisation. It introduced 3 new rule(s): 2 mixed, 1 contrary rule. It also introduced the assumption(s) u(b), u(a) to make a rule defeasible, capturing exceptions. It differs from the symbolic reference on: r: model wrote ['r(X) :- s(X).', 'r(a) :- u(a).', 'r(b) :- u(b).'], reference has ['nothing']; u: model wrote ['nothing'], reference has ['u(X) :- p(X).'].

### t1_mono_0009_anon  (gen@1=33%, gen@k=yes)
On 't1_mono_0009_anon', the model produced a framework that fits the training examples and solves the full problem in one stable extension. It introduced 4 new rule(s): 4 mixed. These are all ground facts — the model MEMORISED the training positives rather than learning a general rule, which is why it fails on held-out examples. It also introduced the assumption(s) u(a), u(d), u(f) to make a rule defeasible, capturing exceptions. It differs from the symbolic reference on: v: model wrote ['v(a) :- r(a).', 'v(c) :- r(c).', 'v(d) :- r(d).', 'v(f) :- r(f).'], reference has ['v(X) :- p(X).'].

### t1_mono_0010_anon  (gen@1=0%, gen@k=no)
On 't1_mono_0010_anon', the candidate is NOT a legal solution: reserved or malformed head: 'The framework is now a solution as v(e) from E- is attacked by the new rule v(X)'. The outcome below is reported for diagnosis only. On 't1_mono_0010_anon', the model failed to fit the training examples. It introduced 3 new rule(s): 1 intensional copy, 1 ground fact, 1 mixed. The rule 'v(X) :- s(X), alpha1(X).' generalises by conditioning the target on the background predicate(s) s, alpha1, so it applies to any constant satisfying them — including unseen ones. It differs from the symbolic reference on: The framework is now a solution as v(e) from E- is attacked by the new rule v(X): model wrote ['The framework is now a solution as v(e) from E- is attacked by the new rule v(X) :- s(X), alpha1(X).'], reference has ['nothing']; c_alpha1: model wrote ['c_alpha1(X) :- X = e.'], reference has ['nothing']; v: model wrote ['v(X) :- s(X), alpha1(X).'], reference has ['v(X) :- p(X).'].

### t1_mono_0011_anon  (gen@1=0%, gen@k=no)
On 't1_mono_0011_anon', the model failed to fit the training examples. It introduced 2 new rule(s): 2 mixed. These are all ground facts — the model MEMORISED the training positives rather than learning a general rule, which is why it fails on held-out examples. It differs from the symbolic reference on: s: model wrote ['s(b) :- t(b).', 's(d) :- t(d).'], reference has ['nothing']; v: model wrote ['nothing'], reference has ['v(X) :- p(X).'].

### t1_mono_0012_anon  (gen@1=0%, gen@k=no)
On 't1_mono_0012_anon', the model failed to fit the training examples. It introduced 2 new rule(s): 2 mixed. These are all ground facts — the model MEMORISED the training positives rather than learning a general rule, which is why it fails on held-out examples. It differs from the symbolic reference on: v: model wrote ['v(X) :- v(a), s(X).', 'v(X) :- v(d), s(X).'], reference has ['v(X) :- p(X).'].

### t1_mono_0013_anon  (gen@1=0%, gen@k=no)
On 't1_mono_0013_anon', the model failed to fit the training examples. It differs from the symbolic reference on: v: model wrote ['nothing'], reference has ['v(X) :- p(X).'].

### t1_mono_0014_anon  (gen@1=0%, gen@k=no)
On 't1_mono_0014_anon', the model failed to fit the training examples. It differs from the symbolic reference on: v: model wrote ['nothing'], reference has ['v(X) :- p(X).'].

### t1_mono_0015_anon  (gen@1=0%, gen@k=no)
On 't1_mono_0015_anon', the model failed to fit the training examples. It introduced 1 new rule(s): 1 intensional copy. The rule 'v(X) :- s(X).' generalises by conditioning the target on the background predicate(s) s, so it applies to any constant satisfying them — including unseen ones. It differs from the symbolic reference on: v: model wrote ['v(X) :- s(X).'], reference has ['v(X) :- p(X).'].

### t1_mono_0016_anon  (gen@1=0%, gen@k=no)
On 't1_mono_0016_anon', the model failed to fit the training examples. It differs from the symbolic reference on: v: model wrote ['nothing'], reference has ['v(X) :- p(X).'].

### t1_mono_0017_anon  (gen@1=0%, gen@k=no)
On 't1_mono_0017_anon', the model failed to fit the training examples. It introduced 2 new rule(s): 2 mixed. These are all ground facts — the model MEMORISED the training positives rather than learning a general rule, which is why it fails on held-out examples. It differs from the symbolic reference on: v: model wrote ['v(X) :- v(b), s(X).', 'v(X) :- v(d), s(X).'], reference has ['v(X) :- p(X).'].

### t1_mono_0018_anon  (gen@1=0%, gen@k=no)
On 't1_mono_0018_anon', the candidate is NOT a legal solution: condition (ii) violated: head 'r' is a background predicate not in the learnable set. The outcome below is reported for diagnosis only. On 't1_mono_0018_anon', the model failed to fit the training examples. It introduced 1 new rule(s): 1 assumption guarded. It differs from the symbolic reference on: r: model wrote ['r(X) :- u(X).'], reference has ['nothing']; v: model wrote ['nothing'], reference has ['v(X) :- p(X).'].

### t1_mono_0019_anon  (gen@1=0%, gen@k=no)
On 't1_mono_0019_anon', the candidate is NOT a legal solution: condition (ii) violated: head 'r' is a background predicate not in the learnable set. The outcome below is reported for diagnosis only. On 't1_mono_0019_anon', the model failed to fit the training examples. It introduced 2 new rule(s): 2 assumption guarded. It differs from the symbolic reference on: r: model wrote ['r(X) :- r(X), u(X).'], reference has ['nothing']; v: model wrote ['v(X) :- r(X), u(X).'], reference has ['v(X) :- p(X).'].

### t2_defeas_0000_anon  (gen@1=0%, gen@k=no)
On 't2_defeas_0000_anon', the model failed to fit the training examples. It introduced 1 new rule(s): 1 contrary rule. It also introduced the assumption(s) u(a), u(c) to make a rule defeasible, capturing exceptions. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; t: model wrote ['t(X) :- v(X).'], reference has ['nothing']; v: model wrote ['nothing'], reference has ['v(X) :- p(X), alpha_0(X).'].

### t2_defeas_0001_anon  (gen@1=0%, gen@k=no)
On 't2_defeas_0001_anon', the model failed to fit the training examples. It introduced 2 new rule(s): 1 intensional copy, 1 contrary rule. The rule 'v(X) :- t(X).' generalises by conditioning the target on the background predicate(s) t, so it applies to any constant satisfying them — including unseen ones. The rule 't(X) :- q(X).' generalises by conditioning the target on the background predicate(s) q, so it applies to any constant satisfying them — including unseen ones. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; t: model wrote ['t(X) :- q(X).'], reference has ['nothing']; v: model wrote ['v(X) :- t(X).'], reference has ['v(X) :- p(X), alpha_0(X).'].

### t2_defeas_0002_anon  (gen@1=0%, gen@k=no)
On 't2_defeas_0002_anon', the model failed to fit the training examples. It introduced 2 new rule(s): 1 intensional copy, 1 contrary rule. The rule 'v(X) :- t(X).' generalises by conditioning the target on the background predicate(s) t, so it applies to any constant satisfying them — including unseen ones. The rule 't(X) :- q(X).' generalises by conditioning the target on the background predicate(s) q, so it applies to any constant satisfying them — including unseen ones. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; t: model wrote ['t(X) :- q(X).'], reference has ['nothing']; v: model wrote ['v(X) :- t(X).'], reference has ['v(X) :- p(X), alpha_0(X).'].

### t2_defeas_0003_anon  (gen@1=0%, gen@k=no)
On 't2_defeas_0003_anon', the model failed to fit the training examples. It introduced 1 new rule(s): 1 contrary rule. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; t: model wrote ['t(X) :- v(X).'], reference has ['nothing']; v: model wrote ['nothing'], reference has ['v(X) :- p(X), alpha_0(X).'].

### t2_defeas_0004_anon  (gen@1=0%, gen@k=no)
On 't2_defeas_0004_anon', the model failed to fit the training examples. It introduced 2 new rule(s): 1 intensional copy, 1 contrary rule. The rule 'v(X) :- t(X).' generalises by conditioning the target on the background predicate(s) t, so it applies to any constant satisfying them — including unseen ones. The rule 't(X) :- u(X).' generalises by conditioning the target on the background predicate(s) u, so it applies to any constant satisfying them — including unseen ones. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; t: model wrote ['t(X) :- u(X).'], reference has ['nothing']; v: model wrote ['v(X) :- t(X).'], reference has ['v(X) :- p(X), alpha_0(X).'].

### t2_defeas_0005_anon  (gen@1=0%, gen@k=no)
On 't2_defeas_0005_anon', the model failed to fit the training examples. It introduced 1 new rule(s): 1 contrary rule. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; t: model wrote ['t(X) :- v(X).'], reference has ['nothing']; v: model wrote ['nothing'], reference has ['v(X) :- p(X), alpha_0(X).'].

### t2_defeas_0006_anon  (gen@1=0%, gen@k=no)
On 't2_defeas_0006_anon', the model failed to fit the training examples. It introduced 1 new rule(s): 1 contrary rule. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; t: model wrote ['t(X) :- v(X), u(X).'], reference has ['nothing']; v: model wrote ['nothing'], reference has ['v(X) :- p(X), alpha_0(X).', 'v(X) :- r(X).'].

### t2_defeas_0007_anon  (gen@1=0%, gen@k=no)
On 't2_defeas_0007_anon', the model failed to fit the training examples. It introduced 2 new rule(s): 1 intensional copy, 1 ground fact. The rule 'v(X) :- r(X), alpha(X).' generalises by conditioning the target on the background predicate(s) r, alpha, so it applies to any constant satisfying them — including unseen ones. It also introduced the assumption(s) alpha(X) to make a rule defeasible, capturing exceptions. It differs from the symbolic reference on: c_alpha: model wrote ['c_alpha(X) :- X = f.'], reference has ['nothing']; c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; v: model wrote ['v(X) :- r(X), alpha(X).'], reference has ['v(X) :- p(X), alpha_0(X).'].

### t2_defeas_0008_anon  (gen@1=0%, gen@k=no)
On 't2_defeas_0008_anon', the model failed to fit the training examples. It introduced 1 new rule(s): 1 intensional copy. The rule 'v(X) :- t(X).' generalises by conditioning the target on the background predicate(s) t, so it applies to any constant satisfying them — including unseen ones. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; v: model wrote ['v(X) :- t(X).'], reference has ['v(X) :- p(X), alpha_0(X).'].

### t2_defeas_0009_anon  (gen@1=0%, gen@k=no)
On 't2_defeas_0009_anon', the model failed to fit the training examples. It introduced 1 new rule(s): 1 intensional copy. The rule 'v(X) :- q(X).' generalises by conditioning the target on the background predicate(s) q, so it applies to any constant satisfying them — including unseen ones. It also introduced the assumption(s) u(d), u(f) to make a rule defeasible, capturing exceptions. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; v: model wrote ['v(X) :- q(X).'], reference has ['v(X) :- p(X), alpha_0(X).'].

### t2_defeas_0010_anon  (gen@1=0%, gen@k=no)
On 't2_defeas_0010_anon', the model failed to fit the training examples. It introduced 4 new rule(s): 3 mixed, 1 assumption guarded. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; t: model wrote ['t(a) :- r(a).', 't(c) :- r(c).', 't(d) :- r(d).'], reference has ['nothing']; v: model wrote ['v(X) :- t(X), u(X).'], reference has ['v(X) :- p(X), alpha_0(X).'].

### t2_defeas_0011_anon  (gen@1=0%, gen@k=no)
On 't2_defeas_0011_anon', the model failed to fit the training examples. It introduced 2 new rule(s): 2 intensional copy. The rule 'v(X) :- q(X).' generalises by conditioning the target on the background predicate(s) q, so it applies to any constant satisfying them — including unseen ones. The rule 'v(X) :- s(X).' generalises by conditioning the target on the background predicate(s) s, so it applies to any constant satisfying them — including unseen ones. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; v: model wrote ['v(X) :- q(X).', 'v(X) :- s(X).'], reference has ['v(X) :- p(X), alpha_0(X).'].

### t2_defeas_0012_anon  (gen@1=0%, gen@k=no)
On 't2_defeas_0012_anon', the model failed to fit the training examples. It introduced 2 new rule(s): 2 intensional copy. The rule 'v(X) :- t(X).' generalises by conditioning the target on the background predicate(s) t, so it applies to any constant satisfying them — including unseen ones. The rule 'v(X) :- r(X).' generalises by conditioning the target on the background predicate(s) r, so it applies to any constant satisfying them — including unseen ones. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; v: model wrote ['v(X) :- r(X).', 'v(X) :- t(X).'], reference has ['v(X) :- p(X), alpha_0(X).'].

### t2_defeas_0013_anon  (gen@1=0%, gen@k=no)
On 't2_defeas_0013_anon', the model failed to fit the training examples. It introduced 1 new rule(s): 1 contrary rule. It differs from the symbolic reference on: t: model wrote ['t(X) :- v(X).'], reference has ['nothing']; v: model wrote ['nothing'], reference has ['v(X) :- r(X).'].

### t2_defeas_0014_anon  (gen@1=0%, gen@k=no)
On 't2_defeas_0014_anon', the model failed to fit the training examples. It introduced 3 new rule(s): 1 contrary rule, 2 mixed. It also introduced the assumption(s) u(b), u(d) to make a rule defeasible, capturing exceptions. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; t: model wrote ['t(X) :- r(X).'], reference has ['nothing']; v: model wrote ['v(b) :- b = b, r(b).', 'v(d) :- d = d, r(d).'], reference has ['v(X) :- p(X), alpha_0(X).'].

### t2_defeas_0015_anon  (gen@1=0%, gen@k=no)
On 't2_defeas_0015_anon', the candidate is NOT a legal solution: reserved or malformed head: '**RoLe**: Added the ground fact v(X)'; reserved or malformed head: '**Gen**: Folded the ground fact v(X)'. The outcome below is reported for diagnosis only. On 't2_defeas_0015_anon', the model failed to fit the training examples. It introduced 4 new rule(s): 1 contrary rule, 2 assumption guarded, 1 mixed. It differs from the symbolic reference on: **Gen**: Folded the ground fact v(X): model wrote ['**Gen**: Folded the ground fact v(X) :- t(X), u(X) to obtain the intensional rule v(X) :- t(X), u(X).'], reference has ['nothing']; **RoLe**: Added the ground fact v(X): model wrote ['**RoLe**: Added the ground fact v(X) :- t(X), u(X) to make v(c) and v(b) derivable.'], reference has ['nothing']; c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).'].

### t2_defeas_0016_anon  (gen@1=0%, gen@k=no)
On 't2_defeas_0016_anon', the model failed to fit the training examples. It introduced 1 new rule(s): 1 contrary rule. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; t: model wrote ['t(X) :- v(X).'], reference has ['nothing']; v: model wrote ['nothing'], reference has ['v(X) :- p(X), alpha_0(X).'].

### t2_defeas_0017_anon  (gen@1=0%, gen@k=no)
On 't2_defeas_0017_anon', the model failed to fit the training examples. It introduced 1 new rule(s): 1 intensional copy. The rule 'v(X) :- q(X).' generalises by conditioning the target on the background predicate(s) q, so it applies to any constant satisfying them — including unseen ones. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; v: model wrote ['v(X) :- q(X).'], reference has ['v(X) :- p(X), alpha_0(X).'].

### t2_defeas_0018_anon  (gen@1=0%, gen@k=no)
On 't2_defeas_0018_anon', the model failed to fit the training examples. It introduced 2 new rule(s): 1 ground fact, 1 contrary rule. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; t: model wrote ['t(X) :- q(X), u(X).'], reference has ['nothing']; v: model wrote ['v(X) :- X = c.'], reference has ['v(X) :- p(X), alpha_0(X).'].

### t2_defeas_0019_anon  (gen@1=0%, gen@k=no)
On 't2_defeas_0019_anon', the model failed to fit the training examples. It introduced 2 new rule(s): 1 assumption guarded, 1 contrary rule. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; t: model wrote ['t(X) :- q(X).'], reference has ['nothing']; v: model wrote ['v(X) :- t(X), u(X).'], reference has ['v(X) :- p(X), alpha_0(X).'].

### t3_noise_0000_anon  (gen@1=0%, gen@k=no)
On 't3_noise_0000_anon', the model fits the training examples but only classifies 50% of held-out examples correctly — partial generalisation. It introduced 2 new rule(s): 2 assumption guarded. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; p1: model wrote ['p1(X) :- p(X), w(X).', 'p1(X) :- r(X), w(X).'], reference has ['p1(X) :- p(X), alpha_0(X).'].

### t3_noise_0001_anon  (gen@1=33%, gen@k=yes)
On 't3_noise_0001_anon', the model produced a framework that fits the training examples and solves the full problem in one stable extension. It introduced 1 new rule(s): 1 assumption guarded. Semantically, the learned framework is equivalent to the symbolic reference (same entailments over the whole domain), even though some rules are written differently.

### t3_noise_0002_anon  (gen@1=33%, gen@k=yes)
On 't3_noise_0002_anon', the model produced a framework that fits the training examples and solves the full problem in one stable extension. It introduced 1 new rule(s): 1 assumption guarded. Semantically, the learned framework is equivalent to the symbolic reference (same entailments over the whole domain), even though some rules are written differently.

### t3_noise_0003_anon  (gen@1=0%, gen@k=no)
On 't3_noise_0003_anon', the model failed to fit the training examples. It introduced 2 new rule(s): 2 mixed. These are all ground facts — the model MEMORISED the training positives rather than learning a general rule, which is why it fails on held-out examples. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; p1: model wrote ['p1(c) :- q(c).', 'p1(e) :- q(e).'], reference has ['p1(X) :- p(X), alpha_0(X).', 'p1(X) :- u(X).'].

### t3_noise_0004_anon  (gen@1=0%, gen@k=no)
On 't3_noise_0004_anon', the model failed to fit the training examples. It introduced 1 new rule(s): 1 intensional copy. The rule 'p1(X) :- p(X).' generalises by conditioning the target on the background predicate(s) p, so it applies to any constant satisfying them — including unseen ones. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; p1: model wrote ['p1(X) :- p(X).'], reference has ['p1(X) :- p(X), alpha_0(X).'].

### t3_noise_0005_anon  (gen@1=0%, gen@k=no)
On 't3_noise_0005_anon', the model failed to fit the training examples. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; p1: model wrote ['nothing'], reference has ['p1(X) :- p(X), alpha_0(X).'].

### t3_noise_0006_anon  (gen@1=33%, gen@k=yes)
On 't3_noise_0006_anon', the model produced a framework that fits the training examples and solves the full problem in one stable extension. It introduced 1 new rule(s): 1 assumption guarded. Semantically, the learned framework is equivalent to the symbolic reference (same entailments over the whole domain), even though some rules are written differently.

### t3_noise_0007_anon  (gen@1=0%, gen@k=no)
On 't3_noise_0007_anon', the model failed to fit the training examples. It introduced 2 new rule(s): 2 intensional copy. The rule 'p1(X) :- v(X).' generalises by conditioning the target on the background predicate(s) v, so it applies to any constant satisfying them — including unseen ones. The rule 'c_alpha(X) :- p1(X).' generalises by conditioning the target on the background predicate(s) p1, so it applies to any constant satisfying them — including unseen ones. It also introduced the assumption(s) alpha(X) to make a rule defeasible, capturing exceptions. It differs from the symbolic reference on: c_alpha: model wrote ['c_alpha(X) :- p1(X).'], reference has ['nothing']; c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; p1: model wrote ['p1(X) :- v(X).'], reference has ['p1(X) :- p(X), alpha_0(X).', 'p1(X) :- t(X).'].

### t3_noise_0008_anon  (gen@1=0%, gen@k=no)
On 't3_noise_0008_anon', the model failed to fit the training examples. It introduced 1 new rule(s): 1 intensional copy. The rule 'p1(X) :- p(X).' generalises by conditioning the target on the background predicate(s) p, so it applies to any constant satisfying them — including unseen ones. It differs from the symbolic reference on: p1: model wrote ['p1(X) :- p(X).'], reference has ['p1(X) :- r(X).'].

### t3_noise_0009_anon  (gen@1=0%, gen@k=no)
On 't3_noise_0009_anon', the model failed to fit the training examples. It introduced 2 new rule(s): 1 intensional copy, 1 assumption guarded. The rule 'p1(X) :- p(X).' generalises by conditioning the target on the background predicate(s) p, so it applies to any constant satisfying them — including unseen ones. The rule 'p1(X) :- q(X), w(X).' generalises by conditioning the target on the background predicate(s) q, w, so it applies to any constant satisfying them — including unseen ones. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; p1: model wrote ['p1(X) :- p(X).', 'p1(X) :- q(X), w(X).'], reference has ['p1(X) :- p(X), alpha_0(X).'].

### t3_noise_0010_anon  (gen@1=0%, gen@k=no)
On 't3_noise_0010_anon', the model failed to fit the training examples. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; p1: model wrote ['nothing'], reference has ['p1(X) :- p(X), alpha_0(X).'].

### t3_noise_0011_anon  (gen@1=0%, gen@k=no)
On 't3_noise_0011_anon', the model failed to fit the training examples. It introduced 3 new rule(s): 3 intensional copy. The rule 'p1(X) :- p(X).' generalises by conditioning the target on the background predicate(s) p, so it applies to any constant satisfying them — including unseen ones. The rule 'p1(X) :- q(X).' generalises by conditioning the target on the background predicate(s) q, so it applies to any constant satisfying them — including unseen ones. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; p1: model wrote ['p1(X) :- p(X).', 'p1(X) :- q(X).', 'p1(X) :- r(X).'], reference has ['p1(X) :- p(X), alpha_0(X).', 'p1(X) :- t(X).'].

### t3_noise_0012_anon  (gen@1=0%, gen@k=no)
On 't3_noise_0012_anon', the candidate is NOT a legal solution: condition (ii) violated: head 'u' is a background predicate not in the learnable set. The outcome below is reported for diagnosis only. On 't3_noise_0012_anon', the model failed to fit the training examples. It introduced 1 new rule(s): 1 assumption guarded. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; p1: model wrote ['nothing'], reference has ['p1(X) :- p(X), alpha_0(X).']; u: model wrote ['u(X) :- q(X), w(X).'], reference has ['nothing'].

### t3_noise_0013_anon  (gen@1=33%, gen@k=yes)
On 't3_noise_0013_anon', the model produced a framework that fits the training examples and solves the full problem in one stable extension. It introduced 2 new rule(s): 1 assumption guarded, 1 contrary rule. Semantically, the learned framework is equivalent to the symbolic reference (same entailments over the whole domain), even though some rules are written differently.

### t3_noise_0014_anon  (gen@1=0%, gen@k=no)
On 't3_noise_0014_anon', the model failed to fit the training examples. It introduced 4 new rule(s): 2 intensional copy, 2 contrary rule. The rule 'p1(X) :- p(X).' generalises by conditioning the target on the background predicate(s) p, so it applies to any constant satisfying them — including unseen ones. The rule 'p1(X) :- q(X).' generalises by conditioning the target on the background predicate(s) q, so it applies to any constant satisfying them — including unseen ones. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; p1: model wrote ['p1(X) :- p(X).', 'p1(X) :- q(X).'], reference has ['p1(X) :- p(X), alpha_0(X).', 'p1(X) :- t(X).']; v: model wrote ['v(X) :- p(X).', 'v(X) :- q(X).'], reference has ['nothing'].

### t3_noise_0015_anon  (gen@1=0%, gen@k=no)
On 't3_noise_0015_anon', the model failed to fit the training examples. It introduced 1 new rule(s): 1 intensional copy. The rule 'p1(X) :- p(X).' generalises by conditioning the target on the background predicate(s) p, so it applies to any constant satisfying them — including unseen ones. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; p1: model wrote ['p1(X) :- p(X).'], reference has ['p1(X) :- p(X), alpha_0(X).'].

### t3_noise_0016_anon  (gen@1=0%, gen@k=no)
On 't3_noise_0016_anon', the model failed to fit the training examples. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; p1: model wrote ['nothing'], reference has ['p1(X) :- p(X), alpha_0(X).'].

### t3_noise_0017_anon  (gen@1=0%, gen@k=no)
On 't3_noise_0017_anon', the model failed to fit the training examples. It introduced 2 new rule(s): 1 assumption guarded, 1 contrary rule. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; p1: model wrote ['p1(X) :- p(X), w(X).'], reference has ['p1(X) :- p(X), alpha_0(X).']; v: model wrote ['v(X) :- r(X).'], reference has ['nothing'].

### t3_noise_0018_anon  (gen@1=33%, gen@k=yes)
On 't3_noise_0018_anon', the model produced a framework that fits the training examples and solves the full problem in one stable extension. It introduced 1 new rule(s): 1 assumption guarded. Semantically, the learned framework is equivalent to the symbolic reference (same entailments over the whole domain), even though some rules are written differently.

### t3_noise_0019_anon  (gen@1=0%, gen@k=no)
On 't3_noise_0019_anon', the model failed to fit the training examples. It introduced 2 new rule(s): 2 mixed. These are all ground facts — the model MEMORISED the training positives rather than learning a general rule, which is why it fails on held-out examples. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; p1: model wrote ['nothing'], reference has ['p1(X) :- p(X), alpha_0(X).', 'p1(X) :- t(X).']; v: model wrote ['v(c) :- p(c).', 'v(d) :- p(d).'], reference has ['nothing'].

### t4_domain_0000_anon  (gen@1=0%, gen@k=no)
On 't4_domain_0000_anon', the model failed to fit the training examples. It introduced 1 new rule(s): 1 contrary rule. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; t: model wrote ['t(X) :- r(X).'], reference has ['nothing']; v: model wrote ['nothing'], reference has ['v(X) :- p(X), alpha_0(X).'].

### t4_domain_0001_anon  (gen@1=0%, gen@k=no)
On 't4_domain_0001_anon', the model failed to fit the training examples. It introduced 1 new rule(s): 1 assumption guarded. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; v: model wrote ['v(X) :- q(X), u(X).'], reference has ['v(X) :- p(X), alpha_0(X).'].

### t4_domain_0002_anon  (gen@1=0%, gen@k=no)
On 't4_domain_0002_anon', the model failed to fit the training examples. It introduced 1 new rule(s): 1 contrary rule. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; t: model wrote ['t(X) :- v(X).'], reference has ['nothing']; v: model wrote ['nothing'], reference has ['v(X) :- p(X), alpha_0(X).'].

### t4_domain_0003_anon  (gen@1=0%, gen@k=no)
On 't4_domain_0003_anon', the model failed to fit the training examples. It introduced 4 new rule(s): 1 contrary rule, 3 mixed. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; t: model wrote ['t(X) :- q(X).'], reference has ['nothing']; v: model wrote ['v(b) :- a.', 'v(e) :- e.', 'v(f) :- f.'], reference has ['v(X) :- p(X), alpha_0(X).'].

### t4_domain_0004_anon  (gen@1=0%, gen@k=no)
On 't4_domain_0004_anon', the model failed to fit the training examples. It introduced 3 new rule(s): 3 assumption guarded. These are all ground facts — the model MEMORISED the training positives rather than learning a general rule, which is why it fails on held-out examples. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; v: model wrote ['v(b) :- v(X), u(X).', 'v(d) :- v(X), u(X).', 'v(e) :- v(X), u(X).'], reference has ['v(X) :- p(X), alpha_0(X).'].

### t4_domain_0005_anon  (gen@1=0%, gen@k=no)
On 't4_domain_0005_anon', the model failed to fit the training examples. It introduced 1 new rule(s): 1 contrary rule. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; t: model wrote ['t(X) :- q(X), u(X).'], reference has ['nothing']; v: model wrote ['nothing'], reference has ['v(X) :- p(X), alpha_0(X).'].

### t4_domain_0006_anon  (gen@1=0%, gen@k=no)
On 't4_domain_0006_anon', the model failed to fit the training examples. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; v: model wrote ['nothing'], reference has ['v(X) :- p(X), alpha_0(X).'].

### t4_domain_0007_anon  (gen@1=0%, gen@k=no)
On 't4_domain_0007_anon', the model failed to fit the training examples. It introduced 1 new rule(s): 1 contrary rule. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; t: model wrote ['t(X) :- v(X).'], reference has ['nothing']; v: model wrote ['nothing'], reference has ['v(X) :- p(X), alpha_0(X).'].

### t4_domain_0008_anon  (gen@1=0%, gen@k=no)
On 't4_domain_0008_anon', the model failed to fit the training examples. It introduced 4 new rule(s): 3 intensional copy, 1 contrary rule. The rule 'v(X) :- g(X).' generalises by conditioning the target on the background predicate(s) g, so it applies to any constant satisfying them — including unseen ones. The rule 'v(X) :- c(X).' generalises by conditioning the target on the background predicate(s) c, so it applies to any constant satisfying them — including unseen ones. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; t: model wrote ['t(X) :- q(X).'], reference has ['nothing']; v: model wrote ['v(X) :- c(X).', 'v(X) :- d(X).', 'v(X) :- g(X).'], reference has ['v(X) :- p(X), alpha_0(X).', 'v(X) :- s(X).'].

### t4_domain_0009_anon  (gen@1=0%, gen@k=no)
On 't4_domain_0009_anon', the model failed to fit the training examples. It introduced 1 new rule(s): 1 contrary rule. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; t: model wrote ['t(X) :- q(X).'], reference has ['nothing']; v: model wrote ['nothing'], reference has ['v(X) :- p(X), alpha_0(X).'].

### t4_domain_0010_anon  (gen@1=0%, gen@k=no)
On 't4_domain_0010_anon', the model failed to fit the training examples. It introduced 1 new rule(s): 1 contrary rule. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; t: model wrote ['t(X) :- u(X).'], reference has ['nothing']; v: model wrote ['nothing'], reference has ['v(X) :- p(X), alpha_0(X).'].

### t4_domain_0011_anon  (gen@1=0%, gen@k=no)
On 't4_domain_0011_anon', the model failed to fit the training examples. It introduced 1 new rule(s): 1 contrary rule. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; t: model wrote ['t(X) :- q(X), u(X).'], reference has ['nothing']; v: model wrote ['nothing'], reference has ['v(X) :- p(X), alpha_0(X).'].

### t4_domain_0012_anon  (gen@1=0%, gen@k=no)
On 't4_domain_0012_anon', the model failed to fit the training examples. It introduced 1 new rule(s): 1 contrary rule. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; t: model wrote ['t(X) :- q(X), u(X).'], reference has ['nothing']; v: model wrote ['nothing'], reference has ['v(X) :- p(X), alpha_0(X).'].

### t4_domain_0013_anon  (gen@1=0%, gen@k=no)
On 't4_domain_0013_anon', the model failed to fit the training examples. It introduced 1 new rule(s): 1 intensional copy. The rule 'v(X) :- q(X).' generalises by conditioning the target on the background predicate(s) q, so it applies to any constant satisfying them — including unseen ones. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; v: model wrote ['v(X) :- q(X).'], reference has ['v(X) :- p(X), alpha_0(X).', 'v(X) :- s(X).'].

### t4_domain_0014_anon  (gen@1=0%, gen@k=no)
On 't4_domain_0014_anon', the model failed to fit the training examples. It introduced 1 new rule(s): 1 contrary rule. It also introduced the assumption(s) v(X) to make a rule defeasible, capturing exceptions. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; t: model wrote ['t(X) :- q(X), v(X).'], reference has ['nothing']; v: model wrote ['nothing'], reference has ['v(X) :- p(X), alpha_0(X).'].

### t4_domain_0015_anon  (gen@1=0%, gen@k=no)
On 't4_domain_0015_anon', the model failed to fit the training examples. It introduced 2 new rule(s): 1 contrary rule, 1 mixed. It also introduced the assumption(s) u(f) to make a rule defeasible, capturing exceptions. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; t: model wrote ['t(X) :- v(X), u(X).'], reference has ['nothing']; v: model wrote ['v(f) :- r(f).'], reference has ['v(X) :- p(X), alpha_0(X).'].

### t4_domain_0016_anon  (gen@1=0%, gen@k=no)
On 't4_domain_0016_anon', the model failed to fit the training examples. It introduced 1 new rule(s): 1 assumption guarded. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; v: model wrote ['v(X) :- t(X), u(X).'], reference has ['v(X) :- p(X), alpha_0(X).'].

### t4_domain_0017_anon  (gen@1=0%, gen@k=no)
On 't4_domain_0017_anon', the model failed to fit the training examples. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; v: model wrote ['nothing'], reference has ['v(X) :- p(X), alpha_0(X).'].

### t4_domain_0018_anon  (gen@1=0%, gen@k=no)
On 't4_domain_0018_anon', the model failed to fit the training examples. It introduced 2 new rule(s): 1 assumption guarded, 1 contrary rule. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; t: model wrote ['t(X) :- q(X).'], reference has ['nothing']; v: model wrote ['v(X) :- q(X), u(X).'], reference has ['v(X) :- p(X), alpha_0(X).'].

### t4_domain_0019_anon  (gen@1=0%, gen@k=no)
On 't4_domain_0019_anon', the model failed to fit the training examples. It introduced 1 new rule(s): 1 contrary rule. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; t: model wrote ['t(X) :- q(X), u(X).'], reference has ['nothing']; v: model wrote ['nothing'], reference has ['v(X) :- p(X), alpha_0(X).'].

### t5_twopath_0000_anon  (gen@1=0%, gen@k=no)
On 't5_twopath_0000_anon', the model failed to fit the training examples. It introduced 2 new rule(s): 2 intensional copy. The rule 'p1(X) :- q(X), c(X).' generalises by conditioning the target on the background predicate(s) q, c, so it applies to any constant satisfying them — including unseen ones. The rule 'p1(X) :- q(X), d(X).' generalises by conditioning the target on the background predicate(s) q, d, so it applies to any constant satisfying them — including unseen ones. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- s(X).']; c_alpha_1: model wrote ['nothing'], reference has ['c_alpha_1(X) :- r(X).']; p1: model wrote ['p1(X) :- q(X), c(X).', 'p1(X) :- q(X), d(X).'], reference has ['p1(X) :- p(X), alpha_1(X).', 'p1(X) :- q(X), alpha_0(X).'].

### t5_twopath_0001_anon  (gen@1=0%, gen@k=no)
On 't5_twopath_0001_anon', the model failed to fit the training examples. It introduced 1 new rule(s): 1 intensional copy. The rule 'p1(X) :- p(X).' generalises by conditioning the target on the background predicate(s) p, so it applies to any constant satisfying them — including unseen ones. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- s(X).']; c_alpha_1: model wrote ['nothing'], reference has ['c_alpha_1(X) :- r(X).']; p1: model wrote ['p1(X) :- p(X).'], reference has ['p1(X) :- p(X), alpha_1(X).', 'p1(X) :- q(X), alpha_0(X).'].

### t5_twopath_0002_anon  (gen@1=0%, gen@k=no)
On 't5_twopath_0002_anon', the candidate is NOT a legal solution: condition (ii) violated: head 't' is a background predicate not in the learnable set; condition (ii) violated: head 'u' is a background predicate not in the learnable set. The outcome below is reported for diagnosis only. On 't5_twopath_0002_anon', the model failed to fit the training examples. It introduced 2 new rule(s): 2 contrary rule. It also introduced the assumption(s) p1(X) to make a rule defeasible, capturing exceptions. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- r(X).']; c_alpha_1: model wrote ['nothing'], reference has ['c_alpha_1(X) :- s(X).']; p1: model wrote ['nothing'], reference has ['p1(X) :- p(X), alpha_0(X).', 'p1(X) :- q(X), alpha_1(X).'].

### t5_twopath_0003_anon  (gen@1=0%, gen@k=no)
On 't5_twopath_0003_anon', the model failed to fit the training examples. It introduced 2 new rule(s): 2 intensional copy. The rule 'p1(X) :- p(X).' generalises by conditioning the target on the background predicate(s) p, so it applies to any constant satisfying them — including unseen ones. The rule 'p1(X) :- q(X).' generalises by conditioning the target on the background predicate(s) q, so it applies to any constant satisfying them — including unseen ones. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- r(X).']; c_alpha_1: model wrote ['nothing'], reference has ['c_alpha_1(X) :- s(X).']; p1: model wrote ['p1(X) :- p(X).', 'p1(X) :- q(X).'], reference has ['p1(X) :- p(X), alpha_0(X).', 'p1(X) :- q(X), alpha_1(X).'].

### t5_twopath_0004_anon  (gen@1=0%, gen@k=no)
On 't5_twopath_0004_anon', the candidate is NOT a legal solution: condition (ii) violated: head 't' is a background predicate not in the learnable set. The outcome below is reported for diagnosis only. On 't5_twopath_0004_anon', the model failed to fit the training examples. It introduced 1 new rule(s): 1 contrary rule. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- r(X).']; c_alpha_1: model wrote ['nothing'], reference has ['c_alpha_1(X) :- s(X).']; p1: model wrote ['nothing'], reference has ['p1(X) :- p(X), alpha_0(X).', 'p1(X) :- q(X), alpha_1(X).'].

### t5_twopath_0005_anon  (gen@1=0%, gen@k=no)
On 't5_twopath_0005_anon', the candidate is NOT a legal solution: condition (ii) violated: head 'q' is a background predicate not in the learnable set; condition (ii) violated: head 'r' is a background predicate not in the learnable set; condition (ii) violated: head 'u' is a background predicate not in the learnable set. The outcome below is reported for diagnosis only. On 't5_twopath_0005_anon', the model failed to fit the training examples. It introduced 4 new rule(s): 3 intensional copy, 1 contrary rule. The rule 'p1(X) :- p(X).' generalises by conditioning the target on the background predicate(s) p, so it applies to any constant satisfying them — including unseen ones. The rule 'q(X) :- q(X).' generalises by conditioning the target on the background predicate(s) q, so it applies to any constant satisfying them — including unseen ones. It also introduced the assumption(s) alpha1(X) to make a rule defeasible, capturing exceptions. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- r(X).']; c_alpha_1: model wrote ['nothing'], reference has ['c_alpha_1(X) :- s(X).']; p1: model wrote ['p1(X) :- p(X).'], reference has ['p1(X) :- p(X), alpha_0(X).', 'p1(X) :- q(X), alpha_1(X).'].

### t5_twopath_0006_anon  (gen@1=0%, gen@k=no)
On 't5_twopath_0006_anon', the candidate is NOT a legal solution: condition (ii) violated: head 't' is a background predicate not in the learnable set; condition (iv) violated: contrary of existing assumption 'w(X)' changed from 'u(X)' to 'p1(X)'. The outcome below is reported for diagnosis only. On 't5_twopath_0006_anon', the model failed to fit the training examples. It introduced 4 new rule(s): 3 mixed, 1 contrary rule. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- s(X).']; c_alpha_1: model wrote ['nothing'], reference has ['c_alpha_1(X) :- r(X).']; p1: model wrote ['p1(X) :- p(X), c = X.', 'p1(X) :- p(X), d = X.', 'p1(X) :- p(X), f = X.'], reference has ['p1(X) :- p(X), alpha_1(X).', 'p1(X) :- q(X), alpha_0(X).'].

### t5_twopath_0007_anon  (gen@1=0%, gen@k=no)
On 't5_twopath_0007_anon', the model failed to fit the training examples. It introduced 8 new rule(s): 1 intensional copy, 7 mixed. The rule 'p1(X) :- p(X), r(X).' generalises by conditioning the target on the background predicate(s) p, r, so it applies to any constant satisfying them — including unseen ones. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- r(X).']; c_alpha_1: model wrote ['nothing'], reference has ['c_alpha_1(X) :- s(X).']; p1: model wrote ['p1(X) :- p(X), r(X), b = X.', 'p1(X) :- p(X), r(X), c = X.', 'p1(X) :- p(X), r(X), d = X.', 'p1(X) :- p(X), r(X), e = X.', 'p1(X) :- p(X), r(X), f = X.', 'p1(X) :- p(X), r(X), g = X.', 'p1(X) :- p(X), r(X), h = X.', 'p1(X) :- p(X), r(X).'], reference has ['p1(X) :- p(X), alpha_0(X).', 'p1(X) :- q(X), alpha_1(X).'].

### t5_twopath_0008_anon  (gen@1=0%, gen@k=no)
On 't5_twopath_0008_anon', the model failed to fit the training examples. It introduced 1 new rule(s): 1 intensional copy. The rule 'p1(X) :- p(X).' generalises by conditioning the target on the background predicate(s) p, so it applies to any constant satisfying them — including unseen ones. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- r(X).']; c_alpha_1: model wrote ['nothing'], reference has ['c_alpha_1(X) :- s(X).']; p1: model wrote ['p1(X) :- p(X).'], reference has ['p1(X) :- p(X), alpha_0(X).', 'p1(X) :- q(X), alpha_1(X).'].

### t5_twopath_0009_anon  (gen@1=0%, gen@k=no)
On 't5_twopath_0009_anon', the candidate is NOT a legal solution: condition (ii) violated: head 't' is a background predicate not in the learnable set. The outcome below is reported for diagnosis only. On 't5_twopath_0009_anon', the model failed to fit the training examples. It introduced 1 new rule(s): 1 contrary rule. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- r(X).']; c_alpha_1: model wrote ['nothing'], reference has ['c_alpha_1(X) :- s(X).']; p1: model wrote ['nothing'], reference has ['p1(X) :- p(X), alpha_0(X).', 'p1(X) :- q(X), alpha_1(X).'].

### t5_twopath_0010_anon  (gen@1=0%, gen@k=no)
On 't5_twopath_0010_anon', the model failed to fit the training examples. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- r(X).']; c_alpha_1: model wrote ['nothing'], reference has ['c_alpha_1(X) :- s(X).']; p1: model wrote ['nothing'], reference has ['p1(X) :- p(X), alpha_0(X).', 'p1(X) :- q(X), alpha_1(X).'].

### t5_twopath_0011_anon  (gen@1=0%, gen@k=no)
On 't5_twopath_0011_anon', the model failed to fit the training examples. It introduced 1 new rule(s): 1 intensional copy. The rule 'p1(X) :- p(X).' generalises by conditioning the target on the background predicate(s) p, so it applies to any constant satisfying them — including unseen ones. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- r(X).']; c_alpha_1: model wrote ['nothing'], reference has ['c_alpha_1(X) :- s(X).']; p1: model wrote ['p1(X) :- p(X).'], reference has ['p1(X) :- p(X), alpha_0(X).', 'p1(X) :- q(X), alpha_1(X).'].

### t5_twopath_0012_anon  (gen@1=0%, gen@k=no)
On 't5_twopath_0012_anon', the model failed to fit the training examples. It introduced 1 new rule(s): 1 intensional copy. The rule 'p1(X) :- p(X).' generalises by conditioning the target on the background predicate(s) p, so it applies to any constant satisfying them — including unseen ones. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- r(X).']; c_alpha_1: model wrote ['nothing'], reference has ['c_alpha_1(X) :- s(X).']; p1: model wrote ['p1(X) :- p(X).'], reference has ['p1(X) :- p(X), alpha_0(X).', 'p1(X) :- q(X), alpha_1(X).'].

### t5_twopath_0013_anon  (gen@1=0%, gen@k=no)
On 't5_twopath_0013_anon', the model failed to fit the training examples. It introduced 4 new rule(s): 3 mixed, 1 intensional copy. The rule 'p1(X) :- q(X).' generalises by conditioning the target on the background predicate(s) q, so it applies to any constant satisfying them — including unseen ones. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- r(X).']; c_alpha_1: model wrote ['nothing'], reference has ['c_alpha_1(X) :- s(X).']; p1: model wrote ['p1(X) :- p(X), b = X.', 'p1(X) :- p(X), c = X.', 'p1(X) :- p(X), d = X.', 'p1(X) :- q(X).'], reference has ['p1(X) :- p(X), alpha_0(X).', 'p1(X) :- q(X), alpha_1(X).'].

### t5_twopath_0014_anon  (gen@1=0%, gen@k=no)
On 't5_twopath_0014_anon', the model failed to fit the training examples. It introduced 1 new rule(s): 1 intensional copy. The rule 'p1(X) :- p(X).' generalises by conditioning the target on the background predicate(s) p, so it applies to any constant satisfying them — including unseen ones. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- r(X).']; c_alpha_1: model wrote ['nothing'], reference has ['c_alpha_1(X) :- s(X).']; p1: model wrote ['p1(X) :- p(X).'], reference has ['p1(X) :- p(X), alpha_0(X).', 'p1(X) :- q(X), alpha_1(X).'].

### t5_twopath_0015_anon  (gen@1=0%, gen@k=no)
On 't5_twopath_0015_anon', the model failed to fit the training examples. It introduced 1 new rule(s): 1 intensional copy. The rule 'p1(X) :- p(X).' generalises by conditioning the target on the background predicate(s) p, so it applies to any constant satisfying them — including unseen ones. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- r(X).']; c_alpha_1: model wrote ['nothing'], reference has ['c_alpha_1(X) :- s(X).']; p1: model wrote ['p1(X) :- p(X).'], reference has ['p1(X) :- p(X), alpha_0(X).', 'p1(X) :- q(X), alpha_1(X).'].

### t5_twopath_0016_anon  (gen@1=0%, gen@k=no)
On 't5_twopath_0016_anon', the model failed to fit the training examples. It introduced 1 new rule(s): 1 intensional copy. The rule 'p1(X) :- p(X).' generalises by conditioning the target on the background predicate(s) p, so it applies to any constant satisfying them — including unseen ones. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- s(X).']; c_alpha_1: model wrote ['nothing'], reference has ['c_alpha_1(X) :- r(X).']; p1: model wrote ['p1(X) :- p(X).'], reference has ['p1(X) :- p(X), alpha_1(X).', 'p1(X) :- q(X), alpha_0(X).'].

### t5_twopath_0017_anon  (gen@1=0%, gen@k=no)
On 't5_twopath_0017_anon', the model failed to fit the training examples. It introduced 1 new rule(s): 1 assumption guarded. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- s(X).']; c_alpha_1: model wrote ['nothing'], reference has ['c_alpha_1(X) :- r(X).']; p1: model wrote ['p1(X) :- p(X), v(X).'], reference has ['p1(X) :- p(X), alpha_1(X).', 'p1(X) :- q(X), alpha_0(X).'].

### t5_twopath_0018_anon  (gen@1=0%, gen@k=no)
On 't5_twopath_0018_anon', the model failed to fit the training examples. It introduced 2 new rule(s): 2 assumption guarded. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- r(X).']; c_alpha_1: model wrote ['nothing'], reference has ['c_alpha_1(X) :- s(X).']; p1: model wrote ['p1(X) :- p(X), v(X).', 'p1(X) :- p(X), w(X).'], reference has ['p1(X) :- p(X), alpha_0(X).', 'p1(X) :- q(X), alpha_1(X).'].

### t5_twopath_0019_anon  (gen@1=0%, gen@k=no)
On 't5_twopath_0019_anon', the candidate is NOT a legal solution: condition (ii) violated: head 't' is a background predicate not in the learnable set. The outcome below is reported for diagnosis only. On 't5_twopath_0019_anon', the model failed to fit the training examples. It introduced 1 new rule(s): 1 contrary rule. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- r(X).']; c_alpha_1: model wrote ['nothing'], reference has ['c_alpha_1(X) :- s(X).']; p1: model wrote ['nothing'], reference has ['p1(X) :- p(X), alpha_0(X).', 'p1(X) :- q(X), alpha_1(X).'].


## Mechanism vs. generalisation (success rate)

How often each rule mechanism co-occurred with full generalisation:

- **assumption guarded**: 30%
- **contrary rule**: 11%
- **intensional copy**: 4%
- **mixed**: 3%
- **ground fact**: 0%