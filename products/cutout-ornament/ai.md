You can ask ChatGPT, Claude, Gemini or another assistant to help you order a stencil ornament. This
page is written for you and for it. Your assistant can do most of the work. You see the ornament
before you pay, and you pay on Stripe's checkout page.

## What your assistant can do

1. **Make the drawing,** if it can make images. Give it your photo and this page; the instructions
   below are for it. Or skip this: add the photo on the [product page](../) and we make the drawing.
   A ready-made design needs no drawing at all.
2. **Help you choose:** two colours (a base and a stencil), a name tag or not, and the tag's font.
   The colours, fonts, prices and ready-made designs are in our [product data](../product.json).
3. **Set up the order** on the [product page](../): it uploads the drawing under "I have my own
   drawing" (or adds your photo, or picks a ready-made design), then sets your choices. Every
   control on the page is a plain, labelled form control.

## What only you do

- **Look at the preview.** It's the ornament as we'll print it. What you approve there is what we
  make.
- **Pay.** On Stripe's checkout page, yourself, or by approving the payment in your own
  assistant's wallet. We never take card details any other way.

If an assistant acts for you, you're responsible for what it orders and sends ([terms](/terms/)).

## Photos and people

- Use only photos you have the right to use. For a photo of a person, have their OK. For a child,
  you're their parent or guardian or have one's OK.
- No logos, brand marks, cartoon or film characters, or other people's artwork.
- If you add a photo on our page, it's sent to OpenAI to make the drawing (see the
  [privacy page](/privacy/)). If your assistant makes the drawing, we never get the photo, only the
  drawing. Your assistant's provider handles the photo under its own terms.

## If something goes wrong

If an ornament can't be printed as you approved it, we email you to offer a fresh drawing or a
full refund. Questions: [help@robotlantern.com](mailto:help@robotlantern.com).

## Instructions for your assistant: make the drawing

The same rules as JSON: [drawing-spec.json](../drawing-spec.json).

You are making one image that Robot Lantern (robotlantern.com) will cut into a two-part 3D-printed
ornament: a stencil sheet in one colour laid on a base in another. Our builder reads the image
exactly as given, so follow every rule. Make one image.

### How to make it

- **If you have no image model, stop here.** Don't draw one with code or SVG. Tell the customer to
  add their photo on the product page instead, and we'll make the drawing.
- **Generate it with an image model** (for example GPT Image, Gemini or Midjourney), from the
  customer's photo, as one new picture. Don't trace the photo with code, threshold it, or draw it as
  SVG or shapes: that loses the likeness.
- **Hand over the image exactly as the image model made it.** Save that file as it is, or, if you
  can't save files, show it to the customer to download. Never redraw it because you couldn't find
  the file. Don't resize it, recolour it, sharpen it or "fix" it with code afterwards: we resize it
  and clean the two colours ourselves. If it breaks a rule below, generate a new one instead. If you
  made several, pick the one that keeps the likeness best and breaks no rule.

### The file

- A square PNG, 1024 × 1024 or larger (up to 4096), under 4 MB.
- Two flat colours: red (#E01010) for what becomes the stencil sheet, and white for everything else,
  background included. No grey, no shading, no gradients, no texture, no third colour.
- The red artwork fills about 80% of the image width, centred, with plain white all round it. No
  frame, border, box or background shape: the subject's own outline is the edge of the red.

### What to draw

- One subject from the customer's photo: a pet's head and the top of its neck, or a person's head,
  hair and the top of the neck. If the photo has several, draw only the largest one nearest the
  centre.
- Keep the likeness, markings and expression exactly as in the photo. Never change the expression.
- Leave out the body, clothes, collars, tags, hands, background and every other object.
- No text, letters, numbers, logos, brand marks or cartoon characters anywhere. The name goes on a
  separate tag that we add.

### The style

A bold poster stencil or linocut. The subject is mostly solid red, and its features (eyes, nose
highlights, mouth, ear edges, fur or hair lines, markings) are white cut-outs in the red.

- **One piece.** All the red is ONE connected shape. No floating red dots, strokes or islands, and no
  red inside a white cut-out. Where a detail would float, join it to its neighbour with a short red
  bridge, the way real stencils do.
- **Filled cut-outs, never outlines.** Every white cut-out is a filled white shape. Never draw a
  feature as a thin white line round a red shape: thin white lines are filled in when the sheet is
  cut, and the feature disappears.
- **Chunky.** No red line thinner than 2% of the image width, and no white gap thinner than 2%. Few,
  bold shapes. Eyes are bold filled shapes (a solid red eye in a white socket, or a white eye whose
  red pupil touches the lid), never a thin outline or a tiny dot.
- **A closed outline.** A continuous red border at least 2.5% of the image width thick runs all the
  way round the outside, so the outer edge is one smooth closed shape.

### Check before you hand it over

1. It came straight from the image model, unedited. Two colours only, and the background is white.
2. No frame or box: white all round the subject.
3. The red is one connected piece.
4. Nothing is thinner than 2% of the width, red or white.
5. No text, logos or characters.

Then give the PNG to the customer to upload at https://robotlantern.com/shop/cutout-ornament/ ("I
have my own drawing"). The page checks it and says what's wrong if it can't be printed.
