import { Maximize, Minimize } from "lucide-react";
import { useEffect, useState } from "react";
import { Button } from "./Button";

/** Toggles the whole page in and out of full screen; hidden where the browser cannot. */
export function FullscreenButton({ className }: { className?: string }) {
  const [active, setActive] = useState(() => Boolean(document.fullscreenElement));

  useEffect(() => {
    const sync = () => setActive(Boolean(document.fullscreenElement));
    document.addEventListener("fullscreenchange", sync);
    return () => document.removeEventListener("fullscreenchange", sync);
  }, []);

  if (!document.fullscreenEnabled) return null;

  const toggle = () => {
    // A refusal (e.g. no user gesture) leaves the page as it was; nothing to report.
    const request = active
      ? document.exitFullscreen()
      : document.documentElement.requestFullscreen({ navigationUI: "hide" });
    request.catch(() => undefined);
  };

  return (
    <Button
      variant="ghost"
      size="sm"
      className={className}
      aria-label={active ? "Exit full screen" : "Full screen"}
      aria-pressed={active}
      icon={active ? <Minimize aria-hidden="true" /> : <Maximize aria-hidden="true" />}
      onClick={toggle}
    />
  );
}
