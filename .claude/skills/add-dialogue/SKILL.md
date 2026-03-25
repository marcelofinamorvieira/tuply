---
name: add-dialogue
description: Add a new dialogue state to the mascot's conversation tree. Use when the user wants to add a new menu option, gag, or interaction flow.
---

Add a new dialogue state to the mascot. The user describes the interaction as `$ARGUMENTS`.

## How the dialogue system works

The `DIALOGUE` object in `content-script.js` is a state machine. Each state key maps to:

```js
{
  message: 'Text shown in the speech bubble (supports HTML)',
  anim: 'animationKey',           // Key from ANIMS object
  options: [                       // Buttons shown below the message
    { label: 'Text', action: 'stateKey' },  // Navigate to another state
    { label: 'Text', url: 'https://...' },  // Open external link
  ],
  // Optional fields:
  animLoop: true,                  // Ping-pong the animation forever
  animSegments: { intro: [0, N], loop: [N, M] },  // Segment-based playback
  afterAnim: 'animKey',           // Use a different idle animation after this state
  hideBubbleTail: true,           // Remove the speech arrow (for thought/loading states)
  autoAdvance: 'stateKey',        // Auto-transition when animation ends
  autoAdvanceDelay: 15000,        // Timer-based auto-advance (ms) instead of animation-based
  custom: 'customType',           // Special bubble content (see below)
  strongShadow: true,             // Extra shadow for animations with white elements
}
```

## Custom bubble types

- `'ai-loading'` — loading bar + rotating status text
- `'thought-bubble'` — cloud-shaped bubble with bouncing dots
- `'copy-result'` — result box + copy-to-clipboard button (uses `copyText` field)
- `'schema-reveal'` — staggered text reveal with timed fade-ins
- `'feedback-form'` — textarea + submit button

## Steps

1. Ask the user what the interaction should do (message, animation, options, special effects)
2. If a new animation is needed, use `/process-animation` first
3. Add the new state(s) to the `DIALOGUE` object
4. Add a menu option pointing to the new state (usually in the `menu` state's options)
5. If using segment-based playback or baked ping-pong, handle that in the animation file
6. Test the full flow: menu → new state → back to menu
