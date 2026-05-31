# Pricing Module Architecture

## Data Flow

```
 Caller
   │
   │  items: [(name, qty, price), ...]
   │  country: ISO-2 str
   │  customer: {vip?, coupon?} | None
   ▼
┌─────────────────────────────────────┐
│              calc()                 │
│                                     │
│  ┌──────────────┐                   │
│  │  Item Filter │ skip None /       │
│  │              │ bad-shape /       │
│  │              │ qty≤0 / price≤0   │
│  └──────┬───────┘                   │
│         │ valid (qty, price)        │
│  ┌──────▼───────┐                   │
│  │  Discount    │ VIP → ×0.9        │
│  │  Engine      │ SAVE10 → ×0.9     │
│  │              │ SAVE20 → ×0.8     │
│  └──────┬───────┘                   │
│         │ line total                │
│  ┌──────▼───────┐                   │
│  │  Subtotal    │ Σ line totals     │
│  │  Accumulator │                   │
│  └──────┬───────┘                   │
│         │ subtotal                  │
│  ┌──────▼───────┐  ┌─────────────┐  │
│  │  Tax Lookup  │◄─│ _TAX_RATES  │  │
│  │              │  │ dict        │  │
│  └──────┬───────┘  └─────────────┘  │
│         │ tax                       │
│  ┌──────▼───────┐                   │
│  │  Shipping    │ <50 → $9.99       │
│  │  Tier        │ <200 → $4.99      │
│  │              │ ≥200 → free       │
│  └──────┬───────┘                   │
│         │                           │
│   round(subtotal + tax + ship, 2)   │
└─────────────────┬───────────────────┘
                  │
                  ▼ float (2 decimal places)
```

## Components

**Item Filter** — Guards the loop body. Drops `None` entries, tuples that aren't length-3, and any item where `qty <= 0` or `price <= 0`. Inputs: raw item from the caller's list. Output: unpacked `(qty, price)` or skipped.

**Discount Engine** — Applies at most one discount multiplier per line item. VIP membership takes precedence over coupons. Recognized coupons: `SAVE10` (10% off), `SAVE20` (20% off). Unknown coupons are silently ignored. Input: `line` subtotal + `customer` dict. Output: adjusted `line`.

**Subtotal Accumulator** — Sums discounted line totals across all valid items. Input: per-line floats. Output: single `subtotal` float.

**Tax Lookup** — Multiplies `subtotal` by the rate from `_TAX_RATES`. Unknown countries default to 10%. Input: `subtotal`, `country`. Output: `tax` float.

**Shipping Tier** — Three-bracket threshold on `subtotal` (pre-tax). Input: `subtotal`. Output: `ship` flat fee.

## Known Limitations

1. **No compound discounts** — VIP and coupon cannot stack; VIP always wins silently.
2. **Tax applied to pre-discount subtotal is wrong** — tax is correctly on the discounted subtotal, but shipping threshold is also pre-tax, which may not match jurisdictional rules.
3. **Float arithmetic** — no `Decimal` usage; rounding is deferred to the final return, which can produce ±$0.01 drift on large orders with many items.
4. **`_TAX_RATES` is a module-level mutable dict** — callers can mutate it at runtime; there is no protection against accidental modification.
5. **Item name is unused** — the first tuple element is unpacked as `_` and discarded; any name-based pricing logic would require a signature change.
