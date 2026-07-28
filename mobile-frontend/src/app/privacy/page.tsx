import type { Metadata } from "next";
import { PublicShell } from "@/components/layout/public-shell";

export const metadata: Metadata = { title: "Privacy Policy" };

const sections = [
  {
    title: "1. Information we collect",
    body: "We collect account information (name, email, authentication credentials), portfolio and transaction data you create on the platform, and technical data such as device and usage information necessary to operate and secure the service.",
  },
  {
    title: "2. How we use your information",
    body: "Your information is used to provide portfolio tracking, AI-driven analytics, blockchain integrations, and account security features. We do not sell your personal data to third parties.",
  },
  {
    title: "3. AI and market data processing",
    body: "Market, sentiment, and portfolio data may be processed by our AI models to generate forecasts, recommendations, and risk assessments. These outputs are informational and not financial advice.",
  },
  {
    title: "4. Data retention",
    body: "We retain account and portfolio data for as long as your account is active, or as needed to comply with legal obligations, resolve disputes, and enforce our agreements.",
  },
  {
    title: "5. Security",
    body: "We use industry-standard practices including encrypted transport, hashed credentials, and role-based access control to protect your data. No system is completely secure, and we encourage strong, unique passwords.",
  },
  {
    title: "6. Your choices",
    body: "You may update your profile information at any time from Settings, and may request account deletion by contacting support.",
  },
  {
    title: "7. Changes to this policy",
    body: "We may update this policy periodically. Material changes will be communicated within the platform.",
  },
];

export default function PrivacyPage() {
  return (
    <PublicShell>
      <div className="container max-w-3xl py-16 sm:py-24">
        <p className="text-xs font-semibold uppercase tracking-widest text-primary">
          Legal
        </p>
        <h1 className="mt-3 font-display text-3xl font-semibold sm:text-4xl">
          Privacy Policy
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
