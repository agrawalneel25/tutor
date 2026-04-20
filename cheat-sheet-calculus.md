# MATH40004 Calculus & Applications — Term 2 Cheat Sheet

---

## 0. FOURIER TRANSFORMS (brief — covered term 2 lectures)

**Definition:**
  f_hat(omega) = integral_{-inf}^{inf} f(x) e^{-i*omega*x} dx

**Inverse:**
  f(x) = (1/2*pi) * integral f_hat(omega) e^{i*omega*x} d_omega

**Cosine / sine transforms** (for x >= 0):
  f_hat_c(omega) = integral_0^inf f(x) cos(omega*x) dx   [use when f even]
  f_hat_s(omega) = integral_0^inf f(x) sin(omega*x) dx   [use when f odd]

  If f even:  f_hat(omega) = 2 * f_hat_c(omega)
  If f odd:   f_hat(omega) = -2i * f_hat_s(omega)

**Key pair to memorise:**
  f(x) = e^{-a|x|}, a > 0  =>  f_hat(omega) = 2a / (a^2 + omega^2)

**Properties (exam-tested):**
| Property | Formula |
|---|---|
| Linearity | F{af+bg} = a*f_hat + b*g_hat |
| Scaling (a>0) | F{f(ax)} = (1/a)*f_hat(omega/a) |
| Shift in x | F{f(x-x0)} = e^{-i*omega*x0} * f_hat(omega) |
| Shift in freq | F{e^{i*omega0*x} f(x)} = f_hat(omega - omega0) |
| Symmetry | F{f_hat(x)} = 2*pi*f(-omega) |
| Derivative | F{d^n f/dx^n} = (i*omega)^n * f_hat(omega) |
| x*f(x) | F{x*f(x)} = i * f_hat'(omega) |
| Conjugate | F{f*(x)} = [f_hat(-omega)]* |

**Convolution:** (f*g)(x) = integral_{-inf}^{inf} f(x-u)g(u) du
  Convolution theorem: F{f*g} = f_hat(omega) * g_hat(omega)
  Inverse convolution: F{f(x)g(x)} = (1/2*pi) * f_hat(omega) * g_hat(omega)

**Energy (Parseval):**
  (1/2*pi) * integral |f_hat(omega)|^2 d_omega = integral [f(x)]^2 dx

**Dirac delta:**
  delta(x) = limit of rectangle with unit area, width -> 0
  Sifting: integral g(x) delta(x-a) dx = g(a)
  F{delta(x)} = 1;  therefore  delta(x) = (1/2*pi) integral e^{+/-i*omega*x} d_omega

---

## 1. FIRST-ORDER ODEs

### Recognition table

| Type | Form | Method |
|---|---|---|
| Separable | dy/dx = F1(x)*F2(y) | Separate: integral dy/F1(y) = integral F2(x) dx |
| Linear | dy/dx + p(x)y = q(x) | Integrating factor I(x) = e^{integral p(x)dx} |
| Homogeneous | dy/dx = F(y/x) | Substitute u = y/x |
| Bernoulli | dy/dx + p(x)y = q(x)*y^n | Substitute u = y^{1-n} |
| Exact | F(x,y)dx + G(x,y)dy = 0, with dF/dy = dG/dx | Find u: du/dx = F, du/dy = G |

**Exam tip:** Always check which type first. Separable is easiest; if linear fails, try Bernoulli (look for y^n on RHS).

### Linear first-order detail
  dy/dx + p(x)y = q(x)
  I(x) = e^{integral p(x)dx}
  d/dx [I(x)*y] = I(x)*q(x)
  => y = (1/I(x)) * integral I(x)*q(x) dx + C/I(x)

### Exact ODEs
  F(x,y)dx + G(x,y)dy = 0 is exact iff dF/dy = dG/dx
  Solution: find u(x,y) where du/dx = F, du/dy = G (integrate one, compare the other)
  General solution: u(x,y) = constant

**If not exact:** try integrating factor lambda(x) or lambda(y).
  For lambda(x): (dF/dy - dG/dx)/G must be a function of x only.
  Then d(lambda)/dx = lambda * (dF/dy - dG/dx)/G  =>  solve this ODE for lambda.

---

## 2. SECOND-ORDER ODEs — SPECIAL CASES

