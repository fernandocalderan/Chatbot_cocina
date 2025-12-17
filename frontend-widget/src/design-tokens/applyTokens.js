const DEFAULT_TOKENS = {
  colors: {
    primary: "#3A4F7A",
    secondary: "#E6EAF2",
    accent: "#C9A24D",
  },
  font: {
    family: "Inter",
    size_base: 14,
  },
  bubble: {
    position: "bottom-right",
    size: "md",
    border_radius: 16,
  },
  tone: "serio",
};

function safeNumber(value, fallback) {
  const num = Number(value);
  return Number.isFinite(num) ? num : fallback;
}

export function applyTokens(runtime) {
  const tokens = runtime?.tokens || {};
  const visual = runtime?.visual || {};
  const colors = {
    ...DEFAULT_TOKENS.colors,
    primary: visual.primary_color || DEFAULT_TOKENS.colors.primary,
    secondary: visual.secondary_color || DEFAULT_TOKENS.colors.secondary,
    accent: visual.accent_color || DEFAULT_TOKENS.colors.accent,
    ...(tokens.colors || {}),
  };
  const font = {
    ...DEFAULT_TOKENS.font,
    family: visual.font_family || DEFAULT_TOKENS.font.family,
    size_base: visual.font_size || DEFAULT_TOKENS.font.size_base,
    ...(tokens.font || {}),
  };
  const bubble = {
    ...DEFAULT_TOKENS.bubble,
    position: visual.position || DEFAULT_TOKENS.bubble.position,
    size: visual.size || DEFAULT_TOKENS.bubble.size,
    border_radius: visual.border_radius || DEFAULT_TOKENS.bubble.border_radius,
    ...(tokens.bubble || {}),
  };
  const tone = tokens.tone || runtime?.messages?.tone || runtime?.visual?.tone || DEFAULT_TOKENS.tone;

  const root = document.documentElement;
  root.style.setProperty("--widget-primary", String(colors.primary));
  root.style.setProperty("--widget-secondary", String(colors.secondary));
  root.style.setProperty("--widget-accent", String(colors.accent));
  root.style.setProperty("--widget-font-family", String(font.family || DEFAULT_TOKENS.font.family));
  root.style.setProperty("--widget-font-size", `${safeNumber(font.size_base, DEFAULT_TOKENS.font.size_base)}px`);
  root.style.setProperty("--widget-radius", `${safeNumber(bubble.border_radius, DEFAULT_TOKENS.bubble.border_radius)}px`);
  root.style.setProperty("--widget-position", String(bubble.position || DEFAULT_TOKENS.bubble.position));
  root.style.setProperty("--widget-size", String(bubble.size || DEFAULT_TOKENS.bubble.size));
  root.style.setProperty("--widget-tone", String(tone));
}
