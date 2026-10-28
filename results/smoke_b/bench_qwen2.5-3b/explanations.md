# Per-problem explanations


## Mode: direct

### nixon_diamond_anon  (clean@1=0%, exact@k=no)
On 'nixon_diamond_anon', the answer is not a solution: no stable extension accepts every positive example and no negative one. Taken one at a time, it gets 2 of 5 posed examples wrong (v(d), v(b)). It differs from the algorithm's answer on: c_alpha_0: model wrote ['nothing'], the algorithm has ['c_alpha_0(X) :- p(X), w(X).']; p1: model wrote ['nothing'], the algorithm has ['p1(X) :- r(X), alpha_0(X).']; v: model wrote ['nothing'], the algorithm has ['v(X) :- q(X).'].

### flies_anon  (clean@1=0%, exact@k=no)
On 'flies_anon', the candidate is NOT a legal solution: new assumption predicate 's' repurposes background non-assumption predicate 's'. The outcome below is reported for diagnosis only. On 'flies_anon', the answer is not a solution: no stable extension accepts every positive example and no negative one. Taken one at a time, it gets 1 of 3 posed examples wrong (t(a)). It differs from the algorithm's answer on: c_alpha_0: model wrote ['nothing'], the algorithm has ['c_alpha_0(X) :- q(X).']; t: model wrote ['nothing'], the algorithm has ['t(X) :- p(X), alpha_0(X).'].

### tax_law_anon  (clean@1=0%, exact@k=no)
On 'tax_law_anon', the candidate is NOT a legal solution: new assumption predicate 't' repurposes background non-assumption predicate 't'; new assumption predicate 't' repurposes background non-assumption predicate 't'. The outcome below is reported for diagnosis only. On 'tax_law_anon', the answer is not a solution: no stable extension accepts every positive example and no negative one. Taken one at a time, it gets 2 of 3 posed examples wrong (u(a), u(c)). It differs from the algorithm's answer on: c_alpha_0: model wrote ['nothing'], the algorithm has ['c_alpha_0(X) :- dom(X), alpha_1(X).']; c_alpha_1: model wrote ['nothing'], the algorithm has ['c_alpha_1(X) :- p(X), alpha_0(X).']; u: model wrote ['nothing'], the algorithm has ['u(X) :- p(X), alpha_0(X).', 'u(X) :- q(X).'].

### t1_mono_0000_anon  (clean@1=0%, exact@k=no)
On 't1_mono_0000_anon', the answer is not a solution: no stable extension accepts every positive example and no negative one. Taken one at a time, it gets 3 of 5 posed examples wrong (v(a), v(b), v(d)). It differs from the algorithm's answer on: v: model wrote ['nothing'], the algorithm has ['v(X) :- p(X).']. Off the posed examples, it decides 0% of the example predicate's atoms as the algorithm's answer does.

### t2_defeas_0000_anon  (clean@1=0%, exact@k=no)
On 't2_defeas_0000_anon', the answer is not a solution: no stable extension accepts every positive example and no negative one. Taken one at a time, it gets 3 of 6 posed examples wrong (v(d), v(c), v(b)). It differs from the algorithm's answer on: c_alpha_0: model wrote ['nothing'], the algorithm has ['c_alpha_0(X) :- q(X).']; v: model wrote ['nothing'], the algorithm has ['v(X) :- p(X), alpha_0(X).'].

### t3_noise_0000_anon  (clean@1=0%, exact@k=no)
On 't3_noise_0000_anon', the answer is not a solution: no stable extension accepts every positive example and no negative one. Taken one at a time, it gets 3 of 6 posed examples wrong (p1(b), p1(c), p1(d)). It differs from the algorithm's answer on: c_alpha_0: model wrote ['nothing'], the algorithm has ['c_alpha_0(X) :- q(X).']; p1: model wrote ['nothing'], the algorithm has ['p1(X) :- p(X), alpha_0(X).']. Off the posed examples, it decides 0% of the example predicate's atoms as the algorithm's answer does.