| Form | Substitution | Result |
|---|---|---|
| d^2y/dx^2 = F(x) | integrate twice | direct |
| d^2y/dx^2 = F(x, dy/dx) | u = dy/dx | du/dx = F(x,u), 1st order |
| d^2y/dx^2 = F(y) | u = dy/dx, then u*du/dy = F(y) | energy method |
| d^2y/dx^2 = F(y, dy/dx) | u = dy/dx, u*du/dy = F(y,u) | 1st order in u(y) |

---

## 3. LINEAR ODEs WITH CONSTANT COEFFICIENTS

**General solution = complementary function + particular integral:**
  y_GS = y_CF + y_PI

**Step 1 — y_CF:** Solve auxiliary equation by substituting y = e^{lambda*x}:
  alpha_k * lambda^k + ... + alpha_1 * lambda + alpha_0 = 0

| Roots | y_CF |
|---|---|
| Real, distinct lambda_1, lambda_2 | c1*e^{lambda1*x} + c2*e^{lambda2*x} |
| Complex lambda = a +/- ib | e^{a*x}*(c1*cos(b*x) + c2*sin(b*x)) |
| Repeated lambda | c1*e^{lambda*x} + c2*x*e^{lambda*x} |

**Step 2 — y_PI:** Ansatz (method of undetermined coefficients):
| RHS f(x) | Try |
|---|---|
| polynomial degree n | polynomial degree n (one higher if in y_CF) |
| e^{bx} (b not a root) | A*e^{bx} |
| e^{bx} (b is a root, multiplicity m) | A*x^m*e^{bx} |
| cos(omega*x) or sin(omega*x) | A*cos(omega*x) + B*sin(omega*x) |

**Euler-Cauchy:** x^k * d^k y/dx^k + ... = f(x)
  Substitute x = e^z to get constant-coefficient ODE in y(z).

---

## 4. SYSTEMS OF LINEAR ODEs

**Matrix form:** dy/dt = A*y + g(t),  y, g column vectors, A matrix.

### Eigenvalue method (A diagonalisable, distinct eigenvalues)

1. Find eigenvalues: det(A - lambda*I) = 0
2. Find eigenvectors v1, v2 for each lambda
3. y_CF(t) = c1*e^{lambda1*t}*v1 + c2*e^{lambda2*t}*v2

**Repeated eigenvalue, A non-diagonalisable:** use Jordan normal form.
Find w2 such that (A - lambda*I)*w2 = v1, then:
  y_GS(t) = c1*e^{lambda*t}*v1 + c2*(t*e^{lambda*t}*v1 + e^{lambda*t}*w2)

**Particular integral:** If g(t) is constant, y_PI = -A^{-1}*g. Otherwise use ansatz.

---

## 5. PHASE PLANE ANALYSIS — 2D LINEAR SYSTEMS

dy/dt = A*y,  tau = trace(A),  Delta = det(A)

Eigenvalues: lambda = (tau +/- sqrt(tau^2 - 4*Delta)) / 2

### Trace-determinant classification (the tau-Delta plane)

```
Delta ^
      |        stable spiral    unstable spiral
      |    (tau<0, Delta>tau^2/4)  (tau>0, Delta>tau^2/4)
      |        \     centre      /
      |         \  (tau=0)      /
      |          \             /    curve: Delta = tau^2/4
      |   stable  \-----------/ unstable
      |   node     \         /  node
      |  (tau<0)    \       / (tau>0)
      |              \     /
 -----+--------------\---/----------> tau
      |               \ /
      |    saddle point (Delta < 0)
      |
```

| Region | Name | Stability | Trajectories |
|---|---|---|---|
| Delta < 0 | Saddle point | unstable | hyperbolic, 2 straight-line separatrices |
| Delta > 0, Delta > tau^2/4, tau < 0 | Stable spiral | asymptotically stable | inward spirals |
| Delta > 0, Delta > tau^2/4, tau > 0 | Unstable spiral | unstable | outward spirals |
| Delta > 0, Delta > tau^2/4, tau = 0 | Centre | Lyapunov stable (not asymptotic) | closed ellipses |
| 0 < Delta < tau^2/4, tau < 0 | Stable node | asymptotically stable | curves in along slower eigenvector |
| 0 < Delta < tau^2/4, tau > 0 | Unstable node | unstable | curves out along faster eigenvector |
| Delta = tau^2/4, A diagonalisable | Star node | stable/unstable | straight lines radially |
| Delta = tau^2/4, A non-diag | Degenerate node | stable/unstable | bent trajectories |

