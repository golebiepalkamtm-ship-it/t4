import { ShieldCheck } from "lucide-react";

export function SiteFooter() {
  return (
    <footer className="border-t-2 border-primary/25 bg-card/60">
      <div className="mx-auto max-w-6xl px-5 py-14">
        <div className="grid gap-10 md:grid-cols-3">
          <div>
            <p className="flex items-center gap-2 font-display text-lg font-semibold">
              <span className="inline-flex size-9 items-center justify-center rounded-md bg-accent/12 ring-1 ring-accent/25">
                <ShieldCheck className="size-5 text-accent" aria-hidden="true" />
              </span>
              Audyt Zgodności
            </p>
            <p className="mt-3 text-sm text-muted-foreground">
              Niezależny audyt prawny, techniczny i UX serwisów internetowych oraz sklepów
              e-commerce.
            </p>
          </div>

          <div>
            <h2 className="border-b border-border pb-2 text-sm font-semibold uppercase tracking-widest text-muted-foreground">
              Dane rejestrowe
            </h2>
            <address className="mt-3 space-y-1 text-sm not-italic text-muted-foreground">
              <p className="text-foreground">AUDYT ZGODNOŚCI Sp. z o.o.</p>
              <p>ul. Przykładowa 12/3, 00-001 Warszawa</p>
              <p>NIP: 000-000-00-00</p>
              <p>REGON: 000000000</p>
              <p>KRS: 0000000000, Sąd Rejonowy dla m.st. Warszawy, XII Wydział Gospodarczy</p>
              <p>Kapitał zakładowy: 50 000,00 PLN (wpłacony w całości)</p>
              <p>
                E-mail:{" "}
                <a className="text-primary underline underline-offset-4" href="mailto:kontakt@example.pl">
                  kontakt@example.pl
                </a>{" "}
                · Tel.{" "}
                <a className="text-primary underline underline-offset-4" href="tel:+48000000000">
                  +48 000 000 000
                </a>
              </p>
              <p>
                Inspektor Ochrony Danych:{" "}
                <a className="text-primary underline underline-offset-4" href="mailto:iod@example.pl">
                  iod@example.pl
                </a>
              </p>
            </address>
          </div>

          <nav aria-label="Informacje prawne">
            <h2 className="border-b border-border pb-2 text-sm font-semibold uppercase tracking-widest text-muted-foreground">
              Informacje prawne
            </h2>
            <ul className="mt-3 space-y-2 text-sm">
              {[
                "Regulamin świadczenia usług",
                "Polityka prywatności",
                "Polityka cookies",
                "Deklaracja dostępności (WCAG 2.1 AA)",
                "Informacja o przetwarzaniu danych (art. 13 RODO)",
                "Procedura reklamacji i odstąpienia od umowy",
                "Zgłaszanie nielegalnych treści (DSA)",
              ].map((label) => (
                <li key={label}>
                  <a href="#" className="text-muted-foreground underline-offset-4 hover:text-foreground hover:underline">
                    {label}
                  </a>
                </li>
              ))}
              <li>
                <button
                  type="button"
                  onClick={() => window.dispatchEvent(new Event("open-cookie-settings"))}
                  className="text-muted-foreground underline-offset-4 hover:text-foreground hover:underline"
                >
                  Zmień ustawienia cookies
                </button>
              </li>
            </ul>
          </nav>
        </div>

        <p className="mt-12 border-t border-border pt-6 text-xs leading-relaxed text-muted-foreground">
          Pozasądowe rozwiązywanie sporów konsumenckich: platforma ODR Komisji Europejskiej oraz
          Wojewódzkie Inspektoraty Inspekcji Handlowej. Podmiotom niebędącym konsumentami powyższe
          uprawnienia nie przysługują. Treści serwisu mają charakter informacyjny i nie stanowią
          porady prawnej w rozumieniu ustawy o radcach prawnych.
        </p>
        <p className="mt-4 text-xs text-muted-foreground">
          © {new Date().getFullYear()} AUDYT ZGODNOŚCI Sp. z o.o. Wszelkie prawa zastrzeżone.
        </p>
      </div>
    </footer>
  );
}