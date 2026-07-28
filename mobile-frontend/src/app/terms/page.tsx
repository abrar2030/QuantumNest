import type { Metadata } from "next";
import { PublicShell } from "@/components/layout/public-shell";

export const metadata: Metadata = { title: "Terms of Service" };

const sections = [
  {
    title: "1. Acceptance of terms",
    body: "By creating an account or using QuantumNest Capital, you agree to be bound by these Terms of Service and our Privacy Policy.",
  },
  {
    title: "2. Not financial advice",
    body: "QuantumNest provides analytics, forecasts, and AI-generated recommendations for informational purposes only. Nothing on the platform constitutes financial, investment, tax, or legal advice. You are solely responsible for your investment decisions.",
  },
  {
    title: "3. Account responsibilities",
    body: "You are responsible for maintaining the confidentiality of your credentials and for all activity that occurs under your account. Notify us immediately of any unauthorized use.",
  },
  {
    title: "4. Tokenized and blockchain assets",
    body: "Interactions with smart contracts and blockchain networks are irreversible by nature. QuantumNest is not responsible for losses resulting from network congestion, smart contract risk, or third-party wallet issues.",
  },
  {
    title: "5. Acceptable use",
    body: "You agree not to misuse the platform, attempt to disrupt its infrastructure, or use it for unlawful purposes, including market manipulation or money laundering.",
  },
  {
    title: "6. Service availability",
    body: "We aim for high availability but do not guarantee uninterrupted access. Scheduled maintenance and unforeseen outages may occur.",
  },
  {
    title: "7. Limitation of liability",
    body: "To the maximum extent permitted by law, QuantumNest and its affiliates are not liable for indirect, incidental, or consequential damages arising from use of the platform.",
  },
  {
    title: "8. Changes to these terms",
    body: "We may revise these terms from time to time. Continued use of the platform after changes constitutes acceptance of the revised terms.",
  },
];

export default function TermsPage() {
  return (
    <PublicShell>
      <div className="container max-w-3xl py-16 sm:py-24">
        <p className="text-xs font-semibold uppercase tracking-widest text-primary">
          Legal
        </p>
        <h1 className="mt-3 font-display text-3xl font-semibold sm:text-4xl">
          Terms of Service
        </h1>
        <p className="mt-3 text-sm text-muted-foreground">
          Last updated: January 2026
        </p>

        <div className="mt-10 space-y-8">
          {sections.map((section) => (
            <div key={section.title}>
              <h2 className="font-display text-lg font-semibold">
                {section.title}
              </h2>
              <p className="mt-2 text-sm leading-relaxed text-muted-foreground">
                {section.body}
              </p>
            </div>
          ))}
        </div>
      </div>
    </PublicShell>
  );
}
