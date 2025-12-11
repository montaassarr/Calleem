"use client";

import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { ArrowLeft, Phone } from "lucide-react";

export default function BuyPhoneNumberPage() {
  return (
    <div className="container mx-auto p-6 space-y-6">
      <div className="flex items-center gap-4">
        <Button variant="ghost" onClick={() => window.history.back()}>
          <ArrowLeft className="w-4 h-4 mr-2" />
          Back
        </Button>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Phone Number Provisioning</CardTitle>
        </CardHeader>
        <CardContent className="text-center py-12">
          <Phone className="w-12 h-12 mx-auto text-muted-foreground mb-4" />
          <h2 className="text-xl font-semibold mb-2">Coming Soon</h2>
          <p className="text-muted-foreground mb-6">
            Direct phone number purchasing via Vapi is being integrated.
            <br />
            Please contact support to provision a number manually for now.
          </p>
          <Button onClick={() => window.open('mailto:support@callflow.ai')}>
            Contact Support
          </Button>
        </CardContent>
      </Card>
    </div>
  );
}