**How to sketch a phase portrait:**
1. Compute tau and Delta, locate in plane above.
2. Find eigenvalues + eigenvectors -> draw invariant lines.
3. Determine direction along each invariant line (sign of lambda).
4. Sketch general trajectories asymptotically parallel to slowest-decaying eigenvector.
5. Add directional arrows; label eigenvector lines.
6. For PS5: to find y(x), divide dy/dt by dx/dt to get dy/dx, then solve the 1D ODE.

**Exam tip:** Always draw arrows on the eigenvector lines and state whether the fixed point is stable/unstable/Lyapunov stable. Marks are lost without arrows.

---

## 6. NONLINEAR ODEs — STABILITY OF FIXED POINTS (LINEARISATION)

For dy/dt = f(y), a fixed point y* satisfies f(y*) = 0.

**Linear stability:** let eta = y - y*  (small perturbation)
  d(eta)/dt = f'(y*) * eta + O(eta^2)
  => eta(t) ~ e^{f'(y*)*t}
  
  f'(y*) < 0 => stable (asymptotically)
  f'(y*) > 0 => unstable
  f'(y*) = 0 => inconclusive (need higher order)

**For 2D nonlinear systems:** dy/dt = F(y), fixed point y*:
  Linearise: delta_y' = J(y*) * delta_y  where  J = Jacobian = [dFi/dyj] evaluated at y*
  Then classify using tau = trace(J), Delta = det(J) as in Section 5.

**Exam tip:** For PS6 Q2 (competing populations), find nullclines (set each equation to zero), locate intersections as fixed points, compute J at each, classify.

---

## 7. 1D BIFURCATIONS

dy/dt = f(y; r),  r = bifurcation parameter.

**Method:**
1. Find fixed points: f(y*; r) = 0
2. Determine stability: sign of df/dy at each y*
3. Draw bifurcation diagram: y* vs r (solid = stable, dashed = unstable)
4. Add flow arrows on each branch

### Three canonical types

**Saddle-node (fold):**
  Normal form: dy/dt = r + y^2
  r < 0: two fixed points (stable at -sqrt(-r), unstable at +sqrt(-r))
  r = 0: one half-stable fixed point at y=0
  r > 0: no fixed points
  Mechanism: creation/destruction of fixed points. Look for it when two branches meet at a parabolic tip.

**Transcritical:**
  Normal form: dy/dt = r*y - y^2
  Two fixed points for all r (at y=0 and y=r), but they exchange stability at r=0.
  y=0 stable for r<0, unstable for r>0; y=r unstable for r<0, stable for r>0.
  Mechanism: fixed point that cannot be destroyed, only changes stability.

**Supercritical pitchfork:**
  Normal form: dy/dt = r*y - y^3
  r < 0: one stable fixed point (y=0)
  r = 0: one (weakly) stable fixed point (y=0)
  r > 0: y=0 unstable, two new stable fixed points at y = +/-sqrt(r)
  Mechanism: spontaneous symmetry breaking. Equation invariant under y -> -y.
  Physical example: buckling rod — straight position becomes unstable, rod buckles left or right.

**Subcritical pitchfork:**
  Normal form: dy/dt = r*y + y^3
  r > 0: one unstable fixed point (y=0)
  r < 0: y=0 stable, two unstable fixed points at y = +/-sqrt(-r)
  Much more dangerous — trajectories can escape to infinity.
  Diagram is pitchfork pointing in opposite direction to supercritical.

**Exam tip — sketching bifurcation diagrams:**
- Always add flow arrows (up/down on the real line for 1D systems).
- The question will often say "classify the bifurcation" — name it explicitly.
- For subtle cases (e.g. dy/dt = r*y + y^3 - y^5), split f into two parts and sketch intersection graphically (technique from L16 transcript).

**Sketching technique for complex RHS:** Write f(y;r) = r*h1(y) - h2(y). Plot h2(y) once (fixed curve). Fixed points are where h2 = r*h1, i.e. intersections of h2 with a line/curve that shifts with r. As r varies, count intersections.

---

## 8. PARTIAL DIFFERENTIATION

**Definition:** partial f/partial x_i = lim_{h->0} [f(...,x_i+h,...) - f(...)]/h
(all other variables held constant)

**Schwarz/Clairaut theorem:** If second partials continuous:
  partial^2 f / (partial x partial y) = partial^2 f / (partial y partial x)

**Total differential:** df = (partial f/partial x) dx + (partial f/partial y) dy

**Chain rule — f(x,y) with x=x(t), y=y(t):**
  df/dt = (partial f/partial x)(dx/dt) + (partial f/partial y)(dy/dt)

**Chain rule — f(x,y) with x=x(s,t), y=y(s,t):**
  partial f/partial s = (partial f/partial x)(partial x/partial s) + (partial f/partial y)(partial y/partial s)
  [same for t]

**Implicit differentiation — F(x,y,z)=0:**
  partial z/partial x = -(partial F/partial x) / (partial F/partial z)
  partial z/partial y = -(partial F/partial y) / (partial F/partial z)

**Reciprocity theorem (thermodynamics PS7 Q2e):**
  (partial p/partial V)_T * (partial V/partial T)_p * (partial T/partial p)_V = -1

---

## 9. TAYLOR EXPANSION FOR f(x,y)

  f(x0+Dx, y0+Dy) = f(x0,y0) + [grad f]^T . [Dx,Dy]^T + (1/2)[Dx,Dy] H [Dx,Dy]^T + ...

where:
  grad f = [partial f/partial x,  partial f/partial y]^T  (evaluated at (x0,y0))

  H = Hessian = | partial^2 f/partial x^2       partial^2 f/(partial x partial y) |
                | partial^2 f/(partial y partial x)  partial^2 f/partial y^2       |

**Error estimation:** If Dx is uncertainty in x, Dy uncertainty in y:
  |Df| <= |partial f/partial x| |Dx| + |partial f/partial y| |Dy|
  For percentage error: |Df/f| <= |partial ln f/partial x| |Dx| + |partial ln f/partial y| |Dy|

**Exam tip (PS7 Q3 — projectile):** For R = U^2*sin(2*theta)/g, use total differential to get absolute errors; divide by R for percentage.

---

## 10. STATIONARY POINTS OF f(x,y) — HESSIAN CLASSIFICATION

**Step 1:** Find stationary points by solving simultaneously:
  partial f/partial x = 0  AND  partial f/partial y = 0

**Step 2:** Evaluate Hessian H at each stationary point. Compute:
  tau = trace(H) = partial^2 f/partial x^2 + partial^2 f/partial y^2
  Delta = det(H) = (partial^2 f/partial x^2)(partial^2 f/partial y^2) - (partial^2 f/(partial x partial y))^2

| Delta | tau | Type |
|---|---|---|
| Delta > 0, tau > 0 | both eigenvalues positive | Local minimum |
| Delta > 0, tau < 0 | both eigenvalues negative | Local maximum |
| Delta < 0 | eigenvalues opposite sign | Saddle point |
| Delta = 0 | — | Degenerate (inconclusive) |

**Sketch procedure (PS8 Q6):**
1. Find zero contours: set f(x,y) = 0, sketch the curves
2. Find stationary points and classify
3. Determine sign of f in each region bounded by zero contours
4. Sketch level curves around stationary points

---

## 11. EXACT ODEs + INTEGRATING FACTORS (PS8 Q5)

**Test:** F(x,y)dx + G(x,y)dy = 0 is exact iff
  partial F/partial y = partial G/partial x

**If exact — find solution u(x,y) = C:**
  partial u/partial x = F  => u = integral F dx + phi(y)
  partial u/partial y = G  => differentiate u w.r.t. y, match to G to find phi'(y), integrate

**If not exact — find integrating factor:**
  Try lambda = lambda(x):  (partial F/partial y - partial G/partial x)/G = function of x only
    => d(lambda)/dx = lambda * [(partial F/partial y - partial G/partial x)/G]
  Try lambda = lambda(y):  (partial G/partial x - partial F/partial y)/F = function of y only
    => d(lambda)/dy = lambda * [(partial G/partial x - partial F/partial y)/F]
  Then solve the new (exact) equation.

---

## 12. PARTIAL DIFFERENTIAL EQUATIONS (brief)

**Laplace equation:** partial^2 u/partial x^2 + partial^2 u/partial y^2 = 0
  In polar: partial^2 u/partial r^2 + (1/r)(partial u/partial r) + (1/r^2)(partial^2 u/partial theta^2) = 0
  Radially symmetric solution u(r): r*u'' + u' = 0 => u = A*ln(r) + B

**Wave equation:** partial^2 u/partial x^2 - (1/c^2) partial^2 u/partial t^2 = 0
  D'Alembert solution: u = f(x - ct) + g(x + ct)  [travelling waves at speed c]
  A shape u(x,0) propagates at constant speed c without distortion.

**Jacobian for coordinate change x=x(u,v), y=y(u,v):**
  J = | partial x/partial u    partial x/partial v |
      | partial y/partial u    partial y/partial v |
  Area element: dx*dy = |det(J)| * du*dv
  For polar (x=r*cos theta, y=r*sin theta): |det(J)| = r, so dx*dy = r*dr*d(theta)

---

## KEY FORMULAE FAST REFERENCE

**Integrating factor (1st order linear):**
  I(x) = e^{integral p(x) dx}

**2D eigenvalues from tau, Delta:**
  lambda = (tau +/- sqrt(tau^2 - 4*Delta)) / 2

**Linear stability of 1D ODE at fixed point y*:**
  stable iff f'(y*) < 0

**Total derivative along trajectory x(t), y(t):**
  df/dt = (partial f/partial x) x'(t) + (partial f/partial y) y'(t)

**Hessian classification shortcut:**
  Delta = fxx*fyy - (fxy)^2
  Delta > 0, fxx > 0 => min; Delta > 0, fxx < 0 => max; Delta < 0 => saddle

**Exact ODE compatibility:**
  partial F/partial y = partial G/partial x

---

## PROBLEM SHEET TOPIC MAP

| Sheet | Topics |
|---|---|
| PS1 | FT definitions, cosine/sine transforms, computing transforms |
| PS2 | FT properties, convolution theorem, energy theorem |
| PS3 | FT applied to ODEs; delta function |
| PS4 | 1st order ODE types; 2nd order special cases; linear ODEs CF+PI; systems eigenvalue method |
| PS5 | Phase portraits for 2D linear systems; solve y(x) from system; applications (combat, political) |
| PS6 | Damped oscillator phase portraits; nonlinear 2D systems; 1D bifurcations (saddle-node, classification) |
| PS7 | Partial derivatives; total derivative & chain rule; Taylor expansion; error estimation; thermodynamic identity |
| PS8 | Laplace equation; chain rule for PDEs; exact ODEs + integrating factors; stationary points + Hessian; sketching |

---

## EXAM STRATEGY NOTES

1. **Read carefully:** distinguish between "sketch the phase portrait" (qualitative, with arrows) and "find the general solution" (explicit formula).

2. **Phase portrait checklist:**
   - State tau and Delta
   - Classify the fixed point (name it)
   - Find eigenvectors and draw them as straight-line trajectories
   - Add arrows showing direction of motion
   - Sketch 2-3 representative curved trajectories

3. **Bifurcation diagram checklist:**
   - y* vs r axes clearly labelled
   - Solid lines = stable, dashed = unstable
   - Arrows showing flow direction
   - Name the bifurcation type at each critical r
   - Mark bifurcation point(s) explicitly

4. **Exact ODE checklist:**
   - Check condition first (partial F/partial y = partial G/partial x)
   - If not exact, attempt integrating factor (only x or only y)
   - After finding u(x,y), write solution as u = C (not u = 0)

5. **Taylor expansion / error:**
   - For %age errors, divide delta_f/f, use logarithmic differentiation
   - At theta = 45 degrees, sin(2*theta) = 1 and the theta-error term drops — this is a special case (PS7 Q3c)

6. **Stationary points:**
   - Solve both partial derivatives = 0 simultaneously (often requires substitution)
   - Always evaluate H at each point separately
   - If Delta = 0, the test is inconclusive — say so
