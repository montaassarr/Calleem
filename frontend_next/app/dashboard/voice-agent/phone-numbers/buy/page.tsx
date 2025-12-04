"use client";

import { useEffect, useMemo, useState } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert";
import { Label } from "@/components/ui/label";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { useMutation, useQuery } from "@tanstack/react-query";
import { toast } from "sonner";
import { voiceApi } from "@/lib/api-endpoints";
import { Phone, ArrowLeft, Plug, ShieldCheck, ExternalLink, AlertTriangle, CheckCircle2, Loader2, ShoppingCart } from "lucide-react";
import type { VoiceAgentStatus } from "@/lib/types";

interface ProvisioningStep {
  title: string;
  description: string;
}

export default function BuyPhoneNumberPage() {
  const [status, setStatus] = useState<VoiceAgentStatus | null>(null);
  const [statusError, setStatusError] = useState<string | null>(null);
  const [loadingStatus, setLoadingStatus] = useState(true);
  const [selectedCountry, setSelectedCountry] = useState("US");
  const [areaCode, setAreaCode] = useState("");
  const [availableNumbers, setAvailableNumbers] = useState<any[]>([]);
  const [searching, setSearching] = useState(false);

  const { data: countries } = useQuery({
    queryKey: ["livekit", "countries"],
    queryFn: () => voiceApi.listCountries(),
  });

  const {
    data: ownedNumbers,
    refetch: refetchOwned,
    isLoading: ownedLoading,
  } = useQuery({
    queryKey: ["livekit", "numbers"],
    queryFn: () => voiceApi.listNumbers(),
  });

  const purchaseMutation = useMutation({
    mutationFn: (phoneNumber: string) =>
      voiceApi.purchaseNumber({ country: selectedCountry, phone_number: phoneNumber }),
    onSuccess: () => {
      toast.success("Number purchased and wired to Parker");
      refetchOwned();
      setAvailableNumbers([]);
    },
    onError: (error: any) => {
      const detail = error?.response?.data?.detail ?? "Unable to purchase number";
      toast.error(detail);
    },
  });

  useEffect(() => {
    let mounted = true;
    const fetchStatus = async () => {
      try {
        const data = await voiceApi.testAgent();
        if (mounted) setStatus(data);
      } catch (error: any) {
        const detail = error?.response?.data?.detail ?? "Unable to load LiveKit status";
        if (mounted) setStatusError(detail);
      } finally {
        if (mounted) setLoadingStatus(false);
      }
    };
    fetchStatus();
    return () => {
      mounted = false;
    };
  }, []);

  const livekitConfigured = Boolean(status?.configured);
  const voiceAgentEnabled = Boolean(status?.voice_agent_enabled);
  const primaryNumber = ownedNumbers?.[0]?.phone_number;

  const countryOptions = useMemo(() => {
    if (!countries) return [];
    return countries.map((country: any) => ({
      code: country.code || country.iso_code,
      name: country.name,
    }));
  }, [countries]);

  const searchNumbers = async () => {
    setSearching(true);
    try {
      const response = await voiceApi.searchNumbers({
        country: selectedCountry,
        area_code: areaCode || undefined,
      });
      setAvailableNumbers(response.numbers || []);
    } catch (error: any) {
      const detail = error?.response?.data?.detail ?? "Unable to fetch numbers";
      toast.error(detail);
    } finally {
      setSearching(false);
    }
  };

  const provisioningSteps: ProvisioningStep[] = [
    {
      title: "Reserve or port a DID inside LiveKit",
      description: "Use the LiveKit Console (Voice → Numbers) to provision a number or import an existing carrier." ,
    },
    {
      title: "Map the number to your Parker queue",
      description: "Point the LiveKit call flow to queue " + (status?.agent_queue || "parker-receptionist") + " and reuse the same assistant profile you preview in the dashboard.",
    },
    {
      title: "Forward call-end webhooks",
      description: "Set the webhook target to /api/v1/webhook/livekit/call-ended so Parker can log transcripts and trigger automations.",
    },
  ];

  const openLiveKitConsole = () => {
    window.open("https://cloud.livekit.io/", "_blank");
  };

  const emailSupport = () => {
    window.open("mailto:support@parkerlabs.ai?subject=LiveKit%20Number%20Request", "_blank");
  };

  return (
    <div className="container mx-auto p-6 space-y-6">
      <div className="flex items-center gap-4">
        <Button variant="ghost" onClick={() => window.history.back()}>
          <ArrowLeft className="w-4 h-4 mr-2" />
          Back
        </Button>
        <div>
          <h1 className="text-3xl font-bold">Provision LiveKit Numbers</h1>
          <p className="text-muted-foreground mt-1">
            LiveKit now powers telephony. Follow the steps below to connect a DID to your Parker receptionist.
          </p>
        </div>
      </div>

      <Alert>
        <AlertTitle>LiveKit telephony rollout</AlertTitle>
        <AlertDescription>
          Numbers are now provisioned inside LiveKit instead of Vapi. Use this page as a checklist to request or port a
          DID, then map it to your Parker queue.
        </AlertDescription>
      </Alert>

      {!loadingStatus && !livekitConfigured && (
        <Alert variant="destructive">
          <AlertTriangle className="w-4 h-4" />
          <AlertTitle>LiveKit credentials missing</AlertTitle>
          <AlertDescription>
            Set LIVEKIT_URL, LIVEKIT_API_KEY, and LIVEKIT_API_SECRET in the backend environment before provisioning phone numbers.
          </AlertDescription>
        </Alert>
      )}

      {statusError && (
        <Alert variant="destructive">
          <AlertDescription>{statusError}</AlertDescription>
        </Alert>
      )}

      <div className="grid grid-cols-1 gap-4 xl:grid-cols-3">
        <Card className="xl:col-span-2">
          <CardHeader>
            <CardTitle>Search LiveKit Numbers</CardTitle>
            <CardDescription>Choose a country and optional area code to reserve a DID.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-1 gap-4 md:grid-cols-3">
              <div>
                <Label htmlFor="country">Country</Label>
                <Select value={selectedCountry} onValueChange={setSelectedCountry}>
                  <SelectTrigger id="country">
                    <SelectValue placeholder="Select country" />
                  </SelectTrigger>
                  <SelectContent>
                    {countryOptions
                      .filter(country => Boolean(country.code))
                      .map(country => (
                        <SelectItem key={country.code} value={country.code}>
                          {country.name}
                        </SelectItem>
                      ))}
                  </SelectContent>
                </Select>
              </div>

              <div>
                <Label htmlFor="area">Area Code (optional)</Label>
                <Input
                  id="area"
                  placeholder="415"
                  value={areaCode}
                  onChange={event => setAreaCode(event.target.value)}
                />
              </div>

              <div className="flex items-end">
                <Button className="w-full" onClick={searchNumbers} disabled={searching || !selectedCountry}>
                  {searching ? (
                    <>
                      <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                      Searching
                    </>
                  ) : (
                    "Search"
                  )}
                </Button>
              </div>
            </div>

            {availableNumbers.length > 0 && (
              <div className="space-y-3">
                {availableNumbers.map(number => (
                  <div key={number.phone_number} className="flex flex-col gap-3 rounded-lg border p-4 md:flex-row md:items-center md:justify-between">
                    <div>
                      <p className="text-lg font-semibold">{number.phone_number}</p>
                      <p className="text-sm text-muted-foreground">{number.location || number.region || "Global"}</p>
                    </div>
                    <div className="flex flex-col items-start gap-2 md:flex-row md:items-center">
                      <div className="text-sm text-muted-foreground">
                        Monthly {number.monthly_cost ? `$${number.monthly_cost.toFixed?.(2)}` : "included"}
                      </div>
                      <Button
                        size="sm"
                        disabled={purchaseMutation.isPending}
                        onClick={() => purchaseMutation.mutate(number.phone_number)}
                      >
                        {purchaseMutation.isPending ? (
                          <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                        ) : (
                          <ShoppingCart className="mr-2 h-4 w-4" />
                        )}
                        Reserve
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Your Numbers</CardTitle>
            <CardDescription>LiveKit DID inventory tied to this tenant.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            {ownedLoading && <p className="text-sm text-muted-foreground">Loading numbers...</p>}
            {!ownedLoading && (!ownedNumbers || ownedNumbers.length === 0) && (
              <p className="text-sm text-muted-foreground">No numbers yet. Purchase one to unlock PSTN routing.</p>
            )}
            {ownedNumbers?.map((item: any) => (
              <div key={item.id} className="rounded-lg border p-3">
                <div className="flex items-center justify-between">
                  <p className="font-semibold">{item.phone_number}</p>
                  <Badge variant={item.status === "active" ? "default" : "secondary"}>{item.status}</Badge>
                </div>
                <p className="text-xs text-muted-foreground">{item.country}</p>
                {item.trunks && (
                  <p className="text-xs text-muted-foreground">Trunks: {item.trunks}</p>
                )}
              </div>
            ))}
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Platform status</CardTitle>
            <CardDescription>Snapshot from /voice-agent/status</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">LiveKit credentials</p>
                <p className="text-sm font-medium truncate max-w-[200px]">{status?.url || "Not configured"}</p>
              </div>
              <Badge variant={livekitConfigured ? "default" : "destructive"}>
                {livekitConfigured ? "Configured" : "Missing"}
              </Badge>
            </div>
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Voice agent toggle</p>
                <p className="text-sm font-medium">{voiceAgentEnabled ? "Enabled" : "Disabled"}</p>
              </div>
              <Badge variant={voiceAgentEnabled ? "default" : "secondary"}>
                {voiceAgentEnabled ? "Active" : "Off"}
              </Badge>
            </div>
              {primaryNumber && (
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-muted-foreground">Primary number</p>
                  <p className="text-sm font-medium">{primaryNumber}</p>
                </div>
                <Badge variant="outline">{status?.number_status || "provisioning"}</Badge>
              </div>
            )}
            <div className="flex items-center justify-between">
              <div>
                <p className="text-sm text-muted-foreground">Queue name</p>
                <p className="text-sm font-medium">{status?.agent_queue || "n/a"}</p>
              </div>
              <Badge variant="outline">{status?.agent_name || "LiveKit Agent"}</Badge>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Need a number fast?</CardTitle>
            <CardDescription>We'll provision the LiveKit queue for you.</CardDescription>
          </CardHeader>
          <CardContent className="space-y-3">
            <Button className="w-full" onClick={openLiveKitConsole}>
              <ExternalLink className="w-4 h-4 mr-2" />
              Open LiveKit Console
            </Button>
            <Button variant="secondary" className="w-full" onClick={emailSupport}>
              <Phone className="w-4 h-4 mr-2" />
              Email Parker Support
            </Button>
            <p className="text-xs text-muted-foreground">
              💡 Invite-only SIP trunking is rolling out now. Opening a ticket gets you fast-tracked and ensures numbers are
              auto-wired into Parker’s analytics + automations.
            </p>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>LiveKit provisioning checklist</CardTitle>
          <CardDescription>Follow these steps to attach a DID to Parker.</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {provisioningSteps.map((step, index) => (
            <div key={step.title} className="flex gap-4">
              <div className="flex h-10 w-10 items-center justify-center rounded-full bg-primary/10 text-primary">
                {index === 0 && <Plug className="w-5 h-5" />}
                {index === 1 && <ShieldCheck className="w-5 h-5" />}
                {index === 2 && <CheckCircle2 className="w-5 h-5" />}
              </div>
              <div>
                <p className="font-medium">{step.title}</p>
                <p className="text-sm text-muted-foreground">{step.description}</p>
              </div>
            </div>
          ))}
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>FAQ</CardTitle>
        </CardHeader>
        <CardContent className="space-y-3 text-sm text-muted-foreground">
          <p><strong>Where are numbers billed?</strong> LiveKit bills minutes + DIDs directly. Parker only meters AI usage.</p>
          <p><strong>Can I keep my carrier?</strong> Yes. Point your downstream SIP trunk to LiveKit or forward to your Parker queue.</p>
          <p><strong>What about SMS?</strong> SMS routing remains on Twilio for now. Voice stays entirely inside LiveKit.</p>
        </CardContent>
      </Card>

    </div>
  );
}
