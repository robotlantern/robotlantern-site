// The section marks' geometry (src/components/SectionMark.astro), shared with the nav so each
// item can leave room for how far its mark reaches past the end of its word.
export type Section = 'thoughts' | 'chats' | 'builds' | 'shop';
type Star = [number, number, number]; // x, y, half-width
// Thoughts' star trails a short dashed tail down to the left, the same in the nav and the menu (RJ, 2026-10-01).
export const marks: Record<Section, { stars: Star[]; ring?: [number, number, number]; poly?: [number, number][]; tail?: [number, number][] }> = {
  thoughts: { stars: [[1.504, -0.379, 0.806]], tail: [[-0.446, 0.821], [0.859, 0.024]] },
  chats: { ring: [-0.819, 0.026, 1.291], stars: [[0.118, -0.861, 0.448], [-1.193, 1.261, 0.346]] },
  builds: {
    poly: [[-2.542, 0.152], [-1.374, -1.455], [0.515, -0.841], [0.515, 1.146], [-1.374, 1.759]],
    stars: [[-1.374, -1.455, 0.332], [0.515, -0.841, 0.244], [0.515, 1.146, 0.367]],
  },
  shop: {
    poly: [[-1.943, -1.481], [0.244, -0.403], [-0.024, 2.014], [-2.216, 0.924]],
    stars: [[-1.943, -1.481, 0.367], [0.244, -0.403, 0.154], [-0.024, 2.014, 0.244], [-2.216, 0.924, 0.284]],
  },
};

// How far past the end of the word the mark reaches, in em (the nav's padding).
export const markReach = (name: Section) => {
  const m = marks[name];
  const xs = m.stars.map(([x, , r]) => x + r);
  if (m.ring) xs.push(m.ring[0] + m.ring[2]);
  if (m.poly) xs.push(...m.poly.map(([x]) => x));
  return Math.max(...xs);
};
