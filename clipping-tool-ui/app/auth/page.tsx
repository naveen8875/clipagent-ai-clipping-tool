import Link from "next/link";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

export default function AuthPage() {
  return (
    <div className="min-h-screen bg-background">
      <div className="container flex min-h-screen items-center justify-center py-12">
        <Card className="w-full max-w-2xl">
          <CardHeader>
            <CardTitle>Archived Account Route</CardTitle>
            <CardDescription>
              The open-source clipping workflow does not require sign-in by
              default.
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <p className="text-sm text-muted-foreground">
              This route is kept only as a placeholder for teams that want to
              wire optional Supabase authentication back into the project. The
              main product flow is the local project upload and processing flow
              available from the homepage.
            </p>
            <div className="flex gap-3">
              <Button asChild>
                <Link href="/">Go to Clipping Dashboard</Link>
              </Button>
              <Button asChild variant="outline">
                <Link href="/profile">View Archive Notice</Link>
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
