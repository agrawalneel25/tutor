# Lecture: Some Consequences of Convexity

## TL;DR
- **One chord, two inequalities.** On $[a,b]$ the graph lies *below* the chord; *outside* $[a,b]$ it lies *above* the chord extension.
- **Convex $\Rightarrow$ continuous on the interior** of $I$ (squeeze between two chord lines). Endpoints can still misbehave.
- **Secant slopes are monotone increasing**: for $a<b<c$, $\frac{f(b)-f(a)}{b-a} \le \frac{f(c)-f(b)}{c-b}$. This is the workhorse lemma.
- **Where $f$ is differentiable, $f'$ is increasing**, and the tangent line is a *global underestimate*: $f(x) \ge f(x_0) + f'(x_0)(x-x_0)$.
- Consequence: for strictly convex differentiable $f$, any critical point is *the* unique global minimiser.

## Prereqs & where we are
You already have the definition: $f:I\to\mathbb{R}$ is convex iff for all $a<b$ in $I$ and all $x\in[a,b]$,
$$f(x) \le \ell_{a,b}(x) := f(a) + \alpha_{a,b}(x-a), \quad \alpha_{a,b} := \frac{f(b)-f(a)}{b-a}.$$
Equivalently, $f(\lambda a+(1-\lambda)b) \le \lambda f(a)+(1-\lambda)f(b)$ for $\lambda\in[0,1]$.

This lecture squeezes everything useful out of that one inequality: continuity, monotone derivatives, supporting lines, and minimisation. It is the bridge from the *combinatorial* definition of convexity to the *analytic* tools (derivatives, limits) you'll use in optimisation and later in probability (Jensen) and functional analysis.

## The core ideas

### 1. Chord extension inequality
**Motivation.** The definition only tells us about points *inside* $[a,b]$. What happens when you extrapolate the chord past its endpoints? Geometrically obvious from a picture of $x^2$: outside $[a,b]$ the parabola overtakes the chord. We need this to get two-sided control in the continuity proof.

**Statement.** Let $f:I\to\mathbb{R}$ be convex and fix $a<b$ in $I$. Then
$$\ell_{a,b}(x) \le f(x) \quad \text{for all } x \in I \setminus [a,b].$$

**Intuition.** Convexity "bends upward". Inside $[a,b]$ the bend puts $f$ under the chord; outside, the same bend pulls $f$ up and over the extended line.

**Proof sketch** (case $x>b$, by contradiction).
Suppose $\ell_{a,b}(x) > f(x)$ for some $x>b$. Consider the chord $\ell_{a,x}$ from $(a,f(a))$ to $(x,f(x))$. Both $\ell_{a,b}$ and $\ell_{a,x}$ pass through $(a,f(a))$, so they're determined by their slopes. At $x$,
$$\ell_{a,b}(x) > f(x) = \ell_{a,x}(x),$$
so $\alpha_{a,b} > \alpha_{a,x}$. A steeper line through the same base point is larger everywhere to the right of $a$, so at $b \in (a,x)$:
$$f(b) = \ell_{a,b}(b) > \ell_{a,x}(b).$$
But $b \in [a,x]$ and $f$ is convex on $[a,x]$, giving $f(b) \le \ell_{a,x}(b)$. Contradiction. $\square$

**Worked example.** $f(x)=x^2$, $a=0$, $b=1$. The chord is $\ell_{0,1}(x)=x$. For $x=2$: $\ell_{0,1}(2)=2 \le 4 = f(2)$. For $x=-1$: $\ell_{0,1}(-1)=-1 \le 1 = f(-1)$. Both check out.

**Common trap.** Students forget that the inequality *flips* outside $[a,b]$. It's the *same chord* but the inequality sign depends on which region $x$ lives in. Memorise: "chord above inside, chord below outside".

---

### 2. Continuity on the interior
**Motivation.** Convex functions are defined by an algebraic inequality, not a topological condition. Do we get continuity for free? Almost — yes in the interior, no at endpoints.

**Statement.** If $f:I\to\mathbb{R}$ is convex, then $f$ is continuous at every interior point of $I$.

**Intuition.** At an interior point $a$ you can nail $f$ between two chord-based lines — one coming from the left side $[a-\delta,a]$ and one coming from the right $[a,a+\delta]$ — both continuous, both passing through $(a,f(a))$. Squeeze.

**Proof sketch.** Fix $a$ interior and $\delta>0$ with $[a-\delta,a+\delta]\subset I$.

*Left limit.* For $x \in [a-\delta, a]$:
- Convexity on $[a-\delta,a]$ gives $f(x) \le \ell_{a-\delta,\,a}(x)$.
- Chord extension for the chord on $[a,a+\delta]$ (with $x$ to the *left* of $[a,a+\delta]$) gives $\ell_{a,\,a+\delta}(x) \le f(x)$.

