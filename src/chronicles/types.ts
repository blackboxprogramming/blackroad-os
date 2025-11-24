export interface Episode {
  id: string;
  title: string;
  agent: string;
  date: string;
  mp3: string;
  transcript: boolean;
}

export interface Chronicles {
  episodes: Episode[];
}

export interface EpisodeFrontmatter {
  id: string;
  title: string;
  agent: string;
  date: string;
  voice: string;
  transcript: boolean;
}
