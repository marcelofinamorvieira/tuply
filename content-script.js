(() => {
  const ROOT_ID = 'dato-welcome-mascot-root';
  const ANIMS = {
    wave: 'assets/mascot-wave.json',
    idle: 'assets/mascot-idle.json',
    talk: 'assets/mascot-talk.json',
    write: 'assets/mascot-write.json',
    celebrate: 'assets/mascot-celebrate.json',
    think: 'assets/mascot-think.json',
    eureka: 'assets/mascot-eureka.json',
    toss: 'assets/mascot-toss.json',
    proud: 'assets/mascot-proud.json',
    intro: 'assets/mascot-intro.json',
    sad: 'assets/mascot-sad.json',
  };

  // Dialogue tree — each state has a message, options, and an optional animation trigger
  const DIALOGUE = {
    greeting: {
      message: 'Welcome to DatoCMS!',
      options: [],
    },
    introduction: {
      message: 'I\'m <b style="color:#FF7751">Tuply</b>, your advanced AI assistant',
      anim: 'intro',
      autoAdvance: 'menu',
      options: [],
    },
    menu: {
      message: 'What AI operation do you want to use?',
      anim: 'talk',
      options: [
        { label: 'AI Analysis', action: 'ai-thinking' },
        { label: 'Write my content', action: 'writing' },
        { label: 'Review my schema', action: 'schema-review' },
      ],
    },
    'schema-review': {
      message: 'Looking at your content schema...',
      anim: 'sad',
      animSegments: { intro: [0, 204], loop: [204, 456] },
      custom: 'schema-reveal',
      options: [],
    },
    'ai-thinking': {
      message: 'Analyzing your project with advanced AI',
      anim: 'think',
      animLoop: true,
      hideBubbleTail: true,
      custom: 'ai-loading',
      autoAdvanceDelay: 15000,
      autoAdvance: 'ai-result',
    },
    'ai-result': {
      message: 'This is <u><b>definitely</b></u> a DatoCMS project',
      anim: 'eureka',
      afterAnim: 'proud',
      options: [
        { label: '← Back', action: 'menu' },
      ],
    },
    writing: {
      message: 'Let me think of a groundbreaking title...',
      anim: 'write',
      animSegments: { intro: [0, 84], loop: [84, 258], outro: [258, 330] },
      hideBubbleTail: true,
      custom: 'thought-bubble',
      autoAdvanceDelay: 8000,
      autoAdvance: 'content-result',
    },
    'content-result': {
      message: 'Here is the perfect title for your next post:',
      anim: 'celebrate',
      custom: 'copy-result',
      copyText: 'Lorem ipsum dolor sit amet',
      options: [
        { label: '← Back', action: 'menu' },
      ],
    },
  };

  if (!/\.admin\.datocms\.com$/i.test(window.location.hostname)) {
    return;
  }

  let dismissed = false;
  let observer = null;

  const styles = `
    :host {
      all: initial;
    }

    *, *::before, *::after {
      box-sizing: border-box;
    }

    .dw-shell {
      position: fixed;
      right: -50px;
      top: 48px;
      z-index: 2147483647;
      display: flex;
      align-items: center;
      gap: 0;
      pointer-events: none;
      font-family: "Avenir Next", "Helvetica Neue", sans-serif;
      color: #292524;
    }

    .dw-bubble {
      position: relative;
      max-width: min(220px, calc(100vw - 244px));
      padding: 12px 14px;
      border: 1px solid rgba(0, 0, 0, 0.08);
      border-left: 3px solid #FF7751;
      border-radius: 4px;
      background: #fff;
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.14), 0 0 0 1px rgba(0, 0, 0, 0.04);
      pointer-events: auto;
      transform-origin: right center;
      animation: dw-speak-intro 400ms cubic-bezier(0.34, 1.56, 0.64, 1) 2050ms 1 both;
    }

    .dw-bubble.is-replay-a {
      animation: dw-speak-replay-a 350ms cubic-bezier(0.34, 1.56, 0.64, 1) 300ms 1 both;
    }

    .dw-bubble.is-replay-b {
      animation: dw-speak-replay-b 350ms cubic-bezier(0.34, 1.56, 0.64, 1) 300ms 1 both;
      opacity: 0;
      will-change: transform, opacity;
      transition: opacity 200ms ease, transform 200ms cubic-bezier(0.34, 1.56, 0.64, 1);
    }

    .dw-bubble.no-tail::after {
      display: none;
    }

    .dw-bubble.thought-cloud {
      border: none;
      border-left: none;
      border-radius: 30px;
      box-shadow: 0 2px 10px rgba(0, 0, 0, 0.18), 0 0 0 1px rgba(0, 0, 0, 0.05);
      padding: 16px 18px;
    }

    .dw-bubble.thought-cloud::after {
      display: none;
    }

    .dw-bubble.thought-cloud::before {
      content: "";
      position: absolute;
      top: -9px;
      right: -6px;
      width: 13px;
      height: 13px;
      border-radius: 50%;
      background: #fff;
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.2), 0 0 0 1px rgba(0, 0, 0, 0.05);
      animation: dw-cloud-bob 2s ease-in-out infinite;
    }

    .dw-thought-trail-1 {
      position: absolute;
      top: -16px;
      right: -18px;
      width: 9px;
      height: 9px;
      border-radius: 50%;
      background: #fff;
      box-shadow: 0 2px 6px rgba(0, 0, 0, 0.2), 0 0 0 1px rgba(0, 0, 0, 0.05);
      animation: dw-cloud-bob 2s ease-in-out 0.2s infinite;
    }

    .dw-thought-trail-2 {
      position: absolute;
      top: -20px;
      right: -32px;
      width: 6px;
      height: 6px;
      border-radius: 50%;
      background: #fff;
      box-shadow: 0 2px 5px rgba(0, 0, 0, 0.2), 0 0 0 1px rgba(0, 0, 0, 0.05);
      animation: dw-cloud-bob 2s ease-in-out 0.4s infinite;
    }

    @keyframes dw-cloud-bob {
      0%, 100% { transform: translateY(0); }
      50% { transform: translateY(-3px); }
    }

    .dw-bubble::after {
      content: "";
      position: absolute;
      top: 50%;
      right: -8px;
      width: 16px;
      height: 16px;
      background: #fff;
      border-right: 1px solid rgba(0, 0, 0, 0.08);
      border-bottom: 1px solid rgba(0, 0, 0, 0.08);
      box-shadow: 3px 3px 4px rgba(0, 0, 0, 0.06);
      transform: translateY(-50%) rotate(-45deg);
    }

    .dw-message {
      margin: 0;
      font-size: 14px;
      line-height: 1.4;
      font-weight: 500;
      color: #30343F;
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      text-align: center;
    }

    .dw-dismiss {
      position: absolute;
      top: 6px;
      right: 6px;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      width: 22px;
      height: 22px;
      padding: 0;
      border: 0;
      border-radius: 4px;
      background: transparent;
      color: #9a9a9a;
      cursor: pointer;
      font-size: 13px;
      transition: background-color 0.2s cubic-bezier(0.55, 0, 0.1, 1), color 0.2s cubic-bezier(0.55, 0, 0.1, 1);
    }

    .dw-dismiss:hover {
      background: rgba(0, 0, 0, 0.05);
      color: #30343F;
    }

    .dw-dismiss:focus-visible {
      outline: 2px solid #FF7751;
      outline-offset: 1px;
    }

    .dw-options {
      display: flex;
      flex-direction: column;
      align-items: stretch;
      gap: 6px;
      margin-top: 10px;
    }

    .dw-option {
      display: block;
      width: 100%;
      padding: 5px 10px;
      border: 1px solid rgba(0, 0, 0, 0.12);
      border-radius: 4px;
      background: #fff;
      color: #FF7751;
      font-size: 13px;
      font-weight: 500;
      font-family: inherit;
      cursor: pointer;
      text-decoration: none;
      text-align: center;
      line-height: 1.3;
      transition: background-color 0.2s cubic-bezier(0.55, 0, 0.1, 1), border-color 0.2s cubic-bezier(0.55, 0, 0.1, 1);
    }

    .dw-option:hover {
      background: rgba(255, 119, 81, 0.06);
      border-color: #FF7751;
    }

    .dw-option:focus-visible {
      outline: 2px solid #FF7751;
      outline-offset: 1px;
    }

    .dw-feedback-form {
      display: flex;
      flex-direction: column;
      gap: 8px;
      margin-top: 10px;
    }

    .dw-feedback-input {
      width: 100%;
      min-height: 60px;
      padding: 8px 10px;
      border: 1px solid rgba(0, 0, 0, 0.12);
      border-radius: 4px;
      font-family: inherit;
      font-size: 13px;
      color: #30343F;
      resize: none;
      line-height: 1.4;
      transition: border-color 0.2s cubic-bezier(0.55, 0, 0.1, 1);
    }

    .dw-feedback-input:focus {
      outline: none;
      border-color: #FF7751;
    }

    .dw-feedback-input::placeholder {
      color: #9a9a9a;
    }

    .dw-feedback-submit {
      padding: 6px 12px;
      border: none;
      border-radius: 4px;
      background: #FF7751;
      color: #fff;
      font-size: 13px;
      font-weight: 500;
      font-family: inherit;
      cursor: pointer;
      transition: opacity 0.2s cubic-bezier(0.55, 0, 0.1, 1);
    }

    .dw-feedback-submit:hover {
      opacity: 0.85;
    }

    .dw-feedback-submit:focus-visible {
      outline: 2px solid #FF7751;
      outline-offset: 2px;
    }

    .dw-loading-bar {
      width: 100%;
      height: 4px;
      border-radius: 2px;
      background: rgba(0, 0, 0, 0.08);
      margin-top: 12px;
      overflow: hidden;
    }

    .dw-loading-fill {
      height: 100%;
      border-radius: 2px;
      background: linear-gradient(90deg, #FF7751, #FF593D);
      width: 0%;
      animation: dw-loading 15s cubic-bezier(0.4, 0, 0.2, 1) forwards;
    }

    @keyframes dw-loading {
      0% { width: 0%; }
      10% { width: 15%; }
      30% { width: 35%; }
      50% { width: 55%; }
      70% { width: 72%; }
      85% { width: 88%; }
      100% { width: 100%; }
    }

    .dw-blink {
      animation: dw-text-blink 1.8s ease-in-out infinite;
    }

    @keyframes dw-text-blink {
      0%, 100% { opacity: 1; }
      50% { opacity: 0.4; }
    }

    .dw-thought-dots {
      display: flex;
      justify-content: center;
      gap: 6px;
      margin-top: 12px;
    }

    .dw-thought-dot {
      width: 8px;
      height: 8px;
      border-radius: 50%;
      background: #FF7751;
      opacity: 0.3;
      animation: dw-thought-bounce 1.4s ease-in-out infinite;
    }

    .dw-thought-dot:nth-child(2) {
      animation-delay: 0.2s;
    }

    .dw-thought-dot:nth-child(3) {
      animation-delay: 0.4s;
    }

    @keyframes dw-thought-bounce {
      0%, 60%, 100% { opacity: 0.3; transform: translateY(0); }
      30% { opacity: 1; transform: translateY(-6px); }
    }

    .dw-copy-btn {
      display: block;
      width: 100%;
      margin-top: 10px;
      padding: 6px 12px;
      border: none;
      border-radius: 4px;
      background: #FF7751;
      color: #fff;
      font-size: 13px;
      font-weight: 500;
      font-family: inherit;
      cursor: pointer;
      text-align: center;
      transition: opacity 0.2s cubic-bezier(0.55, 0, 0.1, 1);
    }

    .dw-copy-btn:hover {
      opacity: 0.85;
    }

    .dw-copy-btn:focus-visible {
      outline: 2px solid #FF7751;
      outline-offset: 2px;
    }

    .dw-result-box {
      margin-top: 8px;
      padding: 8px 10px;
      border: 1px solid rgba(0, 0, 0, 0.1);
      border-radius: 4px;
      background: #f9f9f9;
      font-size: 13px;
      font-style: italic;
      color: #30343F;
      text-align: center;
      line-height: 1.4;
    }

    .dw-schema-lines {
      margin-top: 14px;
      text-align: center;
      font-size: 13px;
      line-height: 1.8;
      color: #30343F;
    }

    .dw-schema-line {
      opacity: 0;
      transition: opacity 400ms ease;
    }

    .dw-schema-line.is-visible {
      opacity: 1;
    }

    .dw-loading-status {
      margin: 8px 0 0;
      font-size: 11px;
      color: #9a9a9a;
      text-align: center;
      font-family: inherit;
      transition: opacity 150ms ease;
    }

    .dw-loading-status.is-switching {
      opacity: 0;
    }

    .dw-mascot.strong-shadow {
      filter: drop-shadow(0 0 5px rgba(0, 0, 0, 0.5)) drop-shadow(0 0 14px rgba(0, 0, 0, 0.3));
    }

    .dw-option--back {
      color: #9a9a9a;
      border-color: transparent;
      background: transparent;
      font-size: 12px;
      padding: 4px 8px;
      align-self: center;
    }

    .dw-option--back:hover {
      color: #30343F;
      background: rgba(0, 0, 0, 0.04);
      border-color: transparent;
    }

    .dw-mascot-frame {
      display: flex;
      align-items: center;
      justify-content: center;
      margin-left: -40px;
      width: 300px;
      pointer-events: none;
      flex: 0 0 auto;
      animation: dw-pop-in 500ms cubic-bezier(0.34, 1.56, 0.64, 1) 1.25s both;
    }

    .dw-mascot {
      display: block;
      width: 300px;
      height: 300px;
      filter: drop-shadow(0 0 3px rgba(0, 0, 0, 0.35)) drop-shadow(0 0 8px rgba(0, 0, 0, 0.2));
      transition: opacity 250ms ease;
    }

    .dw-mascot.is-fading {
      opacity: 0;
    }

    @keyframes dw-pop-in {
      from {
        opacity: 0;
        transform: scale(0);
      }
      to {
        opacity: 1;
        transform: scale(1);
      }
    }

    @keyframes dw-speak-intro {
      from {
        opacity: 0;
        transform: scale(0.85);
      }
      to {
        opacity: 1;
        transform: scale(1);
      }
    }

    @keyframes dw-speak-replay-a {
      from { opacity: 0; transform: scale(0.85); }
      to { opacity: 1; transform: scale(1); }
    }

    @keyframes dw-speak-replay-b {
      from { opacity: 0; transform: scale(0.85); }
      to { opacity: 1; transform: scale(1); }
    }

    @media (max-width: 640px) {
      .dw-shell {
        right: 14px;
        gap: 10px;
      }

      .dw-bubble {
        max-width: min(210px, calc(100vw - 150px));
        padding: 13px 36px 13px 14px;
      }

      .dw-message {
        font-size: 13px;
      }

      .dw-mascot-frame,
      .dw-mascot {
        width: 200px;
      }
    }

    @media (prefers-reduced-motion: reduce) {
      .dw-bubble {
        animation: none;
        transform: none;
        opacity: 1;
      }

      .dw-mascot-frame {
        animation: none;
        opacity: 1;
        transform: scale(1);
      }
    }
  `;

  // --- Animation helpers ---

  const animCache = {};

  function loadAnimationData(name) {
    if (animCache[name]) return Promise.resolve(animCache[name]);
    return fetch(chrome.runtime.getURL(ANIMS[name]))
      .then((res) => res.json())
      .then((data) => { animCache[name] = data; return data; });
  }

  function preloadAll() {
    return Promise.all(Object.keys(ANIMS).map(loadAnimationData));
  }

  let currentAnim = null;

  function playAnim(container, name, { loop = false, onComplete } = {}) {
    return loadAnimationData(name).then((data) => {
      if (currentAnim) currentAnim.destroy();

      const anim = lottie.loadAnimation({
        container,
        renderer: 'svg',
        loop: false,
        autoplay: true,
        animationData: data,
      });

      currentAnim = anim;

      if (loop) {
        anim.addEventListener('complete', () => {
          anim.setDirection(anim.playDirection * -1);
          anim.play();
        });
      }

      if (onComplete) {
        anim.addEventListener('complete', onComplete);
      }

      return anim;
    });
  }

  function fadeToAnim(container, name, opts = {}) {
    container.classList.add('is-fading');
    setTimeout(() => {
      playAnim(container, name, opts);
      // Double rAF: first ensures the browser paints opacity:0 with the new
      // animation, second triggers the fade-in transition
      requestAnimationFrame(() => {
        requestAnimationFrame(() => {
          container.classList.remove('is-fading');
        });
      });
    }, 250);
  }

  function fadeToSegmentAnim(container, name, segments) {
    container.classList.add('is-fading');
    setTimeout(() => {
      loadAnimationData(name).then((data) => {
        if (currentAnim) currentAnim.destroy();

        const anim = lottie.loadAnimation({
          container,
          renderer: 'svg',
          loop: false,
          autoplay: false,
          animationData: data,
        });

        currentAnim = anim;

        // Play intro segment once, then loop the writing segment forward
        anim.playSegments(segments.intro, true);

        anim.addEventListener('complete', function onIntroComplete() {
          anim.removeEventListener('complete', onIntroComplete);
          anim.loop = true;
          anim.playSegments(segments.loop, true);
        });

        requestAnimationFrame(() => {
          requestAnimationFrame(() => {
            container.classList.remove('is-fading');
          });
        });
      });
    }, 250);
  }

  // --- Loading status text ---

  const LOADING_STEPS = [
    'Scanning records...',
    'Analyzing content models...',
    'Inspecting assets...',
    'Reviewing permissions...',
    'Checking environments...',
    'Evaluating SEO metadata...',
    'Parsing GraphQL schema...',
    'Auditing plugins...',
    'Cross-referencing locales...',
    'Running final diagnostics...',
  ];

  let loadingInterval = null;

  function startLoadingStatusCycle(el) {
    if (loadingInterval) clearInterval(loadingInterval);

    let stepIndex = 0;
    el.textContent = LOADING_STEPS[0];

    loadingInterval = setInterval(() => {
      stepIndex += 1;
      if (stepIndex >= LOADING_STEPS.length) {
        clearInterval(loadingInterval);
        loadingInterval = null;
        return;
      }

      el.classList.add('is-switching');
      setTimeout(() => {
        el.textContent = LOADING_STEPS[stepIndex];
        el.classList.remove('is-switching');
      }, 150);
    }, 1400);
  }

  // --- Dialogue state machine ---

  let bubbleEl = null;
  let mascotEl = null;

  function updateBubbleContent(stateKey) {
    const state = DIALOGUE[stateKey];
    if (!bubbleEl || !state) return;

    const messageEl = bubbleEl.querySelector('.dw-message');
    messageEl.innerHTML = state.message;
    messageEl.classList.toggle('dw-blink', state.custom === 'ai-loading' || state.custom === 'thought-bubble');
    const optionsEl = bubbleEl.querySelector('.dw-options');

    // Custom content for special states
    if (state.custom === 'schema-reveal') {
      optionsEl.innerHTML = `
        <div class="dw-schema-lines">
          <div class="dw-schema-line" data-delay="2500" style="font-size: 15px; font-style: italic; color: #9a9a9a; margin-bottom: 20px;">Oh my...</div>
          <div class="dw-schema-line" data-delay="3500" style="font-size: 16px; font-weight: 600;">You should <i>start over</i>.</div>
          <div class="dw-schema-line" data-delay="5000"><button type="button" class="dw-option dw-option--back" data-action="menu">← Back</button></div>
        </div>
      `;
      optionsEl.querySelectorAll('.dw-schema-line').forEach((line) => {
        setTimeout(() => line.classList.add('is-visible'), parseInt(line.dataset.delay));
      });
      return;
    }

    if (state.custom === 'ai-loading') {
      optionsEl.innerHTML = `
        <p class="dw-loading-status"></p>
        <div class="dw-loading-bar">
          <div class="dw-loading-fill"></div>
        </div>
      `;
      startLoadingStatusCycle(optionsEl.querySelector('.dw-loading-status'));
      return;
    }

    if (state.custom === 'thought-bubble') {
      bubbleEl.classList.add('thought-cloud');
      // Add trailing circles for the comic thought bubble look (::before is the 1st)
      for (let i = 1; i <= 2; i++) {
        if (!bubbleEl.querySelector(`.dw-thought-trail-${i}`)) {
          const trail = document.createElement('div');
          trail.className = `dw-thought-trail-${i}`;
          bubbleEl.appendChild(trail);
        }
      }
      optionsEl.innerHTML = `
        <div class="dw-thought-dots">
          <div class="dw-thought-dot"></div>
          <div class="dw-thought-dot"></div>
          <div class="dw-thought-dot"></div>
        </div>
      `;
      return;
    } else {
      bubbleEl.classList.remove('thought-cloud');
      bubbleEl.querySelectorAll('[class^="dw-thought-trail"]').forEach((el) => el.remove());
    }

    if (state.custom === 'copy-result') {
      const resultText = state.copyText || state.message;
      optionsEl.innerHTML = `
        <div class="dw-result-box">${resultText}</div>
        <button type="button" class="dw-copy-btn">Copy to clipboard</button>
      `;
      const copyBtn = optionsEl.querySelector('.dw-copy-btn');
      copyBtn.addEventListener('click', () => {
        navigator.clipboard.writeText(resultText).then(() => {
          copyBtn.textContent = 'Copied!';
          fadeToAnim(mascotEl, 'toss', {
            onComplete: () => fadeToAnim(mascotEl, 'idle', { loop: true }),
          });
          setTimeout(() => { copyBtn.textContent = 'Copy to clipboard'; }, 2000);
        });
      });

      // Still render options (back button) below
      const backHtml = (state.options || []).map((opt) => {
        const isBack = opt.label.includes('←');
        const cls = isBack ? 'dw-option dw-option--back' : 'dw-option';
        return `<button type="button" class="${cls}" data-action="${opt.action}">${opt.label}</button>`;
      }).join('');
      optionsEl.insertAdjacentHTML('beforeend', backHtml);
      return;
    }

    const optionsHtml = (state.options || []).map((opt) => {
      if (opt.url) {
        return `<a class="dw-option" href="${opt.url}" target="_blank" rel="noopener">${opt.label}</a>`;
      }
      const isBack = opt.label.includes('←');
      const cls = isBack ? 'dw-option dw-option--back' : 'dw-option';
      return `<button type="button" class="${cls}" data-action="${opt.action}">${opt.label}</button>`;
    }).join('');

    optionsEl.innerHTML = optionsHtml;
  }

  function transitionTo(stateKey) {
    const state = DIALOGUE[stateKey];
    if (!state) return;

    // What happens when the animation completes
    const idleAnim = state.afterAnim || 'idle';
    const onAnimComplete = state.autoAdvance && !state.autoAdvanceDelay
      ? () => transitionTo(state.autoAdvance)
      : () => fadeToAnim(mascotEl, idleAnim, { loop: true });

    // Animation handling
    if (state.animSegments) {
      fadeToSegmentAnim(mascotEl, state.anim, state.animSegments);
    } else if (state.anim) {
      if (state.animLoop) {
        fadeToAnim(mascotEl, state.anim, { loop: true });
      } else {
        fadeToAnim(mascotEl, state.anim, { onComplete: onAnimComplete });
      }
    }

    // Timer-based auto-advance (for loading states)
    if (state.autoAdvanceDelay && state.autoAdvance) {
      setTimeout(() => transitionTo(state.autoAdvance), state.autoAdvanceDelay);
    }

    // Toggle bubble tail
    if (state.hideBubbleTail) {
      bubbleEl.classList.add('no-tail');
    } else {
      bubbleEl.classList.remove('no-tail');
    }

    // Toggle strong shadow for animations with white elements
    mascotEl.classList.toggle('strong-shadow', !!state.strongShadow);

    // Pop bubble out, swap content, replay pop-in animation
    const wasA = bubbleEl.classList.contains('is-replay-a');
    bubbleEl.classList.remove('is-replay-a', 'is-replay-b');
    bubbleEl.style.opacity = '0';
    bubbleEl.style.transform = 'scale(0.85)';
    setTimeout(() => {
      updateBubbleContent(stateKey);
      bubbleEl.style.opacity = '';
      bubbleEl.style.transform = '';
      bubbleEl.offsetHeight;
      bubbleEl.classList.add(wasA ? 'is-replay-b' : 'is-replay-a');
    }, 220);
  }

  function handleOptionClick(e) {
    const actionBtn = e.target.closest('[data-action]');
    if (!actionBtn) return;

    e.preventDefault();

    if (actionBtn.dataset.action === 'submit-feedback') {
      // For now, just transition to the thank-you state
      transitionTo('thanks');
      return;
    }

    transitionTo(actionBtn.dataset.action);
  }

  // --- Intro sequence ---

  function initMascot(container) {
    preloadAll().then(() => {
      setTimeout(() => {
        playAnim(container, 'wave', {
          onComplete: () => {
            transitionTo('introduction');
          },
        });
      }, 1250);
    }).catch(() => {
      setTimeout(() => {
        playAnim(container, 'idle', { loop: true });
        updateBubbleContent('menu');
      }, 1250);
    });
  }

  // --- DOM creation ---

  function createOverlay() {
    const host = document.createElement('div');
    host.id = ROOT_ID;

    const shadowRoot = host.attachShadow({ mode: 'open' });
    const style = document.createElement('style');
    style.textContent = styles;

    const shell = document.createElement('div');
    shell.className = 'dw-shell';

    shell.innerHTML = `
      <section class="dw-bubble" role="status" aria-live="polite">
        <p class="dw-message"></p>
        <div class="dw-options"></div>
      </section>
      <div class="dw-mascot-frame" aria-hidden="true">
        <div class="dw-mascot"></div>
      </div>
    `;

    bubbleEl = shell.querySelector('.dw-bubble');
    mascotEl = shell.querySelector('.dw-mascot');

    // Render initial dialogue state
    updateBubbleContent('greeting');

    // Dialogue option clicks (delegated)
    bubbleEl.addEventListener('click', handleOptionClick);

    shadowRoot.append(style, shell);
    initMascot(mascotEl);

    return host;
  }

  function teardown() {
    observer?.disconnect();
    observer = null;
    document.getElementById(ROOT_ID)?.remove();
  }

  function observeForRemoval() {
    observer?.disconnect();
    observer = new MutationObserver(() => {
      if (dismissed) {
        return;
      }

      if (!document.getElementById(ROOT_ID)) {
        observer?.disconnect();
        observer = null;
        window.requestAnimationFrame(mount);
      }
    });

    observer.observe(document.documentElement, {
      childList: true,
      subtree: true
    });
  }

  function mount() {
    if (dismissed || document.getElementById(ROOT_ID)) {
      return;
    }

    const parent = document.body || document.documentElement;
    if (!parent) {
      window.requestAnimationFrame(mount);
      return;
    }

    parent.appendChild(createOverlay());
    observeForRemoval();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', mount, { once: true });
  } else {
    mount();
  }
})();
