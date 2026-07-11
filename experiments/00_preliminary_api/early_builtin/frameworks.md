# Learned ABA frameworks

Each problem shows the symbolic ground truth followed by the LLM-generated candidates. `DEFEASIBLE` means the solution uses an assumption (the hard case); `MONOTONIC` means it does not.


## nixon_diamond_anon

**symbolic** — `DEFEASIBLE`  (valid, generalises)
```prolog
v(X) :- q(X).  % [intensional_copy]
p1(X) :- p(X), alpha_0(X).  % [contrary_rule]
c_alpha_0(X) :- p(X), w(X).  % [assumption_guarded]
% assumption: alpha_0(X) defeated_by c_alpha_0(X)
% assumption: w(X) defeated_by p1(X)
```

_Plain language:_
- v(X) holds if q(X).
- p1(X) holds if p(X) and alpha_0(X).
- c_alpha_0(X) holds if p(X) and w(X).

**llama3-70b** / guided / sample 0 — `MONOTONIC`  (invalid, overfits)
```prolog
p1(X) :- r(X).  % [contrary_rule]
```

_Plain language:_
- p1(X) holds if r(X).

> On 'nixon_diamond_anon', the model failed to fit the training examples. It introduced 1 new rule(s): 1 contrary rule. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- p(X), w(X).']; p1: model wrote ['p1(X) :- r(X).'], reference has ['p1(X) :- p(X), alpha_0(X).']; v: model wrote ['nothing'], reference has ['v(X) :- q(X).'].

**llama3-70b** / guided / sample 1 — `MONOTONIC`  (invalid, overfits)
```prolog
p1(X) :- r(X).  % [contrary_rule]
```

_Plain language:_
- p1(X) holds if r(X).

> On 'nixon_diamond_anon', the model failed to fit the training examples. It introduced 1 new rule(s): 1 contrary rule. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- p(X), w(X).']; p1: model wrote ['p1(X) :- r(X).'], reference has ['p1(X) :- p(X), alpha_0(X).']; v: model wrote ['nothing'], reference has ['v(X) :- q(X).'].

**llama3-70b** / guided / sample 2 — `DEFEASIBLE`  (invalid, overfits)
```prolog
p1(X) :- r(X).  % [contrary_rule]
v(X) :- p(X), w(X), p1(X).  % [assumption_guarded]
% assumption: w(X) defeated_by p1(X)
```

_Plain language:_
- p1(X) holds if r(X).
- v(X) holds if p(X) and w(X) and p1(X).

> On 'nixon_diamond_anon', the model failed to fit the training examples. It introduced 2 new rule(s): 1 contrary rule, 1 assumption guarded. It also introduced the assumption(s) w(X) to make a rule defeasible, capturing exceptions. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- p(X), w(X).']; p1: model wrote ['p1(X) :- r(X).'], reference has ['p1(X) :- p(X), alpha_0(X).']; v: model wrote ['v(X) :- p(X), w(X), p1(X).'], reference has ['v(X) :- q(X).'].

**llama3-70b** / guided / sample 3 — `MONOTONIC`  (invalid, overfits)
```prolog
p1(X) :- r(X).  % [contrary_rule]
```

_Plain language:_
- p1(X) holds if r(X).

> On 'nixon_diamond_anon', the model failed to fit the training examples. It introduced 1 new rule(s): 1 contrary rule. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- p(X), w(X).']; p1: model wrote ['p1(X) :- r(X).'], reference has ['p1(X) :- p(X), alpha_0(X).']; v: model wrote ['nothing'], reference has ['v(X) :- q(X).'].

**llama3-70b** / guided / sample 4 — `MONOTONIC`  (invalid, overfits)
```prolog
p1(X) :- r(X).  % [contrary_rule]
```

_Plain language:_
- p1(X) holds if r(X).

> On 'nixon_diamond_anon', the model failed to fit the training examples. It introduced 1 new rule(s): 1 contrary rule. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- p(X), w(X).']; p1: model wrote ['p1(X) :- r(X).'], reference has ['p1(X) :- p(X), alpha_0(X).']; v: model wrote ['nothing'], reference has ['v(X) :- q(X).'].


## flies_anon

**symbolic** — `DEFEASIBLE`  (valid, generalises)
```prolog
t(X) :- p(X), alpha_0(X).  % [intensional_copy]
c_alpha_0(X) :- q(X).  % [intensional_copy]
% assumption: alpha_0(X) defeated_by c_alpha_0(X)
```

