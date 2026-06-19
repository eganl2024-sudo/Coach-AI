export interface ReelSubmission {
  id: string;
  username: string;
  clip_path: string;
  clip_name: string;
  title: string;
  notes: string;
  duration_seconds: number;
  uploaded_at: string;
  submit_for_review: boolean;
  reviewer_id: string;
  review_question: string;
  review_status: 'not_submitted' | 'pending' | 'reviewed';
  reviewer_response: string;
  reviewed_at: string | null;
}