### t4_domain_0000_anon  (clean@1=0%, exact@k=no)
On 't4_domain_0000_anon', the answer is not a solution: no stable extension accepts every positive example and no negative one. Taken one at a time, it gets 4 of 8 posed examples wrong (v(b), v(g), v(e), v(f)). It differs from the algorithm's answer on: c_alpha_0: model wrote ['nothing'], the algorithm has ['c_alpha_0(X) :- q(X).']; v: model wrote ['nothing'], the algorithm has ['v(X) :- p(X), alpha_0(X).']. Off the posed examples, it decides 0% of the example predicate's atoms as the algorithm's answer does.

### t5_twopath_0000_anon  (clean@1=0%, exact@k=no)
On 't5_twopath_0000_anon', the answer is not a solution: no stable extension accepts every positive example and no negative one. Taken one at a time, it gets 4 of 8 posed examples wrong (p1(d), p1(c), p1(f), p1(b)). It differs from the algorithm's answer on: c_alpha_0: model wrote ['nothing'], the algorithm has ['c_alpha_0(X) :- s(X).']; c_alpha_1: model wrote ['nothing'], the algorithm has ['c_alpha_1(X) :- r(X).']; p1: model wrote ['nothing'], the algorithm has ['p1(X) :- p(X), alpha_1(X).', 'p1(X) :- q(X), alpha_0(X).'].


## Mode: cot

### nixon_diamond_anon  (clean@1=0%, exact@k=no)
On 'nixon_diamond_anon', the answer is not a solution: no stable extension accepts every positive example and no negative one. Taken one at a time, it gets 2 of 5 posed examples wrong (v(d), v(b)). It differs from the algorithm's answer on: c_alpha_0: model wrote ['nothing'], the algorithm has ['c_alpha_0(X) :- p(X), w(X).']; p1: model wrote ['nothing'], the algorithm has ['p1(X) :- r(X), alpha_0(X).']; v: model wrote ['nothing'], the algorithm has ['v(X) :- q(X).'].

### flies_anon  (clean@1=0%, exact@k=no)
On 'flies_anon', the answer is not a solution: no stable extension accepts every positive example and no negative one. Taken one at a time, it gets 1 of 3 posed examples wrong (t(a)). It differs from the algorithm's answer on: c_alpha_0: model wrote ['nothing'], the algorithm has ['c_alpha_0(X) :- q(X).']; t: model wrote ['nothing'], the algorithm has ['t(X) :- p(X), alpha_0(X).'].

### tax_law_anon  (clean@1=50%, exact@k=no)
On 'tax_law_anon', the answer is an intensional solution (Definition 1): one stable extension accepts every positive example and no negative one. It differs from the algorithm's answer on: c_alpha_0: model wrote ['nothing'], the algorithm has ['c_alpha_0(X) :- dom(X), alpha_1(X).']; c_alpha_1: model wrote ['nothing'], the algorithm has ['c_alpha_1(X) :- p(X), alpha_0(X).']; u: model wrote ['nothing'], the algorithm has ['u(X) :- p(X), alpha_0(X).', 'u(X) :- q(X).'].

### t1_mono_0000_anon  (clean@1=0%, exact@k=no)
On 't1_mono_0000_anon', the answer is not a solution: no stable extension accepts every positive example and no negative one. Taken one at a time, it gets 3 of 5 posed examples wrong (v(a), v(b), v(d)). It differs from the algorithm's answer on: v: model wrote ['nothing'], the algorithm has ['v(X) :- p(X).']. Off the posed examples, it decides 0% of the example predicate's atoms as the algorithm's answer does.

### t2_defeas_0000_anon  (clean@1=0%, exact@k=no)
On 't2_defeas_0000_anon', the answer is not a solution: no stable extension accepts every positive example and no negative one. Taken one at a time, it gets 3 of 6 posed examples wrong (v(d), v(c), v(b)). It differs from the algorithm's answer on: c_alpha_0: model wrote ['nothing'], the algorithm has ['c_alpha_0(X) :- q(X).']; v: model wrote ['nothing'], the algorithm has ['v(X) :- p(X), alpha_0(X).'].

