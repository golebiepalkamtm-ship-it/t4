import { createFileRoute } from "@tanstack/react-router";
import {
  AlertTriangle,
  Cookie,
  FileWarning,
  Accessibility,
  MousePointerClick,
  ShieldAlert,
  Scale,
  Code2,
  LayoutDashboard,
  Lock,
  FileCheck2,
  ShieldCheck,
  Quote,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { ContactForm } from "@/components/ContactForm";
import { SiteFooter } from "@/components/SiteFooter";
import { CookieConsent } from "@/components/CookieConsent";
import { Shield3D } from "@/components/Shield3D";
import heroBg from "@/assets/hero-audit.jpg";

export const Route = createFileRoute("/")({
  head: () => ({
    meta: [
      { title: "Audyt zgodności strony i sklepu — RODO, Omnibus, WCAG, OWASP" },
      {
        name: "description",
        content:
          "Niezależny audyt prawny, techniczny, UX i bezpieczeństwa stron oraz sklepów internetowych. Raport niezgodności i wytyczne naprawcze w 7 dni.",
      },
      { property: "og:title", content: "Audyt zgodności strony i sklepu internetowego" },
      {
        property: "og:description",
        content:
          "Wykrywamy błędy prawne, luki bezpieczeństwa, dark patterns i bariery dostępności, zanim zrobi to UOKiK lub UODO.",
      },
      { property: "og:type", content: "website" },
      { name: "twitter:card", content: "summary_large_image" },
    ],
  }),
  component: Index,
});

const problems = [
  {
    icon: FileWarning,
    tag: "Dyrektywa Omnibus",
    title: "Promocje bez najniższej ceny z 30 dni",
    body: "Brak informacji o najniższej cenie z ostatnich 30 dni to najczęściej kwestionowana praktyka w e-commerce. Kara UOKiK: do 10% obrotu z poprzedniego roku.",
  },
  {
    icon: Cookie,
    tag: "RODO / ePrivacy",
    title: "Nielegalne banery cookies",
    body: "Domyślnie zaznaczona analityka, brak równorzędnego „Odrzuć wszystkie”, skrypty ładowane przed zgodą. To zgoda nieważna z mocy prawa — i gotowy materiał dowodowy dla UODO.",
  },
  {
    icon: Scale,
    tag: "Prawo konsumenckie",
    title: "Luki i klauzule abuzywne w regulaminach",
    body: "Skopiowane regulaminy zawierają postanowienia z rejestru klauzul niedozwolonych, błędne terminy odstąpienia i wadliwą procedurę reklamacji zgodności towaru z umową.",
  },
  {
    icon: Accessibility,
    tag: "EAA / WCAG 2.1",
    title: "Wykluczenie użytkowników z niepełnosprawnościami",
    body: "Kontrast poniżej 4.5:1, brak obsługi klawiatury, pola bez etykiet. Europejski Akt o Dostępności obejmuje handel elektroniczny — a to także realna utrata konwersji.",
  },
  {
    icon: MousePointerClick,
    tag: "DSA / UOKiK",
    title: "Dark patterns w ścieżce zakupowej",
    body: "Fałszywe liczniki czasu, dosprzedaż w koszyku, ukryte koszty, utrudniona rezygnacja z subskrypcji. Rozporządzenie DSA zakazuje takich interfejsów wprost.",
  },
  {
    icon: ShieldAlert,
    tag: "Bezpieczeństwo",
    title: "Luki techniczne i wycieki danych",
    body: "Nieaktualne wtyczki, brak nagłówków bezpieczeństwa, otwarte endpointy i formularze bez ochrony. Naruszenie ochrony danych to obowiązek zgłoszenia w 72 godziny.",
  },
];

const pillars = [
  {
    icon: Scale,
    step: "Filar 01",
    title: "Zgodność prawna",
    items: [
      "Regulamin, polityka prywatności i cookies — weryfikacja klauzulowa",
      "Dyrektywa Omnibus, prawa konsumenta, informacje przedumowne",
      "Obowiązki informacyjne RODO (art. 13/14) i rejestr czynności",
      "Wymogi DSA: punkt kontaktowy, zgłaszanie treści, zakaz dark patterns",
    ],
  },
  {
    icon: Code2,
    step: "Filar 02",
    title: "Warstwa techniczna",
    items: [
      "Realny audyt skryptów: co ładuje się przed zgodą użytkownika",
      "Core Web Vitals, indeksacja, błędy renderowania i przekierowań",
      "Poprawność wdrożenia Consent Mode v2 i tagów pomiarowych",
      "Semantyka HTML i struktura nagłówków",
    ],
  },
  {
    icon: LayoutDashboard,
    step: "Filar 03",
    title: "UX/UI i dostępność",
    items: [
      "WCAG 2.1 AA: kontrast, fokus, nawigacja klawiaturą, czytniki ekranu",
      "Identyfikacja dark patterns w koszyku i procesie rejestracji",
      "Czytelność formularzy, komunikatów błędów i ścieżki rezygnacji",
      "Mobilne cele dotykowe i realna użyteczność na małych ekranach",
    ],
  },
  {
    icon: Lock,
    step: "Filar 04",
    title: "Bezpieczeństwo danych",
    items: [
      "Przegląd wg metodyki OWASP Top 10 (bez testów penetracyjnych inwazyjnych)",
      "Nagłówki bezpieczeństwa, TLS, konfiguracja ciasteczek i sesji",
      "Transfery danych poza EOG i umowy powierzenia z dostawcami",
      "Retencja danych i procedura reagowania na incydenty",
    ],
  },
];

const standards = [
  { name: "RODO / GDPR", desc: "Rozporządzenie 2016/679 oraz decyzje i wytyczne EROD i UODO" },
  { name: "Dyrektywa Omnibus", desc: "Ustawa o informowaniu o cenach oraz praktyki UOKiK" },
  { name: "DSA", desc: "Rozporządzenie 2022/2065 o usługach cyfrowych" },
  { name: "WCAG 2.1 AA", desc: "Standard dostępności i Europejski Akt o Dostępności" },
  { name: "OWASP Top 10", desc: "Branżowa metodyka oceny ryzyk aplikacji webowych" },
  { name: "ePrivacy", desc: "Prawo telekomunikacyjne — art. 173 i zasady zgody cookies" },
];

function Index() {
  return (
    <div className="min-h-dvh bg-background">
      <header className="sticky top-0 z-40 border-b border-border bg-background/80 backdrop-blur">
        <div className="mx-auto flex max-w-6xl items-center justify-between px-5 py-4">
          <a href="#" className="flex items-center gap-2 font-display font-semibold">
            <ShieldCheck className="size-5 text-accent" aria-hidden="true" />
            Audyt Zgodności
          </a>
          <nav aria-label="Główna" className="hidden gap-7 text-sm text-muted-foreground md:flex">
            <a href="#ryzyka" className="hover:text-foreground">Ryzyka</a>
            <a href="#audyt" className="hover:text-foreground">Przebieg audytu</a>
            <a href="#standardy" className="hover:text-foreground">Standardy</a>
            <a href="#kontakt" className="hover:text-foreground">Kontakt</a>
          </nav>
          <Button variant="outlineStrong" size="sm" asChild>
            <a href="#kontakt">Bezpłatny pre-audyt</a>
          </Button>
        </div>
      </header>

      <main>
        {/* HERO */}
        <section className="relative overflow-hidden">
          <img
            src={heroBg}
            alt=""
            aria-hidden="true"
            width={1920}
            height={1088}
            className="absolute inset-0 size-full object-cover opacity-15"
          />
          <div
            className="absolute inset-0 bg-[image:var(--gradient-veil)]"
            aria-hidden="true"
          />
          <div className="absolute inset-0 grid-lines opacity-40" aria-hidden="true" />

          <div className="relative mx-auto grid max-w-6xl gap-12 px-5 py-24 md:py-32 lg:grid-cols-[minmax(0,1fr)_auto] lg:items-center">
            <div>
            <p className="inline-flex items-center gap-2 rounded-full border border-border bg-card/70 px-4 py-1.5 text-xs font-medium tracking-wide text-muted-foreground backdrop-blur">
              <AlertTriangle className="size-3.5 text-warning" aria-hidden="true" />
              Kontrole UOKiK i UODO obejmują dziś także małe sklepy i strony usługowe
            </p>

            <h1 className="mt-7 max-w-4xl text-4xl font-bold leading-[1.08] md:text-6xl">
              Sprawdzamy Twoją stronę tak, jak zrobiłby to urząd — zanim on to zrobi.
            </h1>

            <p className="mt-6 max-w-2xl text-lg leading-relaxed text-muted-foreground">
              Kompleksowy audyt prawny, techniczny, UX i bezpieczeństwa serwisów oraz sklepów
              internetowych. Wykrywamy naruszenia RODO, dyrektywy Omnibus, DSA i WCAG, luki OWASP
              oraz dark patterns. Kary UOKiK sięgają 10% rocznego obrotu, a kary UODO — 20 mln EUR
              lub 4% globalnego obrotu. Do tego dochodzi to, czego nie da się odzyskać: zaufanie
              klientów.
            </p>

            <div className="mt-10 flex flex-col items-start gap-3 sm:flex-row sm:items-center">
              <Button variant="cta" size="xl" asChild>
                <a href="#kontakt">Zamów bezpłatny pre-audyt strony</a>
              </Button>
              <Button variant="outlineStrong" size="xl" asChild>
                <a href="#audyt">Zobacz zakres audytu</a>
              </Button>
            </div>

            {/* Klauzula informacyjna RODO bezpośrednio pod CTA */}
            <p className="mt-5 max-w-2xl text-xs leading-relaxed text-muted-foreground">
              Administratorem Twoich danych jest AUDYT ZGODNOŚCI Sp. z o.o. z siedzibą w Warszawie.
              Dane podane w formularzu przetwarzamy wyłącznie w celu przygotowania odpowiedzi i
              oferty (art. 6 ust. 1 lit. b RODO). Podanie danych jest dobrowolne, lecz niezbędne do
              kontaktu. Masz prawo dostępu do danych, ich sprostowania, usunięcia, ograniczenia
              przetwarzania, sprzeciwu i przenoszenia oraz wniesienia skargi do Prezesa UODO.
              Szczegóły w Polityce prywatności.
            </p>

            <dl className="mt-14 grid max-w-3xl grid-cols-2 gap-6 border-t border-border pt-8 md:grid-cols-4">
              {[
                ["10%", "obrotu — maks. kara UOKiK"],
                ["20 mln €", "lub 4% obrotu — kara UODO"],
                ["72 h", "na zgłoszenie naruszenia danych"],
                ["7 dni", "i masz raport niezgodności"],
              ].map(([k, v]) => (
                <div key={v} className="border-l-2 border-accent/50 pl-4">
                  <dt className="font-display text-2xl font-bold tabular-nums text-foreground">{k}</dt>
                  <dd className="mt-1 text-xs text-muted-foreground">{v}</dd>
                </div>
              ))}
            </dl>
            </div>
            <Shield3D />
          </div>
        </section>

        {/* PROBLEMY */}
        <section id="ryzyka" className="mx-auto max-w-6xl px-5 py-24">
          <p className="eyebrow">Punkty zapalne</p>
          <h2 className="mt-4 max-w-3xl text-3xl font-bold md:text-4xl">
            Sześć nieprawidłowości, które znajdujemy w niemal każdym audycie
          </h2>
          <p className="mt-4 max-w-2xl text-muted-foreground">
            Każda z nich jest jednocześnie ryzykiem finansowym i wyciekiem konwersji. Usunięcie ich
            kosztuje ułamek tego, co jedno postępowanie wyjaśniające.
          </p>

          <ul className="mt-12 grid gap-5 md:grid-cols-2 lg:grid-cols-3">
            {problems.map(({ icon: Icon, tag, title, body }) => (
              <li
                key={title}
                className="card-lift group rounded-lg border border-border bg-card p-6"
              >
                <span className="inline-flex size-11 items-center justify-center rounded-md bg-warning/15 text-warning ring-1 ring-warning/25">
                  <Icon className="size-5" aria-hidden="true" />
                </span>
                <p className="mt-5 text-[11px] font-semibold uppercase tracking-widest text-muted-foreground">
                  {tag}
                </p>
                <h3 className="mt-2 text-lg font-semibold">{title}</h3>
                <p className="mt-3 text-sm leading-relaxed text-muted-foreground">{body}</p>
              </li>
            ))}
          </ul>
        </section>

        {/* ROZWIĄZANIE */}
        <section id="audyt" className="border-y border-border bg-card/30">
          <div className="mx-auto max-w-6xl px-5 py-24">
            <p className="eyebrow">Przebieg audytu</p>
            <h2 className="mt-4 max-w-3xl text-3xl font-bold md:text-4xl">
              Cztery filary kontroli. Jeden dokument, z którym idziesz do developera.
            </h2>

            <ol className="mt-12 grid gap-5 md:grid-cols-2">
              {pillars.map(({ icon: Icon, step, title, items }) => (
                <li key={title} className="card-lift relative overflow-hidden rounded-lg border border-border bg-background p-7">
                  <span
                    aria-hidden="true"
                    className="pointer-events-none absolute -right-2 top-1 select-none font-display text-7xl font-bold text-primary/6"
                  >
                    {step.slice(-2)}
                  </span>
                  <div className="flex items-center gap-3">
                    <span className="inline-flex size-11 items-center justify-center rounded-md bg-primary/12 text-primary ring-1 ring-primary/25">
                      <Icon className="size-5" aria-hidden="true" />
                    </span>
                    <div>
                      <p className="text-[11px] font-semibold uppercase tracking-widest text-muted-foreground">
                        {step}
                      </p>
                      <h3 className="text-lg font-semibold">{title}</h3>
                    </div>
                  </div>
                  <ul className="mt-5 space-y-2.5">
                    {items.map((i) => (
                      <li key={i} className="flex gap-3 text-sm text-muted-foreground">
                        <FileCheck2 className="mt-0.5 size-4 shrink-0 text-accent" aria-hidden="true" />
                        <span>{i}</span>
                      </li>
                    ))}
                  </ul>
                </li>
              ))}
            </ol>

            <div className="panel-soft mt-10 rounded-lg border border-accent/40 p-7">
              <h3 className="flex items-center gap-2 text-lg font-semibold">
                <FileCheck2 className="size-5 text-accent" aria-hidden="true" />
                Co dokładnie otrzymujesz
              </h3>
              <div className="mt-5 grid gap-6 md:grid-cols-3">
                {[
                  ["Raport niezgodności", "Lista wykryć z przypisaną podstawą prawną, dowodem (zrzut, żądanie sieciowe) i oceną ryzyka: krytyczne / wysokie / średnie."],
                  ["Wytyczne naprawcze", "Konkretne instrukcje wdrożeniowe dla developera i gotowe treści klauzul — nie ogólniki, tylko „zmień to na to”."],
                  ["Plan priorytetów", "Kolejność napraw według ekspozycji na karę i wpływu na konwersję, z szacowanym nakładem prac oraz retestem po wdrożeniu."],
                ].map(([t, d]) => (
                  <div key={t} className="border-t-2 border-accent/40 pt-4">
                    <p className="font-display font-semibold">{t}</p>
                    <p className="mt-2 text-sm text-muted-foreground">{d}</p>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </section>

        {/* ZAUFANIE */}
        <section id="standardy" className="mx-auto max-w-6xl px-5 py-24">
          <p className="eyebrow">Podstawa metodyczna</p>
          <h2 className="mt-4 max-w-3xl text-3xl font-bold md:text-4xl">
            Nie opinie. Obowiązujące przepisy i uznane standardy branżowe.
          </h2>

          <ul className="mt-12 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {standards.map(({ name, desc }) => (
              <li key={name} className="card-lift rounded-lg border border-border bg-card p-5">
                <p className="flex items-center gap-2 font-display font-semibold">
                  <ShieldCheck className="size-4 text-accent" aria-hidden="true" />
                  {name}
                </p>
                <p className="mt-1.5 text-sm text-muted-foreground">{desc}</p>
              </li>
            ))}
          </ul>

          <div className="mt-14 grid gap-5 md:grid-cols-3">
            {[
              ["Audyt wykrył ładowanie skryptów marketingowych przed zgodą. Poprawka zajęła dzień, a zdjęła z nas realne ryzyko postępowania.", "Miejsce na referencję — sklep e-commerce"],
              ["Dostaliśmy dokument, który developer mógł wdrożyć bez tłumaczenia prawa. To był pierwszy audyt, który faktycznie zamknęliśmy.", "Miejsce na referencję — agencja marketingowa"],
              ["Uporządkowanie regulaminu i ścieżki reklamacyjnej ograniczyło spory z klientami i liczbę zwrotów spornych.", "Miejsce na referencję — firma usługowa"],
            ].map(([quote, author]) => (
              <figure key={author} className="card-lift rounded-lg border border-border bg-card p-6">
                <Quote className="size-6 text-primary/70" aria-hidden="true" />
                <blockquote className="mt-4 text-sm leading-relaxed text-foreground">
                  „{quote}”
                </blockquote>
                <figcaption className="mt-4 border-t border-border pt-3 text-xs text-muted-foreground">
                  {author}
                </figcaption>
              </figure>
            ))}
          </div>
        </section>

        {/* KONTAKT */}
        <section id="kontakt" className="border-t border-border bg-card/30">
          <div className="mx-auto grid max-w-6xl gap-12 px-5 py-24 lg:grid-cols-2">
            <div>
              <p className="eyebrow">Pierwszy krok</p>
              <h2 className="mt-4 text-3xl font-bold md:text-4xl">
                Bezpłatny pre-audyt: 10 kluczowych punktów kontrolnych
              </h2>
              <p className="mt-5 text-muted-foreground">
                Sprawdzamy Twoją stronę pod kątem dziesięciu najczęściej karanych nieprawidłowości i
                odsyłamy podsumowanie w ciągu jednego dnia roboczego. Bez zobowiązań i bez cyklu
                sprzedażowego — jeśli wszystko jest w porządku, tak właśnie napiszemy.
              </p>
              <ul className="mt-8 space-y-3 text-sm text-muted-foreground">
                {[
                  "Weryfikacja banera cookies i skryptów ładowanych przed zgodą",
                  "Kontrola prezentacji cen pod kątem dyrektywy Omnibus",
                  "Szybki przegląd dostępności wg WCAG 2.1 AA",
                  "Podstawowe nagłówki bezpieczeństwa i konfiguracja TLS",
                ].map((i) => (
                  <li key={i} className="flex gap-3">
                    <ShieldCheck className="mt-0.5 size-4 shrink-0 text-accent" aria-hidden="true" />
                    {i}
                  </li>
                ))}
              </ul>
            </div>
            <ContactForm />
          </div>
        </section>
      </main>

      <SiteFooter />
      <CookieConsent />
    </div>
  );
}
