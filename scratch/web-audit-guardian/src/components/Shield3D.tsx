import { useCallback, useEffect, useRef, useState } from "react";
import { RotateCw } from "lucide-react";
import shield from "@/assets/shield-front.png";

/**
 * Interaktywny obiekt 3D — obrót pełne 360°.
 * Sterowanie: przeciąganie myszą/palcem, strzałki na klawiaturze, autorotacja.
 */
export function Shield3D() {
  const [angle, setAngle] = useState(-18);
  const [dragging, setDragging] = useState(false);
  const [auto, setAuto] = useState(true);
  const last = useRef<number | null>(null);

  useEffect(() => {
    if (!auto || dragging) return;
    let raf = 0;
    let prev = performance.now();
    const tick = (t: number) => {
      const dt = t - prev;
      prev = t;
      setAngle((a) => a + dt * 0.02);
      raf = requestAnimationFrame(tick);
    };
    raf = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(raf);
  }, [auto, dragging]);

  const onPointerDown = useCallback((e: React.PointerEvent) => {
    (e.target as HTMLElement).setPointerCapture(e.pointerId);
    last.current = e.clientX;
    setDragging(true);
    setAuto(false);
  }, []);

  const onPointerMove = useCallback(
    (e: React.PointerEvent) => {
      if (!dragging || last.current === null) return;
      const dx = e.clientX - last.current;
      last.current = e.clientX;
      setAngle((a) => a + dx * 0.6);
    },
    [dragging],
  );

  const endDrag = useCallback(() => {
    setDragging(false);
    last.current = null;
  }, []);

  const onKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "ArrowLeft" || e.key === "ArrowRight") {
      e.preventDefault();
      setAuto(false);
      setAngle((a) => a + (e.key === "ArrowRight" ? 15 : -15));
    }
  };

  const normalized = ((Math.round(angle) % 360) + 360) % 360;

  return (
    <figure className="flex flex-col items-center gap-4">
      <div
        role="img"
        tabIndex={0}
        aria-label={`Trójwymiarowy model tarczy zgodności, obrócony o ${normalized} stopni. Użyj strzałek w lewo i w prawo, aby obracać.`}
        onPointerDown={onPointerDown}
        onPointerMove={onPointerMove}
        onPointerUp={endDrag}
        onPointerCancel={endDrag}
        onKeyDown={onKeyDown}
        className="relative grid size-64 cursor-grab touch-none select-none place-items-center rounded-full outline-none ring-offset-4 ring-offset-background focus-visible:ring-2 focus-visible:ring-accent active:cursor-grabbing md:size-80"
        style={{ perspective: "1000px" }}
      >
        <div
          className="absolute inset-6 rounded-full bg-[radial-gradient(circle,color-mix(in_oklch,var(--color-accent)_22%,transparent),transparent_70%)] blur-2xl"
          aria-hidden="true"
        />
        <div
          className="relative size-full"
          style={{
            transform: `rotateY(${angle}deg)`,
            transformStyle: "preserve-3d",
          }}
        >
          {/* Przód */}
          <img
            src={shield}
            alt=""
            aria-hidden="true"
            width={1024}
            height={1024}
            draggable={false}
            className="absolute inset-0 size-full object-contain drop-shadow-[0_25px_40px_rgba(15,23,42,0.25)] [backface-visibility:hidden]"
            style={{ transform: "translateZ(12px)" }}
          />
          {/* Tył — lustrzane odbicie, przyciemnione */}
          <img
            src={shield}
            alt=""
            aria-hidden="true"
            width={1024}
            height={1024}
            draggable={false}
            className="absolute inset-0 size-full object-contain brightness-[0.62] saturate-[0.7] [backface-visibility:hidden]"
            style={{ transform: "rotateY(180deg) translateZ(12px) scaleX(-1)" }}
          />
          {/* Warstwy krawędzi dające grubość bryły */}
          {[-8, -4, 0, 4, 8].map((z) => (
            <img
              key={z}
              src={shield}
              alt=""
              aria-hidden="true"
              draggable={false}
              className="absolute inset-0 size-full object-contain brightness-[0.45]"
              style={{ transform: `translateZ(${z}px)` }}
            />
          ))}
        </div>
      </div>
      <figcaption className="flex items-center gap-2 text-xs text-muted-foreground">
        <RotateCw className="size-3.5 text-accent" aria-hidden="true" />
        Przeciągnij, aby obrócić model o 360°
      </figcaption>
    </figure>
  );
}