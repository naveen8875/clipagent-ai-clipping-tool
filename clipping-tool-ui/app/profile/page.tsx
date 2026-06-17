import Link from "next/link";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

export default function ProfilePage() {
  return (
    <div className="container py-12">
      <Card className="mx-auto max-w-3xl">
        <CardHeader>
          <CardTitle>Archived Profile Route</CardTitle>
          <CardDescription>
            Profile and account-management screens are not part of the default
            open-source clipping workflow.
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <p className="text-sm text-muted-foreground">
            This repository is now centered around local project upload,
            processing, and clip review. If you want multi-user account
            features, you can rebuild them as an optional integration on top of
            the existing backend and UI structure.
          </p>
          <div className="flex gap-3">
            <Button asChild>
              <Link href="/">Go to Clipping Dashboard</Link>
            </Button>
            <Button asChild variant="outline">
              <Link href="/auth">Open Auth Archive Notice</Link>
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
