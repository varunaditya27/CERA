import { Fragment_Mono, Geologica, Onest } from 'next/font/google';

/**
 * Geologica includes the Sharpness axis: one coherent family can shift from
 * clear technical prose to a sharply cut custom display character.
 */
export const geologica=Geologica({
 subsets:['latin'],
 axes:['SHRP'],
 variable:'--font-geologica',
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