### t3_noise_0000_anon  (clean@1=0%, exact@k=no)
On 't3_noise_0000_anon', the answer is not a solution: no stable extension accepts every positive example and no negative one. Taken one at a time, it gets 3 of 6 posed examples wrong (p1(b), p1(c), p1(d)). It differs from the algorithm's answer on: c_alpha_0: model wrote ['nothing'], the algorithm has ['c_alpha_0(X) :- q(X).']; p1: model wrote ['nothing'], the algorithm has ['p1(X) :- p(X), alpha_0(X).']. Off the posed examples, it decides 0% of the example predicate's atoms as the algorithm's answer does.

### t4_domain_0000_anon  (clean@1=0%, exact@k=no)
On 't4_domain_0000_anon', the answer is not a solution: no stable extension accepts every positive example and no negative one. Taken one at a time, it gets 4 of 8 posed examples wrong (v(b), v(g), v(e), v(f)). It differs from the algorithm's answer on: c_alpha_0: model wrote ['nothing'], the algorithm has ['c_alpha_0(X) :- q(X).']; v: model wrote ['nothing'], the algorithm has ['v(X) :- p(X), alpha_0(X).']. Off the posed examples, it decides 0% of the example predicate's atoms as the algorithm's answer does.

### t5_twopath_0000_anon  (clean@1=0%, exact@k=no)
On 't5_twopath_0000_anon', the answer is not a solution: no stable extension accepts every positive example and no negative one. Taken one at a time, it gets 6 of 8 posed examples wrong (p1(d), p1(c), p1(f), p1(g), ...). It differs from the algorithm's answer on: c_alpha_0: model wrote ['nothing'], the algorithm has ['c_alpha_0(X) :- s(X).']; c_alpha_1: model wrote ['nothing'], the algorithm has ['c_alpha_1(X) :- r(X).']; p1: model wrote ['nothing'], the algorithm has ['p1(X) :- p(X), alpha_1(X).', 'p1(X) :- q(X), alpha_0(X).'].


## Mode: guided

### nixon_diamond_anon  (clean@1=0%, exact@k=no)
On 'nixon_diamond_anon', the answer is not a solution: no stable extension accepts every positive example and no negative one. Taken one at a time, it gets 2 of 5 posed examples wrong (v(d), v(b)). It differs from the algorithm's answer on: c_alpha_0: model wrote ['nothing'], the algorithm has ['c_alpha_0(X) :- p(X), w(X).']; p1: model wrote ['nothing'], the algorithm has ['p1(X) :- r(X), alpha_0(X).']; v: model wrote ['nothing'], the algorithm has ['v(X) :- q(X).'].

### flies_anon  (clean@1=0%, exact@k=no)
On 'flies_anon', the answer is not a solution: no stable extension accepts every positive example and no negative one. Taken one at a time, it gets 1 of 3 posed examples wrong (t(a)). It differs from the algorithm's answer on: c_alpha_0: model wrote ['nothing'], the algorithm has ['c_alpha_0(X) :- q(X).']; t: model wrote ['nothing'], the algorithm has ['t(X) :- p(X), alpha_0(X).'].

### tax_law_anon  (clean@1=50%, exact@k=no)
On 'tax_law_anon', the answer is an intensional solution (Definition 1): one stable extension accepts every positive example and no negative one. It differs from the algorithm's answer on: c_alpha_0: model wrote ['nothing'], the algorithm has ['c_alpha_0(X) :- dom(X), alpha_1(X).']; c_alpha_1: model wrote ['nothing'], the algorithm has ['c_alpha_1(X) :- p(X), alpha_0(X).']; u: model wrote ['nothing'], the algorithm has ['u(X) :- p(X), alpha_0(X).', 'u(X) :- q(X).'].

