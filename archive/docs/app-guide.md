# Taylor-Cone Solver App — User Guide

A plain-language guide to the Streamlit app (`app/streamlit_app.py`): what it
simulates, what every sidebar setting means, and how to read the results.
Written for a high-school student — no equations beyond the basics.

## The big picture (what the app actually simulates)

Imagine two flat, circular metal plates facing each other, with a gap between
them:

- The **top plate** is connected to a high voltage `V₀`.
- The **bottom plate** is grounded (0 V).
- Between them sits a cone of liquid — think of a very sharp, pointed water
  droplet stretched by the electric field.

The electric field between the plates **pulls** on the liquid's surface. The
liquid's **surface tension** (its "skin") **pushes back**. Physics says these
two forces must exactly cancel at every point of the surface, or the surface
would move. The famous result (Taylor, 1964): a perfect liquid cone in a
uniform electric field balances when its half-angle is **49.3°** — that's why
it's the default.

The app does three things:

1. **Solves for the electric field** everywhere between the plates
   (Laplace's equation, or Poisson's if you add free charges).
2. **Optionally models space charge** — free charges in the air that pile up
   and partially "block" (shield) the field.
3. **Checks the cone** — it draws a straight cone with the half-angle you
   chose and measures how badly the two forces fail to cancel along its
   surface. That failure is the **residual**.

## Sidebar settings, one by one

### Basic parameters

| Setting | What it means | What it does |
|---|---|---|
| **Voltage V₀ [V]** | The potential difference between the plates. | More volts = stronger electric field = stronger pull on the liquid. Like turning up the water pressure in a hose. |
| **Surface tension γ [N/m]** | How much the liquid's surface resists being stretched or curved — the "stretchiness" of its skin. | Higher γ = the liquid fights harder against the cone shape. Default `0.022` is roughly ethanol; water is about `0.072`. |
| **Electrode spacing [m]** | The gap between the two plates — also the height of the simulated box (the `z` direction). | Smaller gap = stronger field for the same voltage (field ≈ V₀ ÷ gap). |
| **Domain radius [m]** | The radius of the simulated cylinder (the `r` direction) — how far "out to the side" the math extends. | Just needs to be big enough that the cone and the field fit comfortably. Too small and you clip the field, which distorts the answer. |
| **Grid resolution (nr × nz)** | How many sample points the computer uses in the radial (`nr`) and vertical (`nz`) directions. | More points = sharper, more accurate result, but slower. Like pixels in a photo. Use Fine for final runs, Coarse for quick experiments. |
| **Space-charge model** | Whether there are free charges floating in the gap. | See below. |

### Space-charge model — the three choices

| Model | What it does | When to use it |
|---|---|---|
| **none** | Pure vacuum between the plates. No charges. Fastest. | Your baseline: the "textbook" field. |
| **gaussian** | You *place* a blob of charge by hand at a chosen spot, and the solver sees how it changes (shields) the field. | Controlled experiments — "if I put a charge cloud here, what happens to the field?" |
| **threshold** | Charge appears automatically, but **only where the electric field is strong enough** — a crude model of ions being ripped off the liquid at the tip. | More physical, but harder: the charge changes the field, which changes the charge, so the solver must loop until both settle. |

### Advanced → Space-charge closure parameters (shown only for the gaussian model)

| Setting | What it means |
|---|---|
| **ρ₀ [C/m³]** | Charge density at the center of the cloud — how densely packed the charge is (coulombs per cubic meter). |
| **ℓ (cloud width) [m]** | How spread out the blob is — the "standard deviation" of the bell curve. Bigger ℓ = fatter, softer cloud. |
| **Apex r / Apex z [m]** | Where the center of the cloud sits in the domain. Tip: put it near the cone tip (apex z ≈ 0.8 × spacing, the default) to mimic real shielding. |

### Advanced → Threshold parameters (shown only for the threshold model)

| Setting | What it means |
|---|---|
| **E_c (critical field) [V/m]** | The "tripwire". Where the field is below E_c, there is **no charge at all**. Above it, charge turns on. |
| **E_s (scale field) [V/m]** | How quickly the charge ramps up once past the tripwire. Small E_s = sharp, sudden switch-on. |
| **ρ_max [C/m³]** | The ceiling — charge density saturates at this value no matter how strong the field gets. |

