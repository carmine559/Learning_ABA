# Per-problem explanations


## Mode: guided

### nixon_diamond_anon  (gen@1=0%, gen@k=no)
On 'nixon_diamond_anon', the model failed to fit the training examples. It introduced 1 new rule(s): 1 contrary rule. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- p(X), w(X).']; p1: model wrote ['p1(X) :- r(X).'], reference has ['p1(X) :- p(X), alpha_0(X).']; v: model wrote ['nothing'], reference has ['v(X) :- q(X).'].

### flies_anon  (gen@1=0%, gen@k=no)
On 'flies_anon', the model failed to fit the training examples. It introduced 2 new rule(s): 1 intensional copy, 1 contrary rule. The rule 't(X) :- p(X).' generalises by conditioning the target on the background predicate(s) p, so it applies to any constant satisfying them — including unseen ones. The rule 's(X) :- p(X).' generalises by conditioning the target on the background predicate(s) p, so it applies to any constant satisfying them — including unseen ones. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; s: model wrote ['s(X) :- p(X).'], reference has ['nothing']; t: model wrote ['t(X) :- p(X).'], reference has ['t(X) :- p(X), alpha_0(X).'].


## Mode: fewshot


## Mechanism vs. generalisation (success rate)

How often each rule mechanism co-occurred with full generalisation:

- **contrary rule**: 0%
- **intensional copy**: 0%