export type VerificationStatus = 'passed' | 'failed' | string;

export interface Verification {
  status: VerificationStatus;
  notes: string;
}

export interface CategorizedItem {
  line_number: number;
  text_sample: string;
  tags: string[];
  category_confidence: number;
  verification: Verification;
}