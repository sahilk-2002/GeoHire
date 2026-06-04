---
name: Pathfinder
colors:
  surface: '#f8f9ff'
  surface-dim: '#cbdbf5'
  surface-bright: '#f8f9ff'
  surface-container-lowest: '#ffffff'
  surface-container-low: '#eff4ff'
  surface-container: '#e5eeff'
  surface-container-high: '#dce9ff'
  surface-container-highest: '#d3e4fe'
  on-surface: '#0b1c30'
  on-surface-variant: '#464555'
  inverse-surface: '#213145'
  inverse-on-surface: '#eaf1ff'
  outline: '#777587'
  outline-variant: '#c7c4d8'
  surface-tint: '#4d44e3'
  primary: '#3525cd'
  on-primary: '#ffffff'
  primary-container: '#4f46e5'
  on-primary-container: '#dad7ff'
  inverse-primary: '#c3c0ff'
  secondary: '#006a61'
  on-secondary: '#ffffff'
  secondary-container: '#86f2e4'
  on-secondary-container: '#006f66'
  tertiary: '#684000'
  on-tertiary: '#ffffff'
  tertiary-container: '#885500'
  on-tertiary-container: '#ffd4a4'
  error: '#ba1a1a'
  on-error: '#ffffff'
  error-container: '#ffdad6'
  on-error-container: '#93000a'
  primary-fixed: '#e2dfff'
  primary-fixed-dim: '#c3c0ff'
  on-primary-fixed: '#0f0069'
  on-primary-fixed-variant: '#3323cc'
  secondary-fixed: '#89f5e7'
  secondary-fixed-dim: '#6bd8cb'
  on-secondary-fixed: '#00201d'
  on-secondary-fixed-variant: '#005049'
  tertiary-fixed: '#ffddb8'
  tertiary-fixed-dim: '#ffb95f'
  on-tertiary-fixed: '#2a1700'
  on-tertiary-fixed-variant: '#653e00'
  background: '#f8f9ff'
  on-background: '#0b1c30'
  surface-variant: '#d3e4fe'
typography:
  headline-lg:
    fontFamily: Inter
    fontSize: 32px
    fontWeight: '700'
    lineHeight: 40px
    letterSpacing: -0.02em
  headline-lg-mobile:
    fontFamily: Inter
    fontSize: 26px
    fontWeight: '700'
    lineHeight: 32px
    letterSpacing: -0.02em
  headline-md:
    fontFamily: Inter
    fontSize: 24px
    fontWeight: '600'
    lineHeight: 32px
    letterSpacing: -0.01em
  headline-sm:
    fontFamily: Inter
    fontSize: 20px
    fontWeight: '600'
    lineHeight: 28px
  body-lg:
    fontFamily: Inter
    fontSize: 18px
    fontWeight: '400'
    lineHeight: 28px
  body-md:
    fontFamily: Inter
    fontSize: 16px
    fontWeight: '400'
    lineHeight: 24px
  body-sm:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '400'
    lineHeight: 20px
  label-md:
    fontFamily: Inter
    fontSize: 14px
    fontWeight: '600'
    lineHeight: 20px
    letterSpacing: 0.05em
  label-sm:
    fontFamily: Inter
    fontSize: 12px
    fontWeight: '500'
    lineHeight: 16px
rounded:
  sm: 0.25rem
  DEFAULT: 0.5rem
  md: 0.75rem
  lg: 1rem
  xl: 1.5rem
  full: 9999px
spacing:
  base: 4px
  xs: 4px
  sm: 8px
  md: 16px
  lg: 24px
  xl: 32px
  container-margin: 16px
  gutter: 12px
---

## Brand & Style

The design system is built on the pillars of **Trust, Efficiency, and Momentum**. It caters to ambitious professionals who value clarity and speed in their career transitions. The visual language is **Corporate Modern**, blending the reliability of traditional finance with the agility of high-growth technology.

The UI avoids clutter, favoring high-quality typography and strategic whitespace to reduce cognitive load during the high-stakes activity of job seeking. Every interaction should feel intentional and supportive, guiding the user toward their next career milestone with confidence.

## Colors

The palette is anchored by **Deep Indigo**, signaling authority and professional stability. **Vibrant Teal** is reserved for primary actions—applying to jobs and confirming success—associating the color with career progression. 

**High-contrast Amber** acts as a strategic disruptor for "Hot Jobs" or "Expiring Soon" tags, ensuring urgency is felt without causing alarm. Backgrounds utilize a "Paper and Ink" philosophy, using slightly off-white surfaces to reduce eye strain during long browsing sessions.

## Typography

The design system utilizes **Inter** for its exceptional legibility and systematic weight distribution. 

- **Headlines:** Use Bold (700) or SemiBold (600) weights with slightly tightened letter-spacing to create a strong visual anchor for job titles.
- **Metadata:** Details such as salary ranges and locations should use `body-sm` with a Medium (500) weight in a neutral gray color to create a clear information hierarchy below the job title.
- **Labels:** Use `label-md` for section headers or small buttons, utilizing uppercase styling to differentiate functional text from editorial content.

## Layout & Spacing

This design system employs a **Fluid Grid** model optimized for mobile-first consumption. 

- **Grid:** A 4-column layout for mobile with 16px outer margins and 12px gutters.
- **Rhythm:** An 8px linear scale (4, 8, 16, 24, 32, 48, 64) ensures consistent vertical rhythm. 
- **Touch Targets:** All interactive elements maintain a minimum 44x44px hit area. 
- **Safe Areas:** On mobile devices, ensure content respects the bottom home indicator and top status bar, using large 24px-32px padding for screen headers to provide a "premium" feel.

## Elevation & Depth

Hierarchy is established through **Tonal Layers** supplemented by **Ambient Shadows**. 

- **Surface Level (0dp):** The main background uses `#F8FAFC`.
- **Card Level (1dp):** Interactive job cards use white (`#FFFFFF`) with a subtle 4px blur, 10% opacity black shadow. This creates a soft lift that invites clicking.
- **Navigation/Modals (2dp):** Floating action buttons (FABs) and bottom sheets use a more pronounced shadow (12px blur, 15% opacity) to signify they sit atop the primary information plane.
- **Outlines:** Use 1px borders in `#E2E8F0` for non-interactive containers or to define input fields, maintaining a clean, flat appearance.

## Shapes

The shape language is consistently **Rounded**, using a 12px base radius for cards and containers. This softens the "corporate" edge of the brand, making the app feel more approachable and modern.

- **Small elements (Chips, Tags):** Use a 6px radius.
- **Standard elements (Buttons, Input Fields):** Use an 8px radius.
- **Large elements (Job Cards, Modals):** Use a 16px radius.

## Components

- **Buttons:** Primary buttons use the Vibrant Teal background with white text and 8px corners. Secondary buttons use a Deep Indigo outline.
- **Job Cards:** White background, 16px rounded corners, and a subtle shadow. The job title is always `headline-sm` in Deep Indigo.
- **Status Chips:** Use a light tint of the status color (e.g., Light Teal for "Applied", Light Amber for "Hot Job") with high-saturation text for readability.
- **Input Fields:** 1px `#E2E8F0` border, 8px radius. On focus, the border transitions to Deep Indigo 2px.
- **Progress Steppers:** Use a thin Teal line to represent the application lifecycle, providing immediate visual feedback on the user's status.
- **Lists:** Clean dividers (`#F1F5F9`) with 16px vertical padding between items, ensuring each job entry has room to breathe.