import { Fragment_Mono, Newsreader, Onest } from 'next/font/google';

/** One loaded instance per family, exposed through CSS variables. */
export const newsreader=Newsreader({
  subsets:['latin'],
  style:['normal','italic'],
  variable:'--font-newsreader',
  display:'swap',
});

export const onest=Onest({
  subsets:['latin'],
  variable:'--font-onest',
  display:'swap',
});

export const fragmentMono=Fragment_Mono({
  subsets:['latin'],
  weight:'400',
  variable:'--font-fragment-mono',
  display:'swap',
});
