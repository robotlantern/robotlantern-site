---
name: Stereographic projector
stage: feasibility
fulfillment: self
next: Agent writes the generator and a lamp base, and lists LED options with prices (NOW.md, step 23)
waiting_on: agent
updated: 2026-11-10
---

A small lamp for a nightstand that throws a picture across the ceiling or a wall: a name, a short line of
text, a logo, or a silhouette from a photo. The shell over the light is a sphere with the picture cut
into it, mapped by stereographic projection, so a light at its pole draws the picture flat and undistorted
on the ceiling. The lamp is bought once; the shells screw on and swap (RJ's memo, 2026-11-10).

## Sketch

- **Shell (the custom part):** a sphere section with openings. Text and logos come out sharp. A photo
  becomes a coarse halftone of dots (the reference uses 55 × 55, or 85 × 85 at high resolution), so photos
  work best as silhouettes or bold, high-contrast pictures.
- **Lamp (the catalog part):** a base that holds a small, undiffused LED exactly at the shell's pole, with
  USB power and a thread or bayonet for the shells.
- **Light:** it has to be close to a point, because the smaller the emitter, the sharper the picture.
  Slant's lights are diffuse (puck light, tealight), and its mini party light (SL043) is unmeasured. RJ
  buys two or three small LEDs to try once the agent has listed options and prices (*proposed*, NOW.md
  decision 8).
- **Generator:** our own, from the maths: each point of the picture maps back onto the sphere through the
  pole. The input is a mask (text, an uploaded logo, or a subject from the subject picker) or a halftone.
  The output is the shell, checked so every bridge and dot prints.

## Reference and rights

- threonin's "Customizable stereographic picture projector v3" (Thingiverse 2078413), saved in the
  3d-modeling repo under `ideas/series/stereographic-projections/`. It's OpenSCAD, with a 1 W or 10 W
  high-power LED on a heat sink at the pole and threaded shells that swap.
- **Licence: CC BY-SA.** Prints may be sold with credit, and anything adapted from its files must be
  shared under the same licence. Our own generator avoids the share-alike; threonin still gets credit on
  the Credits page (*proposed*, decision 8).
- A customer's logo: they confirm they have the right to use it.

## Risks

The riskiest of the four: the optics (sharpness against LED size and distance to the ceiling), heat
(bright LEDs need a heat sink), and printing a sphere full of holes (overhangs).

## Questions

- Ceiling or wall first? It sets the shell's angle.
- Text and logos only at launch, or photo silhouettes too?