_Plain language:_
- t(X) holds if p(X) and alpha_0(X).
- c_alpha_0(X) holds if q(X).

**llama3-70b** / guided / sample 0 — `MONOTONIC`  (invalid, overfits)
```prolog
t(X) :- p(X).  % [intensional_copy]
s(X) :- p(X).  % [contrary_rule]
```

_Plain language:_
- t(X) holds if p(X).
- s(X) holds if p(X).

> On 'flies_anon', the model failed to fit the training examples. It introduced 2 new rule(s): 1 intensional copy, 1 contrary rule. The rule 't(X) :- p(X).' generalises by conditioning the target on the background predicate(s) p, so it applies to any constant satisfying them — including unseen ones. The rule 's(X) :- p(X).' generalises by conditioning the target on the background predicate(s) p, so it applies to any constant satisfying them — including unseen ones. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; s: model wrote ['s(X) :- p(X).'], reference has ['nothing']; t: model wrote ['t(X) :- p(X).'], reference has ['t(X) :- p(X), alpha_0(X).'].

**llama3-70b** / guided / sample 1 — `MONOTONIC`  (invalid, overfits)
```prolog
t(X) :- p(X).  % [intensional_copy]
s(X) :- p(X).  % [contrary_rule]
```

_Plain language:_
- t(X) holds if p(X).
- s(X) holds if p(X).

> On 'flies_anon', the model failed to fit the training examples. It introduced 2 new rule(s): 1 intensional copy, 1 contrary rule. The rule 't(X) :- p(X).' generalises by conditioning the target on the background predicate(s) p, so it applies to any constant satisfying them — including unseen ones. The rule 's(X) :- p(X).' generalises by conditioning the target on the background predicate(s) p, so it applies to any constant satisfying them — including unseen ones. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; s: model wrote ['s(X) :- p(X).'], reference has ['nothing']; t: model wrote ['t(X) :- p(X).'], reference has ['t(X) :- p(X), alpha_0(X).'].

**llama3-70b** / guided / sample 2 — `MONOTONIC`  (invalid, overfits)
```prolog
t(X) :- p(X).  % [intensional_copy]
s(X) :- p(X).  % [contrary_rule]
```

_Plain language:_
- t(X) holds if p(X).
- s(X) holds if p(X).

> On 'flies_anon', the model failed to fit the training examples. It introduced 2 new rule(s): 1 intensional copy, 1 contrary rule. The rule 't(X) :- p(X).' generalises by conditioning the target on the background predicate(s) p, so it applies to any constant satisfying them — including unseen ones. The rule 's(X) :- p(X).' generalises by conditioning the target on the background predicate(s) p, so it applies to any constant satisfying them — including unseen ones. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; s: model wrote ['s(X) :- p(X).'], reference has ['nothing']; t: model wrote ['t(X) :- p(X).'], reference has ['t(X) :- p(X), alpha_0(X).'].

**llama3-70b** / guided / sample 3 — `MONOTONIC`  (invalid, overfits)
```prolog
t(X) :- p(X).  % [intensional_copy]
s(X) :- p(X).  % [contrary_rule]
```

_Plain language:_
- t(X) holds if p(X).
- s(X) holds if p(X).

> On 'flies_anon', the model failed to fit the training examples. It introduced 2 new rule(s): 1 intensional copy, 1 contrary rule. The rule 't(X) :- p(X).' generalises by conditioning the target on the background predicate(s) p, so it applies to any constant satisfying them — including unseen ones. The rule 's(X) :- p(X).' generalises by conditioning the target on the background predicate(s) p, so it applies to any constant satisfying them — including unseen ones. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; s: model wrote ['s(X) :- p(X).'], reference has ['nothing']; t: model wrote ['t(X) :- p(X).'], reference has ['t(X) :- p(X), alpha_0(X).'].

**llama3-70b** / guided / sample 4 — `MONOTONIC`  (invalid, overfits)
```prolog
t(X) :- p(X).  % [intensional_copy]
s(X) :- p(X).  % [contrary_rule]
```

_Plain language:_
- t(X) holds if p(X).
- s(X) holds if p(X).

