import Link from "next/link";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

export default function UpdatePasswordPage() {
  return (
    <div className="container py-12">
      <Card className="mx-auto max-w-3xl">
        <CardHeader>
          <CardTitle>Archived Password Route</CardTitle>
          <CardDescription>
            Password-management screens have been removed from the default
            open-source clipping product.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <p className="text-sm text-muted-foreground">
            If you decide to ship optional hosted auth later, you can rebuild
            password reset and account management on top of the remaining auth
            API routes. They are no longer part of the core clipping workflow.
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
  );
}