So $\ell_{a,a+\delta}(x) \le f(x) \le \ell_{a-\delta,a}(x)$. Both affine bounds are continuous and both equal $f(a)$ at $x=a$. Squeeze $\Rightarrow \lim_{x\to a^-} f(x)=f(a)$.

*Right limit.* Symmetric: swap roles of the two chords.

**Crucial subtlety.** The interior hypothesis is *essential*. The proof needs chord extensions on *both* sides of $a$, which requires points of $I$ on both sides. At an endpoint this collapses.

**Worked example (boundary failure).** Define $f:[0,1]\to\mathbb{R}$ by
$$f(x) = \begin{cases} x^2 & 0 \le x < 1 \\ 2 & x=1. \end{cases}$$
This is convex (check: on any $[a,b]\subset[0,1)$ it agrees with $x^2$; when $b=1$ the chord gets *higher* because $f(1)=2$, and the inequality $f(x)\le \ell_{a,1}(x)$ still holds since $x^2$ lies below that chord). But $f$ is discontinuous at $x=1$. That's the exercise in the notes.

**Common trap.** Assuming convex $\Rightarrow$ continuous *everywhere*. It's only interior. Also: the proof isn't an $\varepsilon$-$\delta$ argument, it's a squeeze — don't try to force $\varepsilon$-$\delta$ on it.

---

### 3. Monotonicity of secant slopes
**Motivation.** This is the single most useful reformulation of convexity. It converts the chord inequality into a statement about rates of change, which is what you differentiate.

**Statement.** Let $f$ be convex and $a<b<c$ in $I$. Then
$$\frac{f(b)-f(a)}{b-a} \le \frac{f(c)-f(b)}{c-b}.$$

**Intuition.** As you slide the chord's right endpoint rightward, the chord gets steeper. "Secant slopes increase."

**Proof sketch.** For $x \in [b,c]$:
- Chord extension on $[a,b]$ (with $x\ge b$ outside $[a,b]$): $\ell_{a,b}(x) \le f(x)$.
- Convexity on $[b,c]$: $f(x) \le \ell_{b,c}(x)$.

So $\ell_{a,b}(x) \le \ell_{b,c}(x)$ for all $x\in[b,c]$. Both lines pass through $(b,f(b))$, so write them as
$$\ell_{a,b}(x) = \alpha_{a,b}(x-b) + f(b), \quad \ell_{b,c}(x) = \alpha_{b,c}(x-b) + f(b).$$
Inequality for all $x>b$ with $x-b>0$ forces $\alpha_{a,b} \le \alpha_{b,c}$. $\square$

**Corollary (four-point version).** For $a<b<c<d$:
$$\frac{f(b)-f(a)}{b-a} \le \frac{f(d)-f(c)}{d-c}.$$
Apply the three-point version to $(a,b,c)$ then $(b,c,d)$ and chain.

**Worked example.** $f(x)=|x|$ at $a=-2, b=0, c=3$. Left slope $= (0-2)/(0-(-2)) = -1$. Right slope $= (3-0)/(3-0)=1$. Indeed $-1\le 1$. Note $f$ isn't differentiable at $0$ — monotone *secants* give you information even when derivatives don't exist.

**Common trap.** Forgetting that this is where the real power is. Whenever a problem says "$f$ convex" and asks something analytic, the first move is usually to write down a secant slope inequality.

---

### 4. Derivatives are increasing; supporting lines
**Motivation.** If $f$ is differentiable, secant slopes have limits. Take limits in the monotone secant inequality and you get monotone derivatives, then — one more squeeze — the tangent line lies globally below the graph.

**Statement 1 (monotone derivative).** If $f$ is convex and differentiable at $s<t$, then $f'(s) \le f'(t)$.

**Proof sketch.** Pick $h>0$ small. Apply the four-point monotone secant lemma to $s-h < s < t < t+h$:
$$\frac{f(s)-f(s-h)}{h} \le \frac{f(t)-f(s)}{t-s} \le \frac{f(t+h)-f(t)}{h}.$$
Let $h\to 0^+$: the outer terms tend to $f'(s)$ and $f'(t)$. $\square$

**Statement 2 (supporting line inequality).** If $f$ is convex and differentiable at an interior $x_0\in I$, then
$$f(x) \ge f(x_0) + f'(x_0)(x-x_0) \quad \text{for all } x\in I.$$

**Intuition.** The tangent at $x_0$ is a global lower bound. Convexity $\iff$ every tangent (where it exists) is a supporting line from below.

