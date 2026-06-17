import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export default function CreditsPage() {
  return (
    <div className="container mx-auto max-w-3xl py-10">
      <Card>
        <CardHeader>
          <CardTitle>Credits Are Disabled in Local Mode</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3 text-sm text-muted-foreground">
          <p>
            The original hosted product included credit-based usage controls.
            The default open-source self-hosted workflow does not depend on that
            system.
          </p>
          <p>
            Use the home page to create and monitor clipping projects directly
            against the backend.
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
