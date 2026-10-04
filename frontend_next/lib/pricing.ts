/**
 * Calleem's usage-based pricing: a business picks how many calls it gets a month and how long they
 * last, and the monthly price covers the voice cost plus a target margin. Used by the landing page
 * calculator and the dashboard billing page. The backend charges with the same model
 * (backend/services/usage_billing.py: PRICING and quote()); keep the numbers and steps identical.
 */

export interface PricingModel {
    costPerMinute: number;
    costPerCall: number;
    infraPerMonth: number;
    /** 0.40 = 40% of the price is profit. */
    margin: number;
}

export const PRICING: PricingModel = {
    costPerMinute: 0.082,
    costPerCall: 0.1,
    infraPerMonth: 30,
    margin: 0.4,
};

export const USAGE_LIMITS = {
    minCalls: 100,
    /** Above this, self-serve stops: "Talk to us". */
    maxCalls: 4500,
    minAvgMinutes: 1,
    maxAvgMinutes: 15,
} as const;

export interface Quote {
    /** Monthly price in USD, rounded to end in 9. */
    price: number;
    /** Call minutes included each month. */
    minutes: number;
    variableCost: number;
    totalCost: number;
    profit: number;
    /** Actual margin after rounding, in percent. */
    marginPct: number;
}

export function quotePrice(calls: number, avgMinutes: number, model: PricingModel = PRICING): Quote {
    const variableCost = calls * (model.costPerCall + avgMinutes * model.costPerMinute);
    const totalCost = variableCost + model.infraPerMonth;
    const margin = Math.min(model.margin, 0.95);
    const rawRevenue = totalCost / (1 - margin);
    let price = Math.ceil(rawRevenue / 10) * 10 - 1;
    const floorPrice = Math.ceil((model.infraPerMonth * 1.5) / 10) * 10 - 1;
    if (price < floorPrice) price = floorPrice;
    const profit = price - totalCost;
    return {
        price,
        minutes: Math.round(calls * avgMinutes),
        variableCost,
        totalCost,
        profit,
        marginPct: (profit / price) * 100,
    };
}