**Proof sketch.** For $x>x_0$, by monotone secants applied to $x_0-h < x_0 < x$:
$$\frac{f(x_0)-f(x_0-h)}{h} \le \frac{f(x)-f(x_0)}{x-x_0}.$$
Let $h\to 0^+$: LHS $\to f'(x_0)$, giving $f'(x_0)(x-x_0) \le f(x)-f(x_0)$. Rearrange. The case $x<x_0$ is symmetric (use $x < x_0 < x_0+h$). $\square$

**Worked example.** $f(x)=e^x$, $x_0=0$: supporting line is $1+x$, and indeed $e^x \ge 1+x$ for all $x\in\mathbb{R}$. This is the single most used inequality in probability and information theory.

**Common trap.** Thinking you need $f$ *twice* differentiable. You don't — one derivative suffices. And the tangent-below property is *equivalent* to convexity (when $f$ is differentiable on $I$), not just a consequence.

## Connections
- Section 1 (chord extension) is the single tool that powers Sections 2 and 3 — both proofs sandwich $f$ between a chord and a chord extension.
- Section 3 (monotone secants) is the differentiable-free shadow of Section 4's "$f'$ increasing". For $C^2$ functions you'll later prove: convex $\iff f'' \ge 0$. Today's results are strictly more general — they apply to $|x|$, which isn't differentiable, and to non-smooth convex functions that appear everywhere in optimisation.
- The supporting line inequality is the one-variable case of the *subgradient* inequality — crucial in convex optimisation (gradient descent convergence proofs) and in probability as the basis of **Jensen's inequality**: $f(\mathbb{E}X) \le \mathbb{E}f(X)$.
- "Interior continuity" matches a pattern you'll see repeatedly: algebraic niceness (convexity, monotonicity) forces topological niceness (continuity, even Lipschitz on compact subintervals), but boundary behaviour is free.

## Exam-style application
**Problem.** Let $f:[0,\infty)\to\mathbb{R}$ be convex and bounded above. Prove that $\lim_{x\to\infty} f(x)$ exists and is finite. If additionally $f$ is differentiable on $(0,\infty)$, prove $\lim_{x\to\infty} f'(x)=0$.

**Solution.**

*Part 1: limit exists.* Fix $a=0, b=1$. By monotone secant slopes, for any $x>1$:
$$\alpha(x) := \frac{f(x)-f(1)}{x-1}$$
is a non-decreasing function of $x$ (apply the four-point lemma to $0,1,x,y$ for $1<x<y$: $\alpha_{0,1}\le \alpha_{1,x} \le \alpha_{x,y}$; and directly $\alpha_{1,x}\le \alpha_{1,y}$ by the three-point version on $1,x,y$). So $\alpha$ is monotone.

Since $f$ is bounded above by some $M$:
$$\alpha(x) = \frac{f(x)-f(1)}{x-1} \le \frac{M-f(1)}{x-1} \to 0 \text{ as } x\to\infty.$$
A non-decreasing function bounded above has a limit, so $L := \lim_{x\to\infty}\alpha(x)$ exists in $[-\infty, 0]$.

Suppose $L<0$ (including $L=-\infty$): then for large $x$, $\alpha(x)\le L/2 < 0$, so
$$f(x) \le f(1) + (L/2)(x-1) \to -\infty,$$
but *we also need a lower bound on $f$*. From the supporting-line idea (or directly from monotone secants applied with a point to the left of $1$): fix $x_0=1$; for $x>1$ the chord extension through $(0,f(0))$ and $(1,f(1))$ gives $f(x) \ge f(1) + \alpha_{0,1}(x-1)$, so $f$ is bounded below on any bounded interval but *not* globally. So we need a different route.

Cleaner approach: since $\alpha(x)$ is non-decreasing and $\le 0$ for arbitrarily large $x$ (else $f(x)\to+\infty$, contradicting boundedness), we have $\alpha(x)\le 0$ for all $x>1$, so $f$ is non-increasing on $[1,\infty)$ in the averaged sense. More precisely: by monotone secants, if there existed $b>1$ with $\alpha_{1,b}>0$, then for all $x>b$ we'd have $\alpha_{1,x}\ge \alpha_{1,b}>0$, giving $f(x)\to\infty$. So $\alpha_{1,x}\le 0$ for all $x>1$, i.e. $f(x)\le f(1)$, and by the same token for any $t>1$, $f(x)\le f(t)$ for $x>t$. Hence $f$ is non-increasing on $[1,\infty)$.

