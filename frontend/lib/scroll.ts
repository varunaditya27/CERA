/**
 * Reset page navigation without inheriting CSS smooth scrolling.
 * This is used only for route changes and repeated top-level nav clicks.
 * In-page hash links retain their usual smooth anchor behavior.
 */
export function jumpToPageTop(){
  const root=document.documentElement;
  const previous=root.style.scrollBehavior;
  root.style.scrollBehavior='auto';
  window.scrollTo(0,0);
  root.style.scrollBehavior=previous;
}
