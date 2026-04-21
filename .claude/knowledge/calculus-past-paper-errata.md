# Mistakes and Typos in Year 1 MATH40004 May-June Past Papers and Answers
*(Sources from Maths Central — not exhaustive)*

---

## 2020

**Q1(b):** Function $f(x) = (\sin x^2)\sin(1/x^2)$ for $x\neq0$, $f(0)=0$.

The **published answer says $f'(0)$ does not exist** — this is **wrong**.

$f'(x)$ doesn't have to be continuous, so $f'(0)$ may not equal $\lim_{x\to0}f'(x)$. Using the definition of derivative directly: $f'(0)=0$ and $f$ **is** differentiable at $x=0$.

**Q2(c)(iii):** Centre of mass $\xi$ given as $3/4$ in the published answer — **wrong**. By calculating the integral correctly, $\xi = 3/8$.

---

## 2022

**Q1(b)(i):** The phrase "infection points" should be **"inflection points"** (typo in paper).

**Q3(a)(i):** Taylor series remainder — $\xi$ should be a number between $x$ and $\pi/2$, **not** $\pi/2 - x$.

**Q4(b)(i):** Fourier cosine transform — the lower limit of the integral in the third step should be $-1$, not $0$.

---

## 2023

**Q2(a)(i):** Surface area of revolution about $y$-axis — the published answer writes:
$$S_y = 2\pi\int_0^L x[1+(f')^2]^{1/2}\frac{dy}{dx}\,dx$$
There **should not** be a $dy/dx$ inside the integral. The correct formula is:
$$S_y = 2\pi\int_0^L x[1+(f')^2]^{1/2}\,dx$$
Therefore the published relation $S_y = 2S_x$ is **not valid**.
