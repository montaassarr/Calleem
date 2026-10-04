/**
 * Business facts used by the public legal pages (/terms, /privacy, /refund).
 * Edit the values here and every legal page updates. Values marked TODO(owner)
 * must be confirmed by the business owner before the pages are relied on.
 */
export interface LegalInfo {
  /** Product / brand name shown to customers. */
  brand: string;
  /** Registered legal name of the seller (company or sole trader). */
  legalName: string;
  /** Where legal, privacy, billing and refund requests go (the website contact form). */
  contactUrl: string;
  /** Public website URL. */
  website: string;
  /** Country where the seller is established. */
  country: string;
  /** Law that governs the Terms of Service. */
  governingLaw: string;
  /** Date shown as "Last updated" on every legal page. */
  lastUpdated: string;
}

export const LEGAL: Readonly<LegalInfo> = {
  brand: "Calleem",
  legalName: "Calleem", // Pre-launch name; replace with the registered business name once it exists
  contactUrl: "/contact", // TODO(owner): add a support email here too once one is active
  website: "https://calleem.tech",
  country: "Malaysia", // TODO(owner): confirm the country where the seller is registered
  governingLaw: "Malaysia", // TODO(owner): confirm the governing law for the Terms
  lastUpdated: "October 4, 2026",
};

/**
 * How the seller is named in legal text, e.g. "Acme SARL (trading as Calleem)",
 * or just "Calleem" while the legal name and brand are the same.
 */
export const SELLER_NAME: string =
  LEGAL.legalName.trim() === LEGAL.brand.trim()
    ? LEGAL.brand
    : `${LEGAL.legalName} (trading as ${LEGAL.brand})`;

/** The website address without the protocol, e.g. "calleem.tech". */
export const WEBSITE_HOST: string = LEGAL.website.replace(/^https?:\/\//, "").replace(/\/$/, "");
