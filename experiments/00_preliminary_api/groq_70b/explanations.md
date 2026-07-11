# Per-problem explanations


## Mode: guided

### nixon_diamond_anon  (gen@1=0%, gen@k=no)
On 'nixon_diamond_anon', the model failed to fit the training examples. It introduced 1 new rule(s): 1 contrary rule. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- p(X), w(X).']; p1: model wrote ['p1(X) :- r(X).'], reference has ['p1(X) :- p(X), alpha_0(X).']; v: model wrote ['nothing'], reference has ['v(X) :- q(X).'].

### flies_anon  (gen@1=0%, gen@k=no)
On 'flies_anon', the model failed to fit the training examples. It introduced 2 new rule(s): 1 intensional copy, 1 contrary rule. The rule 't(X) :- p(X).' generalises by conditioning the target on the background predicate(s) p, so it applies to any constant satisfying them — including unseen ones. The rule 's(X) :- p(X).' generalises by conditioning the target on the background predicate(s) p, so it applies to any constant satisfying them — including unseen ones. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; s: model wrote ['s(X) :- p(X).'], reference has ['nothing']; t: model wrote ['t(X) :- p(X).'], reference has ['t(X) :- p(X), alpha_0(X).'].

### tax_law_anon  (gen@1=0%, gen@k=no)
On 'tax_law_anon', the model failed to fit the training examples. It introduced 2 new rule(s): 1 intensional copy, 1 contrary rule. The rule 'u(X) :- p(X), u_normal(X).' generalises by conditioning the target on the background predicate(s) p, u_normal, so it applies to any constant satisfying them — including unseen ones. The rule 't(X) :- p(X), t_normal(X).' generalises by conditioning the target on the background predicate(s) p, t_normal, so it applies to any constant satisfying them — including unseen ones. It also introduced the assumption(s) u_normal(X), t_normal(X) to make a rule defeasible, capturing exceptions. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- p(X), alpha_2(X).']; c_alpha_2: model wrote ['nothing'], reference has ['c_alpha_2(X) :- p(X), alpha_0(X).']; t: model wrote ['t(X) :- p(X), t_normal(X).'], reference has ['nothing'].


## Mode: algorithm

### nixon_diamond_anon  (gen@1=0%, gen@k=no)
On 'nixon_diamond_anon', the model failed to fit the training examples. It introduced 2 new rule(s): 1 assumption guarded, 1 intensional copy. The rule 'v(X) :- p(X), w(X).' generalises by conditioning the target on the background predicate(s) p, w, so it applies to any constant satisfying them — including unseen ones. The rule 'w(X) :- r(X).' generalises by conditioning the target on the background predicate(s) r, so it applies to any constant satisfying them — including unseen ones. It also introduced the assumption(s) alpha1(X) to make a rule defeasible, capturing exceptions. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- p(X), w(X).']; p1: model wrote ['nothing'], reference has ['p1(X) :- p(X), alpha_0(X).']; v: model wrote ['v(X) :- p(X), w(X).'], reference has ['v(X) :- q(X).'].

### flies_anon  (gen@1=0%, gen@k=no)
On 'flies_anon', the model failed to fit the training examples. It introduced 1 new rule(s): 1 intensional copy. The rule 't(X) :- p(X).' generalises by conditioning the target on the background predicate(s) p, so it applies to any constant satisfying them — including unseen ones. It also introduced the assumption(s) alpha(X) to make a rule defeasible, capturing exceptions. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; t: model wrote ['t(X) :- p(X).'], reference has ['t(X) :- p(X), alpha_0(X).'].

### tax_law_anon  (gen@1=0%, gen@k=no)
On 'tax_law_anon', the model failed to fit the training examples. It introduced 1 new rule(s): 1 intensional copy. The rule 'u(X) :- p(X).' generalises by conditioning the target on the background predicate(s) p, so it applies to any constant satisfying them — including unseen ones. It also introduced the assumption(s) alpha(X) to make a rule defeasible, capturing exceptions. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- p(X), alpha_2(X).']; c_alpha_2: model wrote ['nothing'], reference has ['c_alpha_2(X) :- p(X), alpha_0(X).']; u: model wrote ['u(X) :- p(X).'], reference has ['u(X) :- p(X), alpha_0(X).', 'u(X) :- q(X).'].


## Mechanism vs. generalisation (success rate)

How often each rule mechanism co-occurred with full generalisation:

- **contrary rule**: 0%
- **intensional copy**: 0%
- **assumption guarded**: 0%