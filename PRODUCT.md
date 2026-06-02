# Product

## Register

product

## Users

Contract supervisors, administrators, and technical operators in the infrastructure/telecommunications sector. They open the dashboard from a desktop at the office to review contract status, validate milestones, and track financial execution. They are comfortable with government-contract terminology but not necessarily with technology. Speed and clarity matter more than visual novelty.

## Product Purpose

ORBIT SERVIALCO is a contract-management dashboard for SERVIALCO's infrastructure projects. It centralizes contract data (financial values, timelines, extensions, additions) and progress tracking across operational modules (surveys, installations, splicing, routing). Success means an operator can open any page and understand the contract state in under 10 seconds without training.

## Brand Personality

Authoritative. Precise. Trustworthy.

The interface should feel like a well-run government contractor's reporting tool: dense where it needs to be, clean where it can afford to be, never flashy. No consumer-app aesthetics. No startup softness. Think: a professional engineering dashboard, not a SaaS landing page.

## Anti-references

- Consumer SaaS dashboards with gradients, animations, and card carousels
- Landing-page aesthetics applied to app UI (big display type, centred hero layouts)
- "Dark mode by default because it looks cool" without operational justification
- Figma-template dashboards with pastel KPI cards and circular progress charts
- Any interface that would make a 55-year-old civil engineer uncomfortable

## Design Principles

1. **Clarity over decoration** - Every visual element must earn its place by communicating information. Decoration that doesn't add meaning is removed.
2. **Density is a feature** - This is a tool for professionals who need to read multiple data points at a glance. Tight spacing is a virtue when it serves comprehension.
3. **Predictable structure** - The same data type always looks the same. Dates, currencies, statuses, and labels use consistent formatting across every page.
4. **Status at a glance** - A user should be able to determine the health of a contract (time progress, financial state, active/inactive) within 3 seconds of loading the page.
5. **Trust through precision** - No fake data, no rounded numbers presented as exact, no "—" where a real value should be. When a value is missing, say why.

## Accessibility & Inclusion

- WCAG AA minimum for all text contrast
- Dark mode supported via `[data-theme="dark"]` (already implemented)
- No motion-dependent information (prefers-reduced-motion respected)
- Keyboard-navigable primary actions
