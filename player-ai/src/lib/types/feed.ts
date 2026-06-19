export interface FeedPost {
  post_id: string;
  presenter_id: string;
  title: string;
  description: string;
  body?: string;           // full post content
  video_url: string;
  date_posted: string;
  tags: string;           // pipe-separated
  position_tags: string;  // pipe-separated
  coming_soon: boolean;
}
