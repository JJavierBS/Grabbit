import { type RefObject, useCallback, useEffect } from "react";

/** On a touch screen, focusing the box pops the keyboard over the conversation. */
const isTouch = () => window.matchMedia?.("(pointer: coarse)").matches ?? false;

const isEditable = (el: Element | null) =>
  el instanceof HTMLElement &&
  (el.isContentEditable || Boolean(el.closest("input, textarea, select, [contenteditable]")));

/** Focuses the message box with the caret after any draft; never on a touch screen. */
export function focusComposer(box: HTMLTextAreaElement | null) {
  if (!box || box.disabled || isTouch()) return;
  box.focus({ preventScroll: true });
  box.setSelectionRange(box.value.length, box.value.length);
}

/**
 * Keeps the message box as the place focus comes back to (#188): it takes focus when the chat
 * opens, when a typed character has nowhere else to go, and when the control that held focus
 * leaves the page or turns disabled (a closed alert, a confirmed report, suggestions that
 * went away).
 * Off on touch screens, and while `enabled` is false (the guided demo).
 */
export function useComposerFocus(field: RefObject<HTMLTextAreaElement>, enabled: boolean) {
  const focus = useCallback(() => focusComposer(field.current), [field]);

  useEffect(() => {
    if (enabled) focus();
  }, [enabled, focus]);

  useEffect(() => {
    if (!enabled) return;
    const onKey = (e: KeyboardEvent) => {
      if (e.defaultPrevented || e.ctrlKey || e.metaKey || e.altKey || e.isComposing) return;
      // One printable character; Space and Enter keep working on buttons and links.
      if (e.key.length !== 1 || e.key === " ") return;
      if (isEditable(document.activeElement)) return;
      // Focusing before the default action lands the character in the box.
      focus();
    };
    window.addEventListener("keydown", onKey);
    return () => window.removeEventListener("keydown", onKey);
  }, [enabled, focus]);

  useEffect(() => {
    if (!enabled) return;
    let last: Element | null = null;
    const onFocusIn = (e: FocusEvent) => {
      last = e.target instanceof Element ? e.target : null;
    };
    // A removed or disabled element drops focus to <body> without a reliable blur event in
    // every browser.
    const observer = new MutationObserver(() => {
      if (!last) return;
      const active = document.activeElement;
      if (active === document.body && !last.isConnected) focus();
      // Chromium drops a disabled element's focus to <body>; other engines keep it there.
      else if ((active === document.body || active === last) && last.matches(":disabled")) focus();
    });
    document.addEventListener("focusin", onFocusIn);
    observer.observe(document.body, {
      childList: true,
      subtree: true,
      attributes: true,
      attributeFilter: ["disabled"],
    });
    return () => {
      document.removeEventListener("focusin", onFocusIn);
      observer.disconnect();
    };
  }, [enabled, focus]);

  return focus;
}