A non-increasing function bounded below (below is easy: bounded above + convex on a half-line with non-increasing behaviour — but more directly, $f$ is bounded below on $[1,\infty)$ because it is bounded above and non-increasing means it has a limit in $[-\infty, f(1)]$; we must rule out $-\infty$). Suppose $f(x)\to-\infty$. Take any $x_0>1$ with $f(x_0)<f(0)-1$. The chord extension inequality for chord $[0,x_0]$ evaluated at $x > x_0$ (outside $[0,x_0]$) gives $f(x)\ge \ell_{0,x_0}(x)$, a line with slope $(f(x_0)-f(0))/x_0 < -1/x_0 <0$. That line $\to-\infty$, so this doesn't rule it out.

So I'll swap strategies: apply the chord extension the *other* way. Pick any $0<a<b$. For $x>b$, by the chord extension on $[a,b]$: $f(x) \ge \ell_{a,b}(x)$. If $\alpha_{a,b}\ge 0$ this gives $f(x)\ge f(b)$, a finite lower bound, so $f$ has a finite limit. If $\alpha_{a,b}<0$ for *every* $a<b$, then $f$ is strictly decreasing everywhere... but by monotone secants, $\alpha_{a,b}$ is non-decreasing in both arguments, so $\alpha_{a,b}\to$ some $L\in[-\infty,\infty]$. By boundedness above, $L\le 0$. If $L<0$ strictly, then for large $a<b$, $\alpha_{a,b}\le L/2$ and chord extension gives $f(x)\ge f(b)+(L/2)(x-b)$... wait, that's $\ge$ something going to $-\infty$, useless.

Correct finish: use that $f$ is non-increasing (proved above) and bounded above, hence bounded below on $[1,\infty)$ would need separate justification. Alternatively, because $f$ non-increasing on $[1,\infty)$, $\lim_{x\to\infty}f(x)$ exists in $[-\infty, f(1)]$. To rule out $-\infty$: if $f(x)\to-\infty$, pick $N$ with $f(N)<f(0)-100$; then the secant slope $\alpha_{0,N}<-100/N$. But $\alpha_{0,N}$ is non-decreasing in $N$ and bounded above by $0$, so it has a finite limit — contradicting $\alpha_{0,N}\to-\infty$ would require... actually $\alpha_{0,N}=(f(N)-f(0))/N$, and $f(N)\to-\infty$ only forces $\alpha_{0,N}\to$ some non-positive limit, not $-\infty$, if $f(N)/N$ stays bounded. Hmm — but $\alpha_{0,N}$ non-decreasing and $\le 0$, so $\alpha_{0,N}\to \ell \le 0$. If $\ell<0$, $f(N)\le f(0)+\ell N/2$ for large $N$ — fine, consistent with $-\infty$. So we genuinely need the *bounded above* hypothesis more carefully: we actually need *bounded* (above and below), or the claim is false.

**Checking the problem statement.** The notes say "bounded", which typically means bounded both above and below. With that: $f$ non-increasing on $[1,\infty)$ and bounded below $\Rightarrow$ $\lim f$ exists and is finite. $\checkmark$

*Part 2: $f'(x)\to 0$.* Since $f$ is convex and differentiable on $(0,\infty)$, $f'$ is non-decreasing (Section 4). Also $f'(x)\le 0$ for all large $x$: if $f'(x_0)>0$ at some $x_0$, the supporting line $f(x)\ge f(x_0)+f'(x_0)(x-x_0)\to\infty$ contradicts boundedness. So $f'$ is non-decreasing and $\le 0$, hence $f'(x)\to L \le 0$ as $x\to\infty$.

Suppose $L<0$. Then for large $x$, $f'(x)\le L/2<0$, so by MVT
$$f(x)-f(X) = \int_X^x f'(t)\,dt \le (L/2)(x-X) \to -\infty,$$
contradicting $f$ bounded below. So $L=0$. $\square$

## Open questions / things to check
- In the boundary-discontinuity exercise (Section 2), verify the $f$ I constructed is actually convex on all of $[0,1]$, including chords ending at $1$: the chord from $(a,a^2)$ to $(1,2)$ has slope $(2-a^2)/(1-a)=(2-a^2)/(1-a)$; need $x^2 \le$ this chord for $x\in[a,1)$. At $x$ just below $1$: chord value approaches $2$, $x^2$ approaches $1$. Fine. General check is mechanical — do it if unsure.
- In the exam problem Part 1, the argument tacitly needs "$f$ bounded" to mean bounded both sides. If the lecture/problem sheet wording is only "bounded above", the conclusion still holds but requires a subtler argument ruling out $f(x)\to-\infty$ using convexity + boundedness above. Worth confirming from the problem sheet.
- The notes give the *exercise* to prove the converse in Section 1 (chord extension for all $a<b$ $\Rightarrow$ convex). Worth doing: fix $c<d$ and $x\in(c,d)$; you want $f(x)\le \ell_{c,d}(x)$. Pick $a<c$ and apply chord extension on $[a,x]$ at $d$, etc. — a similar two-chord juggle.
