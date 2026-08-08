import { useState, useId } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import { Label } from "@/components/ui/label";
import { Checkbox } from "@/components/ui/checkbox";
import { toast } from "sonner";

export function ContactForm() {
  const id = useId();
  // Zgody NIGDY nie są domyślnie zaznaczone (art. 7 RODO, motyw 32).
  const [consentContact, setConsentContact] = useState(false);
  const [consentMarketing, setConsentMarketing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  return (
    <form
      noValidate
      onSubmit={(e) => {
        e.preventDefault();
        if (!consentContact) {
          setError("Aby wysłać zgłoszenie, wymagana jest zgoda na kontakt w sprawie zapytania.");
          return;
        }
        setError(null);
        toast.success("Zgłoszenie przyjęte. Odpowiadamy w ciągu 1 dnia roboczego.");
      }}
      className="space-y-5 rounded-lg border border-border bg-card p-6 shadow-[var(--shadow-elevated)]"
    >
      <div className="grid gap-5 sm:grid-cols-2">
        <div className="space-y-2">
          <Label htmlFor={`${id}-name`}>Imię i nazwisko *</Label>
          <Input id={`${id}-name`} name="name" autoComplete="name" required />
        </div>
        <div className="space-y-2">
          <Label htmlFor={`${id}-email`}>Służbowy e-mail *</Label>
          <Input id={`${id}-email`} name="email" type="email" autoComplete="email" required />
        </div>
      </div>
      <div className="space-y-2">
        <Label htmlFor={`${id}-url`}>Adres strony do audytu *</Label>
        <Input id={`${id}-url`} name="url" type="url" placeholder="https://" required />
      </div>
      <div className="space-y-2">
        <Label htmlFor={`${id}-msg`}>Zakres i kontekst (opcjonalnie)</Label>
        <Textarea id={`${id}-msg`} name="message" rows={4} />
      </div>

      <fieldset className="space-y-4 rounded-md border border-border p-4">
        <legend className="px-1 text-xs font-semibold uppercase tracking-widest text-muted-foreground">
          Zgody
        </legend>

        <div className="flex items-start gap-3">
          <Checkbox
            id={`${id}-c1`}
            checked={consentContact}
            onCheckedChange={(v) => setConsentContact(v === true)}
            aria-describedby={`${id}-c1-d`}
          />
          <Label htmlFor={`${id}-c1`} id={`${id}-c1-d`} className="text-xs font-normal leading-relaxed text-muted-foreground">
            * Wyrażam zgodę na przetwarzanie moich danych osobowych podanych w formularzu przez
            AUDYT ZGODNOŚCI Sp. z o.o. w celu udzielenia odpowiedzi na moje zapytanie i
            przedstawienia oferty audytu (art. 6 ust. 1 lit. a i b RODO).
          </Label>
        </div>

        <div className="flex items-start gap-3">
          <Checkbox
            id={`${id}-c2`}
            checked={consentMarketing}
            onCheckedChange={(v) => setConsentMarketing(v === true)}
            aria-describedby={`${id}-c2-d`}
          />
          <Label htmlFor={`${id}-c2`} id={`${id}-c2-d`} className="text-xs font-normal leading-relaxed text-muted-foreground">
            (Opcjonalnie) Wyrażam zgodę na otrzymywanie informacji handlowych drogą elektroniczną
            oraz kontakt telefoniczny w celach marketingowych (art. 10 ustawy o świadczeniu usług
            drogą elektroniczną i art. 172 Prawa telekomunikacyjnego). Zgoda nie jest warunkiem
            wysłania formularza.
          </Label>
        </div>

        <p className="text-[11px] leading-relaxed text-muted-foreground">
          Administratorem danych jest AUDYT ZGODNOŚCI Sp. z o.o., ul. Przykładowa 12/3, 00-001
          Warszawa. Kontakt do IOD: iod@example.pl. Dane przetwarzamy w celu obsługi zapytania, a za
          zgodą — także marketingowo. Przysługuje Ci prawo dostępu, sprostowania, usunięcia,
          ograniczenia i przenoszenia danych, sprzeciwu oraz wycofania zgody w dowolnym momencie
          (bez wpływu na legalność wcześniejszego przetwarzania), a także skargi do Prezesa UODO.
          Dane przechowujemy maks. 24 miesiące od ostatniego kontaktu. Szczegóły: Polityka
          prywatności.
        </p>
      </fieldset>

      {error && (
        <p role="alert" className="text-sm font-medium text-destructive">
          {error}
        </p>
      )}

      <Button type="submit" variant="cta" size="xl" className="w-full">
        Zamów bezpłatny pre-audyt
      </Button>
      <p className="text-center text-[11px] text-muted-foreground">
        Wysyłając formularz nie zawierasz umowy. Pre-audyt jest bezpłatny i niezobowiązujący.
      </p>
    </form>
  );
}