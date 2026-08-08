import { useEffect, useState } from "react";
import { Button } from "@/components/ui/button";
import { Switch } from "@/components/ui/switch";
import { Cookie, ShieldCheck } from "lucide-react";

const STORAGE_KEY = "cookie-consent-v1";

type Consent = {
  necessary: true;
  analytics: boolean;
  marketing: boolean;
  date: string;
  version: 1;
};

function save(consent: Omit<Consent, "date" | "version" | "necessary">) {
  const payload: Consent = { necessary: true, ...consent, date: new Date().toISOString(), version: 1 };
  localStorage.setItem(STORAGE_KEY, JSON.stringify(payload));
  // Consent Mode v2 – skrypty analityczne/marketingowe uruchamiane wyłącznie po zgodzie.
  window.dispatchEvent(new CustomEvent("cookie-consent-change", { detail: payload }));
}

export function CookieConsent() {
  const [open, setOpen] = useState(false);
  const [details, setDetails] = useState(false);
  // Wymóg RODO/ePrivacy: zgody nieobowiązkowe DOMYŚLNIE WYŁĄCZONE.
  const [analytics, setAnalytics] = useState(false);
  const [marketing, setMarketing] = useState(false);

  useEffect(() => {
    if (!localStorage.getItem(STORAGE_KEY)) setOpen(true);
    const reopen = () => {
      setDetails(true);
      setOpen(true);
    };
    window.addEventListener("open-cookie-settings", reopen);
    return () => window.removeEventListener("open-cookie-settings", reopen);
  }, []);

  if (!open) return null;

  const decide = (a: boolean, m: boolean) => {
    save({ analytics: a, marketing: m });
    setOpen(false);
  };

  return (
    <div
      role="dialog"
      aria-modal="false"
      aria-labelledby="cookie-title"
      aria-describedby="cookie-desc"
      className="fixed inset-x-0 bottom-0 z-50 border-t border-border bg-card/95 backdrop-blur-md"
    >
      <div className="mx-auto grid max-w-6xl gap-6 px-5 py-6 lg:grid-cols-[1fr_auto] lg:items-start">
        <div>
          <h2 id="cookie-title" className="flex items-center gap-2 text-base font-semibold">
            <Cookie className="size-4 text-accent" aria-hidden="true" />
            Ustawienia plików cookies
          </h2>
          <p id="cookie-desc" className="mt-2 max-w-3xl text-sm text-muted-foreground">
            Używamy plików cookies niezbędnych do działania serwisu. Za Twoją dobrowolną zgodą
            korzystamy także z cookies analitycznych i marketingowych (art. 6 ust. 1 lit. a RODO oraz
            art. 173 Prawa telekomunikacyjnego). Zgoda jest dobrowolna i możesz ją wycofać w każdej
            chwili — bez wpływu na zgodność z prawem przetwarzania sprzed wycofania. Administratorem
            danych jest AUDYT ZGODNOŚCI Sp. z o.o.
          </p>

          {details && (
            <ul className="mt-5 space-y-3">
              <li className="flex items-start justify-between gap-4 rounded-md border border-border bg-background/50 p-4">
                <div>
                  <p className="text-sm font-semibold">Niezbędne (zawsze aktywne)</p>
                  <p className="text-xs text-muted-foreground">
                    Sesja, bezpieczeństwo, zapis Twojego wyboru zgód. Podstawa: prawnie uzasadniony
                    interes — nie wymagają zgody.
                  </p>
                </div>
                <Switch checked disabled aria-label="Cookies niezbędne — zawsze aktywne" />
              </li>
              <li className="flex items-start justify-between gap-4 rounded-md border border-border bg-background/50 p-4">
                <div>
                  <p className="text-sm font-semibold">Analityczne</p>
                  <p className="text-xs text-muted-foreground">
                    Statystyka ruchu i skuteczności treści. Domyślnie wyłączone.
                  </p>
                </div>
                <Switch checked={analytics} onCheckedChange={setAnalytics} aria-label="Cookies analityczne" />
              </li>
              <li className="flex items-start justify-between gap-4 rounded-md border border-border bg-background/50 p-4">
                <div>
                  <p className="text-sm font-semibold">Marketingowe</p>
                  <p className="text-xs text-muted-foreground">
                    Personalizacja reklam i pomiar konwersji. Domyślnie wyłączone.
                  </p>
                </div>
                <Switch checked={marketing} onCheckedChange={setMarketing} aria-label="Cookies marketingowe" />
              </li>
            </ul>
          )}

          <button
            type="button"
            onClick={() => setDetails((d) => !d)}
            className="mt-4 text-xs font-medium text-primary underline underline-offset-4"
          >
            {details ? "Ukryj szczegóły" : "Dostosuj / pokaż kategorie i cele"}
          </button>
        </div>

        <div className="flex w-full flex-col gap-2 lg:w-64">
          {/* Równorzędne przyciski: odrzucenie tak samo łatwe jak akceptacja (zakaz dark patterns). */}
          <Button variant="cta" size="lg" onClick={() => decide(true, true)}>
            Akceptuj wszystkie
          </Button>
          <Button variant="outlineStrong" size="lg" onClick={() => decide(false, false)}>
            Odrzuć wszystkie
          </Button>
          {details && (
            <Button variant="ghost" size="lg" onClick={() => decide(analytics, marketing)}>
              Zapisz mój wybór
            </Button>
          )}
          <p className="flex items-center gap-1.5 text-[11px] text-muted-foreground">
            <ShieldCheck className="size-3.5 text-accent" aria-hidden="true" />
            Brak cookies nie-niezbędnych przed Twoją zgodą.
          </p>
        </div>
      </div>
    </div>
  );
}