import Link from "next/link";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

export default function EmailUpdatedPage() {
  return (
    <div className="min-h-screen bg-background">
      <div className="container flex min-h-screen items-center justify-center py-12">
        <Card className="w-full max-w-2xl">
          <CardHeader>
            <CardTitle>Archived Account Callback Route</CardTitle>
            <CardDescription>
              This page is no longer part of the default product flow.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <p className="text-sm text-muted-foreground">
              Email-change confirmation screens were part of the earlier hosted
              account experience. The open-source clipping tool works without
              those flows by default.
            </p>
            <div className="flex gap-3">
              <Button asChild>
                <Link href="/">Go to Clipping Dashboard</Link>
              </Button>
              <Button asChild variant="outline">
                <Link href="/auth">Go to Auth Archive Notice</Link>
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