### Advanced → Iteration controls

The charge and field depend on each other (charge moves the field, the field
moves the charge), so the solver goes around in a loop:
*field → charge → new field → …* until things stop changing.

| Setting | What it means |
|---|---|
| **Under-relaxation ω** | How much of each new "guess" the solver accepts per round. ω = 0.5 (default) means it mixes half new + half old. **Lower ω = more cautious = more likely to converge, but slower.** Think of it like slowly mixing two paints to avoid sloshing. |
| **Max iterations** | The cap on how many rounds the loop may take before giving up. |

### Advanced → Interface for residual diagnostics

| Setting | What it means |
|---|---|
| **Cone half-angle [°]** | The shape of the test cone used for the force-balance check (angle between the cone wall and the symmetry axis). Default **49.3°** = Taylor's magic angle. |

## Reading the results

### The six metric cards

| Metric | How to read it |
|---|---|
| **Interface half-angle (input)** | ⚠️ Just echoes the angle you set in the sidebar. It's an *input*, not a prediction — don't be fooled by it. |
| **Peak |E|** | The strongest electric field **along the cone's surface**, in V/m. Expect it near the tip. Higher voltage, smaller spacing, sharper cone → bigger value. |
| **RMS residual** | ⭐ **The key number.** The electric field pushes on the surface with a "pressure" (Maxwell pressure); surface tension also exerts a pressure. The residual is the amount they *fail* to cancel, in pascals. RMS = "typical size" of that leftover. **0 Pa = perfect balance; small = good.** If it's large, the cone shape you chose is not a real equilibrium shape. |
| **Shielding metric S_E** | How much the space charge weakened the field compared to the no-charge case: **0 = no shielding, 0.5 = field halved, ~1 = almost fully shielded.** Shows "—" when the model is `none`, since there's nothing to shield. |
| **Runtime** | How long the solve took. |
| **Converged / Iterations** | Whether the charge↔field loop settled down, and how many rounds it used. With model `none` this is always "Yes" (Laplace solves in one step). If it's "**No**", **lower ω or raise max iterations** and rerun. |

### The five plots

| Plot | What you're looking at |
|---|---|
| **Electric Potential** | A topographic map of voltage: top edge bright (V₀), bottom edge dark (0), contour lines like a hiking map. |
| **Electric Field Magnitude** | Heatmap of field strength — brighter = stronger. Look for hotspots at the cone tip and electrode corners. |
| **Potential with Interface Overlay** | The potential map with your test cone drawn on top. |
| **Space-Charge Density** | Where the charge actually sits (only non-zero when a space-charge model is on). |
| **YLM Residual Profile** | The force-balance error plotted point-by-point along the cone (YLM = Young–Laplace–Maxwell, the name of the balance). **Flat and near zero = the cone shape is a good equilibrium.** Bumps = trouble spots along the surface. |

## A 5-minute experiment to build intuition

1. **Baseline:** model = `none`, half-angle = 49.3°. Run. Note the RMS residual
   (should be small) and peak |E|.
2. **Mess up the shape:** set half-angle to 30° and rerun. The residual jumps —
   you've forced a shape that doesn't balance.
3. **Back to Taylor:** return to 49.3° → residual drops again. You just
   reproduced Taylor's balance argument.
4. **Add shielding:** switch to the gaussian model, keep the cloud near the tip,
   and raise ρ₀. Watch **peak |E| drop** and **S_E rise** — the charge cloud is
   absorbing part of the field.
5. **Stress the solver:** switch to `threshold` with a small E_c. If it stops
   converging, lower ω (e.g. 0.3) and/or raise max iterations.

## Honest caveats (important for an ISEF project)

- **This is a reduced-order model**, not full CFD. It doesn't simulate
  cone-jet breakup, plasma, or ion emission in detail.
- **The Gaussian charge model is a scaffold** — good for testing the Poisson
  source path and sensitivity, not a physically predictive emission model.
- **Global peak |E| can mislead**: the strongest field may sit at electrode
  corners or artificial far boundaries rather than the cone tip.
- **The residual is diagnostic**: it checks a *prescribed* straight cone; it
  does not yet optimize the free surface shape.