> On 'flies_anon', the model failed to fit the training examples. It introduced 2 new rule(s): 1 intensional copy, 1 contrary rule. The rule 't(X) :- p(X).' generalises by conditioning the target on the background predicate(s) p, so it applies to any constant satisfying them — including unseen ones. The rule 's(X) :- p(X).' generalises by conditioning the target on the background predicate(s) p, so it applies to any constant satisfying them — including unseen ones. It differs from the symbolic reference on: c_alpha_0: model wrote ['nothing'], reference has ['c_alpha_0(X) :- q(X).']; s: model wrote ['s(X) :- p(X).'], reference has ['nothing']; t: model wrote ['t(X) :- p(X).'], reference has ['t(X) :- p(X), alpha_0(X).'].


## tax_law_anon

**symbolic** — `DEFEASIBLE`  (valid, generalises)
```prolog
u(X) :- p(X), alpha_0(X).  % [intensional_copy]
u(X) :- q(X).  % [intensional_copy]
c_alpha_0(X) :- p(X), alpha_2(X).  % [intensional_copy]
c_alpha_2(X) :- p(X), alpha_0(X).  % [intensional_copy]
% assumption: alpha_0(X) defeated_by c_alpha_0(X)
% assumption: alpha_2(X) defeated_by c_alpha_2(X)
```

_Plain language:_
- u(X) holds if p(X) and alpha_0(X).
- u(X) holds if q(X).
- c_alpha_0(X) holds if p(X) and alpha_2(X).
- c_alpha_2(X) holds if p(X) and alpha_0(X).


## complex_0000_anon

**symbolic** — `DEFEASIBLE`  (valid, generalises)
```prolog
p1(X) :- q(X), alpha_0(X).  % [intensional_copy]
p1(X) :- p(X), alpha_2(X).  % [intensional_copy]
c_alpha_0(X) :- s(X).  % [intensional_copy]
c_alpha_2(X) :- r(X).  % [intensional_copy]
% assumption: alpha_0(X) defeated_by c_alpha_0(X)
% assumption: alpha_2(X) defeated_by c_alpha_2(X)
```

_Plain language:_
- p1(X) holds if q(X) and alpha_0(X).
- p1(X) holds if p(X) and alpha_2(X).
- c_alpha_0(X) holds if s(X).
- c_alpha_2(X) holds if r(X).


## complex_0001_anon

**symbolic** — `DEFEASIBLE`  (valid, generalises)
```prolog
p1(X) :- p(X), alpha_0(X).  % [intensional_copy]
p1(X) :- q(X), alpha_2(X).  % [intensional_copy]
c_alpha_0(X) :- r(X).  % [intensional_copy]
c_alpha_2(X) :- s(X).  % [intensional_copy]
% assumption: alpha_0(X) defeated_by c_alpha_0(X)
% assumption: alpha_2(X) defeated_by c_alpha_2(X)
```

_Plain language:_
- p1(X) holds if p(X) and alpha_0(X).
- p1(X) holds if q(X) and alpha_2(X).
- c_alpha_0(X) holds if r(X).
- c_alpha_2(X) holds if s(X).


## complex_0002_anon

**symbolic** — `DEFEASIBLE`  (valid, generalises)
```prolog
p1(X) :- q(X), alpha_0(X).  % [intensional_copy]
p1(X) :- p(X), alpha_2(X).  % [intensional_copy]
c_alpha_0(X) :- s(X).  % [intensional_copy]
c_alpha_2(X) :- r(X).  % [intensional_copy]
% assumption: alpha_0(X) defeated_by c_alpha_0(X)
% assumption: alpha_2(X) defeated_by c_alpha_2(X)
```

_Plain language:_
- p1(X) holds if q(X) and alpha_0(X).
- p1(X) holds if p(X) and alpha_2(X).
- c_alpha_0(X) holds if s(X).
- c_alpha_2(X) holds if r(X).


## complex_0003_anon

**symbolic** — `DEFEASIBLE`  (valid, generalises)
```prolog
p1(X) :- p(X), alpha_0(X).  % [intensional_copy]
p1(X) :- q(X), alpha_2(X).  % [intensional_copy]
c_alpha_0(X) :- r(X).  % [intensional_copy]
c_alpha_2(X) :- s(X).  % [intensional_copy]
% assumption: alpha_0(X) defeated_by c_alpha_0(X)
% assumption: alpha_2(X) defeated_by c_alpha_2(X)
```

_Plain language:_
- p1(X) holds if p(X) and alpha_0(X).
- p1(X) holds if q(X) and alpha_2(X).
- c_alpha_0(X) holds if r(X).
- c_alpha_2(X) holds if s(X).


## complex_0004_anon