### t1_mono_0000_anon  (clean@1=0%, exact@k=no)
On 't1_mono_0000_anon', the answer is not a solution: no stable extension accepts every positive example and no negative one. Taken one at a time, it gets 3 of 5 posed examples wrong (v(a), v(b), v(d)). It differs from the algorithm's answer on: v: model wrote ['nothing'], the algorithm has ['v(X) :- p(X).']. Off the posed examples, it decides 0% of the example predicate's atoms as the algorithm's answer does.

### t2_defeas_0000_anon  (clean@1=0%, exact@k=no)
On 't2_defeas_0000_anon', the answer is not a solution: no stable extension accepts every positive example and no negative one. Taken one at a time, it gets 3 of 6 posed examples wrong (v(d), v(c), v(b)). It differs from the algorithm's answer on: c_alpha_0: model wrote ['nothing'], the algorithm has ['c_alpha_0(X) :- q(X).']; v: model wrote ['nothing'], the algorithm has ['v(X) :- p(X), alpha_0(X).'].

### t3_noise_0000_anon  (clean@1=0%, exact@k=no)
On 't3_noise_0000_anon', the answer is not a solution: no stable extension accepts every positive example and no negative one. Taken one at a time, it gets 3 of 6 posed examples wrong (p1(b), p1(c), p1(d)). It differs from the algorithm's answer on: c_alpha_0: model wrote ['nothing'], the algorithm has ['c_alpha_0(X) :- q(X).']; p1: model wrote ['nothing'], the algorithm has ['p1(X) :- p(X), alpha_0(X).']. Off the posed examples, it decides 0% of the example predicate's atoms as the algorithm's answer does.

### t4_domain_0000_anon  (clean@1=0%, exact@k=no)
On 't4_domain_0000_anon', the answer is not a solution: no stable extension accepts every positive example and no negative one. Taken one at a time, it gets 4 of 8 posed examples wrong (v(b), v(g), v(e), v(f)). It differs from the algorithm's answer on: c_alpha_0: model wrote ['nothing'], the algorithm has ['c_alpha_0(X) :- q(X).']; v: model wrote ['nothing'], the algorithm has ['v(X) :- p(X), alpha_0(X).']. Off the posed examples, it decides 0% of the example predicate's atoms as the algorithm's answer does.

### t5_twopath_0000_anon  (clean@1=0%, exact@k=no)
On 't5_twopath_0000_anon', the answer is not a solution: no stable extension accepts every positive example and no negative one. Taken one at a time, it gets 8 of 8 posed examples wrong (p1(d), p1(c), p1(f), p1(b), ...). It differs from the algorithm's answer on: c_alpha_0: model wrote ['nothing'], the algorithm has ['c_alpha_0(X) :- s(X).']; c_alpha_1: model wrote ['nothing'], the algorithm has ['c_alpha_1(X) :- r(X).']; p1: model wrote ['nothing'], the algorithm has ['p1(X) :- p(X), alpha_1(X).', 'p1(X) :- q(X), alpha_0(X).'].


## Mode: algorithm

### nixon_diamond_anon  (clean@1=0%, exact@k=no)
On 'nixon_diamond_anon', the answer is not a solution: no stable extension accepts every positive example and no negative one. Taken one at a time, it gets 2 of 5 posed examples wrong (v(d), v(b)). It differs from the algorithm's answer on: c_alpha_0: model wrote ['nothing'], the algorithm has ['c_alpha_0(X) :- p(X), w(X).']; p1: model wrote ['nothing'], the algorithm has ['p1(X) :- r(X), alpha_0(X).']; v: model wrote ['nothing'], the algorithm has ['v(X) :- q(X).'].

### flies_anon  (clean@1=0%, exact@k=no)
On 'flies_anon', the answer is not a solution: no stable extension accepts every positive example and no negative one. Taken one at a time, it gets 1 of 3 posed examples wrong (t(a)). It differs from the algorithm's answer on: c_alpha_0: model wrote ['nothing'], the algorithm has ['c_alpha_0(X) :- q(X).']; t: model wrote ['nothing'], the algorithm has ['t(X) :- p(X), alpha_0(X).'].

