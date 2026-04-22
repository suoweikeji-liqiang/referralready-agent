# Safety and Scope

ReferralReady is intentionally scoped to referral workflow support. It does not provide diagnosis or treatment recommendations.

## Data policy

- Synthetic data only.
- No real PHI.
- Demo patients are explicitly marked `synthetic: true`.
- The data loader fails closed if the patient record is not marked synthetic.

## Medical boundary

ReferralReady may assemble synthetic patient context, list missing referral information, and generate administrative care coordination tasks.

ReferralReady may not diagnose, recommend treatment, replace clinician judgment, or claim clinical validation.