**symbolic** — `DEFEASIBLE`  (valid, generalises)
```prolog
p1(X) :- p(X), alpha_0(X).  % [intensional_copy]
p1(X) :- q(X), alpha_2(X).  % [intensional_copy]
c_alpha_0(X) :- r(X).  % [intensional_copy]
c_alpha_2(X) :- s(X).  % [intensional_copy]
% assumption: alpha_0(X) defeated_by c_alpha_0(X)
% assumption: alpha_2(X) defeated_by c_alpha_2(X)
```

_Plain language:_
- p1(X) holds if p(X) and alpha_0(X).
- p1(X) holds if q(X) and alpha_2(X).
- c_alpha_0(X) holds if r(X).
- c_alpha_2(X) holds if s(X).


## complex_0005_anon

**symbolic** — `DEFEASIBLE`  (valid, generalises)
```prolog
p1(X) :- q(X), alpha_0(X).  % [intensional_copy]
p1(X) :- p(X), alpha_2(X).  % [intensional_copy]
c_alpha_0(X) :- s(X).  % [intensional_copy]
c_alpha_2(X) :- r(X).  % [intensional_copy]
% assumption: alpha_0(X) defeated_by c_alpha_0(X)
% assumption: alpha_2(X) defeated_by c_alpha_2(X)
```

_Plain language:_
- p1(X) holds if q(X) and alpha_0(X).
- p1(X) holds if p(X) and alpha_2(X).
- c_alpha_0(X) holds if s(X).
- c_alpha_2(X) holds if r(X).


## complex_0006_anon

**symbolic** — `DEFEASIBLE`  (valid, generalises)
```prolog
p1(X) :- p(X), alpha_0(X).  % [intensional_copy]
p1(X) :- q(X), alpha_2(X).  % [intensional_copy]
c_alpha_0(X) :- r(X).  % [intensional_copy]
c_alpha_2(X) :- s(X).  % [intensional_copy]
% assumption: alpha_0(X) defeated_by c_alpha_0(X)
% assumption: alpha_2(X) defeated_by c_alpha_2(X)
```

_Plain language:_
- p1(X) holds if p(X) and alpha_0(X).
- p1(X) holds if q(X) and alpha_2(X).
- c_alpha_0(X) holds if r(X).
- c_alpha_2(X) holds if s(X).


## complex_0007_anon

**symbolic** — `DEFEASIBLE`  (valid, generalises)
```prolog
p1(X) :- p(X), alpha_0(X).  % [intensional_copy]
p1(X) :- q(X), alpha_2(X).  % [intensional_copy]
c_alpha_0(X) :- r(X).  % [intensional_copy]
c_alpha_2(X) :- s(X).  % [intensional_copy]
% assumption: alpha_0(X) defeated_by c_alpha_0(X)
% assumption: alpha_2(X) defeated_by c_alpha_2(X)
```

_Plain language:_
- p1(X) holds if p(X) and alpha_0(X).
- p1(X) holds if q(X) and alpha_2(X).
- c_alpha_0(X) holds if r(X).
- c_alpha_2(X) holds if s(X).


## complex_0008_anon

**symbolic** — `DEFEASIBLE`  (valid, generalises)
```prolog
p1(X) :- p(X), alpha_0(X).  % [intensional_copy]
p1(X) :- q(X), alpha_2(X).  % [intensional_copy]
c_alpha_0(X) :- r(X).  % [intensional_copy]
c_alpha_2(X) :- s(X).  % [intensional_copy]
% assumption: alpha_0(X) defeated_by c_alpha_0(X)
% assumption: alpha_2(X) defeated_by c_alpha_2(X)
```

_Plain language:_
- p1(X) holds if p(X) and alpha_0(X).
- p1(X) holds if q(X) and alpha_2(X).
- c_alpha_0(X) holds if r(X).
- c_alpha_2(X) holds if s(X).


## complex_0009_anon

**symbolic** — `DEFEASIBLE`  (valid, generalises)
```prolog
p1(X) :- p(X), alpha_0(X).  % [intensional_copy]
p1(X) :- q(X), alpha_2(X).  % [intensional_copy]
c_alpha_0(X) :- r(X).  % [intensional_copy]
c_alpha_2(X) :- s(X).  % [intensional_copy]
% assumption: alpha_0(X) defeated_by c_alpha_0(X)
% assumption: alpha_2(X) defeated_by c_alpha_2(X)
```

_Plain language:_
- p1(X) holds if p(X) and alpha_0(X).
- p1(X) holds if q(X) and alpha_2(X).
- c_alpha_0(X) holds if r(X).
- c_alpha_2(X) holds if s(X).