### tax_law_anon  (clean@1=0%, exact@k=no)
On 'tax_law_anon', the answer is not a solution: no stable extension accepts every positive example and no negative one. Taken one at a time, it gets 2 of 3 posed examples wrong (u(a), u(c)). It differs from the algorithm's answer on: c_alpha_0: model wrote ['nothing'], the algorithm has ['c_alpha_0(X) :- dom(X), alpha_1(X).']; c_alpha_1: model wrote ['nothing'], the algorithm has ['c_alpha_1(X) :- p(X), alpha_0(X).']; u: model wrote ['nothing'], the algorithm has ['u(X) :- p(X), alpha_0(X).', 'u(X) :- q(X).'].

### t1_mono_0000_anon  (clean@1=0%, exact@k=no)
On 't1_mono_0000_anon', the answer is not a solution: no stable extension accepts every positive example and no negative one. Taken one at a time, it gets 3 of 5 posed examples wrong (v(a), v(b), v(d)). It differs from the algorithm's answer on: v: model wrote ['nothing'], the algorithm has ['v(X) :- p(X).']. Off the posed examples, it decides 0% of the example predicate's atoms as the algorithm's answer does.

### t2_defeas_0000_anon  (clean@1=0%, exact@k=no)
On 't2_defeas_0000_anon', the answer is not a solution: no stable extension accepts every positive example and no negative one. Taken one at a time, it gets 3 of 6 posed examples wrong (v(d), v(c), v(b)). It differs from the algorithm's answer on: c_alpha_0: model wrote ['nothing'], the algorithm has ['c_alpha_0(X) :- q(X).']; v: model wrote ['nothing'], the algorithm has ['v(X) :- p(X), alpha_0(X).'].

### t3_noise_0000_anon  (clean@1=0%, exact@k=no)
On 't3_noise_0000_anon', the answer is not a solution: no stable extension accepts every positive example and no negative one. Taken one at a time, it gets 3 of 6 posed examples wrong (p1(b), p1(c), p1(d)). It differs from the algorithm's answer on: c_alpha_0: model wrote ['nothing'], the algorithm has ['c_alpha_0(X) :- q(X).']; p1: model wrote ['nothing'], the algorithm has ['p1(X) :- p(X), alpha_0(X).']. Off the posed examples, it decides 0% of the example predicate's atoms as the algorithm's answer does.

### t4_domain_0000_anon  (clean@1=0%, exact@k=no)
On 't4_domain_0000_anon', the answer is not a solution: no stable extension accepts every positive example and no negative one. Taken one at a time, it gets 4 of 8 posed examples wrong (v(b), v(g), v(e), v(f)). It differs from the algorithm's answer on: c_alpha_0: model wrote ['nothing'], the algorithm has ['c_alpha_0(X) :- q(X).']; v: model wrote ['nothing'], the algorithm has ['v(X) :- p(X), alpha_0(X).']. Off the posed examples, it decides 0% of the example predicate's atoms as the algorithm's answer does.

### t5_twopath_0000_anon  (clean@1=0%, exact@k=no)
On 't5_twopath_0000_anon', the answer is not a solution: no stable extension accepts every positive example and no negative one. Taken one at a time, it gets 4 of 8 posed examples wrong (p1(d), p1(c), p1(f), p1(b)). It differs from the algorithm's answer on: c_alpha_0: model wrote ['nothing'], the algorithm has ['c_alpha_0(X) :- s(X).']; c_alpha_1: model wrote ['nothing'], the algorithm has ['c_alpha_1(X) :- r(X).']; p1: model wrote ['nothing'], the algorithm has ['p1(X) :- p(X), alpha_1(X).', 'p1(X) :- q(X), alpha_0(X).'].
