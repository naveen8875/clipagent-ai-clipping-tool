import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";

export default function BillingPage() {
  return (
    <div className="container mx-auto max-w-3xl py-10">
      <Card>
        <CardHeader>
          <CardTitle>Billing Is Not Part of the Default Open-Source Flow</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3 text-sm text-muted-foreground">
          <p>
            This UI was originally built with SaaS-oriented billing and subscription
            features. Those flows are being isolated from the default self-hosted
            clipping product.
          </p>
          <p>
            For the open-source version, the main experience is the project-based
            clipping workflow on the home page.
          </p>
        </CardContent>
      </Card>
    </div>
  );
}
